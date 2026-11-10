# 15대 핵심 SQL 쿼리 실제 실행 결과 리포트

> `python3 test/verify_sql.py`가 SQLite 인메모리 DB(sql/schema.sql + sql/seed.sql)에서 15개 쿼리를 순서대로 실행한 실제 출력이다.
> Q14(UPDATE)·Q15(DELETE)는 실행 자체와 영향 행 수를 기록한다.

## Q01. 특정 카테고리(컴퓨터) 도서를 가격 내림차순으로 조회

```sql
SELECT
    b.book_id,
    b.title,
    b.author,
    b.price,
    b.published_year
FROM books b
INNER JOIN categories c ON b.category_id = c.category_id
WHERE c.category_name = '컴퓨터'
ORDER BY b.price DESC;
```

**반환 행 수**: 2 (단언 일치)

| book_id | title | author | price | published_year |
|---|---|---|---|---|
| 9 | 클린 코드 | 로버트 마틴 | 33000 | 2013 |
| 8 | 혼자 공부하는 SQL | 우재남 | 26000 | 2021 |

## Q02. 연체(OVERDUE) 상태인 대여 건 조회

```sql
SELECT
    r.rental_id,
    m.name        AS 회원명,
    b.title       AS 도서명,
    r.rental_date AS 대여일,
    r.due_date    AS 반납기한,
    r.status      AS 상태
FROM rentals r
INNER JOIN members m ON r.member_id = m.member_id
INNER JOIN books   b ON r.book_id   = b.book_id
WHERE r.status = 'OVERDUE';
```

**반환 행 수**: 4 (단언 일치)

| rental_id | 회원명 | 도서명 | 대여일 | 반납기한 | 상태 |
|---|---|---|---|---|---|
| 8 | 김민준 | 총균쇠 | 2026-06-01 | 2026-06-15 | OVERDUE |
| 9 | 이서연 | 혼자 공부하는 SQL | 2026-06-10 | 2026-06-24 | OVERDUE |
| 10 | 박지호 | 부의 추월차선 | 2026-07-05 | 2026-07-19 | OVERDUE |
| … |  |  |  |  |  |

*(전체 4행 중 상위 3행만 표시)*

## Q03. 가장 최근에 가입한 회원 5명 조회

```sql
SELECT
    member_id,
    name,
    email,
    join_date
FROM members
ORDER BY join_date DESC
LIMIT 5;
```

**반환 행 수**: 5 (단언 일치)

| member_id | name | email | join_date |
|---|---|---|---|
| 12 | 류미나 | mina.ryu@email.com | 2025-01-07 |
| 11 | 신현우 | hyunwoo.shin@email.com | 2024-09-01 |
| 10 | 강소희 | sohee.kang@email.com | 2024-06-14 |
| … |  |  |  |

*(전체 5행 중 상위 3행만 표시)*

## Q04. 2020년 이후 출판되고 가격이 20,000원 이상인 도서 조회

```sql
SELECT
    book_id,
    title,
    author,
    published_year,
    price
FROM books
WHERE published_year >= 2020
  AND price >= 20000
ORDER BY published_year DESC, price DESC;
```

**반환 행 수**: 2 (단언 일치)

| book_id | title | author | published_year | price |
|---|---|---|---|---|
| 8 | 혼자 공부하는 SQL | 우재남 | 2021 | 26000 |
| 5 | 조선왕조실록 | 이덕일 | 2020 | 22000 |

## Q05. 도서별 카테고리명을 포함한 전체 도서 목록 (INNER JOIN)

```sql
SELECT
    b.book_id,
    b.title,
    b.author,
    c.category_name AS 카테고리,
    b.published_year,
    b.price
FROM books b
INNER JOIN categories c ON b.category_id = c.category_id
ORDER BY c.category_name, b.title;
```

**반환 행 수**: 13 (단언 일치)

| book_id | title | author | 카테고리 | published_year | price |
|---|---|---|---|---|---|
| 10 | 부의 추월차선 | 엠제이 드마코 | 경제경영 | 2013 | 16500 |
| 7 | 코스모스 | 칼 세이건 | 과학 | 2006 | 23000 |
| 2 | 아몬드 | 손원평 | 소설 | 2017 | 13500 |
| … |  |  |  |  |  |

*(전체 13행 중 상위 3행만 표시)*

## Q06. 현재 대여 중(RENTED)인 회원 이름, 도서명, 반납예정일 조회 (다중 INNER JOIN)

```sql
SELECT
    m.name        AS 회원명,
    b.title       AS 도서명,
    r.rental_date AS 대여일,
    r.due_date    AS 반납예정일
FROM rentals r
INNER JOIN members m ON r.member_id = m.member_id
INNER JOIN books   b ON r.book_id   = b.book_id
WHERE r.status = 'RENTED'
ORDER BY r.due_date;
```

**반환 행 수**: 4 (단언 일치)

| 회원명 | 도서명 | 대여일 | 반납예정일 |
|---|---|---|---|
| 최수아 | 부의 추월차선 | 2026-10-22 | 2026-11-05 |
| 윤채원 | 제주 한 달 살기 | 2026-10-29 | 2026-11-12 |
| 임도현 | 채식주의자 | 2026-11-03 | 2026-11-17 |
| … |  |  |  |

*(전체 4행 중 상위 3행만 표시)*

## Q07. 대여 이력이 한 번도 없는 도서 조회 (LEFT JOIN + IS NULL)

```sql
SELECT
    b.book_id,
    b.title,
    b.author,
    b.price
FROM books b
LEFT JOIN rentals r ON b.book_id = r.book_id
WHERE r.rental_id IS NULL
ORDER BY b.book_id;
```

**반환 행 수**: 2 (단언 일치)

| book_id | title | author | price |
|---|---|---|---|
| 11 | 소크라테스의 변명 | 플라톤 | 9800 |
| 12 | 구름빵 | 백희나 | 9500 |

## Q08. 전체 회원별 대여 횟수 조회, 대여 이력이 없는 회원은 0으로 표시 (LEFT JOIN + COUNT + GROUP BY)

```sql
SELECT
    m.member_id,
    m.name                  AS 회원명,
    COUNT(r.rental_id)      AS 총대여횟수
FROM members m
LEFT JOIN rentals r ON m.member_id = r.member_id
GROUP BY m.member_id, m.name
ORDER BY 총대여횟수 DESC, m.member_id;
```

**반환 행 수**: 12 (단언 일치)

| member_id | 회원명 | 총대여횟수 |
|---|---|---|
| 1 | 김민준 | 3 |
| 2 | 이서연 | 2 |
| 3 | 박지호 | 2 |
| … |  |  |

*(전체 12행 중 상위 3행만 표시)*

## Q09. 카테고리별 도서 권수와 평균 가격 조회 (COUNT, AVG, GROUP BY, 반올림)

```sql
SELECT
    c.category_name             AS 카테고리,
    COUNT(b.book_id)            AS 도서권수,
    ROUND(AVG(b.price), 0)      AS 평균가격
FROM categories c
LEFT JOIN books b ON c.category_id = b.category_id
GROUP BY c.category_id, c.category_name
ORDER BY 도서권수 DESC;
```

**반환 행 수**: 10 (단언 일치)

| 카테고리 | 도서권수 | 평균가격 |
|---|---|---|
| 소설 | 2 | 12750.0 |
| 역사 | 2 | 23500.0 |
| 자기계발 | 2 | 16400.0 |
| … |  |  |

*(전체 10행 중 상위 3행만 표시)*

## Q10. 회원별 총 연체 대여 건수, 연체가 1건 이상인 회원만 조회 (GROUP BY + HAVING)

```sql
SELECT
    m.member_id,
    m.name                          AS 회원명,
    COUNT(r.rental_id)              AS 연체건수
FROM members m
INNER JOIN rentals r ON m.member_id = r.member_id
WHERE r.status = 'OVERDUE'
GROUP BY m.member_id, m.name
HAVING COUNT(r.rental_id) >= 1
ORDER BY 연체건수 DESC;
```

**반환 행 수**: 4 (단언 일치)

| member_id | 회원명 | 연체건수 |
|---|---|---|
| 1 | 김민준 | 1 |
| 2 | 이서연 | 1 |
| 3 | 박지호 | 1 |
| … |  |  |

*(전체 4행 중 상위 3행만 표시)*

## Q11. 월별 총 대여 건수 추이 조회 (strftime, GROUP BY, ORDER BY)

```sql
SELECT
    strftime('%Y-%m', r.rental_date) AS 대여월,
    COUNT(r.rental_id)               AS 대여건수
FROM rentals r
GROUP BY strftime('%Y-%m', r.rental_date)
ORDER BY 대여월;
```

**반환 행 수**: 9 (단언 일치)

| 대여월 | 대여건수 |
|---|---|
| 2026-01 | 1 |
| 2026-02 | 2 |
| 2026-03 | 2 |
| … |  |

*(전체 9행 중 상위 3행만 표시)*

## Q12. 전체 도서 평균 가격보다 비싼 도서 조회 (비상관 서브쿼리)

```sql
SELECT
    b.book_id,
    b.title,
    b.author,
    b.price,
    (SELECT ROUND(AVG(price), 0) FROM books) AS 전체평균가격
FROM books b
WHERE b.price > (SELECT AVG(price) FROM books)
ORDER BY b.price DESC;
```

**반환 행 수**: 5 (단언 일치)

| book_id | title | author | price | 전체평균가격 |
|---|---|---|---|---|
| 9 | 클린 코드 | 로버트 마틴 | 33000 | 18238.0 |
| 8 | 혼자 공부하는 SQL | 우재남 | 26000 | 18238.0 |
| 6 | 총균쇠 | 재레드 다이아몬드 | 25000 | 18238.0 |
| … |  |  |  |  |

*(전체 5행 중 상위 3행만 표시)*

## Q13. 회원별 가장 최근 대여일 조회, 대여 이력 없는 회원은 NULL 표시 (SELECT 절 상관 서브쿼리)

```sql
SELECT
    m.member_id,
    m.name AS 회원명,
    (
        SELECT MAX(r.rental_date)
        FROM rentals r
        WHERE r.member_id = m.member_id
    ) AS 최근대여일
FROM members m
ORDER BY 최근대여일 IS NULL, 최근대여일 DESC;
```

**반환 행 수**: 12 (단언 일치)

| member_id | 회원명 | 최근대여일 |
|---|---|---|
| 10 | 강소희 | 2026-11-08 |
| 9 | 임도현 | 2026-11-03 |
| 8 | 윤채원 | 2026-10-29 |
| … |  |  |

*(전체 12행 중 상위 3행만 표시)*

## Q14. 반납기한이 지났으나 아직 미반납(return_date IS NULL)인 대여 건을 OVERDUE로 일괄 갱신

```sql
-- (재현성 및 시점 독립성을 위해 시드 기준일 '2026-11-10' 이상의 날짜 기준 적용하여 1건 정상 갱신)
UPDATE rentals
SET status = 'OVERDUE'
WHERE return_date IS NULL
  AND due_date < '2026-11-10'
  AND status = 'RENTED';
```

**실행 결과**: 1행 영향 (단언 일치)

## Q15. 탈퇴 대기 회원(member_id=10)의 테스트성 대여 이력 1건 삭제 (서브쿼리로 대상 1건 한정)

```sql
DELETE FROM rentals
WHERE rental_id = (
    SELECT rental_id
    FROM rentals
    WHERE member_id = 10
    ORDER BY rental_date DESC
    LIMIT 1
);
```

**실행 결과**: 1행 영향 (단언 일치)
