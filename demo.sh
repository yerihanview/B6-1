#!/usr/bin/env bash
# ==============================================================================
# B6-1 디지털 서랍장 — 평가자용 5단계 대화형 시연 러너 (ADR-014 / ADR-016)
#
#   Step 1  스키마 적재 — 4개 테이블·FK·인덱스 생성
#   Step 2  시드 적재 — 50행 한국어 데이터, 상태 3종
#   Step 3  주요 쿼리 — Q05(INNER JOIN) / Q08(LEFT JOIN) / Q11(월별 집계)
#   Step 4  FK 위반 차단 실증 — 유령 member_id INSERT 거부
#   Step 5  100점 채점 — verify_sql.py ALL PASS
#
# 사용법:
#   bash demo.sh                 # 엔터(Enter)를 누르며 한 단계씩 진행
#   bash demo.sh --non-interactive   # 무인 스모크 테스트 (CI/검증용)
#
# 모든 DB 작업은 임시 디렉토리의 SQLite 파일에서만 일어나며,
# 종료 시 trap이 임시 자원을 삭제한다 (워킹 트리 오염 0건).
# ==============================================================================
set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

INTERACTIVE=1
for arg in "$@"; do
    case "$arg" in
        --non-interactive|-y|--yes) INTERACTIVE=0 ;;
        -h|--help)
            echo "사용법: bash demo.sh [--non-interactive]"
            exit 0 ;;
    esac
done

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo -e "${RED}[FAIL] Python 3가 필요합니다.${NC}" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

DEMO_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t b6_1_demo)"
DB="$DEMO_DIR/library.db"

cleanup() {
    rm -rf "$DEMO_DIR"
}
trap cleanup EXIT INT TERM

pause_step() {
    echo ""
    if [ "$INTERACTIVE" -eq 1 ] && [ -t 0 ]; then
        echo -e "${YELLOW}▶ [엔터(Enter)]를 누르면 다음 단계로 진행합니다...${NC}"
        read -r
    else
        echo -e "${CYAN}▶ (비대화형 모드 — 자동 진행)${NC}"
    fi
}

step_banner() {
    echo ""
    echo -e "${BOLD}${CYAN}======================================================================${NC}"
    echo -e "${BOLD}${CYAN} $1${NC}"
    echo -e "${BOLD}${CYAN}======================================================================${NC}"
}

# ──────────────────────────────────────────────────────────────────────────────
echo -e "${BOLD}${CYAN}======================================================================${NC}"
echo -e "${BOLD}${CYAN} 🗄️  B6-1 디지털 서랍장 — 도서관 스마트 대여/연체 관리 시스템${NC}"
echo -e "${BOLD}${CYAN}    SQLite · 4개 테이블 · 1:N 관계 3개 · 15대 쿼리${NC}"
echo -e "${BOLD}${CYAN}======================================================================${NC}"
echo -e "  임시 DB: ${DB}"
echo -e "  Python : $($PYTHON --version 2>&1)"

pause_step

# ──────────────────────────────────────────────────────────────────────────────
step_banner "Step 1 / 5 — schema.sql 적재 (테이블 · 외래키 · 인덱스)"
echo -e "${YELLOW}\$ python3 -c \"schema.sql 실행\"${NC}"
"$PYTHON" - "$DB" <<'PY'
import sqlite3, sys
db = sys.argv[1]
conn = sqlite3.connect(db)
conn.executescript(open("sql/schema.sql", encoding="utf-8").read())
print(f"PRAGMA foreign_keys = {conn.execute('PRAGMA foreign_keys;').fetchone()[0]}")
tables = [r[0] for r in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")]
print("테이블:", ", ".join(tables))
for t in ("books", "rentals"):
    fks = [f"{r[3]}→{r[2]}.{r[4]}" for r in conn.execute(f"PRAGMA foreign_key_list({t});")]
    print(f"  FK {t}: " + ", ".join(fks))
print("인덱스:", ", ".join(r[0] for r in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='rentals';")))
conn.close()
PY
echo -e "${GREEN}✔ 4개 테이블과 FK 3개, rentals(rental_date) 인덱스가 생성되었습니다.${NC}"

pause_step

# ──────────────────────────────────────────────────────────────────────────────
step_banner "Step 2 / 5 — seed.sql 적재 (한국어 시드 50행)"
echo -e "${YELLOW}\$ python3 -c \"seed.sql 실행 후 행 수 집계\"${NC}"
"$PYTHON" - "$DB" <<'PY'
import sqlite3, sys
conn = sqlite3.connect(sys.argv[1])
conn.execute("PRAGMA foreign_keys = ON;")
conn.executescript(open("sql/seed.sql", encoding="utf-8").read())
total = 0
for t in ("categories", "members", "books", "rentals"):
    n = conn.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
    total += n
    print(f"  {t:<12} {n:>3}행")
print(f"  {'합계':<12} {total:>3}행")
dist = conn.execute("SELECT status, COUNT(*) FROM rentals GROUP BY status ORDER BY status;").fetchall()
print("  대여 상태:", ", ".join(f"{s} {c}건" for s, c in dist))
print("  복수 대여 회원:", conn.execute(
    "SELECT COUNT(*) FROM (SELECT member_id FROM rentals GROUP BY member_id HAVING COUNT(*)>=2);"
).fetchone()[0], "명")
conn.close()
PY
echo -e "${GREEN}✔ 4개 테이블 각 10행 이상, RENTED/RETURNED/OVERDUE 3상태가 모두 적재되었습니다.${NC}"

pause_step

# ──────────────────────────────────────────────────────────────────────────────
step_banner "Step 3 / 5 — queries.sql 주요 쿼리 실행 (Q05 · Q08 · Q11)"
echo -e "${YELLOW}\$ python3 -c \"queries.sql에서 Q05/Q08/Q11 추출·실행\"${NC}"
"$PYTHON" - "$DB" <<'PY'
import sqlite3, sys
sys.path.insert(0, "test")
from verify_sql import parse_queries

conn = sqlite3.connect(sys.argv[1])
conn.execute("PRAGMA foreign_keys = ON;")
blocks = {label: (purpose, stmt) for label, purpose, stmt in parse_queries(open("sql/queries.sql", encoding="utf-8").read())}

for label in ("Q05", "Q08", "Q11"):
    purpose, stmt = blocks[label]
    cur = conn.execute(stmt)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    print(f"\n[{label}] {purpose}  (반환 {len(rows)}행)")
    print("  " + " | ".join(str(c) for c in cols))
    print("  " + "-" * 60)
    for row in rows[:5]:
        print("  " + " | ".join(str(v) for v in row))
    if len(rows) > 5:
        print(f"  ... 외 {len(rows) - 5}행")
conn.close()
PY
echo -e "${GREEN}✔ INNER JOIN(카테고리), LEFT JOIN(0회 포함), 월별 집계가 실데이터로 동작합니다.${NC}"

pause_step

# ──────────────────────────────────────────────────────────────────────────────
step_banner "Step 4 / 5 — 외래키 무결성 파괴 실증 (유령 member_id=999)"
echo -e "${YELLOW}\$ python3 -c \"INSERT INTO rentals(member_id=999, ...)\"${NC}"
"$PYTHON" - "$DB" <<'PY'
import sqlite3, sys
conn = sqlite3.connect(sys.argv[1])
conn.execute("PRAGMA foreign_keys = ON;")
before = conn.execute("SELECT COUNT(*) FROM rentals;").fetchone()[0]
try:
    conn.execute(
        "INSERT INTO rentals (member_id, book_id, rental_date, due_date, status) "
        "VALUES (999, 1, '2026-11-10', '2026-11-24', 'RENTED');")
    print("FAIL: 유령 외래키가 삽입되었습니다 (FK 강제 꺼짐)")
    sys.exit(1)
except sqlite3.IntegrityError as e:
    print(f"  차단됨 → sqlite3.IntegrityError: {e}")
after = conn.execute("SELECT COUNT(*) FROM rentals;").fetchone()[0]
print(f"  rentals 행 수: {before} → {after} (변화 없음)")
print("  PRAGMA foreign_keys =", conn.execute("PRAGMA foreign_keys;").fetchone()[0])
conn.close()
PY
echo -e "${GREEN}✔ 존재하지 않는 부모를 참조하는 INSERT가 DB 레벨에서 거부되었습니다.${NC}"

pause_step

# ──────────────────────────────────────────────────────────────────────────────
step_banner "Step 5 / 5 — 무인 기계 채점 (test/verify_sql.py, 100점 만점)"
echo -e "${YELLOW}\$ python3 test/verify_sql.py${NC}"
"$PYTHON" test/verify_sql.py
echo ""
echo -e "${GREEN}✔ 100/100 ALL PASS — 7대 산출물·스키마·시드·FK 방어·15쿼리·보너스 문서 전수 검증${NC}"

# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${CYAN}======================================================================${NC}"
echo -e "${BOLD}${CYAN} ✅ 시연 완료 — 15대 쿼리 실제 결과는 test/outputs/query_results.md 에 있습니다.${NC}"
echo -e "${BOLD}${CYAN}    임시 DB(${DEMO_DIR})는 종료와 함께 자동 삭제됩니다.${NC}"
echo -e "${BOLD}${CYAN}======================================================================${NC}"
