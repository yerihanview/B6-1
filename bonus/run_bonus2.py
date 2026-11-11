#!/usr/bin/env python3
"""
[보너스 2] 외래키 참조 무결성 파괴 실증 및 방어 러너
- 실행 위치: 저장소 루트 또는 bonus/ 디렉토리 (자동 경로 보정)
- 실행 방법: python3 bonus/run_bonus2.py
"""

import os
import sqlite3
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCHEMA_PATH = os.path.join(BASE_DIR, "sql", "schema.sql")
SEED_PATH = os.path.join(BASE_DIR, "sql", "seed.sql")

def main():
    print("=" * 70)
    print(" 🎁 [보너스 2] 외래키 참조 무결성 파괴 실증 (존재하지 않는 member_id=999)")
    print("=" * 70)

    invalid_sql = (
        "INSERT INTO rentals (member_id, book_id, rental_date, due_date, status) "
        "VALUES (999, 1, '2026-11-10', '2026-11-24', 'RENTED');"
    )

    # 1. 외래키 활성화 (PRAGMA foreign_keys = ON) 실증
    print("\n[시나리오 1] 외래키 활성화 상태 (정상 시스템 — PRAGMA foreign_keys = ON)")
    conn_on = sqlite3.connect(":memory:")
    conn_on.execute("PRAGMA foreign_keys = ON;")
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn_on.executescript(f.read())
    with open(SEED_PATH, encoding="utf-8") as f:
        conn_on.executescript(f.read())

    before_count = conn_on.execute("SELECT COUNT(*) FROM rentals;").fetchone()[0]
    print(f"  - 초기 rentals 행 수: {before_count}행")
    print("  - 유령 회원(member_id=999) 대여 레코드 삽입 시도...")

    try:
        conn_on.execute(invalid_sql)
        print("  ❌ [치명적 결함] 외래키 검사가 실패하여 유령 데이터가 삽입되었습니다!")
    except sqlite3.IntegrityError as e:
        print(f"  ✔ [정상 차단] {type(e).__name__}: {e}")

    after_count = conn_on.execute("SELECT COUNT(*) FROM rentals;").fetchone()[0]
    print(f"  - 시도 후 rentals 행 수: {after_count}행 (데이터 무결성 100% 보존)")

    # 2. 외래키 비활성화 (PRAGMA foreign_keys = OFF) 대조 실증
    print("\n[시나리오 2] 외래키 비활성화 상태 대조 (위험 상황 — PRAGMA foreign_keys = OFF)")
    conn_off = sqlite3.connect(":memory:")
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn_off.executescript(f.read())
    with open(SEED_PATH, encoding="utf-8") as f:
        conn_off.executescript(f.read())
    # 스키마 로드 후 명시적으로 외래키를 꺼서 취약한 환경 재현
    conn_off.execute("PRAGMA foreign_keys = OFF;")

    print("  - FK OFF 상태에서 동일한 유령 회원(member_id=999) 레코드 삽입...")
    conn_off.execute(invalid_sql)
    off_count = conn_off.execute("SELECT COUNT(*) FROM rentals;").fetchone()[0]
    orphan_row = conn_off.execute("SELECT rental_id, member_id, book_id, rental_date FROM rentals WHERE member_id = 999;").fetchone()
    print(f"  - FK OFF 시 행 수: {off_count}행 (유령 데이터 삽입 허용됨!)")
    print(f"  - 삽입된 고아 레코드: {orphan_row} (부모 없는 데이터 오염 발생)")

    print("\n" + "=" * 70)
    print(" 💡 [결론 및 3대 해결책]")
    print("  1. DDL 수준: schema.sql 최상단에 `PRAGMA foreign_keys = ON;` 명시 필수")
    print("  2. 애플리케이션 수준: DB 커넥션 생성 즉시 FK 활성화 선언 및 try-except 예외 처리")
    print("  3. 사전 검증: INSERT 전 `SELECT 1 FROM members WHERE member_id = ?` 유효성 검증")
    print("=" * 70)

if __name__ == "__main__":
    main()
