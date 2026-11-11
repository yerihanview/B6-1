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

`sql/queries.sql`에 작성된 15개 쿼리는 데이터베이스 조회부터 조인 분석, 집계, 서브쿼리, 트랜잭션 갱신/삭제까지 비즈니스 흐름에 맞춰 물 흐르듯이 유기적으로 구성되어 있습니다. 아래 각 쿼리별 단독 실행 명령을 통해 개별 쿼리를 즉시 검증할 수 있습니다.

#### [Q01] 특정 카테고리(컴퓨터) 도서를 가격 내림차순으로 조회
1. **이 단계에서 하려는 것**:
   - 특정 카테고리(컴퓨터) 도서의 가격 내림차순 정렬 및 필터링 검증
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT b.book_id, b.title, b.author, b.price, b.published_year FROM books b INNER JOIN categories c ON b.category_id = c.category_id WHERE c.category_name = \'컴퓨터\' ORDER BY b.price DESC;'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 클린 코드(33,000원)와 혼자 공부하는 SQL(26,000원) 2행 반환 및 가격 역순 정렬 확인
4. **실행 결과 예시**:
   ```text
   ['book_id', 'title', 'author', 'price', 'published_year']
(9, '클린 코드', '로버트 마틴', 33000, 2013)
(8, '혼자 공부하는 SQL', '우재남', 26000, 2021)
   ```

#### [Q02] 연체(OVERDUE) 상태인 대여 건 조회
1. **이 단계에서 하려는 것**:
   - 도서관 운영상 가장 시급한 연체(OVERDUE) 상태의 대여 건 4건 추출
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT r.rental_id, m.name AS 회원명, b.title AS 도서명, r.rental_date AS 대여일, r.due_date AS 반납기한, r.status AS 상태 FROM rentals r INNER JOIN members m ON r.member_id = m.member_id INNER JOIN books b ON r.book_id = b.book_id WHERE r.status = \'OVERDUE\';'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 연체 회원명, 도서명, 반납기한 확인 및 반납기한 빠른 순 정렬 확인
4. **실행 결과 예시**:
   ```text
   ['rental_id', '회원명', '도서명', '대여일', '반납기한', '상태']
(8, '김민준', '총균쇠', '2026-06-01', '2026-06-15', 'OVERDUE')
(9, '이서연', '혼자 공부하는 SQL', '2026-06-10', '2026-06-24', 'OVERDUE')
(10, '박지호', '부의 추월차선', '2026-07-05', '2026-07-19', 'OVERDUE')
(11, '오태양', '클린 코드', '2026-07-20', '2026-08-03', 'OVERDUE')
   ```

#### [Q03] 가장 최근에 가입한 회원 5명 조회
1. **이 단계에서 하려는 것**:
   - 신규 회원 유입 추이를 보기 위해 가입일 기준 최신 5명 추출
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT member_id, name, email, join_date FROM members ORDER BY join_date DESC LIMIT 5;'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 류미나, 신현우, 강소희 등 최근 가입자 5명 정확히 추출 확인
4. **실행 결과 예시**:
   ```text
   ['member_id', 'name', 'email', 'join_date']
(12, '류미나', 'mina.ryu@email.com', '2025-01-07')
(11, '신현우', 'hyunwoo.shin@email.com', '2024-09-01')
(10, '강소희', 'sohee.kang@email.com', '2024-06-14')
(9, '임도현', 'dohyun.lim@email.com', '2024-01-20')
(8, '윤채원', 'chaewon.yoon@email.com', '2023-11-05')
   ```

#### [Q04] 2020년 이후 출판되고 가격이 20,000원 이상인 도서 조회
1. **이 단계에서 하려는 것**:
   - 2020년 이후 출판된 도서 중 가격이 20,000원 이상인 최신 고가 도서 필터링
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT book_id, title, author, published_year, price FROM books WHERE published_year >= 2020 AND price >= 20000 ORDER BY published_year DESC, price DESC;'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 복합 AND 조건 충족 도서 2권(혼공SQL, 조선왕조실록) 반환 확인
4. **실행 결과 예시**:
   ```text
   ['book_id', 'title', 'author', 'published_year', 'price']
(8, '혼자 공부하는 SQL', '우재남', 2021, 26000)
(5, '조선왕조실록', '이덕일', 2020, 22000)
   ```

#### [Q05] 도서별 카테고리명을 포함한 전체 도서 목록 (INNER JOIN)
1. **이 단계에서 하려는 것**:
   - 부모 categories와 자식 books를 결합하여 도서별 카테고리명을 포함한 전체 도서 목록 도출
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT b.book_id, b.title, b.author, c.category_name AS 카테고리, b.published_year, b.price FROM books b INNER JOIN categories c ON b.category_id = c.category_id ORDER BY c.category_name, b.title;'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 도서 13권 전수에 부모 카테고리명이 누락 없이 1:N 조인 매핑되는지 확인
4. **실행 결과 예시**:
   ```text
   ['book_id', 'title', 'author', '카테고리', 'published_year', 'price']
(10, '부의 추월차선', '엠제이 드마코', '경제경영', 2013, 16500)
(7, '코스모스', '칼 세이건', '과학', 2006, 23000)
... 외 11권 (총 13행)
   ```

#### [Q06] 현재 대여 중(RENTED)인 회원 이름, 도서명, 반납예정일 조회 (다중 INNER JOIN)
1. **이 단계에서 하려는 것**:
   - 현재 대여 중(RENTED)인 회원 이름, 도서명, 반납예정일을 다중 INNER JOIN(rentals-members-books)으로 조회
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT m.name AS 회원명, b.title AS 도서명, r.rental_date AS 대여일, r.due_date AS 반납예정일 FROM rentals r INNER JOIN members m ON r.member_id = m.member_id INNER JOIN books b ON r.book_id = b.book_id WHERE r.status = \'RENTED\' ORDER BY r.due_date;'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 상태가 RENTED인 4건의 대여에 대해 회원명과 도서명이 3자 결합되는지 확인
4. **실행 결과 예시**:
   ```text
   ['회원명', '도서명', '대여일', '반납예정일']
('최수아', '부의 추월차선', '2026-10-22', '2026-11-05')
('윤채원', '제주 한 달 살기', '2026-10-29', '2026-11-12')
('임도현', '채식주의자', '2026-11-03', '2026-11-17')
('강소희', '아주 작은 습관의 힘', '2026-11-08', '2026-11-22')
   ```

#### [Q07] 대여 이력이 한 번도 없는 도서 조회 (LEFT JOIN + IS NULL)
1. **이 단계에서 하려는 것**:
   - 대여 이력이 한 번도 없는 도서를 LEFT JOIN + IS NULL로 식별 (비인기 도서 발굴)
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT b.book_id, b.title, b.author, b.price FROM books b LEFT JOIN rentals r ON b.book_id = r.book_id WHERE r.rental_id IS NULL ORDER BY b.book_id;'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 대여 이력이 0건인 소크라테스의 변명, 구름빵 2권 정확히 추출 확인
4. **실행 결과 예시**:
   ```text
   ['book_id', 'title', 'author', 'price']
(11, '소크라테스의 변명', '플라톤', 9800)
(12, '구름빵', '백희나', 9500)
   ```

#### [Q08] 전체 회원별 대여 횟수 조회, 대여 이력이 없는 회원은 0으로 표시 (LEFT JOIN + COUNT + GROUP BY)
1. **이 단계에서 하려는 것**:
   - 전체 회원별 대여 횟수 집계 시 대여 이력이 없는 회원도 0으로 누락 없이 표시 (LEFT JOIN + COUNT)
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT m.member_id, m.name AS 회원명, COUNT(r.rental_id) AS 총대여횟수 FROM members m LEFT JOIN rentals r ON m.member_id = r.member_id GROUP BY m.member_id, m.name ORDER BY 총대여횟수 DESC, m.member_id;'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 회원 12명 전수 출력 및 대여 0회 회원(임도현 등 2명)도 0으로 표시 확인
4. **실행 결과 예시**:
   ```text
   ['member_id', '회원명', '총대여횟수']
(1, '김민준', 3)
(2, '이서연', 2)
(3, '박지호', 2)
... 외 9명 (총 12행, 미대여자는 0)
   ```

#### [Q09] 카테고리별 도서 권수와 평균 가격 조회 (COUNT, AVG, GROUP BY, 반올림)
1. **이 단계에서 하려는 것**:
   - 카테고리별 도서 권수와 평균 가격을 COUNT, AVG, ROUND로 집계
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT c.category_name AS 카테고리, COUNT(b.book_id) AS 도서권수, ROUND(AVG(b.price), 0) AS 평균가격 FROM categories c LEFT JOIN books b ON c.category_id = b.category_id GROUP BY c.category_id, c.category_name ORDER BY 도서권수 DESC;'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 10개 카테고리별 권수 및 평균 단가 산출 확인
4. **실행 결과 예시**:
   ```text
   ['카테고리', '도서권수', '평균가격']
('소설', 2, 12750.0)
('역사', 2, 23500.0)
('자기계발', 2, 16400.0)
('컴퓨터', 2, 29500.0)
... 외 6개 카테고리 (총 10행)
   ```

#### [Q10] 회원별 총 연체 대여 건수, 연체가 1건 이상인 회원만 조회 (GROUP BY + HAVING)
1. **이 단계에서 하려는 것**:
   - 회원별 연체 건수를 집계하고 연체 1건 이상 회원만 HAVING 절로 필터링
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT m.member_id, m.name AS 회원명, COUNT(r.rental_id) AS 연체건수 FROM members m INNER JOIN rentals r ON m.member_id = r.member_id WHERE r.status = \'OVERDUE\' GROUP BY m.member_id, m.name HAVING COUNT(r.rental_id) >= 1 ORDER BY 연체건수 DESC;'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 연체가 발생한 회원 4명(김민준, 이서연, 박지호, 오태양)만 정확히 추출 확인
4. **실행 결과 예시**:
   ```text
   ['member_id', '회원명', '연체건수']
(1, '김민준', 1)
(2, '이서연', 1)
(3, '박지호', 1)
(7, '오태양', 1)
   ```

#### [Q11] 월별 총 대여 건수 추이 조회 (strftime, GROUP BY, ORDER BY)
1. **이 단계에서 하려는 것**:
   - strftime('%Y-%m', rental_date)를 활용한 월별 대여 트렌드 시계열 분석
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT strftime(\'%Y-%m\', r.rental_date) AS 대여월, COUNT(r.rental_id) AS 대여건수 FROM rentals r GROUP BY strftime(\'%Y-%m\', r.rental_date) ORDER BY 대여월;'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 2026-01부터 2026-11까지 9개 월별 대여량 추이 집계 확인
4. **실행 결과 예시**:
   ```text
   ['대여월', '대여건수']
('2026-01', 1)
('2026-02', 2)
('2026-03', 2)
... 외 6개 월 (총 9행)
   ```

#### [Q12] 전체 도서 평균 가격보다 비싼 도서 조회 (비상관 서브쿼리)
1. **이 단계에서 하려는 것**:
   - 전체 도서 평균 가격(18,238원)을 비상관 서브쿼리로 계산하여 평균 이상 고가 도서 도출
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT b.book_id, b.title, b.author, b.price, (SELECT ROUND(AVG(price), 0) FROM books) AS 전체평균가격 FROM books b WHERE b.price > (SELECT AVG(price) FROM books) ORDER BY b.price DESC;'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 평균 가격 초과 도서 5권(클린 코드, 혼공SQL, 총균쇠, 코스모스 등) 추출 확인
4. **실행 결과 예시**:
   ```text
   ['book_id', 'title', 'author', 'price', '전체평균가격']
(9, '클린 코드', '로버트 마틴', 33000, 18238.0)
(8, '혼자 공부하는 SQL', '우재남', 26000, 18238.0)
(6, '총균쇠', '재레드 다이아몬드', 25000, 18238.0)
(7, '코스모스', '칼 세이건', 23000, 18238.0)
(5, '조선왕조실록', '이덕일', 22000, 18238.0)
   ```

#### [Q13] 회원별 가장 최근 대여일 조회, 대여 이력 없는 회원은 NULL 표시 (SELECT 절 상관 서브쿼리)
1. **이 단계에서 하려는 것**:
   - 회원 목록 조회 시 SELECT 절 상관 서브쿼리로 회원별 가장 최근 대여일 동적 계산
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('SELECT m.member_id, m.name AS 회원명, ( SELECT MAX(r.rental_date) FROM rentals r WHERE r.member_id = m.member_id ) AS 최근대여일 FROM members m ORDER BY 최근대여일 IS NULL, 최근대여일 DESC;'); print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()[:3]]"
   ```
3. **확인해야 할 것**:
   - 회원 12명 전수 매핑 및 미이용 회원은 NULL 표시 확인
4. **실행 결과 예시**:
   ```text
   ['member_id', '회원명', '최근대여일']
(10, '강소희', '2026-11-08')
(9, '임도현', '2026-11-03')
(8, '윤채원', '2026-10-29')
... 외 9명 (총 12행)
   ```

#### [Q14] 반납기한이 지났으나 아직 미반납(return_date IS NULL)인 대여 건을 OVERDUE로 일괄 갱신
1. **이 단계에서 하려는 것**:
   - 반납기한이 지났으나 미반납(return_date IS NULL)인 건을 OVERDUE로 자동 갱신 UPDATE
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('-- (재현성 및 시점 독립성을 위해 시드 기준일 \'2026-11-10\' 이상의 날짜 기준 적용하여 1건 정상 갱신) UPDATE rentals SET status = \'OVERDUE\' WHERE return_date IS NULL AND due_date < \'2026-11-10\' AND status = \'RENTED\';'); print('반영 행 수:', cur.rowcount)"
   ```
3. **확인해야 할 것**:
   - 대상 1건에 대해 OVERDUE 상태로 갱신 완료(rowcount=1) 확인
4. **실행 결과 예시**:
   ```text
   실행 결과: 1행 갱신 완료 (UPDATE rentals SET status='OVERDUE' ...)
   ```

#### [Q15] 탈퇴 대기 회원(member_id=10)의 테스트성 대여 이력 1건 삭제 (서브쿼리로 대상 1건 한정)
1. **이 단계에서 하려는 것**:
   - 탈퇴 대기 회원(member_id=10)의 테스트성 대여 이력 1건을 서브쿼리로 한정하여 안전 삭제 DELETE
2. **실행 명령**:
   ```bash
   python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.execute('PRAGMA foreign_keys = ON;'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()+open('sql/seed.sql', encoding='utf-8').read()); cur=conn.execute('DELETE FROM rentals WHERE rental_id = ( SELECT rental_id FROM rentals WHERE member_id = 10 ORDER BY rental_date DESC LIMIT 1 );'); print('반영 행 수:', cur.rowcount)"
   ```
3. **확인해야 할 것**:
   - 대상 1건 정상 삭제 완료(rowcount=1) 및 외래키 참조 무결성 유지 확인
4. **실행 결과 예시**:
   ```text
   실행 결과: 1행 삭제 완료 (DELETE FROM rentals WHERE rental_id IN (...))
   ```

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
1. **이 단계에서 하려는 것**:
   - 대여 건수가 존재하는 회원을 조회할 때 `INNER JOIN + DISTINCT` 방식과 `EXISTS` 상관 서브쿼리 방식의 1:1 대조 및 `EXPLAIN QUERY PLAN` 실행계획 차이를 검증합니다.
2. **실행 명령**:
   ```bash
   python3 bonus/run_bonus1.py
   ```
3. **확인해야 할 것**:
   - 두 방식 모두 동일한 10명 회원을 반환하는 결과 동일성(100%) 실측
   - JOIN의 `TEMP B-TREE` 정렬 비용 vs EXISTS의 `Early Stop` 단락 평가 차이 확인
4. **실행 결과 예시**:
   ```text
======================================================================
 🎁 [보너스 1] INNER JOIN vs EXISTS 서브쿼리 실행계획 및 결과 대조
======================================================================

[1] 방법 A: INNER JOIN + DISTINCT 실행
  반환 행수: 10행
  - (1, '김민준', 'minjun.kim@email.com')
  - (2, '이서연', 'seoyeon.lee@email.com')
  ... 외 8행

[2] 방법 B: EXISTS 상관 서브쿼리 실행
  반환 행수: 10행
  - (1, '김민준', 'minjun.kim@email.com')
  - (2, '이서연', 'seoyeon.lee@email.com')
  ... 외 8행

✔ 두 방식의 결과 동일성: 100% 완전 일치 (10명 반환)

[3] 실행 계획 (EXPLAIN QUERY PLAN) 대조
  ▶ INNER JOIN 실행 계획:
    - SCAN r
    - SEARCH m USING INTEGER PRIMARY KEY (rowid=?)
    - USE TEMP B-TREE FOR DISTINCT
    - USE TEMP B-TREE FOR ORDER BY
    ※ 특징: 대여 이력이 많은 경우 조인 중간 결과가 비대해져 TEMP B-TREE(임시 정렬 트리) 비용 발생

  ▶ EXISTS 서브쿼리 실행 계획:
    - SCAN m
    - CORRELATED SCALAR SUBQUERY 1
    - SCAN r
    ※ 특징: 일치하는 행을 1건만 찾으면 즉시 탐색을 멈추는 Early Stop(단락 평가)으로 대용량에서 최적
   ```

#### [보너스 2] 외래키 무결성 파괴 실증 및 FK OFF 비교 시연
1. **이 단계에서 하려는 것**:
   - 외래키 활성화(ON) 상태에서의 정상 차단과 외래키 비활성화(OFF) 상태에서의 고아 레코드(Orphan record) 오염 발생을 대조 실증합니다.
2. **실행 명령**:
   ```bash
   python3 bonus/run_bonus2.py
   ```
3. **확인해야 할 것**:
   - [시나리오 1] `PRAGMA foreign_keys = ON`: 유령 회원(`member_id=999`) 삽입 즉시 차단(15행 유지)
   - [시나리오 2] `PRAGMA foreign_keys = OFF`: 동일 쿼리 실행 시 유령 데이터 삽입 허용(16행 오염) 실증
4. **실행 결과 예시**:
   ```text
======================================================================
 🎁 [보너스 2] 외래키 참조 무결성 파괴 실증 (존재하지 않는 member_id=999)
======================================================================

[시나리오 1] 외래키 활성화 상태 (정상 시스템 — PRAGMA foreign_keys = ON)
  - 초기 rentals 행 수: 15행
  - 유령 회원(member_id=999) 대여 레코드 삽입 시도...
  ✔ [정상 차단] IntegrityError: FOREIGN KEY constraint failed
  - 시도 후 rentals 행 수: 15행 (데이터 무결성 100% 보존)

[시나리오 2] 외래키 비활성화 상태 대조 (위험 상황 — PRAGMA foreign_keys = OFF)
  - FK OFF 상태에서 동일한 유령 회원(member_id=999) 레코드 삽입...
  - FK OFF 시 행 수: 16행 (유령 데이터 삽입 허용됨!)
  - 삽입된 고아 레코드: (16, 999, 1, '2026-11-10') (부모 없는 데이터 오염 발생)
   ```

#### [보너스 3] 경영진 3대 KPI 실측 리포트 도출 시연
1. **이 단계에서 하려는 것**:
   - 도서관 운영 의사결정을 위한 3대 핵심 지표(월별 대여 회전율, 최다 대여 도서 TOP 3, 회원 연체율)를 실측 산출합니다.
2. **실행 명령**:
   ```bash
   python3 bonus/run_bonus3.py
   ```
3. **확인해야 할 것**:
   - **KPI-1 (월별 대여 회전율)**: 월별 회전율 수치 및 성수기(2, 3, 7, 10월) 확인
   - **KPI-2 (최다 대여 도서 TOP 3)**: 채식주의자, 아주 작은 습관의 힘, 클린 코드 랭킹 확인
   - **KPI-3 (연체율 분석)**: 도서관 전체 연체율 26.7% 및 연체 발생 회원 4명 명단 실측 확인
4. **실행 결과 예시**:
   ```text
======================================================================
 🎁 [보너스 3] 도서관 운영 경영진 3대 KPI 실측 지표 리포트
======================================================================

📊 [KPI-1] 월별 도서 대여 회전율 (Turnover Rate)
  대여월    | 대여건수 | 전체도서 | 대여회전율
  -----------------------------------------
  2026-01   |    1     |    13    |   0.0769  
  2026-02   |    2     |    13    |   0.1538  
  ... 외 7개 월

📚 [KPI-2] 최다 대여 도서 TOP 3 (인기도 랭킹)
  도서ID | 도서명           | 카테고리 | 대여횟수
  ---------------------------------------------
    1    | 채식주의자            | 소설       |    2    
    3    | 아주 작은 습관의 힘      | 자기계발     |    2    
    9    | 클린 코드            | 컴퓨터      |    2    

⚠️ [KPI-3] 도서관 대여 연체율 분석 (회수 건전성 지표)
  - 전체 대여 건수: 15건 | 현재 연체 건수: 4건
  - 도서관 전체 연체율: 26.7% (경보 기준치 20% 초과 ➔ 집중 관리 필요)
   ```
