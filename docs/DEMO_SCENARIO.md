# B6-1 동료평가 5단계 시연 시나리오 (Demo Scenario)

> **실행 명령**: `bash demo.sh` (엔터 진행형 대화형 러너)  
> **무인 검증**: `bash demo.sh --non-interactive` (CI/E2E 스모크 테스트, Exit 0 보증)  
> **핵심 원칙**: 구두 설명에 그치지 않고, 각 단계마다 **발표자 멘트 · 실행 명령 · 기계적 검증 증적** 3요소를 일치시켜 시연한다.

---

## [Step 1] 스키마 적재 — 무결성은 선언에서 시작된다

* **📌 발표자 멘트**:  
  "SQLite는 기본적으로 외래키(FK) 무결성 검사가 OFF로 꺼져 있는 치명적인 함정이 있습니다. 저희 시스템은 `sql/schema.sql` 첫 줄에 `PRAGMA foreign_keys = ON;`을 명시하여 DDL 수준에서 외래키 검사를 강제합니다."
* **💻 실행 명령**:  
  ```bash
  python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()); print('테이블:', [r[0] for r in conn.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name NOT LIKE \'sqlite_%\' ORDER BY name;')])"
  ```
* **🔍 확인 포인트**:  
  - `PRAGMA foreign_keys = 1` 활성화 확인.
  - `categories, members, books, rentals` 4개 테이블 생성.
  - `books.category_id → categories`, `rentals.member_id → members`, `rentals.book_id → books` 외래키 3개 및 `idx_rentals_date` 인덱스 확인.

---

## [Step 2] 시드 적재 — 부모에서 자식으로 위상정렬

* **📌 발표자 멘트**:  
  "외래키가 활성화된 RDBMS에서는 자식 레코드를 부모보다 먼저 넣으면 삽입 에러가 발생합니다. 따라서 `categories`와 `members`를 먼저 적재한 뒤 `books`, `rentals` 순으로 위상정렬하여 50행을 안전하게 적재합니다."
* **💻 실행 명령**:  
  ```bash
  python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()); conn.executescript(open('sql/seed.sql', encoding='utf-8').read()); print('총 적재 행수:', sum(conn.execute(f'SELECT COUNT(*) FROM {t};').fetchone()[0] for t in ('categories','members','books','rentals')))"
  ```
* **🔍 확인 포인트**:  
  - 테이블당 10행 이상 충족 (categories 10, members 12, books 13, rentals 15 = 총 50행).
  - 대여 상태 3종 분포: `OVERDUE 4건, RENTED 4건, RETURNED 7건`.
  - 복수 대여 회원 4명 포진으로 그룹핑 집계 준비 완료.

---

## [Step 3] 15대 쿼리 핵심 시연 — 조인과 집계가 실데이터로 답한다

* **📌 발표자 멘트**:  
  "단순 조회를 넘어, 카테고리명을 결합하는 `INNER JOIN`(Q05), 대여 이력이 없는 회원까지 0으로 집계하는 `LEFT JOIN`(Q08), 그리고 `strftime` 기반의 월별 대여 추이(Q11)를 실제 한국어 데이터로 시연합니다."
* **💻 실행 명령**:  
  ```bash
  bash demo.sh  # Step 3 진행
  ```
* **🔍 확인 포인트**:  
  - Q05: 도서 13권 전수에 부모 카테고리명 정확히 매핑 (13행 반환).
  - Q08: 신현우, 류미나 등 대여 이력 없는 회원 2명을 포함한 12명 전수 대여 횟수(0회 포함) 집계.
  - Q11: 2026-01부터 2026-11까지 9개 대여월별 건수 시계열 집계.

---

## [Step 4] 무결성 파괴 실증 — 유령 외래키 차단

* **📌 발표자 멘트**:  
  "RDBMS의 가치는 제약을 지키지 않는 나쁜 데이터가 들어왔을 때 실제로 거부할 수 있느냐에 있습니다. 존재하지 않는 회원 ID `999`로 대여 레코드 삽입을 시도해 봅니다."
* **💻 실행 명령**:  
  ```bash
  python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()); conn.executescript(open('sql/seed.sql', encoding='utf-8').read()); conn.execute('INSERT INTO rentals (member_id, book_id, rental_date, due_date, status) VALUES (999, 1, \'2026-11-10\', \'2026-11-24\', \'RENTED\');')"
  ```
* **🔍 확인 포인트**:  
  - `sqlite3.IntegrityError: FOREIGN KEY constraint failed` 에러 발생.
  - `rentals` 테이블의 행 수가 15행에서 단 1행도 증가하지 않고 원자적 롤백 유지.

---

## [Step 5] 무인 기계 채점 — 100점의 공학적 근거

* **📌 발표자 멘트**:  
  "7대 산출물 존재, 스키마 제약조건, 시드 정량, 6대 적대적 음성 변조 테스트(Mutation Testing), 15대 쿼리 기대 행수 단언, 보너스 3종 문서를 기계적으로 채점하여 100점 만점을 확증합니다."
* **💻 실행 명령**:  
  ```bash
  python3 test/verify_sql.py
  ```
* **🔍 확인 포인트**:  
  - `🎉 [100점 만점 ALL PASS] 디지털 서랍장 미션 최종 점수: 100/100점` 출력 및 `Exit Code 0`.
  - `test/outputs/query_results.md`에 15개 쿼리 실행 결과 전문 자동 생성.
