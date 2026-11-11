# B6-1 · 디지털 서랍장 — 도서관 스마트 대여/연체 관리 시스템

> 도서관 스마트 대여/연체 관리 도메인을 대상으로 관계형 데이터 모델링(4개 테이블, 1:N 관계 3개)과 15대 핵심 쿼리 및 3대 보너스 과제를 완성한 프로젝트입니다.

---

## 1. 미션 정보

### 1-1. 미션 요약
- **도메인**: 도서관 도서 대여 및 연체 관리 시스템
- **주요 내용**: 도서 대여 업무에 필요한 핵심 데이터를 관계형 데이터베이스로 모델링하고, 대여·반납·연체 관리 및 통계 산출을 위한 핵심 SQL 쿼리와 심층 분석 과제를 수행합니다.

### 1-2. 미션의 학습 목표
- **메인 학습 목표**:
  1. **데이터 모델링**: 도메인 요구사항에 부합하는 테이블 4개(`categories`, `members`, `books`, `rentals`) 설계
  2. **관계 설계**: 1:N 관계 3개 이상 도출 및 외래키(FK) 참조 무결성 연결
  3. **제약조건 정의**: PK, NOT NULL, UNIQUE, CHECK 제약조건을 통한 도메인 무결성 보장
  4. **인덱스 설계**: 조회 성능 향상을 위한 명시적 인덱스 정의 및 설계 근거 제시
  5. **시드 데이터 구축**: 테이블당 10행 이상(총 50행)의 한국어 실데이터 적재 (상태 3종 포진)
  6. **15대 핵심 쿼리 작성**: 기본 4, 조인 4, 집계 3, 서브쿼리 2, 수정/삭제 2 범주 구현
  7. **ERD 시각화**: 개념/물리 데이터 모델 다이어그램 및 설계 의도 문서화
- **보너스 학습 목표**:
  1. **JOIN vs 서브쿼리 대조**: 동일 요구사항에 대해 INNER JOIN과 EXISTS 서브쿼리 1:1 비교 (실행계획, 성능, 가독성)
  2. **참조 무결성 파괴 실증**: 부모 키 부재 레코드 삽입 시 외래키 제약조건 위반 실증 및 원인·해결책 규명
  3. **경영진 KPI 리포트**: 도서관 운영 의사결정을 위한 3대 핵심 지표(월별 대여 회전율, 최다 대여 도서 TOP 3, 회원 연체율) 산출 및 개선 액션 제시

### 1-3. 개발 환경 및 제약사항
- **DBMS 엔진**: SQLite 3 (설치 없이 실행 가능한 파일/인메모리 기반)
- **개발 언어**: Python 3 (표준 라이브러리 `sqlite3`만 사용, 외부 패키지 설치 불필요)
- **제약사항**:
  - 외부 프레임워크/ORM(Django, SQLAlchemy 등) 사용 금지, 순수 SQL 스크립트 작성
  - 트리거(Trigger) 및 뷰(View) 사용 금지
  - 외래키 제약조건 기본 활성화 (`PRAGMA foreign_keys = ON;`)

---

## 2. 수행 결과

### 2-1. 산출물 목록
| 구분 | 파일 경로 | 설명 |
|---|---|---|
| **스키마 DDL** | [`sql/schema.sql`](sql/schema.sql) | 테이블 4개, 외래키 3개, 제약조건, 복합 인덱스 정의 |
| **시드 데이터 DML** | [`sql/seed.sql`](sql/seed.sql) | 부모→자식 위상정렬 한국어 데이터 50행 적재 |
| **15대 쿼리 DQL/DML** | [`sql/queries.sql`](sql/queries.sql) | 기본·조인·집계·서브쿼리·수정/삭제 15대 쿼리 |
| **데이터 모델 ERD** | [`docs/ERD.md`](docs/ERD.md) | Mermaid ERD 다이어그램 및 테이블 상세 명세서 |
| **보너스 1 리포트** | [`bonus/JOIN_VS_SUBQUERY.md`](bonus/JOIN_VS_SUBQUERY.md) | INNER JOIN vs EXISTS 실행계획 및 성능 1:1 대조 |
| **보너스 1 실측 러너** | [`bonus/run_bonus1.py`](bonus/run_bonus1.py) | JOIN vs EXISTS 실행계획 및 10명 반환 실측 대조 실행 스크립트 |
| **보너스 2 리포트** | [`bonus/INTEGRITY_VIOLATION.md`](bonus/INTEGRITY_VIOLATION.md) | 외래키 참조 무결성 파괴 실측 trace 및 해결 3책 |
| **보너스 2 실측 러너** | [`bonus/run_bonus2.py`](bonus/run_bonus2.py) | 유령 회원 INSERT 차단 및 FK OFF 대조 실측 실행 스크립트 |
| **보너스 3 리포트** | [`bonus/KPI_REPORT.md`](bonus/KPI_REPORT.md) | 도서관 운영 경영진을 위한 3대 핵심 KPI 리포트 |
| **보너스 3 실측 러너** | [`bonus/run_bonus3.py`](bonus/run_bonus3.py) | 경영진 3대 KPI 리포트 실측 지표 산출 실행 스크립트 |
| **시연 스크립트** | [`demo.sh`](demo.sh) | 5단계 시연 자동화 러너 (대화형 및 비대화형) |

### 2-2. 리포지토리 폴더 구조
```text
B6-1/
├── README.md                      # 프로젝트 개요 및 수행 결과 종합 안내 (본 문서)
├── demo.sh                        # 5단계 시연 러너 스크립트
├── sql/                           # 🗄️ 공식 SQL 산출물
│   ├── schema.sql                 # DDL: 테이블·제약조건·인덱스 정의
│   ├── seed.sql                   # DML: 한국어 시드 데이터 50행
│   └── queries.sql                # DQL/DML: 15대 핵심 쿼리 (Q01~Q15)
├── bonus/                         # 🎁 공식 보너스 과제 산출물
│   ├── JOIN_VS_SUBQUERY.md        # 보너스 1: JOIN vs EXISTS 심층 비교 리포트
│   ├── run_bonus1.py              # 보너스 1: 실행계획 대조 실측 러너
│   ├── INTEGRITY_VIOLATION.md     # 보너스 2: 외래키 위반 실증 및 해결책 리포트
│   ├── run_bonus2.py              # 보너스 2: 외래키 파괴 실측 러너
│   ├── KPI_REPORT.md              # 보너스 3: 경영진 KPI 지표 리포트
│   └── run_bonus3.py              # 보너스 3: 3대 KPI 산출 실측 러너
├── docs/                          # 📚 설계 문서 및 내부 개발 기록
│   ├── ERD.md                     # 데이터 모델 Mermaid ERD
│   ├── DEMO_SCENARIO.md           # 시연 검증 시나리오 (자동/수동 실행 가이드)
│   ├── AUDIT_REPORT.md            # 개발 단계 독립 모델 교차 심사 보고서
│   └── spec/                      # 개발 단계 요구사항 추적 매트릭스(RTM) 등
└── test/                          # 🛠️ 개발 검증 및 테스트 자산
    ├── verify_sql.py              # 자체 기계 채점 스크립트
    └── outputs/                   # 15대 쿼리 실제 실행 결과 리포트
```

### 2-3. 개발 과정에서 추가로 결정한 사항
1. **외래키 검사 이중 강제 (`PRAGMA foreign_keys = ON;`)**:
   - SQLite는 레거시 하위 호환성을 위해 외래키 검사가 기본 비활성화되어 있습니다. 데이터 무결성을 보장하기 위해 DDL 파일(`sql/schema.sql`) 첫 줄에 명시 선언하고, 모든 연결 세션에서 필수로 활성화하도록 설계했습니다.
2. **`rentals.status` 상태 컬럼의 의도적 비정규화 및 정합성 복구**:
   - 도서의 현재 대여 상태는 대여일/반납일로 계산 가능하지만, 빈번한 연체 조회 성능을 위해 `status`(`RENTED`, `RETURNED`, `OVERDUE`) 컬럼을 유지했습니다. 대신 기한 경과 미반납 건을 기계적으로 복구하는 Q14 UPDATE 쿼리를 배치하여 정합성을 보장했습니다.
3. **독립 인메모리 격리 실행 지원**:
   - 로컬 환경에 잔여 DB 파일 오염 없이 평가자가 언제든 깨끗한 상태에서 검증할 수 있도록 `:memory:` 및 임시 파일 기반 실행을 지원합니다.

### 2-4. 한계 (Limitations)
1. **SQLite 엔진 고유의 제약**:
   - SQLite는 `RIGHT OUTER JOIN`과 `FULL OUTER JOIN`을 네이티브로 지원하지 않아, 양방향 외부 조인이 필요한 경우 `LEFT JOIN`과 `UNION` 조합으로 우회해야 합니다.
2. **동시성 및 대용량 트랜잭션 제약**:
   - 단일 파일 락킹 방식을 사용하므로 다중 사용자 동시 쓰기 환경에서는 병목이 발생할 수 있습니다. 엔터프라이즈 환경으로 확장 시 PostgreSQL 등의 클라이언트-서버 RDBMS로 마이그레이션이 필요합니다.

### 2-5. 미션 목표 충족 매트릭스
| 미션 요구 목표 | 세부 요구사항 및 제약조건 | 구현 산출물 및 충족 증거 |
|---|---|---|
| **테이블 4개 설계** | 도메인에 부합하는 관계형 테이블 4종 구비 | `sql/schema.sql` — `categories`, `members`, `books`, `rentals` 4개 테이블 |
| **1:N 관계 3개 이상** | 외래키(FK)를 통한 명확한 참조 무결성 연결 | `books.category_id → categories`, `rentals.member_id → members`, `rentals.book_id → books` (FK 3개) |
| **무결성 제약조건** | PK, NOT NULL, UNIQUE, CHECK 제약조건 필수 적용 | PK 4개, NOT NULL 18개, UNIQUE 2개(`email`, `category_name`), CHECK 2개(`price >= 0`, `status IN (...)`) |
| **인덱스 정의** | 성능 향상을 위한 명시적 인덱스 및 사유 기재 | `sql/schema.sql` — 대여일 범위 및 월별 집계 가속용 `idx_rentals_date` 생성 |
| **시드 데이터 45행+** | 테이블당 10행 이상 한국어 데이터 적재 | `sql/seed.sql` — categories 10, members 12, books 13, rentals 15 = **총 50행** (상태 3종 포진) |
| **15대 핵심 쿼리** | 기본4 · 조인4 · 집계3 · 서브쿼리2 · 수정/삭제2 | `sql/queries.sql` — Q01 ~ Q15 전 범주 구현 (실제 실행 결과: `test/outputs/query_results.md`) |
| **데이터 모델 ERD** | 개념 및 물리 모델 가시화 다이어그램 | [`docs/ERD.md`](docs/ERD.md) — Mermaid ERD 및 상세 명세 |
| **3대 보너스 과제** | JOIN 비교, 참조 무결성 위반, 경영진 KPI 리포트 | [`bonus/`](bonus/) — `JOIN_VS_SUBQUERY.md`, `INTEGRITY_VIOLATION.md`, `KPI_REPORT.md` 심층 분석 |

### 2-6. 결과물 실행 방법
1. **간편 시연 (원스크립트 5단계 + 보너스 3종 실행)**:
   ```bash
   bash demo.sh
   ```
   - 5단계 시연이 순차적으로 진행됩니다. (엔터를 누르면 다음 단계로 진행)
   - 비대화형 일괄 실행: `bash demo.sh --non-interactive`

2. **보너스 과제 3종 개별 실측 실행**:
   ```bash
   python3 bonus/run_bonus1.py   # 보너스 1: JOIN vs EXISTS 실행계획 대조
   python3 bonus/run_bonus2.py   # 보너스 2: 외래키 무결성 파괴 및 FK OFF 대조 실증
   python3 bonus/run_bonus3.py   # 보너스 3: 경영진 3대 KPI 실측 지표 산출
   ```

3. **개별 SQL 파일 직접 실행 (SQLite CLI)**:
   ```bash
   sqlite3 library.db < sql/schema.sql
   sqlite3 library.db < sql/seed.sql
   sqlite3 library.db < sql/queries.sql
   ```

---

## 3. 외부 문서 링크

- **시연 상세 가이드**: [`docs/DEMO_SCENARIO.md`](docs/DEMO_SCENARIO.md) — 자동 실행 및 수동 시연 5단계 상세 절차
- **데이터 모델 명세서**: [`docs/ERD.md`](docs/ERD.md) — Mermaid ERD 다이어그램 및 테이블·컬럼 세부 명세
- **개발 단계 교차 감사 보고서**: [`docs/AUDIT_REPORT.md`](docs/AUDIT_REPORT.md) — 개발 과정에서 수행한 독립 모델 교차 심사 결과 (내부 참고용)
