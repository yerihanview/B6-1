# B6-1 저장소 운영 및 기여 가이드 (Contributing Guide)

본 저장소는 **린 에이전틱 개발 방법론(Lean Agentic Methodology)**에 기반하여 운영되며, 수석 아키텍트의 수동 감시 없이도 산출물의 무결성을 공학적으로 보증합니다.

---

## 1. 디렉토리 구조 및 역할 분담 (SSOT)

저장소 루트는 운영 문서와 진입점 스크립트만 유지하며, 각 산출물은 명확한 Bounded Context에 따라 격리 관리됩니다:

* **루트 (`/`)**:
  - `README.md`: 프로젝트 개요, 요구사항 충족 매트릭스, 핵심 설계 판단, 디렉토리 구조, 원클릭 실행 안내.
  - `CONTRIBUTING.md`: 저장소 운영 및 검증 규칙 가이드 (본 문서).
  - `demo.sh`: 평가자 및 발표자용 5단계 인터랙티브 시연 러너.
  - `.gitignore`: 임시 데이터베이스(`*.db`) 및 파이썬 캐시(`__pycache__`) 배제.
* **`sql/` (핵심 데이터베이스 산출물)**:
  - `schema.sql`: DDL 정의서 (PRAGMA 외래키 활성화, 4개 테이블, 제약조건, 인덱스).
  - `seed.sql`: DML 시드 적재 스크립트 (부모➔자식 위상정렬 50행 데이터).
  - `queries.sql`: DQL/DML 15대 쿼리 정의서 (Q01~Q15).
* **`test/` (검증 및 기계 채점)**:
  - `verify_sql.py`: Zero-Dependency 100점 무인 기계 채점기 (6대 음성 변조 테스트 내장).
  - `INTERNAL_TEST_REPORT.md`: 내부 기계 채점 결과 및 적대적 변조 테스트 실측 보고서.
  - `outputs/query_results.md`: 15대 쿼리 실행 결과 마크다운 자동 추출 원장.
* **`docs/` (설계 및 기술 문서)**:
  - `ERD.md`: Mermaid 다이어그램 및 테이블 상세 명세서.
  - `DEMO_SCENARIO.md`: 동료평가 발표자용 5단계 시연 시나리오 가이드.
  - `AUDIT_REPORT.md`: 코디세이 API 경유 독립 모델(GPT-5.4, Claude) 적대적 교차 심사 보고서.
  - `bonus/`: 3대 보너스 과제 심층 분석 문서 (`JOIN_VS_SUBQUERY.md`, `INTEGRITY_VIOLATION.md`, `KPI_REPORT.md`).
  - `spec/`: 요구사항 추적성 매트릭스(`RTM.md`), 내부 작업 지시서(`ORDER_SHEET.md`), 프로젝트 이력(`PROJECT_MANIFEST.json`).
  - `pipeline/`: 무인 생성 파이프라인 스크립트 및 실행 메타데이터.

---

## 2. 코드 변경 및 기계적 검증 규칙

1. **SQL 문법 변경 시 검증**:
   - `sql/schema.sql`, `sql/seed.sql`, `sql/queries.sql` 수정 시 반드시 아래 명령을 실행하여 100/100 ALL PASS를 확인해야 합니다:
     ```bash
     python3 test/verify_sql.py
     ```
2. **시연 러너 무결성 검증**:
   - 시연 스크립트 수정 시 E2E 스모크 테스트를 통해 워킹 트리 오염 없이 Exit 0으로 종료되는지 검증합니다:
     ```bash
     bash demo.sh --non-interactive
     ```
3. **독립 적대적 교차 감사 준수**:
   - 중대한 스펙 변경 시 독립 모델을 통한 적대적 교차 감사를 수행하고, 권고 조치 사항은 즉시 핫픽스 및 회귀 테스트 케이스로 자산화합니다.
