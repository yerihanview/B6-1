# B6-1 시연 검증 시나리오 (Demo Scenario)

본 문서는 디지털 서랍장(도서관 스마트 대여/연체 관리 시스템)의 핵심 기능을 단계별로 시연하고 검증하기 위한 가이드입니다. 자동 실행 스크립트를 통한 일괄 시연과 터미널에서 직접 명령어를 입력하는 수동 시연의 두 가지 방법을 제공합니다.

---

## 1. 자동 실행 방법 (demo.sh)

`demo.sh` 스크립트를 실행하면 5단계 시연이 자동으로 구성된 임시 인메모리 환경에서 안전하게 순차 진행됩니다.

- **대화형 단계별 실행 (권장)**:
  ```bash
  bash demo.sh
  ```
  각 단계의 실행 결과와 검증 포인트를 확인한 후 Enter를 누르면 다음 단계로 진행합니다.

- **비대화형 일괄 실행 (E2E 검증)**:
  ```bash
  bash demo.sh --non-interactive
  ```
  사용자 입력 없이 5단계를 연속으로 실행하고 정상 완료(Exit Code 0)를 확인합니다.

---

## 2. 수동 시연 방법 (Step-by-Step)

평가자가 SQLite CLI 또는 Python 대화형 쉘에서 직접 단계를 밟아가며 시스템 동작을 확인할 수 있는 수동 시연 절차입니다.

### [Step 1] 스키마 적재 — 테이블·외래키·인덱스 생성

1. **이 단계에서 하려는 것**:
   - `sql/schema.sql`을 실행하여 4개 테이블(`categories`, `members`, `books`, `rentals`)과 1:N 외래키 관계 3개, 복합 인덱스를 생성하고 외래키 검사(`PRAGMA foreign_keys = ON;`)가 정상 활성화되는지 확인합니다.
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()); print('PRAGMA foreign_keys =', conn.execute('PRAGMA foreign_keys;').fetchone()[0]); print('테이블 목록:', [r[0] for r in conn.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name NOT LIKE \'sqlite_%\' ORDER BY name;')])"
   ```
3. **확인해야 할 것**:
   - `PRAGMA foreign_keys = 1` 활성화 여부
   - 4개 테이블(`books`, `categories`, `members`, `rentals`) 전수 생성 여부
   - `idx_rentals_date` 인덱스 생성 여부
4. **실행 결과 예시**:
   ```text
   PRAGMA foreign_keys = 1
   테이블 목록: ['books', 'categories', 'members', 'rentals']
   ```

### [Step 2] 시드 적재 — 부모에서 자식으로 위상정렬 데이터 입력

1. **이 단계에서 하려는 것**:
   - `sql/seed.sql`을 실행하여 외래키 제약조건을 준수하며 부모 테이블(`categories`, `members`)부터 자식 테이블(`books`, `rentals`) 순으로 50행의 한국어 실데이터를 적재합니다.
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()); conn.executescript(open('sql/seed.sql', encoding='utf-8').read()); print('행 수 집계:', {t: conn.execute(f'SELECT COUNT(*) FROM {t};').fetchone()[0] for t in ('categories','members','books','rentals')})"
   ```
3. **확인해야 할 것**:
   - 테이블당 10행 이상 충족 (`categories: 10`, `members: 12`, `books: 13`, `rentals: 15`, 총 50행)
   - 대여 상태 3종(`RENTED`, `RETURNED`, `OVERDUE`) 골고루 분포
4. **실행 결과 예시**:
   ```text
   행 수 집계: {'categories': 10, 'members': 12, 'books': 13, 'rentals': 15}
   ```

### [Step 3] 15대 쿼리 핵심 시연 — 조인·집계·시계열 분석

1. **이 단계에서 하려는 것**:
   - `sql/queries.sql`에 작성된 15대 핵심 쿼리 중 대표적인 조인 쿼리(Q05), 외부조인 그룹핑 쿼리(Q08), 시계열 집계 쿼리(Q11)를 실행하여 비즈니스 데이터 처리 결과를 확인합니다.
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()); conn.executescript(open('sql/seed.sql', encoding='utf-8').read());
   print('[Q05 도서-카테고리 INNER JOIN 샘플]');
   for r in conn.execute('SELECT b.book_id, b.title, c.category_name, b.price FROM books b JOIN categories c ON b.category_id = c.category_id LIMIT 3;'): print(' ', r);
   print('[Q08 대여 0회 회원 포함 LEFT JOIN 집계]');
   for r in conn.execute('SELECT m.member_id, m.name, COUNT(r.rental_id) FROM members m LEFT JOIN rentals r ON m.member_id = r.member_id GROUP BY m.member_id, m.name ORDER BY 3 DESC LIMIT 4;'): print(' ', r);
   print('[Q11 월별 대여 건수 시계열 집계]');
   for r in conn.execute('SELECT strftime(\'%Y-%m\', rental_date) ym, COUNT(*) FROM rentals GROUP BY ym ORDER BY ym LIMIT 3;'): print(' ', r);"
   ```
3. **확인해야 할 것**:
   - **Q05 (INNER JOIN)**: 도서 13권 전수에 부모 카테고리명이 정확히 매핑되는지 확인
   - **Q08 (LEFT JOIN + COUNT)**: 대여 이력이 없는 회원도 누락 없이 `0`으로 집계되는지 확인
   - **Q11 (strftime + GROUP BY)**: 대여일 기준 월별 대여 추이가 정렬되어 집계되는지 확인
4. **실행 결과 예시**:
   ```text
   [Q05 도서-카테고리 INNER JOIN 샘플]
     (10, '부의 추월차선', '경제경영', 16500)
     (7, '코스모스', '과학', 23000)
     (2, '아몬드', '소설', 13500)
   [Q08 대여 0회 회원 포함 LEFT JOIN 집계]
     (1, '김민준', 3)
     (2, '이서연', 2)
     (3, '박지호', 2)
     (4, '최수아', 2)
   [Q11 월별 대여 건수 시계열 집계]
     ('2026-01', 1)
     ('2026-02', 2)
     ('2026-03', 2)
   ```

### [Step 4] 무결성 제약조건 위반 실증 — 외래키 방어

1. **이 단계에서 하려는 것**:
   - 데이터베이스에 존재하지 않는 회원 ID(`member_id=999`)로 대여 레코드(`rentals`)를 삽입 시도하여, 외래키 참조 무결성 제약조건에 의해 에러가 발생하고 데이터 오염이 원천 차단되는지 실증합니다.
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()); conn.executescript(open('sql/seed.sql', encoding='utf-8').read());
   try:
       conn.execute('INSERT INTO rentals (member_id, book_id, rental_date, due_date, status) VALUES (999, 1, \'2026-11-10\', \'2026-11-24\', \'RENTED\');')
   except sqlite3.IntegrityError as e:
       print('성공적으로 차단됨:', type(e).__name__, '➔', e)"
   ```
3. **확인해야 할 것**:
   - `sqlite3.IntegrityError: FOREIGN KEY constraint failed` 예외 발생 확인
   - rentals 테이블의 기존 행 수가 15행 그대로 유지되는지 확인
4. **실행 결과 예시**:
   ```text
   성공적으로 차단됨: IntegrityError ➔ FOREIGN KEY constraint failed
   ```

### [Step 5] 보너스 분석 산출물 확인

1. **이 단계에서 하려는 것**:
   - 루트 `bonus/` 디렉토리에 위치한 3대 공식 보너스 과제 분석 리포트의 핵심 분석 내용과 결론을 확인합니다.
2. **실행 명령**:
   ```bash
   head -n 25 bonus/JOIN_VS_SUBQUERY.md
   head -n 25 bonus/INTEGRITY_VIOLATION.md
   head -n 25 bonus/KPI_REPORT.md
   ```
3. **확인해야 할 것**:
   - **보너스 1 (`bonus/JOIN_VS_SUBQUERY.md`)**: `INNER JOIN`과 `EXISTS`의 `EXPLAIN QUERY PLAN` 실행계획 차이와 선택 기준 확인
   - **보너스 2 (`bonus/INTEGRITY_VIOLATION.md`)**: 외래키 위반 재현 코드 및 트랜잭션·어플리케이션 방어 3책 확인
   - **보너스 3 (`bonus/KPI_REPORT.md`)**: 도서관 운영 3대 KPI(회전율, 최다도서, 연체율) 실측 수치와 개선 액션 확인
4. **실행 결과 예시**:
   - 각 마크다운 문서의 개요 및 비교 분석 표 정상 출력
