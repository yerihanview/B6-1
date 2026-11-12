#!/usr/bin/env bash
# ==============================================================================
# B6-1 디지털 서랍장 — 평가자용 대화형 시연 러너 (ADR-014 / ADR-016)
#
#   Step 1  스키마 적재 — 4개 테이블·FK 3개·인덱스 생성
#   Step 2  시드 적재 — 50행 한국어 데이터 (부모→자식 위상정렬)
#   Step 3  15대 쿼리 전수 실행 — 5대 흐름별 물 흐르듯 순차 시연
#   Step 4  외래키 무결성 파괴 실증 — 존재하지 않는 member_id=999 방어
#   Step 5  보너스 3종 실측 실행 시연 — run_bonus1, run_bonus2, run_bonus3
#   자체검증 100점 채점 — test/verify_sql.py (자체 무결성 보증)
#
# 사용법:
#   bash demo.sh                     # 엔터(Enter)를 누르며 한 단계씩 진행
#   bash demo.sh --non-interactive   # 무인 스모크 테스트 (CI/자동 검증용)
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
echo -e "${BOLD}${CYAN}    SQLite · 4개 테이블 · 1:N 관계 3개 · 15대 쿼리 전수 시연${NC}"
echo -e "${BOLD}${CYAN}======================================================================${NC}"
echo -e "  임시 DB: ${DB}"
echo -e "  Python : $($PYTHON --version 2>&1)"

pause_step

# ──────────────────────────────────────────────────────────────────────────────
step_banner "Step 1 / 5 — 스키마 생성 및 상세 검증"
"$PYTHON" - "$DB" <<'PY'
import sqlite3,sys
from pathlib import Path
c=sqlite3.connect(sys.argv[1])
sql=Path("sql/schema.sql").read_text(encoding="utf-8")
print("\n[실행 SQL: schema.sql]\n"+sql,flush=True)
c.executescript(sql)
def show(q):
 print("\nSQL> "+q)
 cur=c.execute(q);print(" | ".join(x[0] for x in cur.description))
 for row in cur.fetchall():print(" | ".join("NULL" if v is None else str(v) for v in row))
show("PRAGMA foreign_keys;")
show("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
show("SELECT name, sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_autoindex_%';")
for t in ("categories","members","books","rentals"):
 show(f"PRAGMA table_info({t});")
 show(f"PRAGMA foreign_key_list({t});")
c.close()
PY
pause_step

step_banner "Step 2 / 5 — 시드 전체 데이터 확인"
"$PYTHON" - "$DB" <<'PY'
import sqlite3,sys
from pathlib import Path
c=sqlite3.connect(sys.argv[1]);c.execute("PRAGMA foreign_keys=ON")
sql=Path("sql/seed.sql").read_text(encoding="utf-8")
print("\n[실행 SQL: seed.sql]\n"+sql,flush=True)
c.executescript(sql)
for t in ("categories","members","books","rentals"):
 q=f"SELECT * FROM {t} ORDER BY 1;"
 cur=c.execute(q);rows=cur.fetchall()
 print("\nSQL> "+q);print(" | ".join(x[0] for x in cur.description))
 for row in rows:print(" | ".join("NULL" if v is None else str(v) for v in row))
 print(f"[{t}: {len(rows)}행 전체 출력]")
 if len(rows)<10:raise RuntimeError(f"{t} 데이터 부족")
print("\nSQL> PRAGMA foreign_key_check;")
issues=c.execute("PRAGMA foreign_key_check").fetchall()
print(issues if issues else "(0행: 위반 없음)")
if issues:raise RuntimeError("FK 제약 위반")
c.close()
PY
pause_step

step_banner "Step 3 / 5 — 15대 SQL 원문과 전체 실행 결과"
"$PYTHON" - "$DB" "$INTERACTIVE" <<'PY'
import sqlite3,sys
sys.path.insert(0,"test")
from verify_sql import parse_queries
c=sqlite3.connect(sys.argv[1]);c.execute("PRAGMA foreign_keys=ON")
interactive=sys.argv[2]=="1"
blocks={label:(purpose,stmt) for label,purpose,stmt in parse_queries(open("sql/queries.sql",encoding="utf-8").read())}
waves=[
 ("Wave 1. 기본 조회",["Q01","Q02","Q03","Q04"]),
 ("Wave 2. JOIN",["Q05","Q06","Q07","Q08"]),
 ("Wave 3. 집계",["Q09","Q10","Q11"]),
 ("Wave 4. 서브쿼리",["Q12","Q13"]),
 ("Wave 5. UPDATE / DELETE",["Q14","Q15"])
]
def show(q):
 print("\nSQL> "+q,flush=True)
 cur=c.execute(q);rows=cur.fetchall()
 print(" | ".join(x[0] for x in cur.description))
 for row in rows:print(" | ".join("NULL" if v is None else str(v) for v in row))
 print(f"반환 {len(rows)}행")
 return rows
def pause(label):
 if interactive:
  try:
   with open("/dev/tty") as tty:
    print(f"\n▶ Enter를 누르면 {label} 실행",flush=True);tty.readline()
  except OSError:print("(터미널 입력 불가: 자동 진행)")
for title,labels in waves:
 print(f"\n{'='*65}\n{title}\n{'='*65}",flush=True)
 for label in labels:
  pause(label)
  purpose,stmt=blocks[label]
  print(f"\n[{label}] {purpose}\n[SQL 원문]\n{stmt}",flush=True)
  if label=="Q14":
   before=show("SELECT rental_id,member_id,book_id,due_date,return_date,status FROM rentals WHERE return_date IS NULL AND due_date < '2026-11-10' AND status='RENTED' ORDER BY rental_id;")
   n=c.execute(stmt).rowcount;print(f"갱신 행 수: {n}")
   ids=[r[0] for r in before]
   after=show("SELECT rental_id,member_id,book_id,due_date,return_date,status FROM rentals WHERE rental_id IN ("+",".join(map(str,ids))+") ORDER BY rental_id;") if ids else []
   if n!=len(before) or len(after)!=len(before) or any(r[-1]!="OVERDUE" for r in after):raise RuntimeError("Q14 변경 검증 실패")
   print("Q14 변경 전/후 검증 PASS")
  elif label=="Q15":
   before=show("SELECT * FROM rentals WHERE rental_id=(SELECT rental_id FROM rentals WHERE member_id=10 ORDER BY rental_date DESC LIMIT 1);")
   n=c.execute(stmt).rowcount;print(f"삭제 행 수: {n}")
   if n!=len(before):raise RuntimeError("Q15 삭제 행 수 불일치")
   for row in before:
    if show(f"SELECT * FROM rentals WHERE rental_id={int(row[0])};"):raise RuntimeError("Q15 삭제 검증 실패")
   show("SELECT COUNT(*) AS 남은_대여_건수 FROM rentals;")
   print("Q15 변경 전/후 검증 PASS")
  else:
   cur=c.execute(stmt);rows=cur.fetchall()
   print("[결과] "+" | ".join(x[0] for x in cur.description))
   for row in rows:print(" | ".join("NULL" if v is None else str(v) for v in row))
   print(f"반환 {len(rows)}행")
c.commit()
print("\nSQL> PRAGMA foreign_key_check;")
issues=c.execute("PRAGMA foreign_key_check").fetchall()
print(issues if issues else "(0행: 위반 없음)")
if issues:raise RuntimeError("외래키 무결성 오류")
c.close()
print("Q14·Q15 COMMIT 완료")
PY
echo "✔ SQL 15개 및 전체 결과 출력, Q14/Q15 전후 검증 완료"
pause_step

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
step_banner "Step 5 / 5 — 보너스 과제 3종 실측 실행 시연 (bonus/run_bonus*.py)"

echo -e "\n${YELLOW}[보너스 1] python3 bonus/run_bonus1.py (JOIN vs EXISTS 실행계획 대조)${NC}"
"$PYTHON" bonus/run_bonus1.py

pause_step

echo -e "\n${YELLOW}[보너스 2] python3 bonus/run_bonus2.py (외래키 무결성 파괴 실증 및 FK OFF 대조)${NC}"
"$PYTHON" bonus/run_bonus2.py

pause_step

echo -e "\n${YELLOW}[보너스 3] python3 bonus/run_bonus3.py (경영진 3대 KPI 리포트 지표 실측)${NC}"
"$PYTHON" bonus/run_bonus3.py

# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${CYAN}======================================================================${NC}"
echo -e "${BOLD}${CYAN} ✅ 5단계 시연 완료 — 15대 쿼리 및 보너스 3종 실행이 완벽히 시연되었습니다.${NC}"
echo -e "${BOLD}${CYAN}    임시 DB(${DEMO_DIR})는 종료와 함께 자동 삭제됩니다.${NC}"
echo -e "${BOLD}${CYAN}======================================================================${NC}"
