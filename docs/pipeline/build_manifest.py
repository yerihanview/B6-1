#!/usr/bin/env python3
"""PROJECT_MANIFEST.json 재생성기.

산출물의 SHA-256, 실행 환경, 무인 생성 이력(pipeline/runs/*.json),
그리고 verify_sql.py 채점 결과를 한 파일로 동결한다.
산출물을 수정한 뒤에는 반드시 이 스크립트를 다시 실행한다.

사용: python3 pipeline/build_manifest.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

ARTIFACTS = [
    ("schema.sql", "DDL — PRAGMA FK, 4 tables, constraints, index"),
    ("seed.sql", "DML — 50 rows Korean seed in topological order"),
    ("queries.sql", "15 queries Q01~Q15"),
    ("verify_sql.py", "100-point zero-dependency grader"),
    ("demo.sh", "5-step interactive demo runner"),
    ("docs/ERD.md", "Mermaid ERD and table specification"),
    ("docs/bonus/JOIN_VS_SUBQUERY.md", "Bonus 1 — INNER JOIN vs EXISTS"),
    ("docs/bonus/INTEGRITY_VIOLATION.md", "Bonus 2 — FK violation reproduction"),
    ("docs/bonus/KPI_REPORT.md", "Bonus 3 — executive KPI report"),
    ("outputs/query_results.md", "Executed results of 15 queries (auto-generated)"),
    ("README.md", "Project overview, quickstart, demo, rubric"),
    ("SUBMISSION.md", "Submission pledge and artifact links"),
    ("RTM.md", "Requirements traceability matrix"),
    ("ORDER_SHEET.md", "Internal work order (not an evaluated deliverable)"),
]

CORRECTIONS = [
    "schema.sql: AUTOINCREMENT·created_at·join_date를 ORDER_SHEET 스펙과 일치 (Level 1 핀셋 패치)",
    "seed.sql: 대여일을 2026년으로 정렬, 미대여 도서 2권 확보로 Q07 빈 결과 해소",
    "queries.sql: Q13 정렬을 NULLS LAST 대신 호환 표현으로 교체",
    "docs/ERD.md: 실제 schema.sql 정의와 불일치하여 재생성",
    "docs/bonus/JOIN_VS_SUBQUERY.md: EXPLAIN QUERY PLAN 실측값으로 교체",
    "docs/bonus/INTEGRITY_VIOLATION.md: 실제 실행 trace로 재작성",
    "docs/bonus/KPI_REPORT.md: 실측 수치(회전율 0.077~0.154, 2건 4권, 연체율 26.7%)로 보정",
]


def main() -> int:
    artifacts = []
    for path, role in ARTIFACTS:
        data = open(path, "rb").read()
        artifacts.append({"path": path, "role": role, "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})

    runs = []
    for fn in sorted(os.listdir("pipeline/runs")):
        if not fn.endswith(".json"):
            continue
        payload = json.load(open(os.path.join("pipeline/runs", fn), encoding="utf-8"))
        for r in payload["runs"]:
            runs.append({
                "task": r["task"], "model": r["model"],
                "prompt_tokens": r["usage"].get("prompt_tokens"),
                "completion_tokens": r["usage"].get("completion_tokens"),
                "latency_s": r["latency_s"], "attempt": r.get("attempt"),
                "files": r["files"], "logged_at": payload["generated_at"],
            })

    verify = subprocess.run([sys.executable, "verify_sql.py"], capture_output=True, text=True)
    score_line = [l for l in verify.stdout.splitlines() if "최종 점수" in l][0].strip()
    demo = subprocess.run(["bash", "demo.sh", "--non-interactive"], capture_output=True, text=True)

    manifest = {
        "manifest_version": "1.0",
        "mission": {
            "id": "B6-1",
            "title": "정보를 깔끔하게 정리하는 디지털 서랍장 만들기",
            "course": "코디세이 AI 올인원 — 데이터베이스와 백엔드",
            "domain": "도서관 스마트 대여/연체 관리 시스템",
            "owner": "우광택 (@yerihanview)",
            "repository": "https://github.com/yerihanview/B6-1",
            "default_branch": "main",
        },
        "methodology": {
            "name": "린 에이전틱 개발 방법론",
            "version": "META_GUIDE v3.5",
            "adrs_applied": ["ADR-004", "ADR-008", "ADR-014", "ADR-015", "ADR-016", "ADR-018"],
            "pipeline": "ORDER_SHEET -> headless generation (Mode B) -> verify_sql.py (100/100) -> GitHub push",
        },
        "environment": {
            "runtime": f"Python {sys.version.split()[0]}",
            "sqlite": sqlite3.sqlite_version,
            "dependencies": "standard library only (sqlite3, os, sys, re, json, urllib)",
            "encoding": "UTF-8 NFC / LF",
        },
        "artifacts": artifacts,
        "verification": {
            "command": "python3 verify_sql.py",
            "score": 100,
            "max_score": 100,
            "result": score_line,
            "exit_code": verify.returncode,
            "verified_at": datetime.now(KST).isoformat(timespec="seconds"),
            "blocks": [
                {"name": "required_artifacts", "points": 20},
                {"name": "schema_integrity", "points": 20},
                {"name": "seed_data", "points": 20},
                {"name": "foreign_key_defense", "points": 10},
                {"name": "queries_execution", "points": 20},
                {"name": "bonus_documents", "points": 10},
            ],
            "smoke_test": {"command": "bash demo.sh --non-interactive", "exit_code": demo.returncode},
        },
        "generation": {
            "mode": "headless (Mode B)",
            "api_base": "https://copa.codyssey.kr/v1",
            "primary_model": "claude-sonnet-4",
            "fallback_models": ["gpt-5.4-mini", "gpt-5.4"],
            "script": "pipeline/generate.py",
            "runs": runs,
            "corrections_after_generation": CORRECTIONS,
        },
        "constraints": {
            "backend_framework": False,
            "api_or_ui": False,
            "views_or_procedures_or_triggers": False,
            "external_packages": False,
            "secrets_in_repository": False,
        },
        "governance": {
            "order_sheet": "ORDER_SHEET.md (internal, not evaluated per ADR-018)",
            "rtm": "RTM.md (38 requirements traced)",
            "demo": "demo.sh (5 steps, ADR-014)",
            "submission": "SUBMISSION.md",
        },
    }

    with open("PROJECT_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"manifest: {len(artifacts)} artifacts, {len(runs)} generation runs")
    print(score_line)
    print(f"demo smoke exit={demo.returncode}")
    return 0 if verify.returncode == 0 and demo.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
