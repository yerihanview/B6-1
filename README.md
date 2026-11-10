# B6-1 · 디지털 서랍장 — 도서관 스마트 대여/연체 관리 시스템

> **미션**: 정보를 깔끔하게 정리하는 디지털 서랍장 만들기 (SQL/RDBMS 데이터 모델링 + 15대 쿼리)  
> **도메인**: 도서관 스마트 대여/연체 관리 시스템 — 4개 테이블, 1:N 관계 3개  
> **엔진**: SQLite 3 (설치 0, 인메모리 격리 지원) · **의존성**: Python 3 표준 라이브러리만  
> **기계 채점**: `python3 test/verify_sql.py` ➔ **100/100 ALL PASS** (적대적 음성 변조 테스트 6종 전수 차단)  
> **외부 교차 감사**: 독립 모델(GPT-5.4 82점, Claude-Sonnet-4 92점) 적대적 심사 완료 및 피드백 반영 ([AUDIT_REPORT.md](docs/AUDIT_REPORT.md))  
> **제출자**: 우광택 (@yerihanview) · **저장소**: [github.com/yerihanview/B6-1](https://github.com/yerihanview/B6-1)

---

## 1. 미션 목표 및 루브릭 100% 충족 현황 (Compliance Matrix)

본 프로젝트는 미션 발제문에서 요구한 모든 정량적·정성적 요건을 100% 충족하도록 설계·구현되었습니다:

| 미션 요구 목표 | 세부 요구사항 및 제약조건 | 구현 산출물 및 충족 증거 | 기계 검증 |
|---|---|---|:---:|
| **테이블 4개 설계** | 도메인에 부합하는 관계형 테이블 4종 구비 | `sql/schema.sql` — `categories`, `members`, `books`, `rentals` 4개 테이블 정의 | ✅ PASS |
| **1:N 관계 3개 이상** | 외래키(FK)를 통한 명확한 참조 무결성 연결 | `books.category_id → categories`, `rentals.member_id → members`, `rentals.book_id → books` (FK 3개) | ✅ PASS |
| **무결성 제약조건** | PK, NOT NULL, UNIQUE, CHECK 제약조건 필수 적용 | PK 4개, NOT NULL 18개(테이블당 2개 이상), UNIQUE 2개(`email`, `category_name`), CHECK 2개(`price >= 0`, `status IN (...)`) | ✅ PASS |
| **인덱스 정의** | 성능 향상을 위한 명시적 인덱스 및 사유 기재 | `sql/schema.sql` — 대여일 범위 및 월별 집계 가속용 `idx_rentals_date` 인덱스 생성 | ✅ PASS |
| **시드 데이터 45행+** | 테이블당 10행 이상 한국어 데이터 적재 | `sql/seed.sql` — categories 10, members 12, books 13, rentals 15 = **총 50행** (상태 3종 포진) | ✅ PASS |
| **15대 핵심 쿼리** | 기본4 · 조인4 · 집계3 · 서브쿼리2 · 수정/삭제2 | `sql/queries.sql` — Q01 ~ Q15 전 범주 구현, [test/outputs/query_results.md](test/outputs/query_results.md) 실측 리포트 | ✅ PASS |
| **데이터 모델 ERD** | 개념 및 물리 모델 가시화 다이어그램 | [docs/ERD.md](docs/ERD.md) — Mermaid ERD 및 정규화/인덱스 설계 의도 명세 | ✅ PASS |
| **3대 보너스 과제** | JOIN 비교, 참조 무결성 위반, 경영진 KPI 리포트 | [docs/bonus/](docs/bonus/) — `JOIN_VS_SUBQUERY.md`, `INTEGRITY_VIOLATION.md`, `KPI_REPORT.md` 심층 분석 | ✅ PASS |
| **원클릭 재현성** | 외부 의존성 없는 원클릭 시연 및 무인 채점기 | `bash demo.sh` (5단계 시연), `python3 test/verify_sql.py` (100점 기계 채점) | ✅ PASS |

---

## 2. 핵심 아키텍처 설계 판단 3가지

1. **SQLite 3 엔진 선택**:
   - 별도 데이터베이스 서버나 클라이언트 CLI 설치가 전혀 필요 없는 파일/인메모리 기반 엔진을 채택하여, 동료평가자가 어떤 OS(Mac, Windows, Linux)에서도 단 0.1초 만에 오류 없이 100% 동일하게 결과를 재현할 수 있습니다.
2. **`PRAGMA foreign_keys = ON;` 이중 방어**:
   - SQLite는 역사적 하위 호환성을 이유로 외래키 검사가 기본 OFF로 비활성화되어 있는 함정이 있습니다. 본 프로젝트는 `sql/schema.sql` 첫 줄 선언과 채점기 인메모리 연결 양쪽에서 이를 강제 활성화하여 외래키 고아 데이터 삽입을 완벽히 방어합니다.
3. **`rentals.status` 상태 컬럼의 의도적 비정규화 및 정합성 복구**:
   - `status`는 `return_date`와 `due_date`로부터 유도될 수 있으나, 빈번한 대여/연체 조회의 단순성과 성능을 위해 의도적으로 컬럼으로 유지(비정규화)했습니다. 대신 Q14(UPDATE)가 기한 경과 미반납 건을 `OVERDUE`로 갱신하여 데이터 정합성을 기계적으로 복구하도록 설계했습니다.

---

## 3. 저장소 디렉토리 구조 (Clean Architecture)

본 저장소는 평가 대상 산출물과 검증 도구, 내부 스펙을 Bounded Context에 따라 명확히 분리하여 루트를 청결하게 유지합니다:

```text
B6-1/
├── README.md                      # 프로젝트 개요, 충족 매트릭스, 설계 판단, 실행 가이드 (본 문서)
├── CONTRIBUTING.md                # 저장소 운영 정책 및 코드 검증 가이드
├── demo.sh                        # 평가자용 5단계 인터랙티브 시연 러너 (E2E 스모크 테스트 지원)
├── .gitignore                     # 임시 파일 및 캐시 제외 규칙
├── sql/                           # 🗄️ 핵심 SQL 산출물
│   ├── schema.sql                 # DDL: PRAGMA FK, 4개 테이블, 제약조건 4종, 복합 인덱스
│   ├── seed.sql                   # DML: 부모→자식 위상정렬 한국어 시드 50행 (상태 3종)
│   └── queries.sql                # DQL/DML: 15대 쿼리 (Q01~Q15, 카테고리 주석 완비)
├── test/                          # 🛠️ 검증 및 기계 채점 자산
│   ├── verify_sql.py              # Zero-Dependency 100점 기계 채점기 (6대 음성 변조 테스트 내장)
│   ├── INTERNAL_TEST_REPORT.md    # 내부 기계 채점 결과 및 회귀 검증 실측 보고서
│   └── outputs/
│       └── query_results.md       # 15대 쿼리 실제 실행 결과 및 반환 표 (채점기 자동 생성)
└── docs/                          # 📚 설계 및 분석 문서
    ├── ERD.md                     # Mermaid ERD 다이어그램 + 테이블 상세 명세서
    ├── DEMO_SCENARIO.md           # 동료평가 발표자용 5단계 시연 시나리오 상세 가이드
    ├── AUDIT_REPORT.md            # 독립 모델(GPT-5.4/Claude) 적대적 교차 심사 종합 보고서
    ├── bonus/                     # 3대 보너스 과제 심층 분석
    │   ├── JOIN_VS_SUBQUERY.md    # 보너스 1: INNER JOIN vs EXISTS 실행계획 실측 대조
    │   ├── INTEGRITY_VIOLATION.md # 보너스 2: 외래키 위반 실측 에러 및 해결 3책
    │   └── KPI_REPORT.md          # 보너스 3: 경영진 3대 KPI 실측 지표 분석
    ├── spec/                      # 내부 요구사항 추적성 매트릭스(RTM) 및 매니페스트
    └── pipeline/                  # 무인 생성 파이프라인 및 실행 메타데이터 로그
```

---

## 4. 원클릭 실행 및 시연 방법 (설치 0)

### 4-1. 100점 무인 기계 채점 (0.05초 만에 확인)

```bash
python3 test/verify_sql.py
```

* **채점 결과**: 6개 블록 전수 PASS ➔ **100/100 ALL PASS**
* **결과지 자동 생성**: [test/outputs/query_results.md](test/outputs/query_results.md)에 15개 쿼리의 실제 실행 표가 결정론적으로 재생성됩니다.
* 상세 내부 검증 실측 증적은 **[test/INTERNAL_TEST_REPORT.md](test/INTERNAL_TEST_REPORT.md)**를 참조하십시오.

### 4-2. 5단계 인터랙티브 시연 러너 (동료평가 발표용)

```bash
# 대화형 시연: 엔터를 누르며 한 단계씩 출력 확인
bash demo.sh

# 무인 스모크 테스트: CI 및 자동화 파이프라인용 (Exit Code 0 검증)
bash demo.sh --non-interactive
```

* 발표자 멘트, 단계별 실행 명령, 세부 확인 포인트가 정리된 전문 시나리오는 **[docs/DEMO_SCENARIO.md](docs/DEMO_SCENARIO.md)**에 구비되어 있습니다.

---

## 5. 15대 핵심 쿼리 카테고리 요약

| 카테고리 | 쿼리 번호 및 내용 | 핵심 사용 SQL 기법 | 반환 행 |
|---|---|---|:---:|
| **기본 조회 (4)** | Q01 카테고리별 가격 내림차순 도서 목록 | `WHERE` + `ORDER BY ... DESC` | 2행 |
| | Q02 현재 연체(OVERDUE) 중인 대여 기록 | `WHERE status = 'OVERDUE'` | 4행 |
| | Q03 최근 가입한 회원 상위 5명 | `ORDER BY join_date DESC` + `LIMIT 5` | 5행 |
| | Q04 2020년 이후 출판 & 2만원 이상 도서 | 복합 조건 (`AND`) | 2행 |
| **조인 (4)** | Q05 도서 목록 및 카테고리명 매핑 | `INNER JOIN` (2개 테이블) | 13행 |
| | Q06 대여 중인 회원명·도서명·반납예정일 | 다중 `INNER JOIN` (3개 테이블) | 4행 |
| | Q07 한 번도 대여되지 않은 도서 목록 | `LEFT JOIN` + `WHERE rentals.rental_id IS NULL` | 2행 |
| | Q08 전체 회원별 대여 횟수 (0회 회원 포함) | `LEFT JOIN` + `COUNT` + `GROUP BY` | 12행 |
| **집계 (3)** | Q09 카테고리별 도서 권수 및 평균 가격 | `COUNT`, `AVG`, `ROUND`, `GROUP BY` | 10행 |
| | Q10 2건 이상 대여한 다독 회원 집계 | `GROUP BY` + `HAVING COUNT(*) >= 2` | 4행 |
| | Q11 월별 총 대여 건수 추이 | `strftime('%Y-%m', rental_date)` + `GROUP BY` | 9행 |
| **서브쿼리 (2)** | Q12 전체 도서 평균 가격을 초과하는 도서 | 비상관 서브쿼리 (`WHERE price > (SELECT AVG...)`) | 5행 |
| | Q13 회원별 최근 대여 일자 조회 | SELECT절 상관 서브쿼리 (`WHERE r.member_id = m.member_id`) | 12행 |
| **수정/삭제 (2)** | Q14 반납기한 경과 미반납 건 연체 처리 | `UPDATE ... SET status = 'OVERDUE' WHERE ...` | 1행 갱신 |
| | Q15 탈퇴 대기 회원의 테스트 대여 이력 삭제 | `DELETE ... WHERE member_id IN (SELECT ...)` | 1행 삭제 |

15개 쿼리의 실제 반환 데이터 표 전문은 **[test/outputs/query_results.md](test/outputs/query_results.md)**에서 확인하실 수 있습니다.

---

## 6. 3대 보너스 과제 심층 분석 요약 (ADR-015 준수)

1. **[보너스 1] INNER JOIN vs EXISTS 성능 및 실행계획 대조 ([docs/bonus/JOIN_VS_SUBQUERY.md](docs/bonus/JOIN_VS_SUBQUERY.md))**:
   - "대여 이력이 있는 회원 조회"를 두 방식으로 구현하고 `EXPLAIN QUERY PLAN`을 실측했습니다.
   - 결과는 10명으로 동일하나, JOIN은 중복 제거를 위해 `TEMP B-TREE FOR DISTINCT` 임시 인메모리 트리를 생성하는 반면, EXISTS는 인덱스 스캔 중 매칭 1건 발견 즉시 단락 평가(Short-circuiting)하여 정렬 오버헤드가 0임을 증명했습니다.
2. **[보너스 2] 외래키 참조 무결성 파괴 실측 및 해결책 ([docs/bonus/INTEGRITY_VIOLATION.md](docs/bonus/INTEGRITY_VIOLATION.md))**:
   - 존재하지 않는 `member_id = 999`를 외래키로 삽입할 때 `sqlite3.IntegrityError: FOREIGN KEY constraint failed` 에러가 발생하며 원자적으로 롤백됨을 실측 캡처했습니다.
   - `PRAGMA foreign_keys = OFF` 상태에서는 고아 행이 조용히 유입되는 위험을 대조하고, 부모 선행 생성, `ON DELETE SET NULL`, 트랜잭션 격리의 3대 해결책을 제시했습니다.
3. **[보너스 3] 도서관 운영 경영진을 위한 3대 핵심 KPI 리포트 ([docs/bonus/KPI_REPORT.md](docs/bonus/KPI_REPORT.md))**:
   - **KPI 1 (장서 회전율)**: 월별 0.077 ~ 0.154 수준 (8~9월 대여 급감 현상 포착).
   - **KPI 2 (인기 도서 TOP 3)**: '채식주의자', '습관의 힘', '클린 코드' 각 2회 대여 (4권 공동 1위).
   - **KPI 3 (도서관 연체율)**: 전체 대여 15건 중 4건으로 **26.7%**의 심각한 연체율 실측 및 SMS 사전 알림·페널티 개선책 제안.

---

## 7. 독립 적대적 교차 심사(Adversarial Cross-Audit) 결과

본 프로젝트는 생성자의 자기 검증 편향을 배제하기 위해, 코디세이 API 경유 독립 프론티어 모델 2종(`gpt-5.4`, `claude-sonnet-4`)을 심사관으로 세워 50개 항목에 대한 2단계 대화형 적대적 감사를 완료했습니다.

* **감사 채점 결과**: GPT-5.4 **82점**, Claude-Sonnet-4 **92점** (조건부 통과).
* **적발 결함 및 권고 조치 전수 반영 완료**:
  1. `verify_sql.py`에 6대 적대적 음성 변조 테스트(Mutation Testing) 및 쿼리 행수 단언을 내장하여 채점기 맹점 완전 극복.
  2. `sql/schema.sql`의 `categories` 테이블에 `created_at NOT NULL DEFAULT CURRENT_TIMESTAMP`를 명시하여 스펙(테이블당 NOT NULL 2개 이상) 완벽 충족.
  3. `docs/bonus/KPI_REPORT.md`의 KPI-2 표를 실제 SQL `LIMIT 3` 실행 결과 3행과 100% 정합 동기화.
  4. `sql/queries.sql`의 Q14 실행 조건을 `due_date < '2026-11-10'`으로 고정하여 날짜 독립적 재현성 보장.
* 감사 상세 로그 전문 및 2단계 검증 프로토콜은 **[docs/AUDIT_REPORT.md](docs/AUDIT_REPORT.md)**에 보존되어 있습니다.

---

## 8. 기술적 한계와 트레이드오프

* **SQLite 고유 문법 종속성**: `strftime('%Y-%m', ...)` 및 `PRAGMA foreign_keys`는 SQLite 전용 문법입니다. PostgreSQL/MySQL 등 엔터프라이즈 RDBMS로 마이그레이션할 경우 `TO_CHAR()` 함수로 치환하고 PRAGMA 선언을 제거해야 합니다.
* **트리거 및 배치 부재**: 미션 규칙 준수를 위해 트리거와 저장 프로시저를 배제했습니다. 실제 프로덕션 환경에서는 반납기한 경과 시 실시간으로 `status`를 `OVERDUE`로 전이시키는 스케줄러 배치가 수반되어야 합니다.
* **표본 데이터 크기**: 50행은 기능성 검증용 시드 데이터입니다. `idx_rentals_date` 인덱스의 B-Tree 스캔 효율성을 상용 수준에서 정량 입증하려면 수만 건 이상의 대량 벤치마크 데이터셋이 필요합니다.
