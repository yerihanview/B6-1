#!/usr/bin/env python3
"""B6-1 '디지털 서랍장' 100점 무인 기계 채점기 (Zero-Dependency).

Python 표준 라이브러리만으로 다음 6개 블록을 채점한다.
  1. 7대 필수 산출물 존재            (20점)
  2. 스키마 생성·제약조건·인덱스       (20점)
  3. 시드 10행 이상 · 상태 다양성      (20점)
  4. 외래키 무결성 위반 차단           (10점)
  5. 15대 쿼리 전수 실행 · 결과 리포트 (20점)
  6. 보너스 문서 3종 무결성            (10점)

실행: python3 verify_sql.py
종료 코드: 100점이면 0, 아니면 1
"""
from __future__ import annotations

import os
import re
import sqlite3
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
REQUIRED_FILES = [
    "schema.sql",
    "seed.sql",
    "queries.sql",
    "docs/ERD.md",
    "docs/bonus/JOIN_VS_SUBQUERY.md",
    "docs/bonus/INTEGRITY_VIOLATION.md",
    "docs/bonus/KPI_REPORT.md",
]
BONUS_FILES = [
    "docs/bonus/JOIN_VS_SUBQUERY.md",
    "docs/bonus/INTEGRITY_VIOLATION.md",
    "docs/bonus/KPI_REPORT.md",
]
EXPECTED_TABLES = ("categories", "members", "books", "rentals")
MAX_ROWS_IN_REPORT = 3


def path(rel: str) -> str:
    return os.path.join(BASE, rel)


def read(rel: str) -> str:
    with open(path(rel), encoding="utf-8") as f:
        return f.read()


def split_statements(sql: str) -> list[str]:
    """문자열 리터럴·주석 안의 세미콜론을 존중해 문장 단위로 분리한다."""
    statements: list[str] = []
    buf = ""
    for line in sql.splitlines(keepends=True):
        buf += line
        if sqlite3.complete_statement(buf):
            statements.append(buf.strip())
            buf = ""
    tail = buf.strip()
    if tail and not all(ln.strip().startswith("--") or not ln.strip() for ln in tail.splitlines()):
        statements.append(tail)
    return statements


def parse_queries(sql: str) -> list[tuple[str, str]]:
    """'-- Q01: ...' 마커 기준으로 15개 쿼리 블록을 분리한다."""
    marks = list(re.finditer(r"^--\s*(Q\d{2})\s*:\s*(.*)$", sql, flags=re.MULTILINE))
    blocks = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(sql)
        body = sql[m.end():end].strip()
        stmts = split_statements(body)
        if stmts:
            blocks.append((m.group(1), m.group(2).strip(), stmts[0]))
    return blocks


def check_files(score: list[int]) -> None:
    missing = [f for f in REQUIRED_FILES if not os.path.exists(path(f))]
    if missing:
        print(f"❌ [FAIL] 필수 산출물 누락: {missing}")
        raise SystemExit(1)
    print("✔ [PASS] 7대 필수 산출물 파일 전수 존재 확인 (+20점)")
    score[0] += 20


def check_schema(conn: sqlite3.Connection, score: list[int]) -> None:
    schema_sql = read("schema.sql")
    if "foreign_keys" not in schema_sql.lower():
        print("❌ [FAIL] schema.sql 내 PRAGMA foreign_keys 선언 누락")
        raise SystemExit(1)
    try:
        conn.executescript(schema_sql)
    except sqlite3.Error as e:
        print(f"❌ [FAIL] schema.sql 실행 실패: {e}")
        raise SystemExit(1)

    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")]
    missing = [t for t in EXPECTED_TABLES if t not in tables]
    if missing:
        print(f"❌ [FAIL] 테이블 누락: {missing} (생성됨: {tables})")
        raise SystemExit(1)

    problems = []
    for t in EXPECTED_TABLES:
        cols = list(conn.execute(f"PRAGMA table_info({t});"))
        pk = [ c[1] for c in cols if c[5] ]
        if not pk:
            problems.append(f"{t}: PK 없음")
    fk_total = sum(len(list(conn.execute(f"PRAGMA foreign_key_list({t});"))) for t in EXPECTED_TABLES)
    if fk_total < 3:
        problems.append(f"외래키 부족: {fk_total}개 (최소 3개)")

    email_unique = any(
        idx[2] == 1 and any(c[2] == "email" for c in conn.execute(f"PRAGMA index_info('{idx[1]}');"))
        for idx in conn.execute("PRAGMA index_list(members);")
    )
    if not email_unique:
        problems.append("members.email UNIQUE 없음")

    indexes = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='rentals';")]
    date_index = [ix for ix in indexes if "rental_date" in [
        c[2] for c in conn.execute(f"PRAGMA index_info('{ix}');")]]
    if not date_index:
        problems.append("rentals(rental_date) 인덱스 없음")

    if problems:
        print(f"❌ [FAIL] 스키마 무결성 결함: {problems}")
        raise SystemExit(1)

    print(f"✔ [PASS] 스키마 생성 및 외래키 활성화 확인 ({len(tables)}개 테이블, FK {fk_total}개) (+20점)")
    print(f"   └ INFO 인덱스: {', '.join(indexes) or '없음'}")
    score[0] += 20


def check_seed(conn: sqlite3.Connection, score: list[int]) -> None:
    try:
        conn.executescript(read("seed.sql"))
    except sqlite3.Error as e:
        print(f"❌ [FAIL] seed.sql 실행 실패: {e}")
        raise SystemExit(1)

    counts = {}
    for t in EXPECTED_TABLES:
        counts[t] = conn.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
    short = {t: c for t, c in counts.items() if c < 10}
    total = sum(counts.values())
    if short:
        print(f"❌ [FAIL] 시드 데이터 부족: {short} (테이블당 최소 10행)")
        raise SystemExit(1)
    if total < 45:
        print(f"❌ [FAIL] 전체 시드 행 수 부족: {total}행 (최소 45행)")
        raise SystemExit(1)

    statuses = {r[0] for r in conn.execute("SELECT DISTINCT status FROM rentals;")}
    if not {"RENTED", "RETURNED", "OVERDUE"}.issubset(statuses):
        print(f"❌ [FAIL] 대여 상태 3종 누락: {sorted(statuses)}")
        raise SystemExit(1)
    multi = conn.execute(
        "SELECT COUNT(*) FROM (SELECT member_id FROM rentals GROUP BY member_id HAVING COUNT(*) >= 2);"
    ).fetchone()[0]
    if multi < 1:
        print("❌ [FAIL] 복수 대여 회원 없음")
        raise SystemExit(1)

    dist = dict(conn.execute("SELECT status, COUNT(*) FROM rentals GROUP BY status;"))
    print(f"✔ [PASS] 4개 테이블 각 10행 이상 시드 적재 확인 "
          f"({', '.join(f'{t} {c}행' for t, c in counts.items())} / 총 {total}행) (+20점)")
    print(f"   └ INFO 상태 분포: {dist}, 복수 대여 회원 {multi}명")
    score[0] += 20


def check_fk(conn: sqlite3.Connection, score: list[int]) -> None:
    if conn.execute("PRAGMA foreign_keys;").fetchone()[0] != 1:
        print("❌ [FAIL] 채점 세션에서 외래키 강제가 꺼져 있음")
        raise SystemExit(1)
    try:
        conn.execute(
            "INSERT INTO rentals (member_id, book_id, rental_date, due_date, status) "
            "VALUES (9999, 9999, '2026-11-10', '2026-11-24', 'RENTED');")
        print("❌ [FAIL] 외래키 무결성 위반 감지 실패 (미등록 ID 삽입 허용됨)")
        raise SystemExit(1)
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY" not in str(e).upper():
            print(f"❌ [FAIL] 예상과 다른 무결성 오류: {e}")
            raise SystemExit(1)
    print("✔ [PASS] 유령 외래키(FK) 삽입 시 IntegrityError 정상 차단 확인 (+10점)")
    score[0] += 10


def md_escape(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def check_queries(conn: sqlite3.Connection, score: list[int]) -> None:
    blocks = parse_queries(read("queries.sql"))
    labels = [b[0] for b in blocks]
    expected = [f"Q{i:02d}" for i in range(1, 16)]
    if labels != expected:
        print(f"❌ [FAIL] 15대 쿼리 번호 불일치: 감지 {len(labels)}개 {labels}")
        print(f"   └ 기대: Q01~Q15 (설명 주석 '-- Q01: 목적' 포함)")
        raise SystemExit(1)

    lines = [
        "# 15대 핵심 SQL 쿼리 실제 실행 결과 리포트",
        "",
        "> `python3 verify_sql.py`가 SQLite 인메모리 DB(schema.sql + seed.sql)에서 15개 쿼리를 순서대로 실행한 실제 출력이다.",
        "> Q14(UPDATE)·Q15(DELETE)는 실행 자체와 영향 행 수를 기록한다.",
        "",
    ]
    for label, purpose, stmt in blocks:
        cur = conn.cursor()
        try:
            cur.execute(stmt)
            rows = cur.fetchall()
        except sqlite3.Error as e:
            print(f"❌ [FAIL] {label} 쿼리 실행 실패: {e}\n   SQL: {stmt[:200]}")
            raise SystemExit(1)

        lines.append(f"## {label}. {purpose}")
        lines.append("")
        lines.append("```sql")
        lines.append(stmt.rstrip())
        lines.append("```")
        lines.append("")
        if cur.description is None:
            lines.append(f"**실행 결과**: {cur.rowcount}행 영향")
            lines.append("")
            continue
        columns = [d[0] for d in cur.description]
        lines.append(f"**반환 행 수**: {len(rows)}")
        lines.append("")
        if rows:
            lines.append("| " + " | ".join(md_escape(c) for c in columns) + " |")
            lines.append("|" + "|".join(["---"] * len(columns)) + "|")
            for row in rows[:MAX_ROWS_IN_REPORT]:
                lines.append("| " + " | ".join(md_escape(v) for v in row) + " |")
            if len(rows) > MAX_ROWS_IN_REPORT:
                rest = ["…"] + [""] * (len(columns) - 1)
                lines.append("| " + " | ".join(rest) + " |")
                lines.append("")
                lines.append(f"*(전체 {len(rows)}행 중 상위 {MAX_ROWS_IN_REPORT}행만 표시)*")
            lines.append("")

    os.makedirs(path("outputs"), exist_ok=True)
    with open(path("outputs/query_results.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines).rstrip() + "\n")

    print("✔ [PASS] 15대 핵심 쿼리 전수 실행 성공 및 결과 리포트 자동 추출 (+20점)")
    print("   └ INFO outputs/query_results.md 재생성 완료")
    score[0] += 20


def check_bonus(score: list[int]) -> None:
    sizes = {}
    for b in BONUS_FILES:
        size = os.path.getsize(path(b))
        sizes[b] = size
        if size < 200:
            print(f"❌ [FAIL] 보너스 문서 분량 미달: {b} ({size} byte)")
            raise SystemExit(1)
    print("✔ [PASS] 3대 보너스 문서 심층 작성 확인 (+10점)")
    print("   └ INFO " + ", ".join(f"{os.path.basename(k)} {v}B" for k, v in sizes.items()))
    score[0] += 10


def check_docs() -> None:
    """채점 외 정보성 점검(감점 없음) — 문서 산출물의 형태만 확인한다."""
    erd = read("docs/ERD.md")
    relations = len(re.findall(r"\|\|--o\{", erd))
    if "erDiagram" not in erd or relations < 3:
        print(f"⚠️ [WARN] docs/ERD.md Mermaid ERD 관계선 부족 (감지 {relations}개)")
    else:
        print(f"✔ [INFO] Mermaid ERD 및 1:N 관계선 {relations}개 확인")
    gov = [n for n in ("README.md", "SUBMISSION.md", "PROJECT_MANIFEST.json", "RTM.md")
           if os.path.exists(path(n))]
    print(f"✔ [INFO] 거버넌스 문서 {len(gov)}/4종 존재: {', '.join(gov) or '없음'}")


def run_verification() -> bool:
    print("=" * 65)
    print(" 🛠️  디지털 서랍장 (SQL) 기계적 검증 및 100점 채점기")
    print("=" * 65)

    score = [0]
    check_files(score)

    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        check_schema(conn, score)
        check_seed(conn, score)
        check_fk(conn, score)
        check_queries(conn, score)
    finally:
        conn.close()
    check_bonus(score)
    check_docs()

    print("=" * 65)
    if score[0] == 100:
        print(" 🎉 [100점 만점 ALL PASS] 디지털 서랍장 미션 최종 점수: 100/100점")
    else:
        print(f" ❌ [FAIL] 최종 점수: {score[0]}/100점 — 미달 블록을 보정하세요")
    print("=" * 65)
    return score[0] == 100


if __name__ == "__main__":
    if not run_verification():
        sys.exit(1)
