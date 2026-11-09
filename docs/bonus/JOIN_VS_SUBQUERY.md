# INNER JOIN vs EXISTS 서브쿼리 비교 분석

> **주제**: '대여 건수가 존재하는 회원 목록' 조회를 두 가지 방식으로 작성하고 실제 SQLite 동작 기준으로 비교한다.

---

## 1. 문제 정의

`rentals` 테이블에 1건 이상의 대여 기록이 있는 회원을 `members` 테이블에서 조회한다.

**기대 결과 컬럼**: `member_id`, `name`, `email`

---

## 2. 방법 A — INNER JOIN + DISTINCT

```sql
SELECT DISTINCT
    m.member_id,
    m.name,
    m.email
FROM members AS m
INNER JOIN rentals AS r
    ON m.member_id = r.member_id
ORDER BY m.member_id;
```

### 동작 원리

1. `members`와 `rentals`를 `member_id` 기준으로 INNER JOIN한다.
2. 한 회원이 여러 건을 대여했으면 JOIN 결과에 해당 회원 행이 여러 번 나타난다.
3. `DISTINCT`로 중복 행을 제거하여 회원당 1행만 남긴다.

### 실행 계획 (EXPLAIN QUERY PLAN 실측)

```text
QUERY PLAN
|--SCAN r
|--SEARCH m USING INTEGER PRIMARY KEY (rowid=?)
|--USE TEMP B-TREE FOR DISTINCT
`--USE TEMP B-TREE FOR ORDER BY
```

- `rentals`를 전체 스캔(SCAN)한 뒤 `members` PK로 룩업한다.
- **DISTINCT 처리를 위해 임시 B-TREE를 추가로 생성**한다.
- 대여 건수가 많을수록 JOIN 중간 결과 집합이 커지고, DISTINCT 정렬 비용이 증가한다.

---

## 3. 방법 B — EXISTS 서브쿼리

```sql
SELECT
    m.member_id,
    m.name,
    m.email
FROM members AS m
WHERE EXISTS (
    SELECT 1
    FROM rentals AS r
    WHERE r.member_id = m.member_id
)
ORDER BY m.member_id;
```

### 동작 원리

1. `members`를 외부 쿼리에서 행 단위로 순회한다.
2. 각 회원에 대해 `rentals`에서 `member_id`가 일치하는 행이 **1건이라도 존재하는지**만 확인한다.
3. 존재하면 즉시 `TRUE`를 반환하고 해당 회원 행을 결과에 포함한다(Short-circuit 평가).
4. 중복 제거가 구조적으로 불필요하다(외부 쿼리는 `members` 행을 1번씩만 처리).

### 실행 계획 (EXPLAIN QUERY PLAN 실측)

```text
QUERY PLAN
|--SCAN m
`--CORRELATED SCALAR SUBQUERY 1
   `--SCAN r
```

> **참고**: 현재 스키마에는 `idx_rentals_date(rental_date)`만 있어 서브쿼리 내부가 `SCAN r`로 표시된다.
> `CREATE INDEX idx_rentals_member ON rentals(member_id);`를 추가하면 `SEARCH r USING INDEX idx_rentals_member (member_id=?)`로
> 바뀌어 회원 수 × 대여 건수 스캔이 인덱스 탐색으로 줄어든다.

- 이 실행 계획에는 `USE TEMP B-TREE FOR DISTINCT`가 없다(중복 제거 단계 자체가 없다). 출력 정렬을 위한 B-TREE는 `ORDER BY` 때문에 생길 수 있다.
- 각 회원에 대해 첫 번째 일치 행을 찾으면 그 회원의 서브쿼리 탐색은 더 진행하지 않는다(존재 확인 의미론).

---

## 4. 결과 동일성 검증

두 쿼리를 동일한 데이터베이스에서 실행하면 아래와 같이 동일한 결과를 반환한다.

| member_id | name   | email                    |
|-----------|--------|--------------------------|
| 1         | 김민준 | minjun.kim@email.com     |
| 2         | 이서연 | seoyeon.lee@email.com    |
| 3         | 박지호 | jiho.park@email.com      |
| 4         | 최수아 | sua.choi@email.com       |
| 5         | 정우진 | woojin.jung@email.com    |
| 6         | 한예린 | yerin.han@email.com      |
| 7         | 오태양 | taeyang.oh@email.com     |
| 8         | 윤채원 | chaewon.yoon@email.com   |
| 9         | 임도현 | dohyun.lim@email.com     |
| 10        | 강소희 | sohee.kang@email.com     |

시드 데이터 기준: `members` 12명 중 대여 기록이 있는 10명(member_id 1~10)이 조회된다.  
member_id 11(신현우), 12(류미나)는 대여 기록 없음 → 두 쿼리 모두 제외.

**결론: 두 쿼리의 결과 집합은 완전히 동일하다.**

---

## 5. 4관점 비교표

| 관점 | INNER JOIN + DISTINCT | EXISTS 서브쿼리 |
|---|---|---|
| **가독성** | "두 테이블을 연결한다"는 의도가 명확하나, `DISTINCT`가 왜 필요한지 처음 보는 독자에게 불명확할 수 있다. | "존재 여부를 확인한다"는 의도가 `EXISTS` 키워드 자체로 자명하다. 비즈니스 요건(존재 여부 필터)과 코드 구조가 1:1 대응된다. |
| **유지보수성** | 조회 컬럼을 추가할 때 `DISTINCT` 범위를 재검토해야 한다. JOIN 대상 테이블이 늘어나면 중복 폭발(fan-out) 위험이 커진다. | 서브쿼리 내부와 외부가 명확히 분리되어 있어 조건 변경 시 영향 범위가 좁다. 외부 쿼리 컬럼 변경이 서브쿼리에 영향을 주지 않는다. |
| **성능** | JOIN 중간 결과가 대여 건수만큼 팽창한 뒤 DISTINCT로 압축한다. 임시 B-TREE 정렬 비용 발생. 대여 건수가 많을수록 불리하다. | Short-circuit 평가로 첫 번째 일치 행 발견 즉시 탐색 중단. 중간 결과 팽창 없음. `rentals(member_id)` 인덱스 추가 시 최적화 효과가 극대화된다. |
| **NULL 안전성** | `member_id`가 NOT NULL이므로 이 스키마에서는 문제없다. 그러나 JOIN 키에 NULL이 허용된 컬럼이 포함되면 NULL 행이 JOIN에서 탈락하여 의도치 않은 결과가 발생할 수 있다. | `EXISTS`는 서브쿼리 내부에서 `SELECT 1`만 반환하므로 NULL 전파 위험이 없다. 외부 쿼리의 NULL 행도 `WHERE EXISTS` 조건에서 안전하게 처리된다. |

---

## 6. SQLite 실제 동작 근거

### 6-1. DISTINCT의 비용

SQLite는 `DISTINCT`를 처리할 때 이미 출력한 행을 추적하기 위한 임시 B-TREE를 만든다(정렬이 보장된 순서면 생략될 수도 있다).  
`EXPLAIN QUERY PLAN` 출력에 `USE TEMP B-TREE FOR DISTINCT`가 나타나는 것이 이를 증명한다.  
대여 건수가 N배 증가하면 이 임시 구조의 크기도 비례하여 증가한다.

### 6-2. EXISTS의 Short-circuit 평가

SQLite 쿼리 플래너는 `EXISTS` 서브쿼리를 평가할 때 조건을 만족하는 첫 행이 발견되는 순간 해당 서브쿼리의 탐색을 중단한다.  
이는 SQL 표준의 `EXISTS` 의미론(존재 여부만 판단)과 일치하며, `EXPLAIN QUERY PLAN`에서도 중복 제거 단계(`USE TEMP B-TREE FOR DISTINCT`)가 나타나지 않는 것으로 확인된다.  
따라서 한 회원이 100건을 대여했더라도 조건을 만족하는 첫 행을 만나면 나머지 99건은 읽지 않는다.

### 6-3. 인덱스 활용 차이

현재 스키마에는 `idx_rentals_date ON rentals(rental_date)` 인덱스만 존재한다.  
`rentals(member_id)` 인덱스가 없으므로 두 방식 모두 `rentals` 테이블을 스캔한다(실측 계획의 `SCAN r`).  
차이는 **스캔을 몇 번 하느냐**다. EXISTS는 회원 1명마다 서브쿼리를 한 번 평가하고 첫 일치 행에서 멈추며,  
INNER JOIN은 `rentals`를 한 번 스캔해 조인 결과를 만든 뒤 DISTINCT로 압축한다.  
즉 회원 수가 적고 대여 건수가 많을수록 JOIN이, 회원 수가 많고 대여 이력이 희소할수록 EXISTS가 유리해질 수 있다 —  
다만 이는 플래너·인덱스·데이터 분포에 좌우되므로 단정하지 않고 `EXPLAIN QUERY PLAN`과 실측 시간으로 판단해야 한다.

---

## 7. 선택 기준

```
목적이 "존재 여부 확인"인가?
    YES → EXISTS 서브쿼리를 선택한다.
    NO  → 아래로 진행

JOIN 결과의 다른 컬럼(rentals.rental_date 등)도 SELECT에 필요한가?
    YES → INNER JOIN을 선택한다. (EXISTS는 서브쿼리 내부 컬럼을 외부로 노출할 수 없다.)
    NO  → EXISTS 서브쿼리를 선택한다.
```

### 요약 권고

| 상황 | 권장 방식 |
|---|---|
| 존재 여부만 필터링 (이 문제의 경우) | **EXISTS** |
| 관련 테이블의 컬럼도 SELECT에 포함 | **INNER JOIN** |
| 대여 건수가 매우 많고 성능이 중요 | **EXISTS** + `rentals(member_id)` 인덱스 추가 |
| ORM 또는 동적 쿼리 빌더 환경 | **INNER JOIN** (대부분의 ORM이 JOIN을 더 자연스럽게 표현) |
| 코드 리뷰 가독성 우선 | **EXISTS** (비즈니스 의도와 코드 구조의 1:1 대응) |

---

## 8. 참고: 두 쿼리를 한 번에 비교 실행하는 방법

```sql
-- 방법 A
SELECT DISTINCT m.member_id, m.name, m.email
FROM members AS m
INNER JOIN rentals AS r ON m.member_id = r.member_id
ORDER BY m.member_id;

-- 방법 B
SELECT m.member_id, m.name, m.email
FROM members AS m
WHERE EXISTS (
    SELECT 1 FROM rentals AS r WHERE r.member_id = m.member_id
)
ORDER BY m.member_id;

-- 실행 계획 확인 (방법 A)
EXPLAIN QUERY PLAN
SELECT DISTINCT m.member_id, m.name, m.email
FROM members AS m
INNER JOIN rentals AS r ON m.member_id = r.member_id;

-- 실행 계획 확인 (방법 B)
EXPLAIN QUERY PLAN
SELECT m.member_id, m.name, m.email
FROM members AS m
WHERE EXISTS (
    SELECT 1 FROM rentals AS r WHERE r.member_id = m.member_id
);
