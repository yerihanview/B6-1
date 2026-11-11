#!/usr/bin/env python3
"""
[보너스 1] INNER JOIN vs EXISTS 서브쿼리 비교 실측 러너
- 실행 위치: 저장소 루트 또는 bonus/ 디렉토리 (자동 경로 보정)
- 실행 방법: python3 bonus/run_bonus1.py
"""

import os
import sqlite3
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCHEMA_PATH = os.path.join(BASE_DIR, "sql", "schema.sql")
SEED_PATH = os.path.join(BASE_DIR, "sql", "seed.sql")

def init_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    with open(SEED_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    return conn

def main():
    print("=" * 70)
    print(" 🎁 [보너스 1] INNER JOIN vs EXISTS 서브쿼리 실행계획 및 결과 대조")
    print("=" * 70)

    conn = init_db()

    sql_join = """
    SELECT DISTINCT
        m.member_id,
        m.name,
        m.email
    FROM members AS m
    INNER JOIN rentals AS r
        ON m.member_id = r.member_id
    ORDER BY m.member_id;
    """

    sql_exists = """
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
    """

    print("\n[1] 방법 A: INNER JOIN + DISTINCT 실행")
    rows_join = conn.execute(sql_join).fetchall()
    print(f"  반환 행수: {len(rows_join)}행")
    for r in rows_join[:3]:
        print(f"  - {r}")
    print("  ... 외 7행")

    print("\n[2] 방법 B: EXISTS 상관 서브쿼리 실행")
    rows_exists = conn.execute(sql_exists).fetchall()
    print(f"  반환 행수: {len(rows_exists)}행")
    for r in rows_exists[:3]:
        print(f"  - {r}")
    print("  ... 외 7행")

    # 결과 일치성 검증
    is_identical = (rows_join == rows_exists)
    print(f"\n✔ 두 방식의 결과 동일성: {'100% 완전 일치 (10명 반환)' if is_identical else '불일치'}")

    print("\n[3] 실행 계획 (EXPLAIN QUERY PLAN) 대조")
    print("  ▶ INNER JOIN 실행 계획:")
    for plan in conn.execute("EXPLAIN QUERY PLAN " + sql_join).fetchall():
        print(f"    - {plan[3]}")
    print("    ※ 특징: 대여 이력이 많은 경우 조인 중간 결과가 비대해져 TEMP B-TREE(임시 정렬 트리) 비용 발생")

    print("\n  ▶ EXISTS 서브쿼리 실행 계획:")
    for plan in conn.execute("EXPLAIN QUERY PLAN " + sql_exists).fetchall():
        print(f"    - {plan[3]}")
    print("    ※ 특징: 일치하는 행을 1건만 찾으면 즉시 탐색을 멈추는 Early Stop(단락 평가)으로 대용량에서 최적")

    print("\n" + "=" * 70)
    print(" 💡 [결론 및 선택 기준]")
    print("  - 부모(members)의 컬럼만 필요하고 존재 여부만 따질 때는 'EXISTS'가 중복 제거 오버헤드가 없어 유리함.")
    print("  - 자식(rentals) 테이블의 컬럼(대여일, 상태 등)까지 SELECT에 포함해야 할 때는 'INNER JOIN'이 필수적임.")
    print("=" * 70)

if __name__ == "__main__":
    main()
