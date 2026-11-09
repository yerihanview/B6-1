# 외래키 무결성 파괴 실증 — 존재하지 않는 `member_id = 999` INSERT

> **실측 환경**: Python 3.12.16 / SQLite 3.46.1 / 2026-11-10 (Asia/Seoul)
> **대상 스키마**: 이 저장소의 `schema.sql` + `seed.sql` (그대로 로드)
> **재현 스크립트**: 아래 `repro.py` 전체 (저장소 루트에서 실행)

---

## 1. 재현 절차

`rentals.member_id`는 `members.member_id`를 참조하는 외래키다. `members`에 존재하지 않는 `999`를 자식 테이블에 넣어 본다.

```python
# repro.py — 저장소 루트에서 python3 repro.py
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("PRAGMA foreign_keys = ON;")
conn.executescript(open("schema.sql", encoding="utf-8").read())
conn.executescript(open("seed.sql", encoding="utf-8").read())

try:
    conn.execute(
        "INSERT INTO rentals (member_id, book_id, rental_date, due_date, status) "
        "VALUES (999, 1, '2026-11-10', '2026-11-24', 'RENTED');"
    )
except sqlite3.IntegrityError as e:
    print(f"sqlite3.IntegrityError: {e}")

print("remaining rentals:", conn.execute("SELECT COUNT(*) FROM rentals").fetchone()[0])
```

---

## 2. 실제 실행 결과 (실측 그대로)

```text
sqlite3.IntegrityError: FOREIGN KEY constraint failed
remaining rentals: 15
```

- INSERT는 **거부**되었고, `rentals` 행 수는 시드 그대로 **15행**이다.
- 예외는 `sqlite3.IntegrityError`이며 메시지는 `FOREIGN KEY constraint failed` 한 줄이다.
- 즉, 스키마의 `FOREIGN KEY (member_id) REFERENCES members (member_id)` 선언이 실제로 집행되었다.

---

## 3. 원인 분석

1. `rentals.member_id = 999`는 부모 테이블 `members`에 존재하지 않는 값이다.
2. SQLite는 DML 시점에 참조 무결성을 검사하여 고아 레코드(Orphan Record) 생성을 차단한다.
3. 실패한 INSERT는 트랜잭션 단위로 롤백되어 **부분 반영이 남지 않는다** (위 결과의 `remaining rentals: 15`).

### 3-1. SQLite의 기본 함정 — `PRAGMA foreign_keys`는 연결 단위로 기본 OFF

같은 DB에서 외래키 검사를 끄고 동일한 INSERT를 실행하면 결과가 달라진다.

```python
conn.execute("PRAGMA foreign_keys = OFF;")   # 기본값과 동일
print(conn.execute("PRAGMA foreign_keys;").fetchone()[0])   # 0
conn.execute(
    "INSERT INTO rentals (member_id, book_id, rental_date, due_date, status) "
    "VALUES (999, 1, '2026-11-10', '2026-11-24', 'RENTED');"
)
# inserted ok; count: 16
# orphan: [(16, 999)]
```

실측 출력:

```text
fk pragma: 0
inserted ok; count: 16
orphan: [(16, 999)]
```

- `schema.sql`에 FK를 선언해도 `PRAGMA foreign_keys = ON;`이 실행되지 않은 연결에서는 검사가 **조용히 생략**된다.
- 그래서 이 저장소는 `schema.sql` 첫 줄에 PRAGMA를 두고, `verify_sql.py`도 연결 직후 PRAGMA를 켠 뒤 `PRAGMA foreign_keys`가 1인지 확인한 다음에야 FK 방어 테스트를 수행한다.
- 함정의 본질은 "에러가 나지 않는다"가 아니라 **"에러 없이 잘못된 데이터가 저장된다"**는 점이다. 오염은 조회·집계 시점에야 드러난다.

---

## 4. 해결책 3가지

### 해결책 1. 연결 즉시 FK 강제 (필수)

```python
conn.execute("PRAGMA foreign_keys = ON;")
assert conn.execute("PRAGMA foreign_keys;").fetchone()[0] == 1
```

- 애플리케이션·배치·테스트·시연 등 **모든 연결 경로**에서 동일하게 적용한다.
- SQLite는 연결마다 설정이 초기화되므로 커넥션 풀을 쓴다면 커넥션 생성 훅에서 강제한다.

### 해결책 2. INSERT 전 부모 존재 검증 (사용자 친화적 오류)

```sql
SELECT 1 FROM members WHERE member_id = 999;
```

```python
if conn.execute("SELECT 1 FROM members WHERE member_id = ?;", (member_id,)).fetchone() is None:
    raise ValueError(f"존재하지 않는 회원입니다: {member_id}")
```

- DB 제약은 최후의 방어선이고, 사용자에게는 "회원을 찾을 수 없습니다" 같은 원인 중심 메시지를 주는 편이 낫다.
- `rentals`는 부모가 둘(`members`, `books`)이므로 두 EXISTS를 한 번에 검사한다.

### 해결책 3. 다건 DML은 트랜잭션으로 원자화

```python
with conn:                      # 예외 시 자동 ROLLBACK
    conn.execute("INSERT INTO rentals (...) VALUES (...)")
    conn.execute("UPDATE books SET ... WHERE ...")
```

- 여러 건을 넣다가 중간에 FK 위반이 나면 앞선 성공분까지 함께 되돌려 **부분 반영**을 막는다.
- 시드 적재(`seed.sql`)도 "부모 ➔ 자식" 순서와 트랜잭션 롤백이 함께 있어야 안전하다.

---

## 5. 재발 방지 체크리스트

- [ ] 모든 SQLite 연결에서 `PRAGMA foreign_keys = ON;` 실행 후 실제 값이 1인지 확인한다.
- [ ] DDL은 위상정렬 순서(categories/members ➔ books ➔ rentals)로 생성한다.
- [ ] DML 시드는 부모 ➔ 자식 순서로 넣는다.
- [ ] 사용자 입력 ID는 INSERT 전에 존재 여부를 검증하고 원인 중심 오류를 반환한다.
- [ ] 다건 변경은 트랜잭션으로 묶어 실패 시 전체 롤백한다.
- [ ] 회귀 테스트에 `member_id = 999` 유령 FK INSERT 차단 케이스를 상시 포함한다 (이 저장소는 `verify_sql.py` 블록 4가 담당).

---

## 6. 이 저장소에서의 검증 연결

| 방어선 | 위치 | 확인 방법 |
|---|---|---|
| DDL 선언 | `schema.sql` FK 3개 | `PRAGMA foreign_key_list(rentals);` |
| 연결 강제 | `schema.sql:1`, `verify_sql.py` | `PRAGMA foreign_keys;` → 1 |
| 런타임 차단 | `verify_sql.py` 4번 블록 (10점) | `python3 verify_sql.py` |
| 시연 실증 | `demo.sh` Step 4 | `bash demo.sh` |
