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

def show_select(conn, sql):
    print("\n[SQL 원문]\n" + sql.strip() + "\n")
    cur = conn.execute(sql)
    rows = cur.fetchall()
    print("[실행 결과]\n")
    print(" | ".join(col[0] for col in cur.description))
    for row in rows:
        print(" | ".join("NULL" if value is None else str(value) for value in row))
    print(f"반환 {len(rows)}행")
    return rows

def set_fk(conn, enabled):
    sql = "PRAGMA foreign_keys = " + ("ON" if enabled else "OFF") + ";"
    print("\n[SQL 원문]\n" + sql + "\n")
    conn.execute(sql)
    print("[실행 결과] 외래키 검사 설정 변경 요청")
    state = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
    if state != int(enabled):
        raise RuntimeError("외래키 검사 설정이 적용되지 않았습니다")

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
    set_fk(conn_on, True)
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn_on.executescript(f.read())
    with open(SEED_PATH, encoding="utf-8") as f:
        conn_on.executescript(f.read())

    before_count = conn_on.execute("SELECT COUNT(*) AS rental_count FROM rentals;").fetchone()[0]
    show_select(conn_on, "SELECT member_id FROM members WHERE member_id = 999;")

    print("\n[SQL 원문]\n" + invalid_sql + "\n")
    try:
        conn_on.execute(invalid_sql)
        conn_on.rollback()
        raise RuntimeError("FK ON 상태에서 잘못된 INSERT가 허용되었습니다")
    except sqlite3.IntegrityError as e:
        print(f"[SQLite 엔진 오류 / 실행 결과] {type(e).__name__}: {e}")

    after_count = conn_on.execute("SELECT COUNT(*) AS rental_count FROM rentals;").fetchone()[0]
    rejected = show_select(conn_on, "SELECT * FROM rentals WHERE member_id = 999;")
    if after_count != before_count or rejected:
        raise RuntimeError("FK ON 데이터 무결성 검증 실패")
    print(f"  - 시도 후 rentals 행 수: {after_count}행 (데이터 무결성 100% 보존)")

    # 2. 외래키 비활성화 (PRAGMA foreign_keys = OFF) 대조 실증
    print("\n[시나리오 2] 외래키 비활성화 상태 대조 (위험 상황 — PRAGMA foreign_keys = OFF)")
    conn_off = sqlite3.connect(":memory:")
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn_off.executescript(f.read())
    with open(SEED_PATH, encoding="utf-8") as f:
        conn_off.executescript(f.read())
    # 스키마 로드 후 명시적으로 외래키를 꺼서 취약한 환경 재현
    set_fk(conn_off, False)

    before_off = conn_off.execute("SELECT COUNT(*) AS rental_count FROM rentals;").fetchone()[0]
    print("\n[SQL 원문]\n" + invalid_sql + "\n")
    conn_off.execute(invalid_sql)
    print("[실행 결과] INSERT 성공 (FK OFF)")
    off_count = conn_off.execute("SELECT COUNT(*) AS rental_count FROM rentals;").fetchone()[0]
    orphan_rows = show_select(conn_off, "SELECT rental_id, member_id, book_id, rental_date FROM rentals WHERE member_id = 999;")
    violations = conn_off.execute("PRAGMA foreign_key_check;").fetchall()
    if off_count != before_off + 1 or len(orphan_rows) != 1 or not violations:
        raise RuntimeError("FK OFF 시나리오 검증 실패")
    orphan_row = orphan_rows[0]
    print(f"  - 삽입된 고아 레코드: {orphan_row} (부모 없는 데이터 오염 발생)")

    print("\n" + "=" * 70)
    print(" 💡 [결론 및 3대 해결책]")
    print("  1. DDL 수준: schema.sql 최상단에 `PRAGMA foreign_keys = ON;` 명시 필수")
    print("  2. 애플리케이션 수준: DB 커넥션 생성 즉시 FK 활성화 선언 및 try-except 예외 처리")
    print("  3. 사전 검증: INSERT 전 `SELECT 1 FROM members WHERE member_id = ?` 유효성 검증")
    print("=" * 70)

if __name__ == "__main__":
    main()
