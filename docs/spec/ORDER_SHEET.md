# B6-1 Lean MBO Order Sheet (내부 작업 지시서) v1.0

> **수석 아키텍트**: 우광택 (@yerihanview)
> **발행 주체**: 오케스트레이터 에이전트 토토 (Pickle)
> **수행 에이전트**: 코디세이 Public API (`claude-sonnet-4`) — 무인(Headless) 생성
> **과제명**: 정보를 깔끔하게 정리하는 디지털 서랍장 만들기 (B6-1)
> **적용 방법론**: 린 에이전틱 개발 방법론 META_GUIDE v3.5 (ADR-004, ADR-008, ADR-014, ADR-015, ADR-016, ADR-018)
> **발행일**: 2026-11-10

> 이 문서는 **평가 대상 산출물이 아닌 내부 작업 계약서(RFC)**이다 (ADR-018 원칙 1).
> 평가자는 `README.md`, `docs/`, 그리고 실제 SQL 산출물만 본다.

---

## 1. Objective (북극성)

도서관의 회원·도서·대여 기록을 4개 테이블(categories, members, books, rentals)의 1:N 관계 3개로 모델링하고, SQLite에서 무결성 제약조건이 실제로 강제되는 스키마와 45행 이상의 시드 데이터, 그리고 기본 조회·조인·집계·서브쿼리·수정/삭제를 모두 포괄하는 15대 쿼리를 표준 SQL만으로 납품한다. 평가자는 별도 설치 없이 `python3 verify_sql.py` 한 줄로 100점 만점의 기계 채점 결과와 15개 쿼리의 실제 실행 결과를 즉시 확인할 수 있어야 한다.

---

## 2. Definition of Done (DoD 7대)

### [DoD-1] 스키마 무결성 (`schema.sql`)
- `PRAGMA foreign_keys = ON;` 최상단 선언.
- 4개 테이블 DDL: PK 4개, FK 3개, NOT NULL(테이블당 2개 이상), UNIQUE(`members.email`, `categories.category_name`), CHECK(`books.price >= 0`, `rentals.status IN ('RENTED','RETURNED','OVERDUE')`).
- `rentals(rental_date)` 인덱스 생성 + 바로 위 1줄 사유 주석.
- 생성 순서: `categories`, `members` ➔ `books` ➔ `rentals` (FK 의존성 위상정렬).

### [DoD-2] 시드 데이터 (`seed.sql`)
- 4개 테이블 각 10행 이상, 총 45행 이상의 현실적인 한국어 데이터.
- INSERT 순서: 부모 ➔ 자식 (categories/members ➔ books ➔ rentals).
- `rentals.status`에 `RENTED`·`RETURNED`·`OVERDUE` 세 상태 모두 포함, 연체 건과 복수 대여 회원 포함.

### [DoD-3] 15대 쿼리 (`queries.sql`)
- 각 쿼리 상단 `-- Q01: 목적` 형식 주석 필수, Q01~Q15 번호 누락 금지.
- 기본 조회 4(Q01~Q04) / 조인 4(Q05·Q06 INNER, Q07·Q08 LEFT) / 집계 3(Q09~Q11) / 서브쿼리 2(Q12 비상관, Q13 상관) / 수정·삭제 2(Q14 UPDATE, Q15 DELETE).
- 15개 모두 SQLite에서 실행 오류 0건.

### [DoD-4] 무의존성 100점 기계 채점기 (`verify_sql.py`)
- Python 표준 라이브러리(`sqlite3`, `os`, `sys`)만 사용. 외부 패키지 0개.
- 6개 채점 블록 합계 100점: 산출물 존재 20 + 스키마 20 + 시드 20 + FK 방어 10 + 15쿼리 실행 20 + 보너스 문서 10.
- 실행 시 `outputs/query_results.md`를 자동 재생성하고 Exit Code 0으로 종료.

### [DoD-5] 문서 산출물 (`docs/`)
- `docs/ERD.md`: Mermaid `erDiagram` + 4개 테이블 명세서(컬럼, 타입, 제약, 관계).
- `docs/bonus/JOIN_VS_SUBQUERY.md`: INNER JOIN vs EXISTS 1:1 대조(가독성·실행계획·성능).
- `docs/bonus/INTEGRITY_VIOLATION.md`: 존재하지 않는 `member_id=999` INSERT 시 `FOREIGN KEY constraint failed` 실증과 해결.
- `docs/bonus/KPI_REPORT.md`: 경영진 3대 KPI(월별 대여 회전율, 최다 대여 도서 TOP 3, 회원 연체율).

### [DoD-6] 실행·시연 자산
- `demo.sh`: 엔터 진행형 5단계(스키마 ➔ 시드 ➔ 주요 쿼리 ➔ FK 위반 차단 ➔ 100점 채점), `--non-interactive` 지원, 종료 시 임시 DB 삭제(trap).
- `README.md`: 개요, ERD, 폴더 구조, 실행 방법, demo.sh 사용법, 루브릭 충족 체크리스트.
- `SUBMISSION.md`: 제출 서약 및 산출물 링크.

### [DoD-7] 거버넌스 이력
- `PROJECT_MANIFEST.json`(미션·모델·산출물·검증 이력), `RTM.md`(요구사항 추적 매트릭스), `ORDER_SHEET.md`(본 문서) 보존.
- Conventional Commits 단위 커밋, `yerihanview/B6-1` public 저장소 main 브랜치 푸시.

---

## 3. RTM (요구사항 추적성 매트릭스)

각 요구사항은 "평가자에게 어떤 명령어로 3초 만에 실증하는가"와 1:1 매핑한다 (ADR-018 원칙 3).

| ID | 요구사항 (미션 원문 기준) | 구현 위치 | 기계 검증 함수 | 시연 검증 명령 |
|---|---|---|---|---|
| RTM-01 | SQLite 외래키 강제 활성화 선언 | `schema.sql:1` | `check_schema()` — `foreign_keys` 문자열 검사 | `head -1 schema.sql` |
| RTM-02 | `categories` 테이블 (PK, NOT NULL, UNIQUE) | `schema.sql` | `check_schema()` — 테이블·제약 존재 | `python3 verify_sql.py` |
| RTM-03 | `members` 테이블 (PK, `email` UNIQUE, NOT NULL 3개) | `schema.sql` | `check_schema()` | `python3 verify_sql.py` |
| RTM-04 | `books` 테이블 (FK `category_id`, `price >= 0` CHECK) | `schema.sql` | `check_schema()` | `python3 verify_sql.py` |
| RTM-05 | `rentals` 테이블 (FK 2개, `status` CHECK 3값) | `schema.sql` | `check_schema()` | `python3 verify_sql.py` |
| RTM-06 | `rentals(rental_date)` 인덱스 + 생성 사유 주석 | `schema.sql` | `check_schema()` — `sqlite_master` 인덱스 확인 | `demo.sh` Step 1 |
| RTM-07 | 4개 테이블 각 10행 이상, 총 45행 이상 | `seed.sql` | `check_seed()` | `demo.sh` Step 2 |
| RTM-08 | `RENTED`/`RETURNED`/`OVERDUE` 3상태 + 연체·복수 대여 포함 | `seed.sql` | `check_seed()` — 상태 분포 | `demo.sh` Step 2 |
| RTM-09 | Q01 카테고리별 가격 내림차순 (WHERE, ORDER BY) | `queries.sql` | `check_queries()` Q01 | `demo.sh` Step 3 |
| RTM-10 | Q02 연체(`OVERDUE`) 대여 조회 | `queries.sql` | Q02 | `demo.sh` Step 3 |
| RTM-11 | Q03 최근 가입 회원 5명 (ORDER BY, LIMIT) | `queries.sql` | Q03 | `python3 verify_sql.py` |
| RTM-12 | Q04 2020년 이후 & 20,000원 이상 (AND 다중 조건) | `queries.sql` | Q04 | `python3 verify_sql.py` |
| RTM-13 | Q05 도서+카테고리 INNER JOIN | `queries.sql` | Q05 | `python3 verify_sql.py` |
| RTM-14 | Q06 대여중 회원·도서·반납예정일 다중 INNER JOIN | `queries.sql` | Q06 | `python3 verify_sql.py` |
| RTM-15 | Q07 대여 이력 없는 도서 LEFT JOIN + IS NULL | `queries.sql` | Q07 | `python3 verify_sql.py` |
| RTM-16 | Q08 회원별 대여 횟수 (0회 포함) LEFT JOIN + COUNT | `queries.sql` | Q08 | `demo.sh` Step 3 |
| RTM-17 | Q09 카테고리별 권수·평균가 (COUNT, AVG, GROUP BY) | `queries.sql` | Q09 | `python3 verify_sql.py` |
| RTM-18 | Q10 회원별 연체 건수 (GROUP BY + HAVING) | `queries.sql` | Q10 | `python3 verify_sql.py` |
| RTM-19 | Q11 월별 대여 추이 (`strftime`, GROUP BY) | `queries.sql` | Q11 | `python3 verify_sql.py` |
| RTM-20 | Q12 평균가 초과 도서 (비상관 서브쿼리) | `queries.sql` | Q12 | `python3 verify_sql.py` |
| RTM-21 | Q13 회원별 최근 대여일 (상관 서브쿼리) | `queries.sql` | Q13 | `python3 verify_sql.py` |
| RTM-22 | Q14 기한 경과 미반납 ➔ `OVERDUE` 일괄 UPDATE | `queries.sql` | Q14 | `python3 verify_sql.py` |
| RTM-23 | Q15 탈퇴 대기 회원 테스트 대여 1건 DELETE | `queries.sql` | Q15 | `python3 verify_sql.py` |
| RTM-24 | Mermaid ERD + 테이블 명세 | `docs/ERD.md` | `check_docs()` — `erDiagram`, `\|\|--o{` | `sed -n '1,40p' docs/ERD.md` |
| RTM-25 | 보너스1 JOIN vs EXISTS 1:1 대조 | `docs/bonus/JOIN_VS_SUBQUERY.md` | `check_bonus()` (≥200 byte) | `cat docs/bonus/JOIN_VS_SUBQUERY.md` |
| RTM-26 | 보너스2 FK 위반 실증·해결 | `docs/bonus/INTEGRITY_VIOLATION.md` | `check_bonus()` | `demo.sh` Step 4 |
| RTM-27 | 보너스3 경영진 3대 KPI | `docs/bonus/KPI_REPORT.md` | `check_bonus()` | `cat docs/bonus/KPI_REPORT.md` |
| RTM-28 | 15대 쿼리 실행 결과 리포트 | `outputs/query_results.md` | `check_queries()` 자동 생성 | `head -40 outputs/query_results.md` |
| RTM-29 | 100점 무인 채점 통과 | `verify_sql.py` | 자체 실행 | `python3 verify_sql.py` |
| RTM-30 | 5단계 대화형 시연 러너 | `demo.sh` | `--non-interactive` exit 0 | `bash demo.sh --non-interactive` |
| RTM-31 | 제출·거버넌스 문서 4종 | `README.md`, `SUBMISSION.md`, `PROJECT_MANIFEST.json`, `RTM.md` | `check_docs()` | `ls -1 *.md PROJECT_MANIFEST.json` |

---

## 4. 절대 준수 규칙 (Rules)

1. 백엔드 프레임워크(Spring, Django, Express 등) 사용 금지.
2. API·웹 화면(UI) 생성 금지.
3. 뷰(VIEW), 저장 프로시저, 트리거 금지.
4. 산출물은 순수 표준 SQL 파일 3개로 한정.
5. SQLite 특성 방어: `schema.sql` 최상단 `PRAGMA foreign_keys = ON;`.
6. 외래키 의존성 역전 방지: DDL·DML 모두 부모 ➔ 자식 순서.
7. 제약조건 누락 금지: PK·NOT NULL(≥2)·UNIQUE·CHECK.
8. 인덱스 `rentals(rental_date)` + 1줄 사유 주석.
9. 민감정보(API 키) 하드코딩 금지 (ADR-016 가드레일 6).
10. Python 3.9+ 호환, UTF-8 NFC 파일명.

## 5. 구조 및 런타임 환경 명세

- 런타임: Python 3.9+ 표준 라이브러리만 (`sqlite3` 포함). 패키지 설치 0건.
- DB: SQLite 인메모리(`:memory:`) — 채점·시연 모두 디스크 오염 없음.
- 인코딩: UTF-8, 줄바꿈 LF.
- 금지: `| tail`로 출력 절단, 실제 키가 들어간 예시.

## 6. 실패 정책

- 스키마·시드 실행 실패 시 채점기는 즉시 `[FAIL]`과 원인을 출력하고 Exit Code 1.
- 쿼리 1개라도 실행 실패 시 실패한 Q번호와 SQLite 오류 메시지를 그대로 노출.
- 시연 러너는 실패 시에도 trap으로 임시 자원을 정리하고 종료.

## 7. 산출물 체크리스트 (Evaluation Rubric 대응)

| 루브릭 항목 | 대응 산출물 | 확인 명령 |
|---|---|---|
| 4개 테이블·PK/FK/제약조건 | `schema.sql` | `python3 verify_sql.py` |
| 10행 이상 한국어 시드 | `seed.sql` | `demo.sh` Step 2 |
| 15대 쿼리 카테고리 충족 | `queries.sql` | `outputs/query_results.md` |
| 실행 결과 캡처 | `outputs/query_results.md` | 파일 열람 |
| ERD | `docs/ERD.md` | Mermaid 미리보기 |
| 보너스 3종 | `docs/bonus/*.md` | 파일 열람 |
| 재현성 | `verify_sql.py`, `demo.sh` | `python3 verify_sql.py` |
