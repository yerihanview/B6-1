# RTM — 요구사항 추적성 매트릭스 (B6-1 디지털 서랍장)

> **미션**: 정보를 깔끔하게 정리하는 디지털 서랍장 만들기 (SQL/RDBMS)
> **도메인**: 도서관 스마트 대여/연체 관리 시스템
> **검증 기준**: `python3 verify_sql.py` → 100/100 ALL PASS (2026-11-10 실측)
> **방법론**: 린 에이전틱 META_GUIDE v3.5 · ADR-008(2단계 교차 감사) · ADR-015(보너스 필수화) · ADR-018(산출물 주도 설계)

상태 표기: ✅ 검증 통과 · 📄 문서 산출물 · 🔁 자동 생성

---

## 1. 스키마 (DoD-1)

| ID | 요구사항 | 구현 위치 | 검증 방법 | 상태 |
|---|---|---|---|---|
| RTM-01 | SQLite 외래키 강제 활성화 (`PRAGMA foreign_keys = ON;`) | `schema.sql:1` | `verify_sql.py` 블록2 — 문자열 + `PRAGMA foreign_keys`=1 | ✅ |
| RTM-02 | `categories` — PK, `category_name` NOT NULL UNIQUE, `created_at` DEFAULT | `schema.sql` | `PRAGMA table_info` / `index_list` | ✅ |
| RTM-03 | `members` — PK, `name`·`phone`·`join_date` NOT NULL, `email` UNIQUE | `schema.sql` | 동일 | ✅ |
| RTM-04 | `books` — PK, FK `category_id`, `price >= 0` CHECK, `published_year` | `schema.sql` | `PRAGMA foreign_key_list(books)` | ✅ |
| RTM-05 | `rentals` — PK, FK `member_id`·`book_id`, `status` CHECK 3값 | `schema.sql` | `PRAGMA foreign_key_list(rentals)` (FK 3개) | ✅ |
| RTM-06 | `rentals(rental_date)` 인덱스 + 1줄 사유 주석 | `schema.sql` `idx_rentals_date` | `PRAGMA index_info` | ✅ |

## 2. 시드 데이터 (DoD-2)

| ID | 요구사항 | 구현 위치 | 검증 방법 | 상태 |
|---|---|---|---|---|
| RTM-07 | 4개 테이블 각 10행 이상, 총 45행 이상 | `seed.sql` (10/12/13/15 = **50행**) | `verify_sql.py` 블록3 | ✅ |
| RTM-08 | RENTED·RETURNED·OVERDUE 3상태, 연체·복수 대여 회원 포함 | `seed.sql` (7/4/4, 복수 대여 4명) | `SELECT status, COUNT(*)` | ✅ |
| RTM-09 | 부모 ➔ 자식 위상정렬 INSERT | `seed.sql` (categories ➔ members ➔ books ➔ rentals) | `verify_sql.py` 블록3 실행 성공 | ✅ |

## 3. 15대 쿼리 (DoD-3)

| ID | 요구 카테고리 | 요구사항 | 실제 쿼리 핵심 | 결과 | 상태 |
|---|---|---|---|---|---|
| RTM-10 | 기본 조회 | Q01 카테고리별 가격 내림차순 (WHERE, ORDER BY) | `WHERE c.category_name='컴퓨터' ORDER BY b.price DESC` | 2행 | ✅ |
| RTM-11 | 기본 조회 | Q02 연체 건 조회 (WHERE) | `WHERE r.status='OVERDUE'` | 4행 | ✅ |
| RTM-12 | 기본 조회 | Q03 최근 가입 회원 5명 (ORDER BY, LIMIT) | `ORDER BY join_date DESC LIMIT 5` | 5행 | ✅ |
| RTM-13 | 기본 조회 | Q04 2020년 이후 & 20,000원 이상 (AND) | `published_year >= 2020 AND price >= 20000` | 2행 | ✅ |
| RTM-14 | 조인 | Q05 도서+카테고리 (INNER JOIN) | `books b INNER JOIN categories c` | 13행 | ✅ |
| RTM-15 | 조인 | Q06 대여 중 회원·도서·반납예정일 (다중 INNER JOIN) | `rentals ⋈ members ⋈ books` | 4행 | ✅ |
| RTM-16 | 조인 | Q07 대여 이력 없는 도서 (LEFT JOIN + IS NULL) | `LEFT JOIN rentals ... WHERE r.rental_id IS NULL` | 2행 | ✅ |
| RTM-17 | 조인 | Q08 회원별 대여 횟수, 0회 포함 (LEFT JOIN + COUNT) | `COUNT(r.rental_id)` | 12행 | ✅ |
| RTM-18 | 집계 | Q09 카테고리별 권수·평균가 (COUNT, AVG, GROUP BY) | `ROUND(AVG(b.price),0)` | 10행 | ✅ |
| RTM-19 | 집계 | Q10 회원별 연체 건수 (GROUP BY + HAVING) | `HAVING COUNT(*) >= 1` | 4행 | ✅ |
| RTM-20 | 집계 | Q11 월별 대여 추이 (strftime + GROUP BY) | `strftime('%Y-%m', rental_date)` | 9행 | ✅ |
| RTM-21 | 서브쿼리 | Q12 평균가 초과 도서 (비상관) | `WHERE price > (SELECT AVG(price) ...)` | 5행 | ✅ |
| RTM-22 | 서브쿼리 | Q13 회원별 최근 대여일 (상관) | `(SELECT MAX(...) WHERE r.member_id = m.member_id)` | 12행 | ✅ |
| RTM-23 | 수정·삭제 | Q14 기한 경과 미반납 ➔ OVERDUE UPDATE | `UPDATE ... WHERE return_date IS NULL AND due_date < DATE('now')` | 1행 영향 | ✅ |
| RTM-24 | 수정·삭제 | Q15 탈퇴 대기 회원 테스트 대여 1건 DELETE | `DELETE ... WHERE rental_id = (SELECT ... LIMIT 1)` | 1행 영향 | ✅ |

## 4. 문서·실행 자산 (DoD-4~6)

| ID | 요구사항 | 구현 위치 | 검증 방법 | 상태 |
|---|---|---|---|---|
| RTM-25 | Mermaid ERD + 4개 테이블 명세 | `docs/ERD.md` (`erDiagram`, 관계선 3개) | `verify_sql.py` INFO 점검 | 📄 |
| RTM-26 | 보너스1 JOIN vs EXISTS 1:1 대조 | `docs/bonus/JOIN_VS_SUBQUERY.md` (8.9KB) | 블록6 분량·내용 | 📄 |
| RTM-27 | 보너스2 FK 위반 실증·해결 | `docs/bonus/INTEGRITY_VIOLATION.md` (5.7KB, 실측 trace 포함) | 블록4·6 | 📄 |
| RTM-28 | 보너스3 경영진 3대 KPI | `docs/bonus/KPI_REPORT.md` (9.2KB, 실측 수치) | 블록6 | 📄 |
| RTM-29 | 15대 쿼리 실행 결과 리포트 | `outputs/query_results.md` (341줄, 15개 전문+결과표) | 블록5가 자동 재생성 | 🔁 |
| RTM-30 | 무의존성 100점 채점기 | `verify_sql.py` (6블록, 표준 라이브러리만) | `python3 verify_sql.py` → 100/100 | ✅ |
| RTM-31 | 5단계 대화형 시연 러너 | `demo.sh` (`--non-interactive` 지원, trap 정리) | `bash demo.sh --non-interactive` exit 0 | ✅ |
| RTM-32 | 실행 방법·루브릭 체크리스트 | `README.md` | 육안 + 문서 린터 | 📄 |
| RTM-33 | 제출 서약·산출물 링크 | `SUBMISSION.md` | 육안 | 📄 |
| RTM-34 | 미션·모델·산출물·검증 이력 | `PROJECT_MANIFEST.json` | JSON 파싱 | 📄 |
| RTM-35 | 요구사항 추적 매트릭스 | `RTM.md` (본 문서) | 육안 | 📄 |

## 5. 무인 파이프라인 (ADR-017/018)

| ID | 요구사항 | 구현 위치 | 검증 방법 | 상태 |
|---|---|---|---|---|
| RTM-36 | ORDER_SHEET 주입 무인 생성 (Mode B) | `pipeline/generate.py` | `pipeline/runs/*.json` 실행 메타데이터 | ✅ |
| RTM-37 | 실행 메타데이터(모델·토큰·지연) 기록 | `pipeline/runs/generate_*.json` | JSON 열람 | ✅ |
| RTM-38 | 키 하드코딩 금지 (환경변수 주입) | `pipeline/generate.py` (`CODY_API_KEY`) | `grep` 기반 API 키 패턴 스캔 0건 | ✅ |

---

## 6. 검증 요약

```
7대 필수 산출물 존재        +20
스키마(4테이블·FK3·UNIQUE·인덱스) +20
시드(10행 이상·3상태·복수대여)     +20
외래키 위반 차단            +10
15대 쿼리 전수 실행·리포트   +20
보너스 문서 3종             +10
────────────────────────────────
합계                       100 / 100
```

- 실행 시각: 2026-11-10 (Asia/Seoul)
- 실행 명령: `python3 verify_sql.py`
- 결과: `🎉 [100점 만점 ALL PASS] ... 100/100점`, Exit Code 0
