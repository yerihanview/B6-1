# 제출서 — B6-1 디지털 서랍장 (도서관 스마트 대여/연체 관리 시스템)

| 항목 | 내용 |
|---|---|
| 과정 | 코디세이 AI 올인원 — 데이터베이스와 백엔드 |
| 미션 | 정보를 깔끔하게 정리하는 디지털 서랍장 만들기 (B6-1) |
| 제출자 | 우광택 (@yerihanview) |
| 제출일 | 2026-11-10 |
| 저장소 | https://github.com/yerihanview/B6-1 (public) |
| 기술 스택 | SQLite 3 · 표준 SQL · Python 3 표준 라이브러리 (외부 패키지 0) |

---

## 1. 제출 서약

1. 이 미션의 산출물(`schema.sql`, `seed.sql`, `queries.sql`, `verify_sql.py`, `docs/`, `outputs/`)은 **본인이 설계하고 직접 실행·검증**하였다. AI 에이전트는 린 에이전틱 방법론에 따라 초안 생성과 교차 점검에 활용했으며, 최종 산출물의 채택·보정·검증 책임은 제출자에게 있다.
2. 미션의 제약을 준수하였다: **백엔드 프레임워크, API, UI, 뷰, 저장 프로시저, 트리거를 사용하지 않았고**, 산출물은 순수 표준 SQL 3종과 이를 검증하는 스크립트·문서로 한정된다.
3. 외부에서 가져온 코드·데이터는 사용하지 않았으며, 시드의 도서·회원 정보는 실습용으로 작성한 가상 데이터이다(실존 인물·연락처와 무관).
4. API 키 등 민감정보를 저장소에 포함하지 않았다. 생성 파이프라인은 환경변수만 사용한다.
5. 아래 실행 명령으로 **누구나 동일하게 재현**할 수 있음을 확인하였다.

```text
Python 3.12.16 / SQLite 3.46.1 / 2026-11-10 실행
$ python3 verify_sql.py
🎉 [100점 만점 ALL PASS] 디지털 서랍장 미션 최종 점수: 100/100점   (Exit Code 0)
```

---

## 2. 산출물 링크

| # | 산출물 | 링크 | 설명 |
|---|---|---|---|
| 1 | 스키마 DDL | [schema.sql](schema.sql) | PRAGMA FK, 4테이블, PK·FK·NOT NULL·UNIQUE·CHECK, `rentals(rental_date)` 인덱스 |
| 2 | 시드 DML | [seed.sql](seed.sql) | 부모→자식 순서, 4테이블 50행 한국어 데이터, 상태 3종 |
| 3 | 15대 쿼리 | [queries.sql](queries.sql) | Q01~Q15 (기본4·조인4·집계3·서브쿼리2·수정삭제2) |
| 4 | 실행 결과 | [outputs/query_results.md](outputs/query_results.md) | 15개 쿼리 전문 + 실제 반환 행·표 |
| 5 | ERD | [docs/ERD.md](docs/ERD.md) | Mermaid ERD, 테이블 명세서, 정규화·인덱스 설계 의도 |
| 6 | 보너스 1 | [docs/bonus/JOIN_VS_SUBQUERY.md](docs/bonus/JOIN_VS_SUBQUERY.md) | INNER JOIN vs EXISTS — 실행계획 실측 대조 |
| 7 | 보너스 2 | [docs/bonus/INTEGRITY_VIOLATION.md](docs/bonus/INTEGRITY_VIOLATION.md) | FK 위반 실측(`FOREIGN KEY constraint failed`)과 해결 3책 |
| 8 | 보너스 3 | [docs/bonus/KPI_REPORT.md](docs/bonus/KPI_REPORT.md) | 경영진 3대 KPI (회전율·인기 도서·연체율) |
| 9 | 기계 채점기 | [verify_sql.py](verify_sql.py) | 무의존성 100점 채점 (6블록) |
| 10 | 시연 러너 | [demo.sh](demo.sh) | 5단계 엔터 진행형, `--non-interactive` 지원 |
| 11 | 실행 안내 | [README.md](README.md) | 개요·ERD·실행·시연·루브릭 체크리스트 |
| 12 | 추적 매트릭스 | [RTM.md](RTM.md) | 요구사항 38항목 1:1 매핑과 검증 상태 |
| 13 | 프로젝트 이력 | [PROJECT_MANIFEST.json](PROJECT_MANIFEST.json) | 미션·모델·산출물 해시·검증 결과 |

> `ORDER_SHEET.md`는 평가 대상 산출물이 아니라 린 방법론의 내부 작업 지시서(계약서)다 (ADR-018).

---

## 3. 재현 절차 (평가자용 3단계)

```bash
# 1) 저장소 클론
git clone https://github.com/yerihanview/B6-1.git && cd B6-1

# 2) 100점 기계 채점 (설치 없음, 0.2초)
python3 verify_sql.py

# 3) 5단계 시연 (엔터 진행형)
bash demo.sh
```

- 요구 환경: Python 3.9+ (표준 라이브러리만). SQLite CLI·DB 서버 설치 불필요.
- 모든 DB 작업은 인메모리 또는 임시 디렉토리에서 수행되어 작업 트리를 오염시키지 않는다.

---

## 4. 핵심 설계 판단 3가지

1. **SQLite 선택**: 설치 0·파일 기반으로 평가자 환경에서 실패 확률이 가장 낮고, Python 표준 라이브러리만으로 인메모리 채점이 가능하다.
2. **PRAGMA foreign_keys 명시**: SQLite의 기본 OFF 함정을 스키마 첫 줄과 채점기 양쪽에서 방어한다. 보너스 2는 이 함정을 실측으로 보여 준다.
3. **상태 컬럼의 의도적 비정규화**: `rentals.status`를 저장해 조회를 단순화하고, Q14(UPDATE)가 `due_date`·`return_date`와의 정합을 복구하도록 설계했다. 트레이드오프는 README 제12장에 명시했다.
