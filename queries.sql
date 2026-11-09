-- Q01: 특정 카테고리(컴퓨터) 도서를 가격 내림차순으로 조회
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

-- Q02: 연체(OVERDUE) 상태인 대여 건 조회
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

-- Q03: 가장 최근에 가입한 회원 5명 조회
SELECT
    member_id,
    name,
    email,
    join_date
FROM members
ORDER BY join_date DESC
LIMIT 5;

-- Q04: 2020년 이후 출판되고 가격이 20,000원 이상인 도서 조회
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

-- Q05: 도서별 카테고리명을 포함한 전체 도서 목록 (INNER JOIN)
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

-- Q06: 현재 대여 중(RENTED)인 회원 이름, 도서명, 반납예정일 조회 (다중 INNER JOIN)
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

-- Q07: 대여 이력이 한 번도 없는 도서 조회 (LEFT JOIN + IS NULL)
SELECT
    b.book_id,
    b.title,
    b.author,
    b.price
FROM books b
LEFT JOIN rentals r ON b.book_id = r.book_id
WHERE r.rental_id IS NULL
ORDER BY b.book_id;

-- Q08: 전체 회원별 대여 횟수 조회, 대여 이력이 없는 회원은 0으로 표시 (LEFT JOIN + COUNT + GROUP BY)
SELECT
    m.member_id,
    m.name                  AS 회원명,
    COUNT(r.rental_id)      AS 총대여횟수
FROM members m
LEFT JOIN rentals r ON m.member_id = r.member_id
GROUP BY m.member_id, m.name
ORDER BY 총대여횟수 DESC, m.member_id;

-- Q09: 카테고리별 도서 권수와 평균 가격 조회 (COUNT, AVG, GROUP BY, 반올림)
SELECT
    c.category_name             AS 카테고리,
    COUNT(b.book_id)            AS 도서권수,
    ROUND(AVG(b.price), 0)      AS 평균가격
FROM categories c
LEFT JOIN books b ON c.category_id = b.category_id
GROUP BY c.category_id, c.category_name
ORDER BY 도서권수 DESC;

-- Q10: 회원별 총 연체 대여 건수, 연체가 1건 이상인 회원만 조회 (GROUP BY + HAVING)
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

-- Q11: 월별 총 대여 건수 추이 조회 (strftime, GROUP BY, ORDER BY)
SELECT
    strftime('%Y-%m', r.rental_date) AS 대여월,
    COUNT(r.rental_id)               AS 대여건수
FROM rentals r
GROUP BY strftime('%Y-%m', r.rental_date)
ORDER BY 대여월;

-- Q12: 전체 도서 평균 가격보다 비싼 도서 조회 (비상관 서브쿼리)
SELECT
    b.book_id,
    b.title,
    b.author,
    b.price,
    (SELECT ROUND(AVG(price), 0) FROM books) AS 전체평균가격
FROM books b
WHERE b.price > (SELECT AVG(price) FROM books)
ORDER BY b.price DESC;

-- Q13: 회원별 가장 최근 대여일 조회, 대여 이력 없는 회원은 NULL 표시 (SELECT 절 상관 서브쿼리)
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

-- Q14: 반납기한이 지났으나 아직 미반납(return_date IS NULL)인 대여 건을 OVERDUE로 일괄 갱신
UPDATE rentals
SET status = 'OVERDUE'
WHERE return_date IS NULL
  AND due_date < DATE('now')
  AND status = 'RENTED';

-- Q15: 탈퇴 대기 회원(member_id=10)의 테스트성 대여 이력 1건 삭제 (서브쿼리로 대상 1건 한정)
DELETE FROM rentals
WHERE rental_id = (
    SELECT rental_id
    FROM rentals
    WHERE member_id = 10
    ORDER BY rental_date DESC
    LIMIT 1
);
