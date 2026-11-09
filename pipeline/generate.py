#!/usr/bin/env python3
"""B6-1 무인(Headless) 생성 파이프라인.

린 에이전틱 방법론(META_GUIDE v3.5) Step 3 Mode B 구현체.
ORDER_SHEET.md(내부 작업 계약서)를 코디세이 Public API에 주입하여
SQL 산출물과 문서를 생성하고, 실행 메타데이터(모델·토큰·지연)를
pipeline/runs/ 에 JSON으로 남긴다.

사용:
    export CODY_API_KEY=...      # 키는 저장소에 절대 기록하지 않는다 (ADR-016)
    python3 pipeline/generate.py --task all
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

API_BASE = os.environ.get("CODY_API_BASE", "https://copa.codyssey.kr/v1")
MODELS = ["claude-sonnet-4", "gpt-5.4-mini", "gpt-5.4"]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COMMON_RULES = """
[절대 규칙]
- SQLite 표준 SQL만 사용한다. 뷰/트리거/프로시저/백엔드 프레임워크 금지.
- 한국어 데이터와 한국어 설명을 사용한다(식별자·SQL 키워드는 영문).
- 출력은 아래 형식만 사용한다. 설명 문장, 인사말, 요약을 덧붙이지 않는다.
- 파일 구분자는 정확히 다음 한 줄이다: === FILE: <상대경로> ===
- 각 파일 본문은 코드 펜스 없이 그대로 출력한다(펜스 금지).
- SQL 문은 세미콜론으로 끝낸다.
"""

TASKS = {
    "schema_seed": (
        "schema.sql 과 seed.sql 을 생성하라.\n"
        "- schema.sql: PRAGMA foreign_keys = ON; 을 첫 줄에. categories, members, books, rentals "
        "순서로 CREATE TABLE. PK 4개, FK 3개(books.category_id, rentals.member_id, rentals.book_id), "
        "NOT NULL 각 테이블 2개 이상, UNIQUE(categories.category_name, members.email), "
        "CHECK(books.price >= 0), CHECK(rentals.status IN ('RENTED','RETURNED','OVERDUE')). "
        "rentals(rental_date) 인덱스 idx_rentals_date 를 만들고 바로 위에 한국어 1줄 사유 주석.\n"
        "- seed.sql: 부모 ➔ 자식 순서로 INSERT. 4개 테이블 각 10행 이상, 총 45행 이상. "
        "현실적인 한국어 도서관 데이터(회원 이름, 도서 제목·저자, 카테고리). "
        "rentals 는 RENTED/RETURNED/OVERDUE 세 상태를 모두 포함하고 연체 건과 복수 대여 회원을 포함한다. "
        "id 값은 1부터 명시적으로 지정한다.\n"
        "출력 파일: schema.sql, seed.sql"
    ),
    "queries": (
        "queries.sql 을 생성하라. 정확히 15개 쿼리, 각 쿼리 위에 '-- Q01: 목적' 형식의 한국어 주석 한 줄.\n"
        "Q01 특정 카테고리(카테고리명 '컴퓨터') 도서를 가격 내림차순 조회 (WHERE, ORDER BY DESC)\n"
        "Q02 연체('OVERDUE') 대여 건 조회 (WHERE)\n"
        "Q03 가장 최근 가입한 회원 5명 (ORDER BY join_date DESC, LIMIT 5)\n"
        "Q04 2020년 이후 출판 & 가격 20,000원 이상 (AND 다중 조건)\n"
        "Q05 도서별 카테고리명 포함 목록 (INNER JOIN books + categories)\n"
        "Q06 현재 대여 중(RENTED) 회원 이름·도서명·반납예정일 (다중 INNER JOIN rentals + members + books)\n"
        "Q07 대여 이력이 한 번도 없는 도서 (LEFT JOIN + WHERE r.rental_id IS NULL)\n"
        "Q08 전체 회원별 대여 횟수, 0회 회원도 0으로 표시 (LEFT JOIN + COUNT + GROUP BY)\n"
        "Q09 카테고리별 도서 권수와 평균 가격 (COUNT, AVG, GROUP BY, 반올림)\n"
        "Q10 회원별 총 연체 대여 건수, 연체가 1건 이상인 회원만 (GROUP BY + HAVING)\n"
        "Q11 월별 총 대여 건수 추이 (strftime('%Y-%m', rental_date), GROUP BY, ORDER BY)\n"
        "Q12 전체 도서 평균 가격보다 비싼 도서 (비상관 서브쿼리)\n"
        "Q13 회원별 가장 최근 대여일 (SELECT 절 상관 서브쿼리, 대여 이력 없는 회원은 NULL)\n"
        "Q14 반납기한이 지났으나 미반납(return_date IS NULL)인 건을 'OVERDUE'로 일괄 갱신 (UPDATE)\n"
        "Q15 탈퇴 대기 회원(member_id=10)의 테스트성 대여 이력 1건 삭제 (DELETE, 서브쿼리로 대상 1건 한정)\n"
        "Q14/Q15 는 UPDATE/DELETE 문이며 그 자체로 실행 가능해야 한다.\n"
        "출력 파일: queries.sql"
    ),
    "erd": (
        "docs/ERD.md 를 생성하라.\n"
        "- 첫 부분에 ```mermaid erDiagram 블록. 4개 테이블의 모든 컬럼과 타입, PK/FK 표기, "
        "관계선은 categories ||--o{ books, members ||--o{ rentals, books ||--o{ rentals (3개 1:N).\n"
        "- 이어서 테이블 명세서 4개를 마크다운 표로: 컬럼, 타입, 제약(PK/FK/NOT NULL/UNIQUE/CHECK/DEFAULT), 설명.\n"
        "- 관계 설명과 설계 의도(정규화, 위상정렬, 인덱스) 절을 포함.\n"
        "출력 파일: docs/ERD.md"
    ),
    "bonus_join": (
        "docs/bonus/JOIN_VS_SUBQUERY.md 를 생성하라.\n"
        "'대여 건수가 존재하는 회원 목록'을 INNER JOIN(DISTINCT)으로 작성한 SQL과 EXISTS 서브쿼리로 작성한 SQL을 "
        "1:1로 대조하라. 두 쿼리 전문, 결과 동일성, 실행계획(EXPLAIN QUERY PLAN) 차이, "
        "가독성·유지보수성·성능·NULL 안전성 관점 비교표, 선택 기준을 포함한다. 실제 SQLite 동작에 근거해 설명한다.\n"
        "출력 파일: docs/bonus/JOIN_VS_SUBQUERY.md"
    ),
    "bonus_integrity": (
        "docs/bonus/INTEGRITY_VIOLATION.md 를 생성하라.\n"
        "존재하지 않는 member_id=999 로 rentals 에 INSERT 를 시도했을 때 SQLite가 "
        "'FOREIGN KEY constraint failed' 를 내는 과정을 재현 SQL, 실제 실행 결과(에러 트레이스 형태), "
        "원인 분석(PRAGMA foreign_keys 기본 OFF 함정 포함), 3가지 해결책(사전 존재 검증, FK 활성화, 트랜잭션 롤백), "
        "재발 방지 체크리스트로 기술한다. 실제로 실행한 것처럼 관측 가능한 출력 형태로 작성하되 사실과 다르게 꾸미지 않는다.\n"
        "출력 파일: docs/bonus/INTEGRITY_VIOLATION.md"
    ),
    "bonus_kpi": (
        "docs/bonus/KPI_REPORT.md 를 생성하라. 경영진용 3대 KPI 리포트.\n"
        "1) 월별 대여 회전율(대여 건수/도서 권수) 2) 최다 대여 도서 TOP 3 3) 회원 연체율(연체 건/전체 대여 건).\n"
        "각 KPI마다 계산 SQL, 해석, 개선 액션을 포함하고, 마지막에 3줄 경영 요약을 둔다. "
        "수치는 seed 데이터 규모(도서 12권 내외, 대여 15건 내외)에 맞는 현실적 서술로 작성하되 특정 값을 단정하지 말고 산출 SQL을 제시한다.\n"
        "출력 파일: docs/bonus/KPI_REPORT.md"
    ),
}


def call_api(prompt: str, model: str, max_tokens: int = 8000) -> tuple[str, dict]:
    key = os.environ.get("CODY_API_KEY", "")
    if not key:
        raise SystemExit("CODY_API_KEY 환경변수가 필요합니다. 키는 저장소에 기록하지 마세요.")
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    started = time.time()
    with urllib.request.urlopen(req, timeout=300) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    elapsed = round(time.time() - started, 2)
    text = payload["choices"][0]["message"]["content"]
    meta = {
        "model": payload.get("model", model),
        "latency_s": elapsed,
        "usage": payload.get("usage", {}),
        "finish_reason": payload["choices"][0].get("finish_reason"),
    }
    return text, meta


def call_with_fallback(prompt: str, max_tokens: int = 8000) -> tuple[str, dict]:
    last_err = None
    for model in MODELS:
        for attempt in range(1, 4):
            try:
                text, meta = call_api(prompt, model, max_tokens)
                meta["attempt"] = attempt
                return text, meta
            except urllib.error.HTTPError as e:  # type: ignore[attr-defined]
                detail = e.read().decode("utf-8", "replace")[:300]
                last_err = f"{model} HTTP {e.code}: {detail}"
                if e.code in (401, 403):
                    raise SystemExit(f"인증 실패: {last_err}")
                time.sleep(min(2 ** attempt, 8))
            except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as e:
                last_err = f"{model} {type(e).__name__}: {e}"
                time.sleep(min(2 ** attempt, 8))
    raise SystemExit(f"모든 모델 호출 실패: {last_err}")


def parse_files(text: str) -> dict[str, str]:
    """=== FILE: path === 구분자로 산출물을 분리하고 코드 펜스를 제거한다."""
    parts = re.split(r"^===\s*FILE:\s*(.+?)\s*===\s*$", text, flags=re.MULTILINE)
    files: dict[str, str] = {}
    for i in range(1, len(parts) - 1, 2):
        path = parts[i].strip().strip("`")
        body = parts[i + 1].strip("\n")
        body = re.sub(r"^```[a-zA-Z]*\n", "", body)
        body = re.sub(r"\n```\s*$", "", body)
        files[path] = body.strip() + "\n"
    return files


def write_files(files: dict[str, str]) -> list[str]:
    written = []
    for path, content in files.items():
        if ".." in path or path.startswith("/"):
            raise SystemExit(f"비정상 경로 거부: {path}")
        full = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        written.append(path)
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description="B6-1 무인 생성 파이프라인")
    ap.add_argument("--task", default="all", choices=["all", *TASKS.keys()])
    ap.add_argument("--max-tokens", type=int, default=8000)
    args = ap.parse_args()

    with open(os.path.join(ROOT, "ORDER_SHEET.md"), encoding="utf-8") as f:
        order_sheet = f.read()

    schema_path = os.path.join(ROOT, "schema.sql")
    schema_sql = open(schema_path, encoding="utf-8").read() if os.path.exists(schema_path) else ""
    seed_path = os.path.join(ROOT, "seed.sql")
    seed_sql = open(seed_path, encoding="utf-8").read() if os.path.exists(seed_path) else ""

    selected = list(TASKS) if args.task == "all" else [args.task]
    runs = []
    for name in selected:
        context = ""
        if name != "schema_seed":
            context = (
                "\n[실제 schema.sql — 컬럼명을 절대 바꾸지 말고 이 정의만 근거로 삼아라]\n"
                f"{schema_sql}\n"
                "\n[실제 seed.sql — 인용할 데이터는 이 내용에서만 가져와라]\n"
                f"{seed_sql}\n"
            )
        prompt = (
            "너는 최고 등급의 SQL/RDBMS 데이터 아키텍트다. 아래 내부 작업 지시서(ORDER_SHEET)를 "
            "100% 준수하여 지정된 산출물만 생성하라.\n\n"
            f"{COMMON_RULES}\n\n[ORDER_SHEET]\n{order_sheet}\n{context}\n[이번 작업]\n{TASKS[name]}"
        )
        text, meta = call_with_fallback(prompt, args.max_tokens)
        files = parse_files(text)
        if not files:
            raise SystemExit(f"[{name}] 파일 구획자를 찾지 못했습니다. 원문 앞부분: {text[:300]}")
        written = write_files(files)
        meta.update({"task": name, "files": written})
        runs.append(meta)
        print(f"✔ {name}: {', '.join(written)} ({meta['model']}, {meta['latency_s']}s, "
              f"{meta['usage'].get('completion_tokens', '?')} completion tokens)")

    os.makedirs(os.path.join(ROOT, "pipeline", "runs"), exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = os.path.join(ROOT, "pipeline", "runs", f"generate_{stamp}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"generated_at": stamp, "api_base": API_BASE, "runs": runs}, f,
                  ensure_ascii=False, indent=2)
    print(f"실행 메타데이터 기록: {os.path.relpath(out, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
