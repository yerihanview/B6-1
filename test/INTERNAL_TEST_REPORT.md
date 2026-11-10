# B6-1 자체 내부 기계 검증 결과 보고서 (Internal Test Report)

> **검증 도구**: `test/verify_sql.py` (Zero-Dependency Python 3 내장 라이브러리 채점기)  
> **검증 일시**: 2026-11-10  
> **검증 환경**: Python 3.12.16 / SQLite 3.46.1 (In-Memory Isolation)  
> **최종 판정**: **100점 만점 ALL PASS (Exit Code 0)**

---

## 1. 6대 검증 블록 채점 결과 요약

| 블록 | 검증 항목 | 배점 | 판정 | 실측 세부 증적 |
|---|---|:---:|:---:|---|
| **블록 1** | 7대 필수 산출물 파일 전수 존재 | 20 | **PASS** | `sql/schema.sql`, `sql/seed.sql`, `sql/queries.sql`, `docs/ERD.md`, `docs/bonus/` 3종 전수 확인 |
| **블록 2** | 스키마 생성 및 DDL 무결성 | 20 | **PASS** | 4개 테이블 생성, PK 4개, FK 3개, `rentals(rental_date)` 인덱스(`idx_rentals_date`) 확인 |
| **블록 3** | 시드 데이터 정량 및 상태 다양성 | 20 | **PASS** | 총 50행 (categories 10, members 12, books 13, rentals 15), 상태 3종, 복수 대여 회원 4명 |
| **블록 4** | 6대 적대적 음성 변조 테스트 (Mutation) | 10 | **PASS** | 가짜 데이터 고의 주입 시 전수 `IntegrityError` 정상 발생 차단 확인 |
| **블록 5** | 15대 핵심 쿼리 실행 및 단언 | 20 | **PASS** | Q01~Q15 전수 무오류 실행, 기대 행수 단언 통과, `test/outputs/query_results.md` 자동 추출 |
| **블록 6** | 3대 보너스 과제 심층 작성 | 10 | **PASS** | `JOIN_VS_SUBQUERY.md`(8.9KB), `INTEGRITY_VIOLATION.md`(5.7KB), `KPI_REPORT.md`(9.6KB) |
| **총점** | **디지털 서랍장 기계 채점 최종 스코어** | **100** | **ALL PASS** | **100 / 100 점 (무결점 통과)** |

---

## 2. 6대 적대적 음성 변조 테스트(Mutation Testing) 실측 증적

외부 감사(GPT-5.4)에서 지적된 "검증기가 단순 존재만 확인하고 제약 위반을 감사하지 않는 맹점"을 극복하기 위해 신설된 회귀 방어 테스트 내역:

1. **유령 외래키(FK) 삽입 차단**: 존재하지 않는 `member_id = 999` 대여 등록 시 `sqlite3.IntegrityError: FOREIGN KEY constraint failed` 발생 확인.
2. **음수 도서 정가(`price = -5000`) 차단**: `CHECK (price >= 0)` 제약 위반 시 `sqlite3.IntegrityError: CHECK constraint failed` 발생 확인.
3. **무효 대여 상태(`status = 'LOST'`) 차단**: `CHECK (status IN ('RENTED','RETURNED','OVERDUE'))` 제약 위반 시 `IntegrityError` 발생 확인.
4. **중복 카테고리명 차단**: `categories.category_name UNIQUE` 제약 위반 시 `sqlite3.IntegrityError: UNIQUE constraint failed` 발생 확인.
5. **중복 회원 이메일 차단**: `members.email UNIQUE` 제약 위반 시 `sqlite3.IntegrityError: UNIQUE constraint failed` 발생 확인.
6. **NOT NULL 컬럼 누락 삽입 차단**: `categories.created_at = NULL` 삽입 시 `sqlite3.IntegrityError: NOT NULL constraint failed` 발생 확인.

---

## 3. 재현 실행 명령

```bash
# 저장소 루트에서 무의존성 단독 실행 (0.05초 소요)
python3 test/verify_sql.py
```
