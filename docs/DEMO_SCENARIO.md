# B6-1 시연 검증 시나리오 (Demo Scenario)

본 문서는 디지털 서랍장(도서관 스마트 대여/연체 관리 시스템)의 핵심 기능을 단계별로 시연하고 검증하기 위한 가이드입니다. 자동 실행 스크립트(`demo.sh`)를 통한 일괄 시연과 터미널에서 직접 명령어를 입력하는 수동 시연의 두 가지 방법을 모두 제공합니다.

---

## 0. SQL 실행 환경 및 Python 런타임 사용 사유

시연 명령에서 `python3`를 활용하는 이유는 다음과 같습니다:
1. **설치 제로(Zero-Dependency) 환경 보장**: Windows, Mac, Linux 어디서나 별도의 `sqlite3` CLI 바이너리 설치(`apt-get` 또는 환경변수 설정) 없이 Python 표준 라이브러리의 내장 `sqlite3` 모듈로 100% 동일하게 즉시 실행됩니다.
2. **외래키 검사(`PRAGMA foreign_keys = ON;`)의 결정론적 강제**: SQLite CLI는 세션 분리 시 FK 검사가 꺼질 위험이 있으나, Python 스크립트는 세션 연결 즉시 FK를 엄격하게 활성화하여 무결성을 보장합니다.
3. **인메모리 격리(`:memory:`)를 통한 파일시스템 무오염**: 디스크에 임시 DB 파일을 남기지 않고 즉시 실행 및 자동 소멸됩니다.
4. **예외 포착(Try-Except) 가독성**: Step 4 외래키 위반 시 CLI의 비정상 종료(exit 1) 대신 `IntegrityError`를 예외 객체로 포착하여 직관적인 실증 메시지를 출력합니다.

*(※ 평가자가 순수 SQLite CLI 환경을 선호할 경우, `sqlite3 library.db < sql/schema.sql` 등 순수 CLI 명령어로도 100% 동일하게 동작합니다.)*

---

## 1. 자동 실행 방법 (demo.sh)

`demo.sh` 스크립트를 실행하면 5단계 시연 및 보너스 3종이 자동으로 구성된 임시 인메모리 환경에서 안전하게 순차 진행됩니다.

- **대화형 단계별 실행 (권장)**:
  ```bash
  bash demo.sh
  ```
  각 단계의 실행 결과와 검증 포인트를 확인한 후 Enter를 누르면 다음 단계로 진행합니다.

- **비대화형 일괄 실행 (CI/자동 검증)**:
  ```bash
  bash demo.sh --non-interactive
  ```
  사용자 입력 없이 5단계 및 보너스 3종을 연속으로 실행하고 정상 완료(Exit Code 0)를 확인합니다.

---

## 2. 수동 시연 방법 (Step-by-Step)

평가자가 터미널에서 직접 단계를 밟아가며 시스템 동작을 확인할 수 있는 수동 시연 절차입니다.

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

---

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

---

### [Step 3] 15대 쿼리 전수 시연 (Q01 ~ Q15) — 5대 비즈니스 흐름 순차 진행

`sql/queries.sql`에 작성된 15개 쿼리는 데이터베이스 조회부터 조인 분석, 집계, 서브쿼리, 트랜잭션 갱신/삭제까지 비즈니스 흐름에 맞춰 물 흐르듯이 유기적으로 구성되어 있습니다.

#### Wave 1. 기본 도서·회원 목록 조회 (WHERE · ORDER BY · LIMIT)

- **[Q01] 특정 카테고리(컴퓨터) 도서를 가격 내림차순 조회**:
  - **하려는 것**: 카테고리 ID 필터링 및 가격 정렬 확인 (2행 반환)
  - **실행 명령**:
    ```bash
    python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); print(conn.execute('SELECT book_id, title, author, price FROM books WHERE category_id = 4 ORDER BY price DESC;').fetchall())"
    ```
  - **확인**: 클린 코드(33,000원), 혼자 공부하는 SQL(26,000원) 정렬 출력

- **[Q02] 연체(OVERDUE) 상태 대여 건 조회**:
  - **하려는 것**: 도서관 운영상 가장 시급한 연체 레코드 4건 추출
  - **실행 명령**:
    ```bash
    python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); print(conn.execute('SELECT r.rental_id, m.name, b.title, r.due_date, r.status FROM rentals r JOIN members m ON r.member_id = m.member_id JOIN books b ON r.book_id = b.book_id WHERE r.status = \'OVERDUE\' ORDER BY r.due_date ASC;').fetchall())"
    ```
  - **확인**: 연체 4건 및 반납기한 경과일 순 정렬 확인

- **[Q03] 가장 최근 가입 회원 5명 조회**:
  - **하려는 것**: 신규 회원 유입 모니터링 (ORDER BY join_date DESC LIMIT 5)
  - **확인**: 류미나, 신현우, 강소희 등 최근 가입자 5명 추출

- **[Q04] 2020년 이후 출판 & 가격 20,000원 이상 도서 조회**:
  - **하려는 것**: 복합 조건(AND) 필터링 검증
  - **확인**: '혼자 공부하는 SQL'(2021년/26,000원), '조선왕조실록'(2020년/22,000원) 2권 추출

#### Wave 2. 관계형 조인 분석 (INNER JOIN · 다중 JOIN · LEFT JOIN)

- **[Q05] 도서별 카테고리명 포함 전체 목록 (INNER JOIN)**:
  - **하려는 것**: 부모 카테고리와 자식 도서 간 1:N 조인 (13권 전수)
  - **확인**: 13권 도서마다 해당 카테고리명이 누락 없이 정확히 매핑됨

- **[Q06] 현재 대여 중(RENTED) 회원명, 도서명, 반납예정일 (다중 INNER JOIN)**:
  - **하려는 것**: `rentals`를 중심으로 `members`와 `books`를 3자 결합
  - **확인**: 최수아, 윤채원, 임도현, 강소희 등 현재 대여 중인 4건 추출

- **[Q07] 대여 이력이 한 번도 없는 도서 조회 (LEFT JOIN + IS NULL)**:
  - **하려는 것**: 비인기 도서 발굴을 위한 외부조인 널 체크
  - **확인**: 대여 이력이 없는 '소크라테스의 변명', '구름빵' 2권 정확히 도출

- **[Q08] 전체 회원별 대여 횟수 (LEFT JOIN + COUNT, 0회 포함)**:
  - **하려는 것**: 대여 건수가 0건인 비활성 회원까지 누락 없이 집계
  - **확인**: 회원 12명 전수 출력, 대여 없는 회원도 `0`으로 표시됨

#### Wave 3. 집계 및 시계열 분석 (COUNT · AVG · HAVING · strftime)

- **[Q09] 카테고리별 도서 권수와 평균 가격**:
  - **하려는 것**: GROUP BY와 AVG 반올림 집계
  - **확인**: 10개 카테고리별 도서 권수 및 평균 단가 산출

- **[Q10] 회원별 연체 대여 건수 (HAVING 연체 1건 이상)**:
  - **하려는 것**: 그룹핑 후 집계 조건 필터링 검증
  - **확인**: 김민준, 이서연, 박지호, 오태양 등 연체자 4명만 정확히 추출

- **[Q11] 월별 총 대여 건수 추이 (strftime 시계열 집계)**:
  - **하려는 것**: 날짜 포맷 함수를 활용한 월별 대여 트렌드 분석
  - **확인**: 2026-01부터 2026-11까지 9개 월별 대여량 추이 산출

#### Wave 4. 서브쿼리 및 고급 분석 (비상관 · SELECT절 상관 서브쿼리)

- **[Q12] 전체 도서 평균 가격보다 비싼 도서 (비상관 서브쿼리)**:
  - **하려는 것**: WHERE 절에 서브쿼리 `(SELECT AVG(price) FROM books)` 결합
  - **확인**: 전체 평균가(18,238원)를 초과하는 5권 도서 추출

- **[Q13] 회원별 가장 최근 대여일 조회 (SELECT 절 상관 서브쿼리)**:
  - **하려는 것**: 각 회원 레코드마다 자식 테이블의 최대 대여일 매핑
  - **확인**: 회원 12명 전수의 최근 이용일 도출 (미이용자는 NULL)

#### Wave 5. 데이터 갱신 및 삭제 실증 (UPDATE · DELETE 트랜잭션)

- **[Q14] 연체 자동 갱신 UPDATE**:
  - **하려는 것**: 반납기한 경과 & 미반납 건을 `OVERDUE` 상태로 일괄 변경
  - **확인**: 1건 대상 행 정상 반영

- **[Q15] 탈퇴 대기 회원 대여 이력 정리 DELETE**:
  - **하려는 것**: 서브쿼리를 이용해 특정 회원의 테스트성 대여 1건 안전 삭제
  - **확인**: 1건 정상 삭제 및 외래키 참조 무결성 유지

---

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

---

### [Step 5] 보너스 과제 3종 실측 실행 시연 (bonus/run_bonus*.py)

루트 `bonus/` 디렉토리에 배치된 3개의 전용 파이썬 러너를 통해 보너스 과제를 터미널에서 즉시 실측 시연합니다.

#### [보너스 1] INNER JOIN vs EXISTS 서브쿼리 실행계획 대조 시연
1. **실행 명령**:
   ```bash
   python3 bonus/run_bonus1.py
   ```
2. **확인해야 할 것**:
   - `INNER JOIN + DISTINCT`와 `EXISTS`가 동일한 10명 회원을 반환하는지 대조
   - `EXPLAIN QUERY PLAN`에서 JOIN의 `TEMP B-TREE` 정렬 오버헤드와 EXISTS의 `Early Stop` 단락 평가 차이 확인
   - 부모 컬럼만 필요할 때 EXISTS가 대용량 환경에서 우수한 이유 확인

#### [보너스 2] 외래키 무결성 파괴 실증 및 FK OFF 비교 시연
1. **실행 명령**:
   ```bash
   python3 bonus/run_bonus2.py
   ```
2. **확인해야 할 것**:
   - [시나리오 1] `PRAGMA foreign_keys = ON`: 유령 회원(`member_id=999`) 삽입 즉시 차단(15행 유지)
   - [시나리오 2] `PRAGMA foreign_keys = OFF`: 동일 쿼리 실행 시 유령 데이터 삽입 허용(16행 오염) 실증
   - DDL(`schema.sql`), 애플리케이션, 사전 검증의 3대 방어 체계 확인

#### [보너스 3] 경영진 3대 KPI 실측 리포트 도출 시연
1. **실행 명령**:
   ```bash
   python3 bonus/run_bonus3.py
   ```
2. **확인해야 할 것**:
   - **KPI-1 (월별 대여 회전율)**: 월별 회전율 수치 및 성수기(2, 3, 7, 10월) 확인
   - **KPI-2 (최다 대여 도서 TOP 3)**: 채식주의자, 아주 작은 습관의 힘, 클린 코드 랭킹 확인
   - **KPI-3 (연체율 분석)**: 도서관 전체 연체율 26.7% 및 연체 발생 회원 4명 명단 실측 확인
