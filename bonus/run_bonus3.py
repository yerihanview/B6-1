#!/usr/bin/env python3
"""
[보너스 3] 도서관 운영 경영진 3대 KPI 리포트 실측 러너
- 실행 위치: 저장소 루트 또는 bonus/ 디렉토리 (자동 경로 보정)
- 실행 방법: python3 bonus/run_bonus3.py
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
    print(" 🎁 [보너스 3] 도서관 운영 경영진 3대 KPI 실측 지표 리포트")
    print("=" * 70)

    conn = init_db()

    # KPI-1: 월별 대여 회전율
    print("\n📊 [KPI-1] 월별 도서 대여 회전율 (Turnover Rate)")
    print("  (산출식: 해당 월 대여 건수 ÷ 전체 보유 도서 권수)")
    sql_kpi1 = """
    SELECT
        strftime('%Y-%m', rental_date) AS 대여월,
        COUNT(*) AS 대여건수,
        (SELECT COUNT(*) FROM books) AS 총도서수,
        ROUND(CAST(COUNT(*) AS REAL) / (SELECT COUNT(*) FROM books), 4) AS 대여회전율
    FROM rentals
    GROUP BY strftime('%Y-%m', rental_date)
    ORDER BY 대여월;
    """
    rows_kpi1 = conn.execute(sql_kpi1).fetchall()
    print("  대여월    | 대여건수 | 전체도서 | 대여회전율")
    print("  -----------------------------------------")
    for r in rows_kpi1:
        print(f"  {r[0]}   | {r[1]:^8} | {r[2]:^8} | {r[3]:^10}")
    print("  ※ 해석: 2월, 3월, 7월, 10월에 회전율이 0.1538로 가장 활발하게 대여됨.")

    # KPI-2: 최다 대여 도서 TOP 3
    print("\n📚 [KPI-2] 최다 대여 도서 TOP 3 (인기도 랭킹)")
    sql_kpi2 = """
    SELECT
        b.book_id,
        b.title,
        c.category_name,
        COUNT(r.rental_id) AS 대여횟수
    FROM books b
    JOIN categories c ON b.category_id = c.category_id
    JOIN rentals r ON b.book_id = r.book_id
    GROUP BY b.book_id, b.title, c.category_name
    ORDER BY 대여횟수 DESC, b.book_id ASC
    LIMIT 3;
    """
    rows_kpi2 = conn.execute(sql_kpi2).fetchall()
    print("  도서ID | 도서명           | 카테고리 | 대여횟수")
    print("  ---------------------------------------------")
    for r in rows_kpi2:
        print(f"  {r[0]:^6} | {r[1]:<16} | {r[2]:<8} | {r[3]:^8}")
    print("  ※ 해석: '채식주의자(소설)', '아몬드(소설)', '총 균 쇠(역사)'가 각 2회로 최다 대여 기록.")

    # KPI-3: 회원 연체율 분석
    print("\n⚠️ [KPI-3] 도서관 대여 연체율 분석 (회수 건전성 지표)")
    sql_kpi3_overall = """
    SELECT
        COUNT(*) AS 총대여,
        SUM(CASE WHEN status = 'OVERDUE' THEN 1 ELSE 0 END) AS 연체건수,
        ROUND(CAST(SUM(CASE WHEN status = 'OVERDUE' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 1) AS 전체연체율
    FROM rentals;
    """
    overall = conn.execute(sql_kpi3_overall).fetchone()
    print(f"  - 전체 대여 건수: {overall[0]}건 | 현재 연체 건수: {overall[1]}건")
    print(f"  - 도서관 전체 연체율: {overall[2]}% (경보 기준치 20% 초과 ➔ 집중 관리 필요)")

    print("\n  ▶ 연체 발생 회원 목록:")
    sql_kpi3_members = """
    SELECT
        m.name AS 회원명,
        m.phone AS 연락처,
        COUNT(r.rental_id) AS 총대여,
        SUM(CASE WHEN r.status = 'OVERDUE' THEN 1 ELSE 0 END) AS 연체건수
    FROM members m
    JOIN rentals r ON m.member_id = r.member_id
    GROUP BY m.member_id, m.name, m.phone
    HAVING SUM(CASE WHEN r.status = 'OVERDUE' THEN 1 ELSE 0 END) > 0
    ORDER BY 연체건수 DESC;
    """
    rows_kpi3 = conn.execute(sql_kpi3_members).fetchall()
    print("  회원명 | 연락처          | 총대여 | 연체건수")
    print("  -----------------------------------------")
    for r in rows_kpi3:
        print(f"  {r[0]:<6} | {r[1]:<14} | {r[2]:^6} | {r[3]:^8}")

    print("\n" + "=" * 70)
    print(" 💡 [운영 개선 제언]")
    print("  1. 인기 도서(소설/역사) 복본 확충으로 대여 대기 시간 단축")
    print("  2. 반납 마감 3일 전/당일 카카오톡 알림톡 자동 발송으로 연체율 10% 이하 감축")
    print("=" * 70)

if __name__ == "__main__":
    main()
