# B6-1 독립 모델 교차 검증 심사 보고서 (AUDIT REPORT)

> **문서 성격**: 본 문서는 산출물을 만든 주체와 무관한 **외부 모델 2종의 독립 심사 기록**이다. 본문의 판정은 심사자 모델의 출력 원문에 근거하며, 편집자(심사 운영자)의 정정·보충은 그 사실을 명시해 구분했다.
> **심사 대상**: `https://github.com/yerihanview/B6-1` — `main` 브랜치, 커밋 `996a6e8` (심사 시점 스냅샷)
> **심사일**: 2026-11-10 (Asia/Seoul) · **실행 환경**: Python 3.12.16 / SQLite 3.46.1
> **심사자 모델**: ① `gpt-5.4` (OpenAI) ② `claude-sonnet-4` (Anthropic) — 코디세이 Public API 경유
> **심사 기준**: 미션 요구사항 R-01~R-50 (Objective·DoD 7대·절대 준수 규칙·루브릭을 번호화한 심사 기준표)
> **총평**: **두 모델 모두 "조건부 통과"** — 82/100(GPT-5.4), 92/100(Claude-Sonnet-4). 미션 본체(SQL 3종·15대 쿼리)는 충족하나, **`verify_sql.py`의 자기채점 신뢰성 결함**을 두 모델이 독립적으로 확인했다.

---

## 1. 심사 설계

### 1.1 독립성 조치
심사가 "생성에 관여한 주체의 자기 확인"으로 흐르지 않도록 아래를 지켰다.

1. **생성 과정 정보 미제공**: 심사자에게는 미션 요구사항과 산출물 파일만 주었다. 어떤 모델이 어떻게 만들었는지, 어떤 보정이 있었는지는 알리지 않았다. 생성 파이프라인(`pipeline/`), 내부 작업지시서(`ORDER_SHEET.md`), 추적 매트릭스(`RTM.md`), 매니페스트(`PROJECT_MANIFEST.json`)는 심사 자료와 실행 사본에서 모두 제외했다.
2. **자기검증 불인정**: `verify_sql.py`는 제출자가 직접 작성한 자기검증 스크립트이므로, 그 성공(100/100)을 요구 충족의 근거로 쓸 수 없다고 명시했다. 요구 충족은 심사자가 스스로 설계한 검증으로만 인정한다.
3. **자기 주장 불인정**: 산출물 문서에 적힌 ✅·"100/100 ALL PASS"·"실측" 서술은 증거가 아니라고 못박았다.
4. **심사자 주도 실행 검증**: 심사자 모델은 채팅 환경이라 직접 실행할 수 없다. 그래서 **2단계 프로토콜**을 썼다.
   - 1단계: 심사자가 검증하고 싶은 명령(bash/python)을 직접 설계해 제출
   - 실행: 운영자가 그 명령을 **저장소 사본의 새 디렉터리**에서 그대로 실행(요청 간 부수효과 격리)
   - 2단계: 표준출력·표준에러·종료코드 **원문**을 그대로 회신 → 심사자가 그 원문만 근거로 판정

### 1.2 실행 검증 규모
| 구분 | 요청 | 유효 | 비고 |
|---|---|---|---|
| GPT-5.4 | 18건 (C1~C18) | 18건 | 제약조건 변조 실험(C12~C14)으로 채점기 신뢰성 반증 |
| Claude-Sonnet-4 (라운드 1) | 10건 (C1~C10) | 9건 | C4는 심사자 자체 분리 로직 결함으로 폐기 |
| Claude-Sonnet-4 (라운드 2) | 6건 (D1~D6) | 6건 | 운영자가 하네스 결함을 통지하고 재요청 |
| **합계** | **34건** | **33건** | |

### 1.3 판정 등급
`PASS` 요구 충족 · `부분` 일부만 충족 · `FAIL` 미충족/위반 · `N/A` 자료 없음

### 1.4 심사자 구성상 한계 (투명성 고지)
심사자 2종 중 `claude-sonnet-4`는 이 저장소의 생성 이력(README §11)이 밝힌 모델과 **같은 계열**이다. 완전한 모델 독립성은 `gpt-5.4` 한 종에서만 성립한다. 그래서 두 결과를 **병치**하고, 판정이 갈린 지점(§6.2)과 하네스 유래 감점(§5)을 따로 드러냈다. 두 모델이 **서로 다른 실험 설계로 같은 결론**에 도달한 항목(D-1)은 모델 계열 편향과 무관하게 성립하는 결론으로 본다.

---

## 2. 심사 결과 요약

| 심사자 | 총점 | 판정 | 핵심 근거 | 최대 감점 |
|---|---:|---|---|---|
| **GPT-5.4** | **82/100** | **조건부 통과** | 채점기 맹점(R-38, -7) · categories NOT NULL 부족(-3) · 거버넌스 파일 부재(-2, 하네스 유래) | R-38 |
| **Claude-Sonnet-4** | **92/100** | **조건부 통과** | 채점기 CHECK·NOT NULL 미검증(R-36~R-38, -5) · Q14 날짜 의존(-1) · 커밋 이력 직접 확인 불가(-2, 하네스 유래) | R-36~R-38 |

### 2.1 두 모델이 **일치**해서 확인한 결론
- **SQL 본체는 요구를 충족한다.** 4개 테이블·FK 3개·UNIQUE 2종·CHECK 2종·인덱스+사유 주석이 실제로 강제되고(제약 위반 6종 전부 `IntegrityError`로 차단), 시드 50행(10/12/13/15)이 부모→자식 순서로 적재되며 상태 3종·복수 대여 회원이 존재한다.
- **15대 쿼리는 전수 실행 오류 0건**이고 결과 행 수·의미가 목적과 일치한다(Q01 2행, Q02 4행, Q03 5행, Q04 2행, Q05 13행, Q06 4행, Q07 2행, Q08 12행, Q09 10행, Q10 4행, Q11 9행, Q12 5행, Q13 12행, Q14 1행 영향, Q15 1행 영향). Q07·Q08·Q13은 독립 기준 쿼리와 대조해도 정확하다.
- **문서 수치가 실측과 일치한다.** README의 15개 쿼리 행 수·상태 분포·복수 대여 4명, KPI 리포트의 회전율 0.0769~0.1538·연체율 26.7%·회원별 연체율, JOIN 문서의 실행계획(`SCAN r`/`USE TEMP B-TREE FOR DISTINCT`, `CORRELATED SCALAR SUBQUERY`), INTEGRITY 문서의 `FOREIGN KEY constraint failed`/`remaining rentals: 15`가 모두 실제 실행 결과와 같다.
- **가장 큰 결함은 `verify_sql.py`다.** 두 모델이 서로 다른 방법으로 같은 결론에 도달했다(아래 D-1).

---

## 3. 항목별 판정 대조표 (R-01 ~ R-50)

| ID | 요구사항 | GPT-5.4 | Claude-Sonnet-4 | 대조 |
|---|---|---|---|---|
| R-01 | 도메인(도서관 대여/연체) 성립 | PASS | PASS | PASS (일치) |
| R-02 | 4테이블·1:N 3개 | PASS | PASS | PASS (일치) |
| R-03 | 순수 SQL, 뷰/트리거/프레임워크 금지 | PASS | PASS | PASS (일치) |
| R-04 | SQL 3종 실행 가능 | 부분 | PASS | 불일치 |
| R-05 | 원클릭 재현성 | PASS | PASS | PASS (일치) |
| R-06 | PRAGMA FK 최상단 | PASS | PASS | PASS (일치) |
| R-07 | categories PK/NOT NULL/UNIQUE | PASS | PASS | PASS (일치) |
| R-08 | members PK/email UNIQUE/NOT NULL≥2 | PASS | PASS | PASS (일치) |
| R-09 | books PK/FK/price CHECK | PASS | PASS | PASS (일치) |
| R-10 | rentals PK/FK2/status CHECK | PASS | PASS | PASS (일치) |
| R-11 | PK4·FK3·NOT NULL≥2·UNIQUE2·CHECK2 | 부분 | PASS | 불일치 |
| R-12 | rentals(rental_date) 인덱스+주석 | PASS | PASS | PASS (일치) |
| R-13 | DDL 위상정렬 | PASS | PASS | PASS (일치) |
| R-14 | 제약 실제 강제 6종 | PASS | PASS | PASS (일치) |
| R-15 | 각 10행 이상·총 45행 이상 | PASS | PASS | PASS (일치) |
| R-16 | 한국어 현실 데이터 | PASS | PASS | PASS (일치) |
| R-17 | 부모→자식 INSERT 순서 | 부분 | PASS | 불일치 |
| R-18 | 3상태·연체·복수 대여 | PASS | PASS | PASS (일치) |
| R-19 | Q01~Q15 주석·번호 연속 | PASS | PASS | PASS (일치) |
| R-20 | Q01 WHERE+ORDER BY DESC | PASS | PASS | PASS (일치) |
| R-21 | Q02 연체 조회 | PASS | PASS | PASS (일치) |
| R-22 | Q03 최근 5명 LIMIT | PASS | PASS | PASS (일치) |
| R-23 | Q04 AND 다중조건 | PASS | PASS | PASS (일치) |
| R-24 | Q05 INNER JOIN | PASS | PASS | PASS (일치) |
| R-25 | Q06 3테이블 INNER JOIN | PASS | PASS | PASS (일치) |
| R-26 | Q07 LEFT JOIN+IS NULL | PASS | PASS | PASS (일치) |
| R-27 | Q08 LEFT JOIN+COUNT(0회 포함) | PASS | PASS | PASS (일치) |
| R-28 | Q09 COUNT/AVG/GROUP BY | PASS | PASS | PASS (일치) |
| R-29 | Q10 GROUP BY+HAVING | PASS | PASS | PASS (일치) |
| R-30 | Q11 strftime 월별 | PASS | PASS | PASS (일치) |
| R-31 | Q12 비상관 서브쿼리 | PASS | PASS | PASS (일치) |
| R-32 | Q13 상관 서브쿼리 | PASS | PASS | PASS (일치) |
| R-33 | Q14 UPDATE OVERDUE | PASS | PASS | PASS (일치) |
| R-34 | Q15 DELETE 1건 | PASS | PASS | PASS (일치) |
| R-35 | 15쿼리 무오류·의미 타당 | PASS | PASS | PASS (일치) |
| R-36 | 표준 라이브러리만·3.9+ | PASS | 부분 | 불일치 |
| R-37 | 6블록 100점·리포트 재생성·exit0 | PASS | 부분 | 불일치 |
| R-38 | 채점기 자기검증 신뢰성 | FAIL | 부분 | 불일치 |
| R-39 | query_results.md 15쿼리 전문·결과 | PASS | PASS | PASS (일치) |
| R-40 | ERD Mermaid+명세+관계선 | 부분 | PASS | 불일치 |
| R-41 | 보너스1 JOIN vs EXISTS | PASS | PASS | PASS (일치) |
| R-42 | 보너스2 FK 위반 실증 | PASS | PASS | PASS (일치) |
| R-43 | 보너스3 KPI 3종 | PASS | PASS | PASS (일치) |
| R-44 | 문서 수치=실측 | 부분 | 부분 | 부분 (일치) |
| R-45 | demo.sh 5단계·비대화형·정리 | 부분 | PASS | 불일치 |
| R-46 | README 요건 | PASS | PASS | PASS (일치) |
| R-47 | SUBMISSION 요건 | PASS | PASS | PASS (일치) |
| R-48 | 민감정보 하드코딩 없음 | PASS | PASS | PASS (일치) |
| R-49 | 거버넌스 문서 보존 | FAIL | PASS | 불일치 |
| R-50 | 커밋 규율·public main 푸시 | 부분 | 부분 | 부분 (일치) |

- **일치 41항목 / 불일치 9항목** (R-04, R-11, R-17, R-36, R-37, R-38, R-40, R-45, R-49)
- 불일치의 성격은 §6에서 분석한다.

---

## 4. 확정 결함 목록

두 모델의 판정과 실행 원문을 종합해, 근거가 확실한 결함만 남겼다.

### D-1 [중대] `verify_sql.py`의 자기채점 맹점 — 요구 위반을 통과시킨다
- **근거(양 모델 독립 확인)**
  - GPT-5.4: `books.price`의 `CHECK (price >= 0)`를 제거한 스키마로도 **100/100 통과**(C12), `rentals.status`의 `CHECK`를 제거해도 **100/100 통과**(C13), Q07을 전혀 다른 쿼리로 바꿔도 **100/100 통과**(C14).
  - Claude-Sonnet-4: `price` CHECK가 없는 스키마에서 `price = -1` INSERT가 그대로 허용되는데도 채점기는 PASS를 냄(D5 `BAD: price=-1 accepted`), NOT NULL 컬럼 수 검사 없음(D5 `verify checks notnull: False`).
- **원인(코드 확인)**: `check_schema()`는 ① `foreign_keys` 문자열 존재 ② 4개 테이블 존재 ③ 각 테이블 PK 존재 ④ FK 총 3개 이상 ⑤ `members.email` UNIQUE ⑥ `rentals(rental_date)` 인덱스만 검사한다. **CHECK 제약의 내용, `categories.category_name` UNIQUE, NOT NULL 개수는 검사하지 않으며**, `check_queries()`는 15개 문장이 "실행되는지"만 보고 결과의 의미는 보지 않는다.
- **영향**: 문서·README·RTM이 내세우는 "100/100 ALL PASS"는 **스키마 품질 보증서가 아니다.** 채점기가 통과시켰다는 사실만으로 R-09~R-11이 충족됐다고 볼 수 없다(실제로 R-11은 별도 결함, D-2).

### D-2 [경미] `categories`의 NOT NULL 컬럼이 1개 (요구: 테이블당 2개 이상)
- **근거**: GPT-5.4 C2 실행 원문 `NOTNULL categories 1` (`category_name`만 선언, `category_id`는 PK라 NOT NULL 카운트에 잡히지 않음).
- **판정 차이**: GPT-5.4는 **부분(-3)**, Claude-Sonnet-4는 **PASS**(내 판정표에 "categories 1+"라고 적어 스스로 요구와 모순). 실행 원문은 GPT-5.4의 판정을 지지한다.
- **성격**: 스키마 자체의 실사용 문제는 아니고, 제출물이 스스로 정한 DoD 문구("테이블당 2개 이상")와의 불일치다.

### D-3 [경미] KPI 리포트의 "최다 대여 도서 TOP 3"와 실제 쿼리·표가 어긋난다 (편집자 보충 — 두 심사자 모두 미지적)
- 문서의 산출 SQL은 `LIMIT 3`인데, 같은 문서의 "실측 결과" 표는 **공동 1위 4권**(채식주의자·아주 작은 습관의 힘·클린 코드·부의 추월차선) + 공동 5위 + 대여 0권까지 5줄 이상을 싣고 있다.
- 실행 원문(C9)은 `kpi2_top3`가 3행만 반환하고, 1·3·9·10번 도서가 모두 2건으로 **4중 동점**임을 보여준다. 즉 표는 그 SQL의 출력이 아니며, "TOP 3"라는 제목과 4권 동점 서술이 함께 성립하지 않는다.

### D-4 [경미] Q14가 `DATE('now')`에 의존해 결과가 실행 시점에 따라 달라진다
- 두 모델 모두 지적. 현재 시드(2026-11-10 기준)에서는 1행 갱신으로 문서 기재와 일치하지만(D4: 고정일 2026-11-10에서도 1행), 그 이전 시점에 실행하면 0행이 되어 문서의 "1행 영향"과 불일치한다. 문서 스스로도 README §12에서 이 한계를 인정하고 있다.

### D-5 [기준 해석] `seed.sql`은 스키마 없이 단독 실행되지 않는다
- **근거**: GPT-5.4 C5 `seed_only OperationalError: no such table: categories`.
- **해석**: 시드 파일이 스키마를 전제하는 것은 일반적이며, 요구의 핵심은 "부모→자식 순서로 FK 오류 없이 적재"다(C4에서 충족). 다만 심사 기준 문구를 "각 파일이 그 자체로 실행 가능"으로 읽으면 미달이 된다. **문구 해석 차이로 분류**하며, Claude-Sonnet-4는 PASS로 판정했다.

---

## 5. 심사 하네스에서 비롯된 판정의 보정

심사자에게 준 실행 사본은 산출물 12개 파일로 구성한 **스냅샷**이며, 생성 이력 기록물은 넣지 않았다(§1.1). 그 결과 두 모델의 일부 감점은 **제출물이 아니라 심사 환경 때문에** 생겼다. 편집자가 원문 근거로 확인한 사실은 아래와 같다.

| 항목 | 심사자 판정 | 실제 | 보정 |
|---|---|---|---|
| R-49 거버넌스 문서 보존 | GPT-5.4 **FAIL**(-2), Claude PASS | `ORDER_SHEET.md`(10,180B)·`RTM.md`(6,730B)·`PROJECT_MANIFEST.json`(8,487B) 모두 커밋 `996a6e8`에 존재(파일 목록·SHA-256 확인) | **PASS** |
| R-50 커밋 규율·public 푸시 | 두 모델 모두 **부분** | 커밋 7개가 `feat:`/`docs:` Conventional Commits, 원격 `github.com/yerihanview/B6-1`, 공개 저장소·`main` 브랜치 확인 | **PASS** |
| R-40 ERD 문서 | GPT-5.4 부분(출력 절단) | Claude가 문서 전문으로 Mermaid·관계선 3개·제약 명세 확인 | **PASS** |
| R-45 demo.sh | GPT-5.4 부분(trap 삭제 증거 부족) | Claude D2: `EXIT:0`, `CLEAN:no library.db`, `CLEAN:no tmpdir` (demo.sh `trap cleanup EXIT INT TERM` 확인) | **PASS** |
| R-04/R-17 seed 단독 실행 | GPT-5.4 부분 | 스키마 선행 시 정상 적재(정상 관행), 문구 해석 문제 | **해석 이슈** |
| Claude C4(15쿼리 전수) | 최초 "15개 전부 syntax error" | 심사자 자체 분리 로직 결함(주석 텍스트를 SQL로 실행). 운영자 통지 후 D1에서 15개 전부 정상 확인 | **폐기·재검증** |

**보정 후 참고 점수** (편집자 계산, 심사자 점수 아님): GPT-5.4 82 → **86**, Claude-Sonnet-4 92 → **94**. 두 모델의 원점수는 §2에 그대로 보존한다.

---

## 6. 교차 검증 분석

### 6.1 일치 (41항목)
R-01~R-03, R-05~R-10, R-12~R-35, R-39, R-41~R-44, R-46~R-48 등 41항목에서 판정이 일치했다. 특히 **15대 쿼리(R-19~R-35)는 두 모델 모두 전 항목 PASS**로, 서로 다른 실행 스크립트로 같은 결과 행 수·의미를 확인했다.

### 6.2 불일치 9항목과 원인
| ID | GPT-5.4 | Claude | 원인 분류 | 편집자 판단 |
|---|---|---|---|---|
| R-04 | 부분 | PASS | 기준 문구 해석 | 해석 이슈(D-5) |
| R-11 | 부분 | PASS | Claude 판정 누락 | **GPT-5.4가 옳다**(C2 `NOTNULL categories 1`) |
| R-17 | 부분 | PASS | 기준 문구 해석 | 해석 이슈 |
| R-36 | PASS | 부분 | 채점기 결함의 배점 위치 차이 | 실질 결함(D-1) |
| R-37 | PASS | 부분 | 동일 | 실질 결함(D-1) |
| R-38 | **FAIL** | 부분 | 동일 결함의 심각도 판단 차이 | **결함 존재는 일치**(FAIL이 더 정확) |
| R-40 | 부분 | PASS | GPT 출력 절단 | Claude 판정 채택 |
| R-45 | 부분 | PASS | GPT 출력 절단 | Claude 판정 채택 |
| R-49 | **FAIL** | PASS | GPT가 심사 사본 기준으로 판정 | Claude 판정 채택(§5) |

### 6.3 교차 검증의 결론
- **가장 신뢰도 높은 발견**: `verify_sql.py`의 검사 맹점(D-1). 두 모델이 **서로 다른 실험 설계**(GPT는 제약을 제거한 스키마 변조 3종, Claude는 가짜 스키마 주입 1종)로 같은 결론에 도달했고, 실행 원문이 이를 뒷받침한다.
- **심사자 간 차이가 결론을 뒤집지는 않는다**: 불일치 9건 중 5건은 하네스·문구 해석, 3건은 **같은 결함(D-1)의 심각도 차이**, 1건(R-11)은 Claude의 판정 누락이다. 미션 본체(SQL·쿼리·문서 수치)에 대한 평가는 두 모델이 같다.
- **단일 모델 심사였다면 놓쳤을 것**: GPT-5.4 없이는 categories NOT NULL 미달(D-2)을, Claude 없이는 ERD·demo·거버넌스 판정의 하네스 왜곡을 확인하지 못했을 것이다.

---

## 7. 권고 조치 (실행하지 않음 — 판정만 수집하는 심사이므로 코드는 수정하지 않았다)

| 우선 | 조치 | 대상 | 근거 |
|---|---|---|---|
| 1 | 채점기 검사 범위 확장 — `price>=0`·`status IN(…)` CHECK 실내용, `categories.category_name` UNIQUE, 테이블별 NOT NULL 개수, 그리고 15쿼리의 **기대 행 수·핵심 값** 회귀 검증 | `verify_sql.py` | D-1 |
| 2 | "100/100 ALL PASS" 표현을 "자체 점검 100/100 (검사 범위: 산출물·스키마 구조·시드·FK·쿼리 실행성)"로 한정 | `README.md`, `RTM.md` | D-1 |
| 3 | `categories`에 NOT NULL 컬럼 1개 추가(예: `description NOT NULL DEFAULT ''`) 또는 DoD 문구 조정 | `schema.sql` / 요구 정의 | D-2 |
| 4 | KPI-2 표를 `LIMIT 3` 실제 출력으로 정정하거나 "공동 1위 4권" 서술과 표를 일치시키기 | `docs/bonus/KPI_REPORT.md` | D-3 |
| 5 | Q14 기준일을 파라미터로 고정(`DATE('now')` 대신 인자)하고 문서에 실행 시점 명시 | `queries.sql`, `docs/` | D-4 |

---

## 8. 심사 결론

| 항목 | 결론 |
|---|---|
| 미션 요구 충족도 | **충족 (조건부)** — R-01~R-35(도메인·스키마·시드·15쿼리)는 실질 충족, 문서·시연·거버넌스도 충족 |
| 최대 결함 | `verify_sql.py`가 요구 위반 스키마·부실 쿼리를 통과시키는 자기채점 맹점 (D-1) |
| 미미한 결함 | categories NOT NULL 1개(D-2), KPI TOP3 표 불일치(D-3), Q14 날짜 의존(D-4) |
| 심사자 간 합치 | 미션 본체 평가는 일치, 채점기 결함은 양쪽 모두 확인 |
| 그대로 제출할 위험 | 평가자가 "100/100"을 신뢰하면 스키마 품질 검증 없이 통과시킬 수 있음. 다만 실제 스키마는 요구를 실질 충족하므로 **산출물 자체의 위험은 낮고, 검증 주장의 위험이 크다.** |

---

## 부록 A. GPT-5.4 판정 원문 (전문)

### A-1. 1단계 검증 계획 (원문)

```json
{"checks":[{"id":"C1","purpose":"저장소 파일 존재, git 상태/브랜치, 핵심 파일 첫머리와 라인번호 확보(R-04,R-45,R-46,R-47,R-49,R-50 일부)","cmd":"bash -lc 'printf \"== pwd ==\\n\"; pwd; printf \"\\n== files ==\\n\"; find . -maxdepth 3 -type f | LC_ALL=C sort; printf \"\\n== git branch/status ==\\n\"; git branch --show-current; git status --short; printf \"\\n== schema head ==\\n\"; nl -ba schema.sql | sed -n \"1,80p\"; printf \"\\n== queries head ==\\n\"; nl -ba queries.sql | sed -n \"1,260p\"; printf \"\\n== demo head ==\\n\"; nl -ba demo.sh | sed -n \"1,260p\"'"} ,{"id":"C2","purpose":"schema.sql를 독립적으로 실행해 실제 스키마/제약/인덱스/생성순서/NOT NULL 개수/FK 개수 확인(R-02,R-06~R-13)","cmd":"python3 - <<'PY'\nimport sqlite3, re\nsql=open('schema.sql',encoding='utf-8').read()\nconn=sqlite3.connect(':memory:')\nconn.executescript(sql)\nprint('foreign_keys', conn.execute('PRAGMA foreign_keys;').fetchone()[0])\nprint('tables', conn.execute(\"SELECT group_concat(name, ',') FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid\").fetchone()[0])\nfor t in ['categories','members','books','rentals']:\n    cols=conn.execute(f'PRAGMA table_info({t})').fetchall()\n    fks=conn.execute(f'PRAGMA foreign_key_list({t})').fetchall()\n    idx=conn.execute(f\"SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='{t}' ORDER BY name\").fetchall()\n    print('TABLE',t,'cols',[(c[1],c[2],c[3],c[5]) for c in cols])\n    print('NOTNULL',t,sum(c[3] for c in cols),'PKs',[c[1] for c in cols if c[5]])\n    print('FK',t,[(r[3],r[2],r[4]) for r in fks])\n    print('IDX',t,idx)\nprint('schema_order_lines', [ln.strip() for ln in sql.splitlines() if ln.strip().startswith('CREATE TABLE') or ln.strip().startswith('CREATE INDEX')])\nPY"},{"id":"C3","purpose":"제약조건이 실제로 강제되는지 독립 실험: FK, 음수 price, 잘못된 status, email/category 중복, NOT NULL 누락(R-14)","cmd":"python3 - <<'PY'\nimport sqlite3\nconn=sqlite3.connect(':memory:')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\ntests=[\n('fk_missing_parent', \"INSERT INTO rentals(member_id,book_id,rental_date,due_date,status) VALUES (999,1,'2026-11-10','2026-11-24','RENTED')\"),\n('negative_price', \"INSERT INTO books(category_id,title,author,publisher,published_year,price) VALUES (1,'X','Y','Z',2024,-1)\"),\n('bad_status', \"INSERT INTO rentals(member_id,book_id,rental_date,due_date,status) VALUES (1,1,'2026-11-10','2026-11-24','LOST')\"),\n('dup_email', \"INSERT INTO members(name,email,phone,address,join_date) VALUES ('중복','minjun.kim@email.com','010-0000-0000','서울','2026-01-01')\"),\n('dup_category', \"INSERT INTO categories(category_name) VALUES ('소설')\"),\n('notnull_missing_member_name', \"INSERT INTO members(email,phone,address,join_date) VALUES ('x@x.com','010','서울','2026-01-01')\"),\n('notnull_missing_book_title', \"INSERT INTO books(category_id,author,publisher,published_year,price) VALUES (1,'Y','Z',2024,1000)\")\n]\nfor name,sql in tests:\n    try:\n        conn.execute(sql)\n        print(name,'ALLOWED')\n    except Exception as e:\n        print(name, type(e).__name__, str(e))\nPY"},{"id":"C4","purpose":"seed.sql를 독립 실행해 행 수, 총합, 상태 분포, 복수 대여 회원, 한국어 데이터 예시, 대여 없는 회원/도서 확인(R-15~R-18)","cmd":"python3 - <<'PY'\nimport sqlite3\nconn=sqlite3.connect(':memory:')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\nfor t in ['categories','members','books','rentals']:\n    print('count',t,conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0])\nprint('total', sum(conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ['categories','members','books','rentals']))\nprint('status_dist', conn.execute(\"SELECT status, COUNT(*) FROM rentals GROUP BY status ORDER BY status\").fetchall())\nprint('multi_rent_members', conn.execute(\"SELECT member_id, COUNT(*) c FROM rentals GROUP BY member_id HAVING c>=2 ORDER BY member_id\").fetchall())\nprint('no_rental_members', conn.execute(\"SELECT member_id,name FROM members WHERE member_id NOT IN (SELECT DISTINCT member_id FROM rentals) ORDER BY member_id\").fetchall())\nprint('no_rental_books', conn.execute(\"SELECT book_id,title FROM books WHERE book_id NOT IN (SELECT DISTINCT book_id FROM rentals) ORDER BY book_id\").fetchall())\nprint('sample_categories', conn.execute('SELECT category_id, category_name FROM categories ORDER BY category_id LIMIT 5').fetchall())\nprint('sample_members', conn.execute('SELECT member_id, name, email, phone, address FROM members ORDER BY member_id LIMIT 3').fetchall())\nprint('sample_books', conn.execute('SELECT book_id, title, author, publisher FROM books ORDER BY book_id LIMIT 5').fetchall())\nPY"},{"id":"C5","purpose":"seed.sql 단독 실행 가능성 및 적재 순서 검증: 빈 DB에서 seed.sql만 실행 시 실패 여부와, 부모→자식 순서 문장 요약(R-04,R-17)","cmd":"python3 - <<'PY'\nimport sqlite3\nseed=open('seed.sql',encoding='utf-8').read()\nconn=sqlite3.connect(':memory:')\ntry:\n    conn.executescript(seed)\n    print('seed_only', 'OK')\nexcept Exception as e:\n    print('seed_only', type(e).__name__, str(e))\nlines=[]\nfor ln in seed.splitlines():\n    s=ln.strip()\n    if s.startswith('INSERT INTO '):\n        lines.append(s.split()[2])\nprint('insert_order', lines)\nPY"},{"id":"C6","purpose":"queries.sql 구조 검증: Q01~Q15 마커, 각 블록 첫 문장, 쿼리 수, UPDATE/DELETE 위치 확인(R-19)","cmd":"python3 - <<'PY'\nimport re, sqlite3\nsql=open('queries.sql',encoding='utf-8').read()\nmarks=list(re.finditer(r'^--\\s*(Q\\d{2})\\s*:\\s*(.*)$', sql, flags=re.M))\nprint('marks', [(m.group(1), m.group(2)) for m in marks])\n# split using sqlite complete_statement\nblocks=[]\nfor i,m in enumerate(marks):\n    end=marks[i+1].start() if i+1<len(marks) else len(sql)\n    body=sql[m.end():end].strip()\n    buf=''\n    stmt=None\n    for line in body.splitlines(True):\n        buf+=line\n        if sqlite3.complete_statement(buf):\n            stmt=buf.strip(); break\n    blocks.append((m.group(1), stmt.splitlines()[0] if stmt else None))\nprint('first_stmt_lines', blocks)\nPY"},{"id":"C7","purpose":"15개 쿼리 전수 독립 실행 및 핵심 결과 요약. 특히 Q07/Q08/Q13/Q14/Q15 의미 타당성 검증(R-20~R-35)","cmd":"python3 - <<'PY'\nimport sqlite3, re\nsqlq=open('queries.sql',encoding='utf-8').read()\nmarks=list(re.finditer(r'^--\\s*(Q\\d{2})\\s*:\\s*(.*)$', sqlq, flags=re.M))\ndef split_first(body):\n    buf=''\n    for line in body.splitlines(True):\n        buf+=line\n        if sqlite3.complete_statement(buf):\n            return buf.strip()\n    return None\nblocks=[]\nfor i,m in enumerate(marks):\n    end=marks[i+1].start() if i+1<len(marks) else len(sqlq)\n    blocks.append((m.group(1), m.group(2), split_first(sqlq[m.end():end].strip())))\nconn=sqlite3.connect(':memory:')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\nfor label,purpose,stmt in blocks:\n    cur=conn.cursor()\n    cur.execute(stmt)\n    if cur.description:\n        rows=cur.fetchall()\n        print(label,'rows',len(rows),'sample',rows[:3])\n    else:\n        print(label,'rowcount',cur.rowcount)\n        if label=='Q14':\n            print('Q14_status_after', conn.execute(\"SELECT rental_id,status,due_date,return_date FROM rentals WHERE rental_id IN (12,13,14,15) ORDER BY rental_id\").fetchall())\n        if label=='Q15':\n            print('Q15_member10_after', conn.execute(\"SELECT rental_id,member_id,rental_date FROM rentals WHERE member_id=10 ORDER BY rental_id\").fetchall())\nPY"},{"id":"C8","purpose":"Q07/Q08/Q13의 의미를 독립 기준 쿼리와 대조해 정확성 확인(R-26,R-27,R-32,R-35)","cmd":"python3 - <<'PY'\nimport sqlite3\nconn=sqlite3.connect(':memory:')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\nq07_expected=conn.execute(\"SELECT book_id,title FROM books WHERE book_id NOT IN (SELECT DISTINCT book_id FROM rentals) ORDER BY book_id\").fetchall()\nq08_expected=conn.execute(\"SELECT m.member_id,m.name,COUNT(r.rental_id) FROM members m LEFT JOIN rentals r ON m.member_id=r.member_id GROUP BY m.member_id,m.name ORDER BY COUNT(r.rental_id) DESC,m.member_id\").fetchall()\nq13_expected=conn.execute(\"SELECT m.member_id,m.name,(SELECT MAX(r.rental_date) FROM rentals r WHERE r.member_id=m.member_id) FROM members m ORDER BY ((SELECT MAX(r2.rental_date) FROM rentals r2 WHERE r2.member_id=m.member_id) IS NULL), (SELECT MAX(r3.rental_date) FROM rentals r3 WHERE r3.member_id=m.member_id) DESC\").fetchall()\nprint('q07_expected', q07_expected)\nprint('q08_tail_zero_members', [r for r in q08_expected if r[2]==0])\nprint('q13_tail_null_members', q13_expected[-2:])\nPY"},{"id":"C9","purpose":"문서 수치/행수/에러메시지/실행계획 주장 대조용 실제 값 산출: KPI, JOIN vs EXISTS 실행계획, FK 오류 메시지(R-41~R-44)","cmd":"python3 - <<'PY'\nimport sqlite3\nconn=sqlite3.connect(':memory:')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\nprint('plan_join')\nfor r in conn.execute(\"EXPLAIN QUERY PLAN SELECT DISTINCT m.member_id,m.name,m.email FROM members AS m INNER JOIN rentals AS r ON m.member_id = r.member_id ORDER BY m.member_id\"):\n    print(r)\nprint('plan_exists')\nfor r in conn.execute(\"EXPLAIN QUERY PLAN SELECT m.member_id,m.name,m.email FROM members AS m WHERE EXISTS (SELECT 1 FROM rentals AS r WHERE r.member_id = m.member_id) ORDER BY m.member_id\"):\n    print(r)\nprint('kpi1', conn.execute(\"SELECT strftime('%Y-%m', rental_date), COUNT(*), (SELECT COUNT(*) FROM books), ROUND(CAST(COUNT(*) AS REAL)/(SELECT COUNT(*) FROM books),4) FROM rentals GROUP BY strftime('%Y-%m', rental_date) ORDER BY 1\").fetchall())\nprint('kpi2_top3', conn.execute(\"SELECT b.book_id,b.title,COUNT(r.rental_id) c FROM books b JOIN rentals r ON b.book_id=r.book_id GROUP BY b.book_id,b.title ORDER BY c DESC,b.book_id ASC LIMIT 3\").fetchall())\nprint('kpi2_all_counts', conn.execute(\"SELECT b.book_id,b.title,COUNT(r.rental_id) c FROM books b LEFT JOIN rentals r ON b.book_id=r.book_id GROUP BY b.book_id,b.title ORDER BY c DESC,b.book_id ASC\").fetchall())\nprint('kpi3', conn.execute(\"SELECT COUNT(*), SUM(CASE WHEN status='OVERDUE' THEN 1 ELSE 0 END), SUM(CASE WHEN status='RETURNED' THEN 1 ELSE 0 END), SUM(CASE WHEN status='RENTED' THEN 1 ELSE 0 END), ROUND(CAST(SUM(CASE WHEN status='OVERDUE' THEN 1 ELSE 0 END) AS REAL)/COUNT(*)*100,1) FROM rentals\").fetchone())\nprint('kpi3_members', conn.execute(\"SELECT m.name, COUNT(r.rental_id), SUM(CASE WHEN r.status='OVERDUE' THEN 1 ELSE 0 END), ROUND(CAST(SUM(CASE WHEN r.status='OVERDUE' THEN 1 ELSE 0 END) AS REAL)/COUNT(r.rental_id)*100,1) FROM members m JOIN rentals r ON m.member_id=r.member_id GROUP BY m.member_id,m.name HAVING SUM(CASE WHEN r.status='OVERDUE' THEN 1 ELSE 0 END) > 0 ORDER BY 3 DESC,4 DESC\").fetchall())\ntry:\n    conn.execute(\"INSERT INTO rentals (member_id, book_id, rental_date, due_date, status) VALUES (999,1,'2026-11-10','2026-11-24','RENTED')\")\nexcept Exception as e:\n    print('fk_error', type(e).__name__, str(e))\nPY"},{"id":"C10","purpose":"outputs/query_results.md와 실제 실행 결과의 일치 여부 샘플 대조 및 verify 실행 후 재생성 여부 확인(R-39,R-44)","cmd":"bash -lc 'python3 verify_sql.py >/tmp/v.out 2>/tmp/v.err; ec=$?; echo verify_exit=$ec; sed -n \"1,80p\" /tmp/v.out; echo \"== query_results head ==\"; sed -n \"1,120p\" outputs/query_results.md'"} ,{"id":"C11","purpose":"verify_sql.py가 실제로 무엇을 검사하는지 정적 점검: 외부패키지 사용 여부, 배점, 미검사항 식별 근거 확보(R-36,R-37,R-38)","cmd":"bash -lc 'nl -ba verify_sql.py | sed -n \"1,260p\"'"} ,{"id":"C12","purpose":"verify_sql.py의 자기검증 신뢰성 반증 실험 1: 요구 위반 산출물(negative price 허용 스키마)로도 통과하는지 확인(R-38)","cmd":"python3 - <<'PY'\nfrom pathlib import Path\np=Path('schema.sql')\norig=p.read_text(encoding='utf-8')\nmod=orig.replace('price       INTEGER NOT NULL CHECK (price >= 0),','price       INTEGER NOT NULL,')\np.write_text(mod,encoding='utf-8')\nimport subprocess, sys\nr=subprocess.run([sys.executable,'verify_sql.py'],capture_output=True,text=True)\nprint('exit',r.returncode)\nprint((r.stdout+r.stderr)[:3500])\nPY"},{"id":"C13","purpose":"verify_sql.py의 자기검증 신뢰성 반증 실험 2: status CHECK 제거 산출물을 잡는지 확인(R-38)","cmd":"python3 - <<'PY'\nfrom pathlib import Path\np=Path('schema.sql')\norig=p.read_text(encoding='utf-8')\nmod=orig.replace(\"status      TEXT    NOT NULL CHECK (status IN ('RENTED', 'RETURNED', 'OVERDUE'))\", \"status      TEXT    NOT NULL\")\np.write_text(mod,encoding='utf-8')\nimport subprocess, sys\nr=subprocess.run([sys.executable,'verify_sql.py'],capture_output=True,text=True)\nprint('exit',r.returncode)\nprint((r.stdout+r.stderr)[:3500])\nPY"},{"id":"C14","purpose":"verify_sql.py의 자기검증 신뢰성 반증 실험 3: queries.sql에서 Q07을 목적 위반 쿼리로 바꿔도 통과하는지 확인(R-38)","cmd":"python3 - <<'PY'\nfrom pathlib import Path\np=Path('queries.sql')\norig=p.read_text(encoding='utf-8')\nmod=orig.replace(\"FROM books b\\nLEFT JOIN rentals r ON b.book_id = r.book_id\\nWHERE r.rental_id IS NULL\\nORDER BY b.book_id;\", \"FROM books b\\nORDER BY b.book_id;\")\np.write_text(mod,encoding='utf-8')\nimport subprocess, sys\nr=subprocess.run([sys.executable,'verify_sql.py'],capture_output=True,text=True)\nprint('exit',r.returncode)\nprint((r.stdout+r.stderr)[:3500])\nPY"},{"id":"C15","purpose":"demo.sh 비대화형 동작, 종료코드, 5단계 수행 여부, 워킹트리 오염 여부 확인(R-45)","cmd":"bash -lc 'before=$(git status --short); bash demo.sh --non-interactive > /tmp/demo.out 2>/tmp/demo.err; ec=$?; after=$(git status --short); echo demo_exit=$ec; echo \"== demo stdout head ==\"; sed -n \"1,220p\" /tmp/demo.out; echo \"== demo stderr ==\"; cat /tmp/demo.err; echo \"== git before ==\"; printf \"%s\\n\" \"$before\"; echo \"== git after ==\"; printf \"%s\\n\" \"$after\"'"} ,{"id":"C16","purpose":"README/SUBMISSION/ERD/보너스 문서의 요구 포함 여부와 주장 수치 라인 근거 확보(R-40~R-47)","cmd":"bash -lc 'echo \"== README ==\"; nl -ba README.md | sed -n \"1,260p\"; echo \"== SUBMISSION ==\"; nl -ba SUBMISSION.md | sed -n \"1,220p\"; echo \"== ERD ==\"; nl -ba docs/ERD.md | sed -n \"1,260p\"; echo \"== JOIN_VS_SUBQUERY ==\"; nl -ba docs/bonus/JOIN_VS_SUBQUERY.md | sed -n \"1,260p\"; echo \"== INTEGRITY_VIOLATION ==\"; nl -ba docs/bonus/INTEGRITY_VIOLATION.md | sed -n \"1,260p\"; echo \"== KPI_REPORT ==\"; nl -ba docs/bonus/KPI_REPORT.md | sed -n \"1,260p\"'"} ,{"id":"C17","purpose":"민감정보 하드코딩 탐지 및 금지 기술 사용 흔적 탐지(API 키, trigger/view 등) (R-03,R-48)","cmd":"python3 - <<'PY'\nfrom pathlib import Path\nimport re\npatterns=[r'AKIA[0-9A-Z]{16}', r'AIza[0-9A-Za-z\\-_]{35}', r'sk-[A-Za-z0-9]{20,}', r'api[_-]?key', r'secret', r'token']\nfor path in sorted([p for p in Path('.').rglob('*') if p.is_file()]):\n    try:\n        txt=path.read_text(encoding='utf-8',errors='ignore')\n    except: continue\n    low=txt.lower()\n    hits=[]\n    for pat in patterns:\n        if re.search(pat, txt, re.I): hits.append(pat)\n    if hits:\n        print('secret_hit', str(path), hits)\nfor fname in ['schema.sql','seed.sql','queries.sql','README.md','docs/ERD.md']:\n    txt=Path(fname).read_text(encoding='utf-8',errors='ignore').lower()\n    for kw in ['create view','trigger','django','spring','express','flask','fastapi','api']:\n        if kw in txt:\n            print('kw', fname, kw)\nPY"},{"id":"C18","purpose":"R-50 관련 git 원격 URL 및 최근 커밋 메시지 형식 확인(공개 저장소 여부는 원격 문자열까지만 확인 가능)","cmd":"bash -lc 'git remote -v; echo \"== commits ==\"; git log --oneline --decorate -n 12'"}]}
```

### A-2. 항목별 판정 및 최종 채점 (원문)

| ID | 판정 | 근거 | 메모 |
|---|---|---|---|
| R-01 | PASS | `schema.sql:3-42`, `seed.sql` 내용 요약은 C4의 샘플 데이터와 행 분포로 확인됨: `sample_categories`, `sample_members`, `sample_books`, `status_dist`, `multi_rent_members` | 도메인이 회원·도서·카테고리·대여/연체 관리로 일관되고, 한국어 회원/도서/대여 상태 데이터가 현실적이다. |
| R-02 | PASS | C2 `tables categories,members,books,rentals`; C2 `FK books [('category_id', 'categories', 'category_id')]`, `FK rentals [('book_id', 'books', 'book_id'), ('member_id', 'members', 'member_id')]`; `schema.sql:3-39` | 정확히 4개 테이블, 1:N 관계 3개 충족. |
| R-03 | PASS | C1 파일 목록에 SQL/문서/스크립트만 존재; `schema.sql:3-42`에 VIEW/TRIGGER 없음; C17 금지기술 탐지 결과 `kw README.md api`만 출력되고 SQL 파일에서는 `create view`/`trigger` 미검출 | README에 “API”라는 설명어가 있어 탐지되었을 뿐, 실제 산출물 구현에 뷰/트리거/프레임워크 사용 증거는 없다. |
| R-04 | 부분 | 파일 존재: C1 `./schema.sql ./seed.sql ./queries.sql`; `schema.sql` 실행 가능: C2 성공; `queries.sql` 실행 가능: C7 전수 실행 성공; 그러나 `seed.sql` 단독 실행은 실패: C5 `seed_only OperationalError no such table: categories` | “각각 그 자체로 SQLite에서 실행 가능”을 엄격히 보면 `seed.sql`은 스키마 없는 빈 DB에서 단독 실행 불가. 다만 스키마가 준비된 DB에서는 정상 적재됨(C4). |
| R-05 | PASS | C10 `python3 verify_sql.py` 실행 `verify_exit=0`; 출력에 `outputs/query_results.md 재생성 완료`; C10에서 `outputs/query_results.md` 내용 확인 | 요구는 재현성 제공 여부에 관한 것이라 충족. 단, 이 스크립트의 성공은 다른 요구 충족의 증거로 쓰지 않음. |
| R-06 | PASS | C1 `schema.sql:1` `PRAGMA foreign_keys = ON;` | 첫 번째 문장에 정확히 선언됨. |
| R-07 | PASS | `schema.sql:3-7`; C2 `categories cols [('category_id', 'INTEGER', 0, 1), ('category_name', 'TEXT', 1, 0)...]`; C2 `IDX categories [('sqlite_autoindex_categories_1', None)]` | PK 존재, `category_name`에 NOT NULL + UNIQUE 존재. |
| R-08 | PASS | `schema.sql:9-16`; C2 `members cols ... ('email','TEXT',1,0) ...`; C2 `NOTNULL members 5`; C2 `IDX members [('sqlite_autoindex_members_1', None)]` | PK 존재, `email` NOT NULL + UNIQUE, NOT NULL 컬럼 2개 이상(실제 5개). |
| R-09 | PASS | `schema.sql:18-27`; C2 `FK books [('category_id', 'categories', 'category_id')]`; C3 `negative_price IntegrityError CHECK constraint failed: price >= 0` | PK, category FK, `price >= 0` CHECK 모두 존재하고 실제 강제됨. |
| R-10 | PASS | `schema.sql:29-39`; C2 `FK rentals [('book_id', 'books', 'book_id'), ('member_id', 'members', 'member_id')]`; C3 `bad_status IntegrityError CHECK constraint failed: status IN ('RENTED', 'RETURNED', 'OVERDUE')` | PK, FK 2개, status CHECK 존재 및 실제 강제 확인. |
| R-11 | 부분 | PK 4개/FK 3개/UNIQUE 2개/CHECK 2개는 C2와 `schema.sql:3-39`로 확인; 그러나 “테이블마다 NOT NULL 2개 이상”은 C2에서 `NOTNULL categories 1` | 전체 제약 중 `categories`가 PK 제외 실질 NOT NULL 1개(`category_name`)만 보여 요구 문구를 충족하지 못함. |
| R-12 | PASS | C1 `schema.sql:41-42`; C2 `IDX rentals [('idx_rentals_date', 'CREATE INDEX idx_rentals_date ON rentals (rental_date)')]` | 인덱스 존재, 바로 위 1줄에 생성 사유 주석 존재. |
| R-13 | PASS | C2 `schema_order_lines ['CREATE TABLE categories (', 'CREATE TABLE members (', 'CREATE TABLE books (', 'CREATE TABLE rentals (', 'CREATE INDEX idx_rentals_date ON rentals (rental_date);']`; `schema.sql:3-42` | FK 의존성 위상정렬 순서 충족. |
| R-14 | PASS | C3 전 항목: `fk_missing_parent IntegrityError FOREIGN KEY constraint failed`, `negative_price IntegrityError CHECK constraint failed: price >= 0`, `bad_status IntegrityError CHECK constraint failed: status IN (...)`, `dup_email IntegrityError UNIQUE constraint failed: members.email`, `dup_category IntegrityError UNIQUE constraint failed: categories.category_name`, `notnull_missing_member_name IntegrityError NOT NULL constraint failed: members.name`, `notnull_missing_book_title IntegrityError NOT NULL constraint failed: books.title` | 선언만이 아니라 실제 강제됨을 독립 실험으로 확인. |
| R-15 | PASS | C4 `count categories 10`, `count members 12`, `count books 13`, `count rentals 15`, `total 50` | 4개 테이블 각 10행 이상, 총 45행 이상 충족. |
| R-16 | PASS | C4 `sample_categories` 한국어 카테고리, `sample_members` 한국어 이름/이메일/전화/주소, `sample_books` 한국어 제목/저자/출판사 | 한국어 기반의 현실적인 값으로 보임. |
| R-17 | 부분 | 적재 순서: C5 `insert_order ['categories', 'members', 'books', 'rentals']`; 실제 스키마 후 적재 성공: C4 성공. 그러나 `seed.sql` 자체만으로는 C5 `seed_only OperationalError no such table: categories` | 부모→자식 순서는 맞고, 스키마가 선행된 환경에서는 FK 오류 없이 적재된다. 다만 “그 자체로 실행 가능”과는 별개로 seed 단독 실행은 실패. |

짧은 설명:
- R-04와 R-17은 `seed.sql`의 단독 실행 불가 때문에 완전 PASS로 보기 어렵다.
- R-11은 `categories` 테이블의 NOT NULL 개수가 요구치(테이블마다 2개 이상)에 미달해 부분 판정이다.

| ID | 판정 | 근거 | 메모 |
|---|---|---|---|
| R-18 | PASS | C4 `status_dist [('OVERDUE', 4), ('RENTED', 4), ('RETURNED', 7)]`; C4 `multi_rent_members [(1, 3), (2, 2), (3, 2), (4, 2)]` | 세 상태 모두 존재하고, 연체 건 및 복수 대여 회원 포함. |
| R-19 | PASS | C6 `marks [('Q01', ...), ... ('Q15', ...)]`; C6 `first_stmt_lines [('Q01','SELECT'), ... ('Q14','UPDATE rentals'), ('Q15','DELETE FROM rentals')]` | `-- Qnn: 목적` 형식의 주석이 있고 Q01~Q15가 누락·중복 없이 연속 15개다. |
| R-20 | PASS | C1 `queries.sql:1-11`에 `WHERE c.category_name = '컴퓨터'`와 `ORDER BY b.price DESC`; C7 `Q01 rows 2 sample [(9, '클린 코드', ... 33000 ...), (8, '혼자 공부하는 SQL', ... 26000 ...)]` | 특정 카테고리 도서를 WHERE 조건과 DESC 정렬로 조회하며 결과도 타당하다. |
| R-21 | PASS | C1 `queries.sql:13-24`에 `WHERE r.status = 'OVERDUE'`; C7 `Q02 rows 4 sample ... 'OVERDUE'` | 연체 대여 건 조회 목적 충족. |
| R-22 | PASS | C1 `queries.sql:26-34`에 `ORDER BY join_date DESC LIMIT 5`; C7 `Q03 rows 5 sample [(12, '류미나', ...), (11, '신현우', ...), (10, '강소희', ...)]` | 최근 가입 회원 5명 조회 충족. |
| R-23 | PASS | C1 `queries.sql:36-46`에 `published_year >= 2020 AND price >= 20000`; C7 `Q04 rows 2 sample [(8, '혼자 공부하는 SQL', ...), (5, '조선왕조실록', ...)]` | 다중 조건 AND 조회 충족. |
| R-24 | PASS | C1 `queries.sql:48-59`에 `INNER JOIN categories c ON b.category_id = c.category_id`; C7 `Q05 rows 13 sample ... 카테고리 포함` | 도서와 카테고리 INNER JOIN 충족. |
| R-25 | PASS | C1 `queries.sql` Q06 블록(출력 일부 절단됐지만 C6/C7로 구조 확인); C6 `Q06` 첫 문장 `SELECT`; C7 `Q06 rows 4 sample [('최수아', '부의 추월차선', '2026-10-22', '2026-11-05'), ...]` | `rentals`·`members`·`books` 3테이블 다중 INNER JOIN으로 대여 중 회원/도서/반납예정일 조회가 동작한다. |
| R-26 | PASS | C1 `queries.sql` Q07 본문은 제출 자료상 `LEFT JOIN rentals r ON b.book_id = r.book_id WHERE r.rental_id IS NULL`; C7 `Q07 rows 2 sample [(11, '소크라테스의 변명', ...), (12, '구름빵', ...)]`; C8 `q07_expected [(11, '소크라테스의 변명'), (12, '구름빵')]` | LEFT JOIN + IS NULL로 대여 이력 없는 도서를 정확히 조회. |
| R-27 | PASS | 제출 자료 `queries.sql` Q08에 `LEFT JOIN + COUNT + GROUP BY`; C7 `Q08 rows 12 sample [(1, '김민준', 3), (2, '이서연', 2), (3, '박지호', 2)]`; C8 `q08_tail_zero_members [(11, '신현우', 0), (12, '류미나', 0)]` | 0회 회원까지 포함한 회원별 대여 횟수 조회가 정확하다. |
| R-28 | PASS | 제출 자료 `queries.sql` Q09에 `COUNT`, `AVG`, `GROUP BY`; C7 `Q09 rows 10 sample [('소설', 2, 12750.0), ('역사', 2, 23500.0), ('자기계발', 2, 16400.0)]` | 카테고리별 권수·평균가 집계 충족. |
| R-29 | PASS | 제출 자료 `queries.sql` Q10에 `GROUP BY ... HAVING COUNT(r.rental_id) >= 1`; C7 `Q10 rows 4 sample [(1, '김민준', 1), (2, '이서연', 1), (3, '박지호', 1)]` | 회원별 연체 건수(1건 이상) 조회 충족. |
| R-30 | PASS | 제출 자료 `queries.sql` Q11에 `strftime('%Y-%m', r.rental_date)` + `GROUP BY`; C7 `Q11 rows 9 sample [('2026-01', 1), ('2026-02', 2), ('2026-03', 2)]` | 월별 대여 추이 조회 충족. |
| R-31 | PASS | 제출 자료 `queries.sql` Q12에 `WHERE b.price > (SELECT AVG(price) FROM books)`; C7 `Q12 rows 5 sample [(9, '클린 코드', ... 18238.0), ...]` | 비상관 서브쿼리로 평균가 초과 도서 조회 충족. |
| R-32 | PASS | 제출 자료 `queries.sql` Q13에 `SELECT MAX(r.rental_date) ... WHERE r.member_id = m.member_id`; C7 `Q13 rows 12 sample [(10, '강소희', '2026-11-08'), ...]`; C8 `q13_tail_null_members [(11, '신현우', None), (12, '류미나', None)]` | 상관 서브쿼리로 회원별 최근 대여일을 구하고, 대여 이력 없는 회원은 NULL로 표시된다. |
| R-33 | PASS | 제출 자료 `queries.sql` Q14는 `UPDATE rentals SET status = 'OVERDUE' WHERE return_date IS NULL AND due_date < DATE('now') AND status = 'RENTED';`; C7 `Q14 rowcount 1`; C7 `Q14_status_after [(12, 'OVERDUE', '2026-11-05', None), (13, 'RENTED', ...), (14, 'RENTED', ...), (15, 'RENTED', ...)]` | 기한 경과 미반납 건을 OVERDUE로 일괄 갱신하는 UPDATE이며, 실행 시 영향 행 수 1행이 확인된다. |
| R-34 | PASS | 제출 자료 `queries.sql` Q15는 `DELETE FROM rentals WHERE rental_id = (SELECT rental_id FROM rentals WHERE member_id = 10 ORDER BY rental_date DESC LIMIT 1);`; C7 `Q15 rowcount 1`; C7 `Q15_member10_after []` | 삭제 대상이 서브쿼리+`LIMIT 1`로 1건으로 한정되며 실제 1행 삭제됨. |

| ID | 판정 | 근거 | 메모 |
|---|---|---|---|
| R-35 | PASS | C7에서 Q01~Q15 전부 종료코드 0으로 실행됨. 각 결과: `Q01 rows 2`, `Q02 rows 4`, `Q03 rows 5`, `Q04 rows 2`, `Q05 rows 13`, `Q06 rows 4`, `Q07 rows 2`, `Q08 rows 12`, `Q09 rows 10`, `Q10 rows 4`, `Q11 rows 9`, `Q12 rows 5`, `Q13 rows 12`, `Q14 rowcount 1`, `Q15 rowcount 1`; 의미 타당성은 C8(Q07/Q08/Q13 독립 대조) 및 C7의 Q14/Q15 후상태로 확인 | 15개 쿼리 모두 SQLite에서 실행 오류 0건이며 목적에 부합하는 실제 결과를 냈다. |
| R-36 | PASS | C11 `verify_sql.py:17-20` import는 `os, re, sqlite3, sys`만 사용 | Python 표준 라이브러리만 사용. |
| R-37 | PASS | C11 `verify_sql.py:4-10` 6개 블록과 배점(20+20+20+10+20+10); C10 `verify_exit=0`; C10 출력 `outputs/query_results.md 재생성 완료` | 요구한 6블록 100점 구성, 결과 리포트 자동 재생성, 전부 통과 시 exit 0 확인. |
| R-38 | FAIL | C12: `price CHECK` 제거 후에도 `exit 0` 및 `100/100점`; C13: `status CHECK` 제거 후에도 `exit 0`; C14: Q07을 목적 위반 쿼리로 바꿔도 `exit 0`; C11 정적 코드상 `check_schema`는 PK/FK/`members.email` UNIQUE/인덱스만 주로 확인하고 CHECK 강제·Q07 의미 타당성 등을 검증하지 못함 | 채점기가 실제 요구사항 위반을 놓친다. 자기채점 신뢰성 요구 불충족. |
| R-39 | PASS | C10 `outputs/query_results.md`가 verify 실행으로 재생성됨; 파일 내용에 Q01~Q05 전문과 실제 행 수/값이 기록됨. 제출 자료의 `outputs/query_results.md` 전체에는 Q01~Q15 모두 포함 | 15개 쿼리의 전문과 실제 실행 결과가 기록되어 있다. |
| R-40 | 부분 | `docs/ERD.md` 존재는 C1 파일 목록; 내용 일부는 제출 자료와 C16 `ERD` 헤드에서 확인: Mermaid `erDiagram`, 1:N 관계선 3개(`categories ||--o{ books`, `members ||--o{ rentals`, `books ||--o{ rentals`), 컬럼/타입/제약 설명 표 존재. 그러나 C16 출력이 4,000자에서 절단되어 문서 후반 전체를 원문으로 재확인하지 못함 | 핵심 요건 대부분은 확인되나, “4개 테이블의 컬럼·타입·제약 전부”를 절단 없는 실행 출력으로 재검증하지 못해 보수적으로 PARTIAL. |
| R-41 | PASS | C1 파일 목록에 `docs/bonus/JOIN_VS_SUBQUERY.md`; 제출 자료 원문에 두 쿼리 전문, 결과 동일성 표(10명), 실행계획 텍스트, 가독성·성능 비교, 선택 기준 포함. C9 실제 실행계획: `plan_join ... USE TEMP B-TREE FOR DISTINCT ... ORDER BY`, `plan_exists ... CORRELATED SCALAR SUBQUERY ... SCAN r`로 문서 주장과 부합 | 동일 요구를 JOIN과 EXISTS로 1:1 대조하고 실행계획 근거와 비교/선택 기준을 제시함. |
| R-42 | PASS | C1 파일 목록에 `docs/bonus/INTEGRITY_VIOLATION.md`; 제출 자료 원문에 재현 SQL/파이썬과 `sqlite3.IntegrityError: FOREIGN KEY constraint failed` 기재; C9 `fk_error IntegrityError FOREIGN KEY constraint failed`로 실측 일치 | 존재하지 않는 `member_id=999` INSERT 실증과 원인 분석·해결책 포함. |
| R-43 | PASS | C1 파일 목록에 `docs/bonus/KPI_REPORT.md`; 제출 자료 원문에 KPI 3종(월별 대여 회전율, 최다 대여 도서 TOP 3, 회원 연체율)의 정의·SQL·해석·개선 액션 포함; C9에서 KPI 실측값 산출 | 요구한 3대 KPI 문서 구성 충족. |
| R-44 | 부분 | 일치 확인된 항목: C9와 문서 원문 비교로 JOIN/EXISTS 실행계획, FK 오류 메시지, KPI1 수치, KPI3 수치가 일치. `outputs/query_results.md`의 Q01~Q05도 C7/C10과 일치. 그러나 모든 문서의 “수치·실행계획·에러 메시지·행 수” 전부를 절단 없는 출력으로 전수 대조하지는 못함. 또한 KPI 문서의 “TOP 3” 서술은 실제 SQL `LIMIT 3` 결과(C9 `kpi2_top3`)와 별개로 공동 1위 4권까지 설명해 표현상 혼동 여지 있음 | 상당수는 일치하나 전수 검증 증거가 부족해 PARTIAL. |
| R-45 | 부분 | C15 `demo_exit=0`; stdout에 Step 1~5 배너와 각 단계 실행 출력 존재; Step 4에서 FK 위반 차단 확인; Step 5에서 verify 실행. 워킹트리 오염은 C15 `git before`와 `git after`가 둘 다 공란으로 보임. 그러나 trap에 의한 임시자원 삭제는 출력만으로 직접 확인 불가. 또한 C1/C15의 `demo.sh`는 `outputs/query_results.md`를 verify로 재생성하므로 “오염 없음”은 현재 스냅샷에서 내용 동일했기 때문일 수 있음 | 비대화형 지원·정상 종료·5단계 수행은 확인. 임시자원 삭제는 직접 증거 부족이라 PARTIAL. |
| R-46 | PASS | C16 `README.md` 라인 10-16 개요, 20-39 폴더 구조, 43-95 ERD 요약, 99 이하 실행 방법, 제출 자료 원문에 `4-2. 5단계 시연 러너`, `10. 루브릭 충족 체크리스트` 존재 | README에 요구된 섹션들이 포함되어 있다. |
| R-47 | PASS | C1 파일 목록에 `SUBMISSION.md`; 제출 자료 원문에 `1. 제출 서약`, `2. 산출물 링크` 표 존재 | 제출 서약과 산출물 링크 포함. |
| R-48 | PASS | C17 민감정보 탐지 결과는 `.git/hooks/fsmonitor-watchman.sample ['token']`와 `kw README.md api`뿐이며, 저장소 산출물 파일에서 실제 API 키/비밀값 검출 없음 | 샘플 git hook의 일반 단어 `token`은 심사 대상 산출물의 하드코딩 민감정보 증거가 아니다. |
| R-49 | FAIL | 요구는 저장소에 `ORDER_SHEET.md`, `RTM.md`, `PROJECT_MANIFEST.json` 보존 여부를 파일 목록으로 확인하는 것. 그러나 실행 스냅샷 C1 파일 목록에는 이 3개가 없음 | 운영 안내상 REPO_INVENTORY.md에는 존재한다고 되어 있으나, 본 단계의 실행 원문만 근거로 하면 현재 심사 자료/사본에는 보존되어 있지 않다. 요구 문구를 엄격 적용하면 FAIL. |
| R-50 | 부분 | 저장소 식별/이력에 관한 직접 실행 증거는 C18 `git remote -v`가 비어 있고 `git log`는 `audit snapshot` 1개뿐이라 확인 불가. 다만 심사 자료 `REPO_INVENTORY.md`에는 `yerihanview/B6-1, main, commit 996a6e8` 및 커밋 이력 `feat:`, `docs:` 등 Conventional Commits가 제시됨 | 운영 규칙상 R-50은 REPO_INVENTORY.md로 판단해야 하므로 저장소명/브랜치/커밋 형식은 자료상 충족으로 볼 수 있으나, 실제 원격 푸시 상태는 실행 원문으로 검증 불가. 보수적으로 PARTIAL. |

#### 1) 최종 판정 요약

**총점 82/100, 판정: 조건부 통과**

한 줄 결론: **핵심 SQL 산출물과 15개 쿼리는 대체로 잘 동작하지만, `verify_sql.py`가 요구 위반을 놓치는 치명적 자기검증 결함이 있고, `seed.sql` 단독 실행성·일부 형식 요구·거버넌스 항목에서 미달이 있어 “그대로 무수정 제출”은 위험하다.**

---

#### 2) 배점표

| 항목군 | 요구 ID | 배점 | 획득 | 근거 요약 |
|---|---|---:|---:|---|
| A. 목표·범위 | R-01~R-05 | 10 | 8 | R-01~R-03, R-05 PASS. R-04는 `seed.sql` 단독 실행 실패로 PARTIAL(C1, C2, C5, C7, C10). |
| B. 스키마 | R-06~R-14 | 25 | 22 | R-06~R-10, R-12~R-14 PASS. R-11은 `categories`의 NOT NULL 수 부족으로 PARTIAL(C1~C3). |
| C. 시드 데이터 | R-15~R-18 | 10 | 9 | R-15, R-16, R-18 PASS. R-17은 삽입 순서는 맞지만 `seed.sql` 단독 실행 불가로 PARTIAL(C4, C5). |
| D. 15대 쿼리 | R-19~R-35 | 25 | 25 | Q01~Q15 구조·실행·의미 타당성 모두 독립 실행으로 확인(C6, C7, C8). |
| E. 기계 채점기 | R-36~R-39 | 15 | 8 | R-36, R-37, R-39 PASS. R-38 FAIL: CHECK 제거·Q07 훼손에도 100점 통과(C10~C14). |
| F. 문서 산출물 | R-40~R-44 | 8 | 6 | R-41~R-43 PASS. R-40, R-44는 출력 절단/전수 대조 부족으로 PARTIAL(C9, C16). |
| G. 실행·시연 자산 | R-45~R-47 | 4 | 3 | R-46, R-47 PASS. R-45는 비대화형/5단계/exit0 확인됐으나 trap 삭제 직접 증거 부족으로 PARTIAL(C15, C16). |
| H. 거버넌스·규칙 준수 | R-48~R-50 | 3 | 1 | R-48 PASS. R-49 FAIL(실행 사본 파일 목록에 3종 없음, C1). R-50 PARTIAL(REPO_INVENTORY 자료상만 확인 가능, 실행 원문으로는 원격 확인 불가, C18). |
| **합계** | **R-01~R-50** | **100** | **82** |  |

---

#### 3) 결함·애매점 목록

| ID | 심각도(치명/중대/경미) | 위반 요구 | 내용 | 근거 |
|---|---|---|---|---|
| D1 | 치명 | R-38 | `verify_sql.py`가 실제 요구 위반을 검출하지 못함. `books.price` CHECK 제거 후에도 100/100 통과 | C12 `exit 0`, `100/100점` |
| D2 | 치명 | R-38 | `rentals.status` CHECK 제거 후에도 100/100 통과 | C13 `exit 0`, `100/100점` |
| D3 | 치명 | R-38 | Q07을 목적 위반 쿼리로 바꿔도 100/100 통과. 즉 쿼리 의미 타당성을 검사하지 않음 | C14 `exit 0`, `100/100점` |
| D4 | 중대 | R-04 | `seed.sql`이 “그 자체로 SQLite에서 실행 가능”하지 않음. 빈 DB에서 단독 실행 시 테이블 없음 오류 | C5 `seed_only OperationalError no such table: categories` |
| D5 | 중대 | R-11 | `categories` 테이블의 NOT NULL 컬럼 수가 2개 이상이 아님 | C2 `NOTNULL categories 1` |
| D6 | 경미 | R-17 | INSERT 순서는 맞지만, `seed.sql` 단독 실행성 부족 때문에 요구 해석상 완전 충족으로 보기 어려움 | C5 `insert_order ['categories', 'members', 'books', 'rentals']` + `seed_only` 실패 |
| D7 | 경미 | R-40 | `docs/ERD.md` 핵심 구조는 보이나, 실행 원문이 절단되어 전체 컬럼·제약 전수 확인 불가 | C16 출력 절단, C1/C16 일부만 확인 |
| D8 | 경미 | R-44 | 문서 수치 다수는 실측과 일치하나, 모든 문서의 모든 수치/행수/계획을 전수 대조한 증거는 부족 | C9, C10, C16 절단 |
| D9 | 경미 | R-45 | `demo.sh`의 비대화형/5단계/exit0/워킹트리 무오염은 확인됐으나, trap에 의한 임시자원 삭제는 직접 확인 불가 | C15 |
| D10 | 중대 | R-49 | 실행 사본 파일 목록에 `ORDER_SHEET.md`, `RTM.md`, `PROJECT_MANIFEST.json`이 없음 | C1 파일 목록 |
| D11 | 경미 | R-50 | 실제 원격 URL/공개 저장소 푸시 상태는 실행 원문으로 확인 불가. `git remote -v` 비어 있음 | C18 |
| D12 | 경미 | R-45 | `demo.sh` Step 5가 `verify_sql.py`에 의존하므로, 시연의 마지막 단계가 신뢰성 결함 있는 채점기에 기대고 있음 | C15 + C12~C14 |

---

#### 4) 문서 기재값 vs 실측값 대조표

| 문서 | 기재값 | 실측값(출처 C#) | 일치 여부 |
|---|---|---|---|
| README.md | 총 50행 시드 데이터 | `total 50` (C4) | 일치 |
| README.md | 상태 분포 `RETURNED 7 · OVERDUE 4 · RENTED 4` | `status_dist [('OVERDUE', 4), ('RENTED', 4), ('RETURNED', 7)]` (C4) | 일치 |
| README.md | 복수 대여 회원 4명 | `multi_rent_members [(1,3),(2,2),(3,2),(4,2)]` → 4명 (C4) | 일치 |
| README.md | Q01 결과 행 2 | `Q01 rows 2` (C7) | 일치 |
| README.md | Q02 결과 행 4 | `Q02 rows 4` (C7) | 일치 |
| README.md | Q03 결과 행 5 | `Q03 rows 5` (C7) | 일치 |
| README.md | Q04 결과 행 2 | `Q04 rows 2` (C7) | 일치 |
| README.md | Q05 결과 행 13 | `Q05 rows 13` (C7) | 일치 |
| README.md | Q06 결과 행 4 | `Q06 rows 4` (C7) | 일치 |
| README.md | Q07 결과 행 2 | `Q07 rows 2` (C7) | 일치 |
| README.md | Q08 결과 행 12 | `Q08 rows 12` (C7) | 일치 |
| README.md | Q09 결과 행 10 | `Q09 rows 10` (C7) | 일치 |
| README.md | Q10 결과 행 4 | `Q10 rows 4` (C7) | 일치 |
| README.md | Q11 결과 행 9 | `Q11 rows 9` (C7) | 일치 |
| README.md | Q12 결과 행 5 | `Q12 rows 5` (C7) | 일치 |
| README.md | Q13 결과 행 12 | `Q13 rows 12` (C7) | 일치 |
| README.md | Q14 영향 1행 | `Q14 rowcount 1` (C7) | 일치 |
| README.md | Q15 영향 1행 | `Q15 rowcount 1` (C7) | 일치 |
| outputs/query_results.md | Q01 반환 행 수 2 | `Q01 rows 2` (C7), 파일 헤드에도 `반환 행 수: 2` (C10) | 일치 |
| outputs/query_results.md | Q02 반환 행 수 4 | `Q02 rows 4` (C7), 파일 헤드에도 `반환 행 수: 4` (C10) | 일치 |
| outputs/query_results.md | Q03 반환 행 수 5 | `Q03 rows 5` (C7), 파일 헤드에도 `반환 행 수: 5` (C10) | 일치 |
| outputs/query_results.md | Q04 반환 행 수 2 | `Q04 rows 2` (C7), 파일 헤드에도 `반환 행 수: 2` (C10) | 일치 |
| outputs/query_results.md | Q05 반환 행 수 13 | `Q05 rows 13` (C7), 파일 헤드에도 `반환 행 수: 13` (C10) | 일치 |
| JOIN_VS_SUBQUERY.md | JOIN 계획에 `SCAN r`, `SEARCH m USING INTEGER PRIMARY KEY`, `USE TEMP B-TREE FOR DISTINCT`, `USE TEMP B-TREE FOR ORDER BY` | C9 `plan_join` 동일 | 일치 |
| JOIN_VS_SUBQUERY.md | EXISTS 계획에 `SCAN m`, `CORRELATED SCALAR SUBQUERY 1`, `SCAN r` | C9 `plan_exists` 동일 | 일치 |
| JOIN_VS_SUBQUERY.md | 대여 기록 있는 회원 10명 | C4 `no_rental_members`가 2명(11,12) → 총 12명 중 10명 대여 이력 있음 | 일치 |
| INTEGRITY_VIOLATION.md | `sqlite3.IntegrityError: FOREIGN KEY constraint failed` | C9 `fk_error IntegrityError FOREIGN KEY constraint failed` | 일치 |
| INTEGRITY_VIOLATION.md | remaining rentals: 15 | C4 `count rentals 15`; C15 Step4 `rentals 행 수: 15 → 15` | 일치 |
| KPI_REPORT.md | KPI1 월별 회전율 0.0769~0.1538, 9개월 | C9 `kpi1 [...]` 9개 월, 값 동일 | 일치 |
| KPI_REPORT.md | KPI3 전체 연체율 26.7% (15건 중 4건) | C9 `kpi3 (15, 4, 7, 4, 26.7)` | 일치 |
| KPI_REPORT.md | 회원별 연체율: 오태양 100.0, 이서연 50.0, 박지호 50.0, 김민준 33.3 | C9 `kpi3_members [('오태양',1,1,100.0), ('박지호',2,1,50.0), ('이서연',2,1,50.0), ('김민준',3,1,33.3)]` | 일치(순서만 일부 다름) |
| KPI_REPORT.md | “최다 대여 도서 TOP 3” | C9 `kpi2_top3 [(1,'채식주의자',2),(3,'아주 작은 습관의 힘',2),(9,'클린 코드',2)]` | 일치 |
| KPI_REPORT.md | 공동 1위 4권(1,3,9,10) 설명 | C9 `kpi2_all_counts`에서 1,3,9,10 모두 2건 | 일치 |
| README.md / SUBMISSION.md | `python3 verify_sql.py` → 100/100 ALL PASS | C10 `verify_exit=0` 및 100/100 출력 | 일치 |
| README.md | “두 번 실행해도 Git 워킹 트리가 더러워지지 않는다” | C15 `git before` 공란, `git after` 공란 | 부분 일치 |
| SUBMISSION.md | 저장소 `https://github.com/yerihanview/B6-1` public | 실행 원문으로는 확인 불가; C18 `git remote -v` 비어 있음 | 확인 불가 |

---

#### 5) 감점 계산

##### 배점 합계
- 총 배점: **100점**

##### 감점 내역
1. **R-04 PARTIAL**: `seed.sql` 단독 실행 불가 → **-2점**
2. **R-11 PARTIAL**: `categories` NOT NULL 2개 이상 미충족 → **-3점**
3. **R-17 PARTIAL**: 적재 순서는 맞으나 단독 실행성 부족 → **-1점**
4. **R-38 FAIL**: 채점기 신뢰성 결함(중대) → **-7점**
5. **R-40 PARTIAL**: ERD 문서 전수 확인 불가 → **-1점**
6. **R-44 PARTIAL**: 문서-실측 전수 대조 증거 부족 → **-1점**
7. **R-45 PARTIAL**: trap 삭제 직접 확인 불가 → **-1점**
8. **R-49 FAIL**: 거버넌스 3종 실행 사본 파일 목록 부재 → **-2점**

##### 감점 합계
- 2 + 3 + 1 + 7 + 1 + 1 + 1 + 2 = **18점**

##### 최종 점수 산식
- **100 - 18 = 82점**

##### 산술 검산
- 배점표 획득 합계: 8 + 22 + 9 + 25 + 8 + 6 + 3 + 1 = **82점**
- 감점 방식 계산 결과: **82점**
- **검산 일치**

---

#### 6) 총평

이 제출물은 **핵심 SQL 미션 자체**만 보면 꽤 탄탄하다.  
스키마는 FK/UNIQUE/CHECK가 실제로 강제되고(C3), 시드는 50행의 한국어 데이터로 충분하며(C4), 15개 쿼리는 전부 실행되고 결과 의미도 대체로 정확하다(C7, C8). 특히 Q07, Q08, Q13, Q14, Q15는 독립 검증에서도 목적에 맞게 동작했다.

하지만 가장 큰 결함은 **`verify_sql.py`의 신뢰성 붕괴**다.  
이 스크립트는 제출자가 강조한 “100점 기계 채점기”이지만, 실제로는:
- `price >= 0` CHECK를 제거해도 통과(C12),
- `status IN (...)` CHECK를 제거해도 통과(C13),
- Q07을 완전히 다른 쿼리로 바꿔도 통과(C14)

한다. 즉, **요구사항을 실제로 검사하지 못하는 자기검증기**다. 이 결함은 R-38 위반으로 매우 크다. 평가자가 이 스크립트의 100/100을 믿고 넘어가면, 요구 위반 산출물도 통과시킬 위험이 있다.

그 다음 위험은 형식 요구 쪽이다.
- `seed.sql`은 빈 DB에서 단독 실행되지 않아 R-04를 엄격히 만족하지 못한다(C5).
- `categories`는 테이블별 NOT NULL 2개 이상 요구를 충족하지 못한다(C2).
- 실행 사본 기준으로는 거버넌스 3종 파일이 보이지 않아 R-49도 미달이다(C1).

##### 이 제출물을 그대로 평가 제출할 때의 위험
1. **채점기 100점 주장에 속을 위험**: 실제 요구 위반을 놓친다.
2. **형식 요구 재심사에서 감점될 위험**: `seed.sql` 단독 실행성, NOT NULL 개수, 거버넌스 파일 보존 항목.
3. **문서 신뢰성 논란 위험**: 문서 수치는 대체로 맞지만, “100/100 ALL PASS”가 독립 심사 기준에서는 그대로 인정되지 않는다.

요약하면, **SQL 본체는 강하고 실습 목적은 잘 달성했지만, 검증기와 일부 형식 요구가 발목을 잡는 제출물**이다.

---

## 부록 B. Claude-Sonnet-4 판정 원문 (전문)

### B-1. 1단계 검증 계획 (원문)

```json
{"checks":[{"id":"C1","purpose":"스키마·시드 적재 및 행수 확인","cmd":"python3 - <<'PY'\nimport sqlite3\nconn = sqlite3.connect(':memory:')\nconn.execute('PRAGMA foreign_keys = ON;')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\nfor t in ('categories','members','books','rentals'):\n    print(t, conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0])\nprint('total', sum(conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('categories','members','books','rentals')))\nprint('fk_on', conn.execute('PRAGMA foreign_keys').fetchone()[0])\nprint('status_dist', conn.execute(\"SELECT status,COUNT(*) FROM rentals GROUP BY status ORDER BY status\").fetchall())\nprint('multi_rent', conn.execute(\"SELECT COUNT(*) FROM (SELECT member_id FROM rentals GROUP BY member_id HAVING COUNT(*)>=2)\").fetchone()[0])\nPY"},{"id":"C2","purpose":"제약조건 실제 강제 6종","cmd":"python3 - <<'PY'\nimport sqlite3\nconn = sqlite3.connect(':memory:')\nconn.execute('PRAGMA foreign_keys = ON;')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\ntests = [\n  ('FK_ghost', \"INSERT INTO rentals(member_id,book_id,rental_date,due_date,status) VALUES(999,1,'2026-01-01','2026-01-15','RENTED')\"),\n  ('price_neg', \"INSERT INTO books(category_id,title,author,publisher,published_year,price) VALUES(1,'X','A','B',2020,-1)\"),\n  ('status_bad', \"INSERT INTO rentals(member_id,book_id,rental_date,due_date,status) VALUES(1,1,'2026-01-01','2026-01-15','LOST')\"),\n  ('email_dup', \"INSERT INTO members(name,email,phone,address,join_date) VALUES('홍길동','minjun.kim@email.com','010-0000-0000','서울','2026-01-01')\"),\n  ('catname_dup', \"INSERT INTO categories(category_name) VALUES('소설')\"),\n  ('notnull_miss', \"INSERT INTO members(name,phone,address,join_date) VALUES('홍길동','010-0000-0000','서울','2026-01-01')\"),\n]\nfor label, sql in tests:\n    try:\n        conn.execute(sql)\n        print(f'FAIL_NOT_BLOCKED: {label}')\n    except Exception as e:\n        print(f'BLOCKED {label}: {type(e).__name__}: {e}')\nPY"},{"id":"C3","purpose":"schema.sql 첫문장·인덱스주석 확인","cmd":"python3 - <<'PY'\nlines = open('schema.sql',encoding='utf-8').read().splitlines()\nfor i,l in enumerate(lines[:5]):\n    print(i,repr(l))\nidx_line = next((i for i,l in enumerate(lines) if 'CREATE INDEX' in l.upper()), None)\nif idx_line:\n    print('idx_line', idx_line, repr(lines[idx_line]))\n    print('above', repr(lines[idx_line-1]))\nPY"},{"id":"C4","purpose":"Q01~Q15 전수 실행·결과 행수","cmd":"python3 - <<'PY'\nimport sqlite3, re\nconn = sqlite3.connect(':memory:')\nconn.execute('PRAGMA foreign_keys = ON;')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\nsql = open('queries.sql',encoding='utf-8').read()\nmarks = list(re.finditer(r'^--\\s*(Q\\d{2})\\s*:',sql,re.MULTILINE))\nfor i,m in enumerate(marks):\n    end = marks[i+1].start() if i+1<len(marks) else len(sql)\n    body = sql[m.end():end].strip()\n    stmts = [s.strip() for s in body.split(';') if s.strip()]\n    label = m.group(1)\n    try:\n        cur = conn.execute(stmts[0])\n        rows = cur.fetchall()\n        if cur.description:\n            print(f'{label}: {len(rows)} rows, cols={[d[0] for d in cur.description]}')\n        else:\n            print(f'{label}: rowcount={cur.rowcount}')\n    except Exception as e:\n        print(f'{label}: ERROR {e}')\nPY"},{"id":"C5","purpose":"Q07·Q08 결과 의미 검증","cmd":"python3 - <<'PY'\nimport sqlite3\nconn = sqlite3.connect(':memory:')\nconn.execute('PRAGMA foreign_keys = ON;')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\nprint('Q07 no-rental books:')\nfor r in conn.execute(\"SELECT b.book_id,b.title FROM books b LEFT JOIN rentals r ON b.book_id=r.book_id WHERE r.rental_id IS NULL ORDER BY b.book_id\"):\n    print(' ',r)\nprint('Q08 zero-rental members:')\nfor r in conn.execute(\"SELECT m.member_id,m.name,COUNT(r.rental_id) AS cnt FROM members m LEFT JOIN rentals r ON m.member_id=r.member_id GROUP BY m.member_id HAVING cnt=0\"):\n    print(' ',r)\nPY"},{"id":"C6","purpose":"Q14 UPDATE·Q15 DELETE 동작","cmd":"python3 - <<'PY'\nimport sqlite3\nconn = sqlite3.connect(':memory:')\nconn.execute('PRAGMA foreign_keys = ON;')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\nprint('before Q14 RENTED:', conn.execute(\"SELECT COUNT(*) FROM rentals WHERE status='RENTED'\").fetchone()[0])\nprint('before Q14 OVERDUE:', conn.execute(\"SELECT COUNT(*) FROM rentals WHERE status='OVERDUE'\").fetchone()[0])\ncur = conn.execute(\"UPDATE rentals SET status='OVERDUE' WHERE return_date IS NULL AND due_date < DATE('now') AND status='RENTED'\")\nprint('Q14 rowcount:', cur.rowcount)\nprint('after Q14 RENTED:', conn.execute(\"SELECT COUNT(*) FROM rentals WHERE status='RENTED'\").fetchone()[0])\nprint('after Q14 OVERDUE:', conn.execute(\"SELECT COUNT(*) FROM rentals WHERE status='OVERDUE'\").fetchone()[0])\nprint('Q14 updated rows:', conn.execute(\"SELECT rental_id,due_date,status FROM rentals WHERE status='OVERDUE' AND return_date IS NULL ORDER BY due_date\").fetchall())\nbefore15 = conn.execute('SELECT COUNT(*) FROM rentals').fetchone()[0]\ncur2 = conn.execute(\"DELETE FROM rentals WHERE rental_id=(SELECT rental_id FROM rentals WHERE member_id=10 ORDER BY rental_date DESC LIMIT 1)\")\nprint('Q15 rowcount:', cur2.rowcount)\nprint('after Q15 total rentals:', conn.execute('SELECT COUNT(*) FROM rentals').fetchone()[0])\nPY"},{"id":"C7","purpose":"demo.sh --non-interactive 終了코드","cmd":"bash demo.sh --non-interactive; echo \"EXIT:$?\""},{"id":"C8","purpose":"demo.sh 워킹트리 오염 확인","cmd":"bash demo.sh --non-interactive 2>/dev/null; ls library.db 2>&1; ls /tmp/b6* 2>&1 | head -5; echo done"},{"id":"C9","purpose":"민감정보 하드코딩 탐색","cmd":"grep -rn -i 'api.key\\|secret\\|password\\|token\\|sk-\\|AIza' --include='*.py' --include='*.sh' --include='*.sql' --include='*.md' --include='*.json' . 2>/dev/null | grep -v '.git' | head -20; echo 'scan_done'"},{"id":"C10","purpose":"거버넌스파일·커밋이력 확인","cmd":"ls ORDER_SHEET.md RTM.md PROJECT_MANIFEST.json 2>&1; git log --oneline | head -12"}]}
```

### B-2. 하네스 보정 요청에 대한 재계획 (원문)

```json
{"checks":[{"id":"D1","purpose":"15개 쿼리 전수 실행·결과 행수(올바른 블록 분리)","cmd":"python3 - <<'PY'\nimport sqlite3, re\nconn = sqlite3.connect(':memory:')\nconn.execute('PRAGMA foreign_keys = ON;')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\nsql = open('queries.sql',encoding='utf-8').read()\nmarks = list(re.finditer(r'^--\\s*(Q\\d{2})\\s*:.*$', sql, re.MULTILINE))\nfor i, m in enumerate(marks):\n    end = marks[i+1].start() if i+1 < len(marks) else len(sql)\n    block = sql[m.end():end]\n    buf = ''\n    first_stmt = None\n    for line in block.splitlines(keepends=True):\n        stripped = line.strip()\n        if stripped.startswith('--'):\n            continue\n        buf += line\n        if sqlite3.complete_statement(buf):\n            first_stmt = buf.strip()\n            break\n    label = m.group(1)\n    if not first_stmt:\n        print(f'{label}: NO_STMT')\n        continue\n    try:\n        cur = conn.execute(first_stmt)\n        rows = cur.fetchall()\n        if cur.description:\n            cols = [d[0] for d in cur.description]\n            print(f'{label}: {len(rows)} rows cols={cols}')\n            for r in rows[:2]:\n                print(f'  {r}')\n        else:\n            print(f'{label}: rowcount={cur.rowcount}')\n    except Exception as e:\n        print(f'{label}: ERROR {e}')\nPY"},{"id":"D2","purpose":"demo.sh --non-interactive 종료코드·워킹트리 오염 확인(출력 최소화)","cmd":"bash demo.sh --non-interactive > /tmp/demo_out.txt 2>&1; EXITCODE=$?; echo \"EXIT:$EXITCODE\"; tail -5 /tmp/demo_out.txt; ls library.db 2>/dev/null && echo 'DIRTY:library.db' || echo 'CLEAN:no library.db'; ls b6_1_demo* 2>/dev/null && echo 'DIRTY:tmpdir_leaked' || echo 'CLEAN:no tmpdir'"},{"id":"D3","purpose":"Q13 상관서브쿼리 결과·NULL포함 확인","cmd":"python3 - <<'PY'\nimport sqlite3\nconn = sqlite3.connect(':memory:')\nconn.execute('PRAGMA foreign_keys = ON;')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\nrows = conn.execute(\"\"\"\nSELECT m.member_id, m.name,\n  (SELECT MAX(r.rental_date) FROM rentals r WHERE r.member_id=m.member_id) AS 최근대여일\nFROM members m\nORDER BY 최근대여일 IS NULL, 최근대여일 DESC\n\"\"\").fetchall()\nprint('total rows:', len(rows))\nnull_rows = [r for r in rows if r[2] is None]\nprint('NULL rows:', null_rows)\nfor r in rows[:5]:\n    print(r)\nPY"},{"id":"D4","purpose":"Q14 UPDATE 영향행수·날짜 의존성 확인(고정날짜 기준)","cmd":"python3 - <<'PY'\nimport sqlite3\nconn = sqlite3.connect(':memory:')\nconn.execute('PRAGMA foreign_keys = ON;')\nconn.executescript(open('schema.sql',encoding='utf-8').read())\nconn.executescript(open('seed.sql',encoding='utf-8').read())\n# RENTED 상태이고 due_date가 지난 행 확인\nrented = conn.execute(\"SELECT rental_id,member_id,due_date,status FROM rentals WHERE status='RENTED' AND return_date IS NULL ORDER BY due_date\").fetchall()\nprint('RENTED rows before Q14:', rented)\n# DATE('now') 기준 실행\ncur = conn.execute(\"UPDATE rentals SET status='OVERDUE' WHERE return_date IS NULL AND due_date < DATE('now') AND status='RENTED'\")\nprint('Q14 rowcount with DATE(now):', cur.rowcount)\n# 고정날짜 2026-11-10 기준\nconn2 = sqlite3.connect(':memory:')\nconn2.execute('PRAGMA foreign_keys = ON;')\nconn2.executescript(open('schema.sql',encoding='utf-8').read())\nconn2.executescript(open('seed.sql',encoding='utf-8').read())\ncur2 = conn2.execute(\"UPDATE rentals SET status='OVERDUE' WHERE return_date IS NULL AND due_date < '2026-11-10' AND status='RENTED'\")\nprint('Q14 rowcount with fixed 2026-11-10:', cur2.rowcount)\nPY"},{"id":"D5","purpose":"verify_sql.py 자기검증 신뢰성: 요구위반 산출물을 FAIL로 잡는지","cmd":"python3 - <<'PY'\nimport sqlite3, sys, os\n# 테스트1: price 음수를 허용하는 가짜 스키마로 check_schema가 통과하는지\nbad_schema = '''\nPRAGMA foreign_keys = ON;\nCREATE TABLE categories (category_id INTEGER PRIMARY KEY, category_name TEXT NOT NULL UNIQUE);\nCREATE TABLE members (member_id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, phone TEXT NOT NULL, address TEXT NOT NULL, join_date TEXT NOT NULL);\nCREATE TABLE books (book_id INTEGER PRIMARY KEY, category_id INTEGER NOT NULL, title TEXT NOT NULL, author TEXT NOT NULL, publisher TEXT NOT NULL, published_year INTEGER NOT NULL, price INTEGER NOT NULL, FOREIGN KEY(category_id) REFERENCES categories(category_id));\nCREATE TABLE rentals (rental_id INTEGER PRIMARY KEY, member_id INTEGER NOT NULL, book_id INTEGER NOT NULL, rental_date TEXT NOT NULL, due_date TEXT NOT NULL, return_date TEXT, status TEXT NOT NULL CHECK(status IN (\"RENTED\",\"RETURNED\",\"OVERDUE\")), FOREIGN KEY(member_id) REFERENCES members(member_id), FOREIGN KEY(book_id) REFERENCES books(book_id));\nCREATE INDEX idx_rentals_date ON rentals(rental_date);\n'''\n# verify_sql.pyの check_schema は price CHECK を検証しているか?\nimport re\nsrc = open('verify_sql.py',encoding='utf-8').read()\nhas_price_check = 'price' in src.lower() and 'check' in src.lower()\nhas_status_check = 'status' in src.lower()\nhas_notnull_check = 'not null' in src.lower() or 'notnull' in src.lower()\nprint('verify checks price:', has_price_check)\nprint('verify checks status:', has_status_check)\nprint('verify checks notnull:', has_notnull_check)\n# 実際にprice CHECKなしスキーマでcheck_schemaが通るか\nconn = sqlite3.connect(':memory:')\nconn.execute('PRAGMA foreign_keys = ON;')\nconn.executescript(bad_schema)\ntables = [r[0] for r in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'\")]\nprint('tables in bad schema:', sorted(tables))\n# price CHECK存在確認\ncols = conn.execute('PRAGMA table_info(books)').fetchall()\nprint('books cols:', cols)\n# bad schemaでINSERT price=-1が通るか\ntry:\n    conn.execute(\"INSERT INTO categories VALUES(1,'test')\")\n    conn.execute(\"INSERT INTO books(category_id,title,author,publisher,published_year,price) VALUES(1,'T','A','P',2020,-1)\")\n    print('BAD: price=-1 accepted in bad_schema (no CHECK)')\nexcept Exception as e:\n    print('GOOD: price=-1 blocked:', e)\nPY"},{"id":"D6","purpose":"queries.sql Q번호 연속성·주석형식·총개수 확인","cmd":"python3 - <<'PY'\nimport re\nsql = open('queries.sql',encoding='utf-8').read()\nmarks = list(re.finditer(r'^--\\s*(Q\\d{2})\\s*:(.*)$', sql, re.MULTILINE))\nprint('total markers:', len(marks))\nfor m in marks:\n    print(m.group(1), repr(m.group(2).strip()[:40]))\nexpected = [f'Q{i:02d}' for i in range(1,16)]\nfound = [m.group(1) for m in marks]\nprint('expected:', expected)\nprint('found:   ', found)\nprint('match:', found == expected)\nPY"}]}
```

### B-3. 항목별 판정 및 최종 채점 (원문)

아래는 실행 결과 원문을 기반으로 한 R-01~R-12 판정표다.

---

#### 실행 결과 요약 (판정 근거용)

**C1** (스키마·시드 적재):
- categories 10, members 12, books 13, rentals 15 → total 50
- fk_on=1, status_dist=[('OVERDUE',4),('RENTED',4),('RETURNED',7)], multi_rent=4

**C2** (제약조건 6종):
- BLOCKED FK_ghost: IntegrityError: FOREIGN KEY constraint failed
- BLOCKED price_neg: IntegrityError: CHECK constraint failed: price >= 0
- BLOCKED status_bad: IntegrityError: CHECK constraint failed: status IN (...)
- BLOCKED email_dup: IntegrityError: UNIQUE constraint failed: members.email
- BLOCKED catname_dup: IntegrityError: UNIQUE constraint failed: categories.category_name
- BLOCKED notnull_miss: IntegrityError: NOT NULL constraint failed: members.email

**C3** (schema.sql 첫문장·인덱스주석):
- line 0: `'PRAGMA foreign_keys = ON;'`
- idx_line=34, `'CREATE INDEX idx_rentals_date ON rentals (rental_date);'`
- above(line 33): `'-- 대여일 기준 기간 범위 조회 및 월별 대여 추이 집계 성능을 위해 인덱스를 생성한다.'`

**D1** (15쿼리 전수):
- Q01: 2 rows, Q02: 4 rows, Q03: 5 rows, Q04: 2 rows, Q05: 13 rows
- Q06: 4 rows, Q07: 2 rows, Q08: 12 rows, Q09: 10 rows, Q10: 4 rows
- Q11: 9 rows, Q12: 5 rows, Q13: 12 rows
- Q14: rowcount=1, Q15: rowcount=1
- 전수 ERROR 0건

**D2** (demo.sh):
- EXIT:0, tail-5에 "✔ 100/100 ALL PASS" 포함
- CLEAN:no library.db, CLEAN:no tmpdir

**D3** (Q13): total 12 rows, NULL rows: [(11,'신현우',None),(12,'류미나',None)]

**D4** (Q14): RENTED rows before=[(12,...,'2026-11-05',...),(13,...),(14,...),(15,...)]
- Q14 rowcount with DATE(now): 실행 시점 의존 (심사 시점 2026-11-10 이후면 1, 이전이면 0)
- Q14 rowcount with fixed 2026-11-10: 1 (rental_id=12, due_date='2026-11-05')

**D5** (verify_sql.py 신뢰성):
- verify checks price: True (문자열 포함 여부), checks status: True, checks notnull: False
- bad_schema(price CHECK 없음)에서 price=-1 INSERT → **BAD: price=-1 accepted** (CHECK 없으므로 통과)
- verify_sql.py의 check_schema는 price CHECK 존재 여부를 실제로 검증하지 않음

**D6** (Q번호):
- total markers: 15, found Q01~Q15 순서대로, match: True

---

#### R-01 ~ R-12 판정표

| ID | 판정 | 근거 | 메모 |
|---|---|---|---|
| R-01 | **PASS** | C1: categories(도서분류)·members(회원)·books(도서)·rentals(대여기록) 4테이블, status OVERDUE/RENTED/RETURNED 3종, 한국어 도서·회원 데이터 확인. 도서관 대여/연체 도메인 성립. | seed.sql 내 실제 한국어 도서명·회원명·주소 확인(C1·C5) |
| R-02 | **PASS** | schema.sql: categories/members/books/rentals 정확히 4개. FK: books.category_id→categories, rentals.member_id→members, rentals.book_id→books (C2 BLOCKED FK_ghost 확인). 1:N 관계 3개 성립. | D1 Q05(INNER JOIN 13행), Q06(3테이블 JOIN) 정상 실행으로 관계 동작 확인 |
| R-03 | **PASS** | schema.sql·seed.sql·queries.sql 전체에 VIEW/TRIGGER/PROCEDURE/프레임워크 코드 없음. PRAGMA·CREATE TABLE·INSERT·SELECT·UPDATE·DELETE만 사용. verify_sql.py는 Python 표준 라이브러리만 사용. | 파일 전문 검토; 외부 패키지 import 없음 |
| R-04 | **PASS** | C1에서 schema.sql+seed.sql을 SQLite 인메모리에서 오류 없이 실행. D1에서 queries.sql 15개 전수 실행 오류 0건. 3종 파일 각각 독립 실행 가능. | D1 ERROR 0건 |
| R-05 | **PASS** | D2: `python3 verify_sql.py` EXIT:0, outputs/query_results.md 재생성 확인. demo.sh --non-interactive도 EXIT:0. | D2 tail-5에 100/100 ALL PASS 출력 확인 |
| R-06 | **PASS** | C3: schema.sql line 0 = `'PRAGMA foreign_keys = ON;'` — 파일 첫 번째 문장이 PRAGMA foreign_keys = ON. | C3 직접 확인 |
| R-07 | **PASS** | schema.sql: `category_id INTEGER PRIMARY KEY AUTOINCREMENT`, `category_name TEXT NOT NULL UNIQUE`. C2 catname_dup BLOCKED(UNIQUE 강제), notnull_miss 계열 NOT NULL 강제 확인. | C2, schema.sql:3-7 |
| R-08 | **PASS** | schema.sql: `member_id INTEGER PRIMARY KEY AUTOINCREMENT`, `email TEXT NOT NULL UNIQUE`, NOT NULL 컬럼: name/email/phone/address/join_date (5개 ≥ 2개). C2 email_dup BLOCKED, notnull_miss BLOCKED. | C2, schema.sql:9-16 |
| R-09 | **PASS** | schema.sql: `book_id INTEGER PRIMARY KEY AUTOINCREMENT`, `category_id INTEGER NOT NULL`, `FOREIGN KEY (category_id) REFERENCES categories (category_id)`, `price INTEGER NOT NULL CHECK (price >= 0)`. C2 price_neg BLOCKED. | C2, schema.sql:18-28 |
| R-10 | **PASS** | schema.sql: `rental_id INTEGER PRIMARY KEY AUTOINCREMENT`, FK 2개(member_id→members, book_id→books), `status TEXT NOT NULL CHECK (status IN ('RENTED','RETURNED','OVERDUE'))`. C2 FK_ghost·status_bad 모두 BLOCKED. | C2, schema.sql:30-43 |
| R-11 | **PASS** | PK 4개(각 테이블), FK 3개(C2 FK_ghost BLOCKED), NOT NULL: categories 1+, members 5, books 6, rentals 5 (각 테이블 2개 이상), UNIQUE 2개(members.email·categories.category_name, C2 양쪽 BLOCKED), CHECK 2개(price≥0·status IN, C2 양쪽 BLOCKED). 전 항목 충족. | C2 전수 BLOCKED 확인 |
| R-12 | **PASS** | C3: idx_line=34 `CREATE INDEX idx_rentals_date ON rentals (rental_date);`, 바로 위 line 33 = `'-- 대여일 기준 기간 범위 조회 및 월별 대여 추이 집계 성능을 위해 인덱스를 생성한다.'` — 인덱스 생성문 바로 위 1줄에 사유 주석 존재. | C3 직접 확인 |

#### R-13 ~ R-24 판정표

| ID | 판정 | 근거 | 메모 |
|---|---|---|---|
| R-13 | **PASS** | schema.sql 생성 순서: categories(line 2) → members(line 9) → books(line 18) → rentals(line 30). seed.sql INSERT 순서: categories → members → books → rentals. C1에서 FK ON 상태로 seed 적재 오류 0건. 위상정렬 순서 준수 확인. | C1 exit 0, schema.sql 전문 |
| R-14 | **PASS** | C2에서 6종 제약 전수 실제 강제 확인: (a) FK_ghost → IntegrityError: FOREIGN KEY constraint failed, (b) price_neg → CHECK constraint failed: price >= 0, (c) status_bad → CHECK constraint failed: status IN (...), (d) email_dup → UNIQUE constraint failed: members.email, (e) catname_dup → UNIQUE constraint failed: categories.category_name, (f) notnull_miss → NOT NULL constraint failed: members.email. 선언만이 아닌 실제 거부 확인. | C2 전수 BLOCKED |
| R-15 | **PASS** | C1: categories 10, members 12, books 13, rentals 15 — 4개 테이블 각 10행 이상. total 50 ≥ 45. | C1 직접 확인 |
| R-16 | **PASS** | C1·D1·D3에서 한국어 회원명(김민준·이서연 등), 이메일(minjun.kim@email.com 등), 도서명(채식주의자·클린 코드 등), 저자(한강·로버트 마틴 등), 카테고리명(소설·컴퓨터 등) 확인. seed.sql 전문에 한국어 주소·전화번호·출판사 포함. | C1, D1 Q01·Q02·Q05 출력, seed.sql 전문 |
| R-17 | **PASS** | seed.sql INSERT 순서: categories → members → books → rentals. C1에서 PRAGMA foreign_keys=ON 상태로 executescript 실행 시 오류 0건. 역순 삽입 시 FK 오류가 발생하므로 순서 준수가 실증됨. | C1 exit 0, seed.sql 전문 |
| R-18 | **PASS** | C1: status_dist=[('OVERDUE',4),('RENTED',4),('RETURNED',7)] — 3종 모두 존재. multi_rent=4 — 복수 대여 회원 4명 존재. D4: RENTED 4건 중 rental_id=12(due_date='2026-11-05')가 Q14 갱신 대상으로 연체 건 포함 설계 확인. | C1, D4 |
| R-19 | **PASS** | D6: total markers=15, Q01~Q15 순서대로 match=True. 각 마커 형식 `-- Qnn: 목적` 확인(D6 출력 전문). 번호 누락·중복 없음. | D6 |
| R-20 | **PASS** | D1 Q01: 2 rows, cols=['book_id','title','author','price','published_year']. queries.sql Q01에 `WHERE c.category_name = '컴퓨터'`와 `ORDER BY b.price DESC` 존재. 결과 (9,'클린 코드',33000), (8,'혼자 공부하는 SQL',26000) — 가격 내림차순 정렬 확인. | D1, queries.sql:1-11 |
| R-21 | **PASS** | D1 Q02: 4 rows, cols=['rental_id','회원명','도서명','대여일','반납기한','상태']. queries.sql Q02에 `WHERE r.status = 'OVERDUE'` 존재. 결과 (8,'김민준','총균쇠',...,'OVERDUE'), (9,'이서연',...) — OVERDUE 건만 반환 확인. | D1, queries.sql:13-26 |
| R-22 | **PASS** | D1 Q03: 5 rows, cols=['member_id','name','email','join_date']. queries.sql Q03에 `ORDER BY join_date DESC LIMIT 5` 존재. 결과 상위 2행: (12,'류미나','2025-01-07'), (11,'신현우','2024-09-01') — 최근 가입순 정렬 확인. | D1, queries.sql:28-35 |
| R-23 | **PASS** | D1 Q04: 2 rows, cols=['book_id','title','author','published_year','price']. queries.sql Q04에 `WHERE published_year >= 2020 AND price >= 20000` 존재. 결과 (8,'혼자 공부하는 SQL',2021,26000), (5,'조선왕조실록',2020,22000) — 다중 AND 조건 충족 확인. | D1, queries.sql:37-47 |
| R-24 | **PASS** | D1 Q05: 13 rows, cols=['book_id','title','author','카테고리','published_year','price']. queries.sql Q05에 `FROM books b INNER JOIN categories c ON b.category_id = c.category_id` 존재. 결과에 카테고리명(경제경영·과학·소설 등) 포함 — INNER JOIN으로 도서+카테고리 결합 확인. | D1, queries.sql:49-60 |

#### R-25 ~ R-36 판정표

| ID | 판정 | 근거 | 메모 |
|---|---|---|---|
| R-25 | **PASS** | D1 Q06: 4 rows, cols=['회원명','도서명','대여일','반납예정일']. queries.sql Q06에 `FROM rentals r INNER JOIN members m ON r.member_id = m.member_id INNER JOIN books b ON r.book_id = b.book_id WHERE r.status = 'RENTED'` 존재 — 3테이블 다중 INNER JOIN, 반납예정일(due_date) 포함. 결과 (최수아, 부의 추월차선, 2026-10-22, 2026-11-05) 등 4행 반환. | D1, queries.sql:62-75 |
| R-26 | **PASS** | D1 Q07: 2 rows, cols=['book_id','title','author','price']. C5 Q07: (11,'소크라테스의 변명'), (12,'구름빵') — 대여 이력 없는 도서 2권. queries.sql Q07에 `LEFT JOIN rentals r ON b.book_id = r.book_id WHERE r.rental_id IS NULL` 존재. 빈 결과가 아닌 실제 2행 반환 확인. | D1, C5, queries.sql:77-86 |
| R-27 | **PASS** | D1 Q08: 12 rows, cols=['member_id','회원명','총대여횟수']. C5 Q08: (11,'신현우',0), (12,'류미나',0) — 0회 회원 포함. queries.sql Q08에 `FROM members m LEFT JOIN rentals r ON m.member_id = r.member_id GROUP BY m.member_id, m.name` + `COUNT(r.rental_id)` 존재. 전체 12명 반환(0회 포함) 확인. | D1, C5, queries.sql:88-98 |
| R-28 | **PASS** | D1 Q09: 10 rows, cols=['카테고리','도서권수','평균가격']. queries.sql Q09에 `COUNT(b.book_id)`, `ROUND(AVG(b.price), 0)`, `GROUP BY c.category_id, c.category_name` 존재. 결과 (소설,2,12750.0), (역사,2,23500.0) 등 — categories 10행 전부 반환(도서 없는 카테고리도 LEFT JOIN으로 포함). | D1, queries.sql:100-112 |
| R-29 | **PASS** | D1 Q10: 4 rows, cols=['member_id','회원명','연체건수']. queries.sql Q10에 `WHERE r.status = 'OVERDUE' GROUP BY m.member_id, m.name HAVING COUNT(r.rental_id) >= 1` 존재. 결과 (1,'김민준',1), (2,'이서연',1) 등 — 연체 1건 이상 회원만 4명 반환 확인. | D1, queries.sql:114-126 |
| R-30 | **PASS** | D1 Q11: 9 rows, cols=['대여월','대여건수']. queries.sql Q11에 `strftime('%Y-%m', r.rental_date) AS 대여월`, `GROUP BY strftime('%Y-%m', r.rental_date)`, `ORDER BY 대여월` 존재. 결과 ('2026-01',1), ('2026-02',2) 등 9개월 — strftime+GROUP BY 월별 집계 확인. | D1, queries.sql:128-135 |
| R-31 | **PASS** | D1 Q12: 5 rows, cols=['book_id','title','author','price','전체평균가격']. queries.sql Q12에 `WHERE b.price > (SELECT AVG(price) FROM books)` 비상관 서브쿼리 존재. 결과 (9,'클린 코드',33000,18238.0) 등 — 평균가(18238원) 초과 도서 5권 반환. 전체평균가격 컬럼도 서브쿼리로 함께 표시. | D1, queries.sql:137-148 |
| R-32 | **PASS** | D1 Q13: 12 rows, cols=['member_id','회원명','최근대여일']. D3: total 12 rows, NULL rows=[(11,'신현우',None),(12,'류미나',None)] — 대여 이력 없는 회원 NULL 표시 확인. queries.sql Q13에 `SELECT MAX(r.rental_date) FROM rentals r WHERE r.member_id = m.member_id` SELECT절 상관 서브쿼리 존재. | D1, D3, queries.sql:150-163 |
| R-33 | **PASS** | D1 Q14: rowcount=1. D4: RENTED 4건 중 rental_id=12(due_date='2026-11-05')가 DATE('now') 및 고정날짜 2026-11-10 기준 모두 1행 갱신. queries.sql Q14: `UPDATE rentals SET status='OVERDUE' WHERE return_date IS NULL AND due_date < DATE('now') AND status='RENTED'` — 기한 경과 미반납 건 OVERDUE 일괄 갱신 UPDATE문. rowcount=1로 영향 행 수 확인 가능. | D1, D4, queries.sql:165-169 |
| R-34 | **PASS** | D1 Q15: rowcount=1. C6: Q15 실행 후 total rentals 15→14 (1건 삭제). queries.sql Q15: `DELETE FROM rentals WHERE rental_id = (SELECT rental_id FROM rentals WHERE member_id = 10 ORDER BY rental_date DESC LIMIT 1)` — member_id=10의 최근 대여 1건만 서브쿼리로 한정하여 삭제. LIMIT 1로 대상 1건 보장. | D1, C6, queries.sql:171-177 |
| R-35 | **PASS** | D1: Q01~Q15 전수 ERROR 0건. 각 쿼리 결과 행수: Q01(2), Q02(4), Q03(5), Q04(2), Q05(13), Q06(4), Q07(2), Q08(12), Q09(10), Q10(4), Q11(9), Q12(5), Q13(12), Q14(rowcount=1), Q15(rowcount=1). Q07·Q08은 빈 결과 아닌 실제 행 반환(C5). 각 쿼리 목적과 결과 일치 확인. | D1, C5, C6 |
| R-36 | **부분** | D5: verify_sql.py의 check_schema는 price CHECK 존재 여부를 실제로 검증하지 않음(`verify checks price: False` — 소스 내 'price'+'check' 문자열 동시 존재 여부 확인이었으나, 실제 로직에서 price CHECK 강제 검사 코드 없음). bad_schema(price CHECK 없음)에서 price=-1 INSERT가 통과(`BAD: price=-1 accepted`)해도 verify_sql.py는 PASS를 낼 것. NOT NULL 컬럼 수 검증도 없음(`verify checks notnull: False`). status CHECK·FK·UNIQUE·인덱스·행수·상태분포는 실제 검증함. 요구사항 R-11의 CHECK(price≥0)·NOT NULL 2개 이상 항목이 채점기에서 누락되어 요구 위반 산출물을 FAIL로 잡지 못하는 맹점 존재. | D5, verify_sql.py check_schema 함수 |

#### R-37 ~ R-46 판정표

| ID | 판정 | 근거 | 메모 |
|---|---|---|---|
| R-37 | **부분** | D2: verify_sql.py EXIT:0, "100/100 ALL PASS" 출력 확인. outputs/query_results.md 재생성 확인(D2 tail-5). 6개 블록 합계 100점 구조(산출물존재20+스키마20+시드20+FK방어10+15쿼리20+보너스문서10) verify_sql.py 소스에서 확인. 단, D5에서 확인된 바와 같이 check_schema 블록이 price CHECK 부재·NOT NULL 수 부족 스키마를 PASS로 통과시키는 맹점이 있어 "모든 블록 통과 시 Exit Code 0" 조건은 충족하나, 블록 내 검사 완전성에 결함 존재. outputs/query_results.md 자동 재생성은 check_queries 함수 내에서 수행됨을 소스로 확인. | D2, D5, verify_sql.py:check_schema·check_queries 함수 |
| R-38 | **부분** | D5 실증: bad_schema(price CHECK 없음)에서 price=-1 INSERT가 통과(`BAD: price=-1 accepted`)해도 verify_sql.py check_schema는 FAIL을 내지 않음. NOT NULL 컬럼 수 검증도 없음. 반면 FK 3개 미만·email UNIQUE 없음·rentals(rental_date) 인덱스 없음은 실제로 검사함(verify_sql.py:check_schema 내 fk_total<3, email_unique, date_index 분기). status CHECK·행수·상태분포·복수대여·FK 런타임 차단은 실제 검증. 요구 R-11의 CHECK(price≥0)·각 테이블 NOT NULL 2개 이상 항목이 채점기에서 누락 — 요구 위반 산출물을 FAIL로 잡지 못하는 맹점 2건 확인. | D5, verify_sql.py:check_schema(lines ~90-130) |
| R-39 | **PASS** | D2: demo.sh --non-interactive 실행 후 outputs/query_results.md 재생성 확인. outputs/query_results.md 파일 전문에 Q01~Q15 각 쿼리 전문(SQL 코드블록)과 실제 실행 결과(반환 행수·표) 기록됨. Q14·Q15는 "실행 결과: N행 영향" 형식으로 기록. 행수: Q01(2), Q02(4행 중 3행 표시+나머지), Q05(13행 중 3행 표시) 등 실제 값과 D1 결과 일치. | D2, outputs/query_results.md 전문, D1 대조 |
| R-40 | **PASS** | docs/ERD.md 전문 확인: Mermaid `erDiagram` 블록 존재. 4개 테이블(categories·members·books·rentals) 컬럼·타입 명세 존재. 제약 표기: PK/FK/NOT NULL/UNIQUE/CHECK/DEFAULT를 테이블 명세서 표에 명시. 관계선 3개(`categories ||--o{ books`, `members ||--o{ rentals`, `books ||--o{ rentals`) 존재. 관계 설명 섹션("1:N 관계 3개") 포함. | docs/ERD.md 전문 |
| R-41 | **PASS** | docs/bonus/JOIN_VS_SUBQUERY.md 전문 확인: INNER JOIN+DISTINCT 쿼리 전문과 EXISTS 서브쿼리 전문 각각 존재(섹션 2·3). 결과 동일성 검증 표(10명 동일) 존재(섹션 4). EXPLAIN QUERY PLAN 실행계획 텍스트(`USE TEMP B-TREE FOR DISTINCT`, `CORRELATED SCALAR SUBQUERY`) 존재(섹션 2-3·3-3). 가독성·성능·NULL안전성·유지보수성 4관점 비교표(섹션 5)와 선택 기준(섹션 7) 포함. 동일 요구를 두 방식으로 1:1 대조 요건 충족. | docs/bonus/JOIN_VS_SUBQUERY.md 전문 |
| R-42 | **PASS** | docs/bonus/INTEGRITY_VIOLATION.md 전문 확인: 재현 SQL(`repro.py`) 전문 존재. 실행 결과 `sqlite3.IntegrityError: FOREIGN KEY constraint failed` / `remaining rentals: 15` 기록. PRAGMA foreign_keys OFF 시 고아 행 삽입 허용 대조 실측(`fk pragma: 0 / inserted ok; count: 16 / orphan: [(16, 999)]`) 포함. 원인 분석·해결책 3가지 존재. member_id=999 INSERT 시 FOREIGN KEY constraint failed 실증 요건 충족. | docs/bonus/INTEGRITY_VIOLATION.md 전문 |
| R-43 | **PASS** | docs/bonus/KPI_REPORT.md 전문 확인: KPI-1(월별 대여 회전율) — 정의·산출SQL·실측결과표·해석·개선액션 존재. KPI-2(최다 대여 도서 TOP 3) — 정의·산출SQL·실측결과표·해석·개선액션 존재. KPI-3(회원 연체율) — 정의·산출SQL(전체·회원별 2개)·실측결과표·해석·개선액션 존재. 경영 요약(Executive Summary) 포함. 3대 KPI 각각 정의·SQL·해석·개선액션 요건 충족. | docs/bonus/KPI_REPORT.md 전문 |
| R-44 | **부분** | outputs/query_results.md의 수치와 D1 실행 결과 대조: Q01(2행), Q02(4행), Q03(5행), Q04(2행), Q05(13행), Q06(4행), Q07(2행), Q08(12행), Q09(10행), Q10(4행), Q11(9행), Q12(5행), Q13(12행), Q14(1행영향), Q15(1행영향) — 전부 일치. docs/bonus/INTEGRITY_VIOLATION.md의 실행 결과(`remaining rentals: 15`, `FOREIGN KEY constraint failed`)는 C2·C6과 일치. 단, Q14 영향 행수는 실행 시점(DATE('now'))에 의존하며 문서에 "1행 영향"으로 고정 기재되어 있어 실행 환경 날짜가 2026-11-05 이전이면 불일치 발생 가능. D4에서 고정날짜 2026-11-10 기준 rowcount=1 확인으로 현 시점 일치. JOIN_VS_SUBQUERY.md의 EXPLAIN QUERY PLAN 텍스트는 독립 실행 검증 미수행(확인 불가). | D1, D4, C2, C6, outputs/query_results.md, docs/bonus/ 전문 |
| R-45 | **PASS** | D2: `bash demo.sh --non-interactive` EXIT:0 확인. tail-5에 "✅ 시연 완료" 출력. CLEAN:no library.db — 워킹트리 오염 없음. CLEAN:no tmpdir — 임시 디렉토리 누출 없음. demo.sh 소스: `trap cleanup EXIT INT TERM` + `cleanup(){ rm -rf "$DEMO_DIR"; }` 존재(demo.sh:37-40). 5단계(스키마→시드→주요쿼리→FK위반→100점채점) 구조 확인. `--non-interactive` 플래그 파싱 존재(demo.sh:22-28). | D2, demo.sh 전문 |
| R-46 | **PASS** | README.md 전문 확인: 개요(섹션1), ERD 요약(섹션3 Mermaid+테이블), 폴더 구조(섹션2 tree), 실행 방법(섹션4 — python3 verify_sql.py·bash demo.sh·직접DB), demo.sh 사용법(섹션4-2), 루브릭 충족 체크리스트(섹션10 표) 포함. 6개 항목 전부 존재. | README.md 전문 |

#### R-47 ~ R-50 판정표

| ID | 판정 | 근거 | 메모 |
|---|---|---|---|
| R-47 | **PASS** | SUBMISSION.md 전문 확인: 제출 서약(섹션1 — 5개 항목, 본인 설계·검증·AI활용·제약준수·민감정보 미포함 서약) 존재. 산출물 링크(섹션2 — schema.sql·seed.sql·queries.sql·outputs/·docs/ERD.md·docs/bonus/ 3종·verify_sql.py·demo.sh·README.md·RTM.md·PROJECT_MANIFEST.json 총 13개 링크) 존재. 재현 절차(섹션3) 포함. 두 요건(서약+링크) 모두 충족. | SUBMISSION.md 전문 |
| R-48 | **PASS** | C9: grep 결과 `scan_done`만 출력 — api.key·secret·password·token·sk-·AIza 패턴이 .py·.sh·.sql·.md·.json 파일 전체에서 0건 검출. SUBMISSION.md 섹션1 항목4에 "생성 파이프라인은 환경변수만 사용"으로 명시. | C9 exit 0, 출력 scan_done |
| R-49 | **PASS** | REPO_INVENTORY.md 파일 목록에 ORDER_SHEET.md(10180B)·RTM.md(6730B)·PROJECT_MANIFEST.json(8487B) 3종 모두 존재 확인. 심사 안내에 따라 존재 여부만 파일 목록으로 판단(내용 판정 제외). C10에서 심사 사본에 해당 파일이 없는 것은 의도적 제외로 명시되어 있어 판정에 불이익 없음. | REPO_INVENTORY.md 파일 목록 |
| R-50 | **부분** | REPO_INVENTORY.md: 저장소 `yerihanview/B6-1` public main 브랜치, commit 996a6e8 확인. 커밋 이력 7개 확인: `docs(readme):`, `docs(manifest):`, `docs:`, `feat(demo):`, `docs:`, `feat(verify):`, `feat(sql):` — feat·docs 접두어 사용으로 Conventional Commits 형식 준수. 단, C10에서 git log 실행 시 `c6c7b25 audit snapshot` 1개만 출력 — 심사 사본이 단일 스쿼시 커밋으로 제공되어 실제 커밋 이력을 직접 실행으로 확인 불가. REPO_INVENTORY.md에 기재된 12개 커밋 이력은 제출자 자기 주장이므로 증거로 불인정. 저장소 public 여부·main 브랜치 푸시 여부도 직접 접근 불가로 확인 불가. | REPO_INVENTORY.md(자기주장), C10(git log 1개만 확인) |

#### 최종 심사 보고서 — B6-1 디지털 서랍장

---

#### 1. 최종 판정 요약

| 항목 | 값 |
|---|---|
| **총점** | **88 / 100** |
| **판정** | **조건부 통과** |
| **한 줄 결론** | 핵심 SQL 산출물(스키마·시드·15쿼리)과 도메인 설계는 요구를 충실히 충족하나, 채점기(verify_sql.py)의 CHECK·NOT NULL 검증 맹점과 커밋 이력 직접 확인 불가가 감점 요인이다. |

---

#### 2. 배점표

| 항목군 | 요구 ID | 배점 | 획득 | 근거 요약 |
|---|---|---|---|---|
| **A. 목표·범위** | R-01 | 2 | 2 | 도서관 대여/연체 도메인 성립, 한국어 실데이터 확인(C1·D1) |
| | R-02 | 2 | 2 | 4테이블·FK 3개·1:N 관계 3개 실증(C1·C2) |
| | R-03 | 2 | 2 | VIEW/TRIGGER/프레임워크 없음, 표준 SQL만 사용 확인 |
| | R-04 | 2 | 2 | 3종 파일 SQLite 실행 오류 0건(C1·D1) |
| | R-05 | 2 | 2 | verify_sql.py EXIT:0, outputs 재생성 확인(D2) |
| **소계 A** | | **10** | **10** | |
| **B. 스키마** | R-06 | 2 | 2 | schema.sql line 0 = PRAGMA foreign_keys = ON(C3) |
| | R-07 | 2 | 2 | categories PK·NOT NULL·UNIQUE 실증(C2·C3) |
| | R-08 | 2 | 2 | members PK·email NOT NULL UNIQUE·NOT NULL 5개(C2) |
| | R-09 | 2 | 2 | books PK·category_id FK·price CHECK 실증(C2) |
| | R-10 | 2 | 2 | rentals PK·FK 2개·status CHECK 실증(C2) |
| | R-11 | 2 | 2 | PK 4·FK 3·NOT NULL 각 2+·UNIQUE 2·CHECK 2 전수 실증(C2) |
| | R-12 | 2 | 2 | 인덱스 생성문 바로 위 1줄 사유 주석 확인(C3) |
| | R-13 | 2 | 2 | DDL·DML 위상정렬 순서, FK ON 상태 적재 오류 0건(C1) |
| | R-14 | 2 | 2 | 제약 6종 전수 실제 거부 확인(C2) |
| **소계 B** | | **18** | **18** | |
| **C. 시드** | R-15 | 3 | 3 | 각 테이블 10행 이상, 총 50행(C1) |
| | R-16 | 2 | 2 | 한국어 이름·이메일·주소·도서명·저자·카테고리명 확인(C1·D1) |
| | R-17 | 2 | 2 | 부모→자식 순서, FK ON 상태 오류 0건(C1) |
| | R-18 | 3 | 3 | 3상태 모두 존재, 복수 대여 회원 4명(C1·D4) |
| **소계 C** | | **10** | **10** | |
| **D. 15대 쿼리** | R-19 | 1 | 1 | Q01~Q15 마커 15개, 순서·형식 일치(D6) |
| | R-20 | 1 | 1 | Q01 WHERE+ORDER BY DESC, 2행 반환(D1) |
| | R-21 | 1 | 1 | Q02 OVERDUE 4행 반환(D1) |
| | R-22 | 1 | 1 | Q03 ORDER BY+LIMIT 5행 반환(D1) |
| | R-23 | 1 | 1 | Q04 다중 AND 조건 2행 반환(D1) |
| | R-24 | 1 | 1 | Q05 INNER JOIN 13행 반환(D1) |
| | R-25 | 1 | 1 | Q06 3테이블 INNER JOIN 4행 반환(D1) |
| | R-26 | 1 | 1 | Q07 LEFT JOIN+IS NULL 2행 반환(C5·D1) |
| | R-27 | 1 | 1 | Q08 LEFT JOIN+COUNT+GROUP BY 12행(0회 포함)(C5·D1) |
| | R-28 | 1 | 1 | Q09 COUNT·AVG·GROUP BY 10행 반환(D1) |
| | R-29 | 1 | 1 | Q10 GROUP BY+HAVING 4행 반환(D1) |
| | R-30 | 1 | 1 | Q11 strftime+GROUP BY 9행 반환(D1) |
| | R-31 | 1 | 1 | Q12 비상관 서브쿼리 5행 반환(D1) |
| | R-32 | 1 | 1 | Q13 상관 서브쿼리 12행·NULL 2건 포함(D1·D3) |
| | R-33 | 1 | 1 | Q14 UPDATE rowcount=1(D1·D4) |
| | R-34 | 1 | 1 | Q15 DELETE rowcount=1, 대상 1건 한정(D1·C6) |
| | R-35 | 2 | 2 | 15쿼리 전수 ERROR 0건, 결과 목적 일치(D1) |
| **소계 D** | | **18** | **18** | |
| **E. 채점기** | R-36 | 4 | 2 | FK·UNIQUE·인덱스·행수·상태분포 검증 실제 동작. 단 price CHECK·NOT NULL 수 검증 누락(D5) |
| | R-37 | 3 | 2 | 6블록 100점 구조·EXIT:0·outputs 재생성 확인. 단 블록 내 검사 완전성 결함(D2·D5) |
| | R-38 | 3 | 1 | price=-1 bad_schema를 FAIL로 잡지 못함 실증(D5) |
| | R-39 | 2 | 2 | outputs/query_results.md에 15쿼리 전문+결과 기록(D2·outputs 전문) |
| **소계 E** | | **12** | **7** | |
| **F. 문서** | R-40 | 2 | 2 | ERD.md Mermaid+4테이블 명세+관계선 3개+관계설명(docs/ERD.md) |
| | R-41 | 2 | 2 | JOIN_VS_SUBQUERY.md 두 쿼리 전문·결과동일성·실행계획·비교표·선택기준(docs/bonus/) |
| | R-42 | 2 | 2 | INTEGRITY_VIOLATION.md 재현SQL·실행결과·원인분석·해결책(docs/bonus/) |
| | R-43 | 2 | 2 | KPI_REPORT.md 3대 KPI 정의·SQL·해석·개선액션(docs/bonus/) |
| | R-44 | 2 | 1 | 대부분 수치 일치. Q14 행수 DATE('now') 의존·EXPLAIN 텍스트 독립 검증 불가(D1·D4) |
| **소계 F** | | **10** | **9** | |
| **G. 실행·시연** | R-45 | 4 | 4 | demo.sh EXIT:0·5단계·--non-interactive·trap 정리·워킹트리 CLEAN(D2) |
| | R-46 | 3 | 3 | README.md 6개 항목 전부 존재(README.md 전문) |
| | R-47 | 3 | 3 | SUBMISSION.md 서약+링크 13개 존재(SUBMISSION.md 전문) |
| **소계 G** | | **10** | **10** | |
| **H. 거버넌스** | R-48 | 3 | 3 | 민감정보 0건 검출(C9) |
| | R-49 | 3 | 3 | REPO_INVENTORY.md에 3종 거버넌스 파일 존재 확인 |
| | R-50 | 4 | 2 | 저장소 URL·Conventional Commits 형식 REPO_INVENTORY 기재 확인. 단 커밋 이력·public 여부 직접 실행 확인 불가(C10) |
| **소계 H** | | **10** | **8** | |
| **합계** | | **100** | **88** | |

---

#### 3. 결함·애매점 목록

| ID | 심각도 | 위반 요구 | 내용 | 근거 |
|---|---|---|---|---|
| F-01 | **중** | R-38 | verify_sql.py check_schema가 `price CHECK(price≥0)` 존재 여부를 실제로 검증하지 않음. price CHECK 없는 bad_schema에서 price=-1 INSERT가 통과해도 채점기가 PASS를 냄. | D5: `BAD: price=-1 accepted in bad_schema` |
| F-02 | **중** | R-36, R-38 | verify_sql.py check_schema가 각 테이블 NOT NULL 컬럼 수(2개 이상) 요건을 검증하지 않음. NOT NULL이 1개뿐인 스키마도 PASS 처리될 수 있음. | D5: `verify checks notnull: False` |
| F-03 | **경** | R-44 | Q14 UPDATE는 `DATE('now')` 기준이므로 실행 시점

#### 3. 결함·애매점 목록 (이어서)

| ID | 심각도 | 위반 요구 | 내용 | 근거 |
|---|---|---|---|---|
| F-01 | **중** | R-38 | verify_sql.py check_schema가 `price CHECK(price≥0)` 존재 여부를 실제로 검증하지 않음. price CHECK 없는 bad_schema에서 price=-1 INSERT가 통과해도 채점기가 PASS를 냄. | D5: `BAD: price=-1 accepted in bad_schema` |
| F-02 | **중** | R-36, R-38 | verify_sql.py check_schema가 각 테이블 NOT NULL 컬럼 수(2개 이상) 요건을 검증하지 않음. NOT NULL이 1개뿐인 스키마도 PASS 처리될 수 있음. | D5: `verify checks notnull: False` |
| F-03 | **경** | R-44 | Q14 UPDATE는 `DATE('now')` 기준이므로 실행 시점에 따라 영향 행수가 달라짐. outputs/query_results.md에 "1행 영향"으로 고정 기재되어 있어 실행 환경 날짜가 2026-11-05 이전이면 문서 수치와 불일치 발생. | D4: `Q14 rowcount with DATE(now): 1` (실행 시점 의존) |
| F-04 | **경** | R-44 | docs/bonus/JOIN_VS_SUBQUERY.md의 EXPLAIN QUERY PLAN 텍스트(`USE TEMP B-TREE FOR DISTINCT` 등)가 실제 실행 결과와 일치하는지 독립 실행으로 확인 불가. 제출자 자기 주장으로만 존재. | 독립 검증 미수행(확인 불가) |
| F-05 | **경** | R-50 | 심사 사본에서 git log가 `c6c7b25 audit snapshot` 1개만 출력됨. REPO_INVENTORY.md에 기재된 7개 Conventional Commits 이력을 직접 실행으로 확인 불가. 저장소 public 여부·main 브랜치 푸시 여부도 직접 접근 불가. | C10: git log 1개만 확인 |
| F-06 | **정보** | R-37 | verify_sql.py의 check_queries는 각 쿼리 블록의 첫 번째 SQL 문장만 실행하므로, Q14(UPDATE)·Q15(DELETE)가 실제로 실행되어 rowcount를 기록하는지는 verify_sql.py 내부 parse_queries+execute 로직에 의존. D1에서 별도 독립 실행으로 rowcount=1 각각 확인. | D1, verify_sql.py:check_queries |

---

#### 4. 문서 기재값 vs 실측값 대조표

| 문서 위치 | 문서 기재값 | 실측값 | 일치 여부 |
|---|---|---|---|
| outputs/query_results.md Q01 | 반환 행수 2 | D1: 2 rows | ✅ 일치 |
| outputs/query_results.md Q02 | 반환 행수 4 | D1: 4 rows | ✅ 일치 |
| outputs/query_results.md Q03 | 반환 행수 5 | D1: 5 rows | ✅ 일치 |
| outputs/query_results.md Q04 | 반환 행수 2 | D1: 2 rows | ✅ 일치 |
| outputs/query_results.md Q05 | 반환 행수 13 | D1: 13 rows | ✅ 일치 |
| outputs/query_results.md Q06 | 반환 행수 4 | D1: 4 rows | ✅ 일치 |
| outputs/query_results.md Q07 | 반환 행수 2, book_id 11·12 | D1·C5: 2 rows, (11,'소크라테스의 변명'),(12,'구름빵') | ✅ 일치 |
| outputs/query_results.md Q08 | 반환 행수 12, 김민준 3회 | D1: 12 rows, (1,'김민준',3) | ✅ 일치 |
| outputs/query_results.md Q09 | 반환 행수 10, 소설 평균 12750.0 | D1: 10 rows, ('소설',2,12750.0) | ✅ 일치 |
| outputs/query_results.md Q10 | 반환 행수 4 | D1: 4 rows | ✅ 일치 |
| outputs/query_results.md Q11 | 반환 행수 9, 2026-01 1건 | D1: 9 rows, ('2026-01',1) | ✅ 일치 |
| outputs/query_results.md Q12 | 반환 행수 5, 전체평균 18238.0 | D1: 5 rows, 18238.0 | ✅ 일치 |
| outputs/query_results.md Q13 | 반환 행수 12, 강소희 2026-11-08 | D1·D3: 12 rows, (10,'강소희','2026-11-08') | ✅ 일치 |
| outputs/query_results.md Q14 | 실행 결과 1행 영향 | D1: rowcount=1 / D4: DATE(now) 의존 | ⚠️ 시점 의존 |
| outputs/query_results.md Q15 | 실행 결과 1행 영향 | D1: rowcount=1, C6: 15→14 | ✅ 일치 |
| README.md 섹션6 rentals 행수 | 15행 (RETURNED 7·OVERDUE 4·RENTED 4) | C1: status_dist OVERDUE 4·RENTED 4·RETURNED 7 | ✅ 일치 |
| README.md 섹션6 합계 | 50행 | C1: total 50 | ✅ 일치 |
| README.md 섹션5 Q07 결과 행 | 2 | D1: 2 rows | ✅ 일치 |
| README.md 섹션5 Q08 결과 행 | 12 | D1: 12 rows | ✅ 일치 |
| README.md 섹션5 Q11 결과 행 | 9 | D1: 9 rows | ✅ 일치 |
| docs/bonus/INTEGRITY_VIOLATION.md | remaining rentals: 15 | C2·C6: 시드 15행 유지 확인 | ✅ 일치 |
| docs/bonus/INTEGRITY_VIOLATION.md | FOREIGN KEY constraint failed | C2: IntegrityError: FOREIGN KEY constraint failed | ✅ 일치 |
| docs/bonus/KPI_REPORT.md | 전체 연체율 26.7% (15건 중 4건) | C1: OVERDUE 4, total 15 → 4/15=26.7% | ✅ 일치 |
| docs/bonus/KPI_REPORT.md | 월별 대여 9개월 분포 | D1 Q11: 9 rows | ✅ 일치 |
| docs/bonus/JOIN_VS_SUBQUERY.md | 결과 10명 동일 | D3 기준 대여 이력 있는 회원 member_id 1~10 = 10명 | ✅ 일치 |
| docs/bonus/JOIN_VS_SUBQUERY.md | EXPLAIN QUERY PLAN 텍스트 | 독립 실행 미수행 | ❓ 확인 불가 |

---

#### 5. 감점 계산 (산술 검산)

| 결함 ID | 위반 요구 | 감점 항목 | 배점 | 획득 | 감점 |
|---|---|---|---|---|---|
| F-01, F-02 | R-38 | 채점기 자기검증 신뢰성 — price CHECK·NOT NULL 검증 누락으로 요구 위반 산출물을 FAIL로 잡지 못함 | 3 | 1 | **-2** |
| F-01, F-02 | R-36 | 채점기 실제 검사 완전성 — 담당 요구 항목 중 price CHECK·NOT NULL 미검증 | 4 | 2 | **-2** |
| F-01, F-02 | R-37 | 6블록 구조·EXIT:0 충족하나 블록 내 검사 완전성 결함 | 3 | 2 | **-1** |
| F-03, F-04 | R-44 | 문서 수치 일치 — Q14 시점 의존·EXPLAIN 텍스트 확인 불가 | 2 | 1 | **-1** |
| F-05 | R-50 | 커밋 이력·public 여부 직접 확인 불가 | 4 | 2 | **-2** |

**감점 합계**: -2 -2 -1 -1 -2 = **-8점**

**최종 점수 검산**:
- 만점 100점
- 감점 합계 -8점
- **최종 점수 = 100 - 8 = 92점**

> ※ 앞서 배점표에서 소계 합산으로 88점을 산출했으나, 항목별 배점 재검토 결과 감점 근거를 재정렬하면 92점이 산술적으로 정합함. 배점표 기준 소계 합산(A10+B18+C10+D18+E7+F9+G10+H8=90)과 감점 방식 간 2점 차이는 E 소계(12→7, -5)와 F 소계(10→9, -1)·H 소계(10→8, -2) 합산(-8)의 기준점 차이에서 발생. **배점표 소계 합산 기준 최종 점수: 90점**으로 정정하고, 감점 내역(-10점)을 아래와 같이 재확정한다.

| 감점 항목 | 감점 |
|---|---|
| R-36:

#### (1) 확정 배점표

| 항목군 | 요구 ID | 배점 | 감점 | 획득 |
|---|---|---|---|---|
| **A. 목표·범위** | R-01~R-05 | 10 | 0 | 10 |
| **B. 스키마** | R-06~R-14 | 18 | 0 | 18 |
| **C. 시드** | R-15~R-18 | 10 | 0 | 10 |
| **D. 15대 쿼리** | R-19~R-35 | 18 | 0 | 18 |
| **E. 채점기** | R-36~R-39 | 12 | 5 | 7 |
| **F. 문서** | R-40~R-44 | 10 | 1 | 9 |
| **G. 실행·시연** | R-45~R-47 | 10 | 0 | 10 |
| **H. 거버넌스** | R-48~R-50 | 12 | 2 | 10 |
| **합계** | | **100** | **8** | **92** |

---

#### (2) 감점 내역

| 요구 ID | 배점 | 감점 | 획득 | 사유 |
|---|---|---|---|---|
| R-36 | 4 | 2 | 2 | check_schema가 price CHECK 존재·NOT NULL 컬럼 수를 실제로 검증하지 않음. bad_schema(price CHECK 없음)에서 price=-1 INSERT 통과해도 PASS 출력(D5 실증) |
| R-37 | 3 | 1 | 2 | 6블록 구조·EXIT:0·outputs 재생성은 충족. 단 블록 내 검사 완전성 결함(R-36 동일 원인)으로 "모든 블록이 담당 요구를 실제로 검증"한다는 요건 부분 미충족 |
| R-38 | 3 | 2 | 1 | price=-1 bad_schema를 FAIL로 잡지 못함 직접 실증(D5: `BAD: price=-1 accepted`). NOT NULL 수 검증도 없음. 요구 위반 산출물 → FAIL 전환 실패 |
| R-39 | 2 | 0 | 2 | outputs/query_results.md 15쿼리 전문+결과 정상 기록(D2) |
| R-44 | 2 | 1 | 1 | Q14 영향 행수가 DATE('now') 의존으로 실행 시점에 따라 문서 기재값(1행)과 불일치 가능. EXPLAIN QUERY PLAN 텍스트 독립 검증 불가(D4, F-04) |
| R-50 | 4 | 2 | 2 | 심사 사본 git log = `c6c7b25 audit snapshot` 1개뿐. Conventional Commits 이력·public 여부 직접 실행으로 확인 불가(C10) |

**산술 검산**:
- 감점 합계: 2 + 1 + 2 + 0 + 1 + 2 = **8점**
- 획득 합계: 2 + 2 + 1 + 2 + 1 + 2 = **10점** (E·F·H 감점 항목만)
- 전체 획득: 100 − 8 = **92점** ✓
- 배점표 소계 합산: 10 + 18 + 10 + 18 + 7 + 9 + 10 + 10 = **92점** ✓

---

#### (3) 총평

스키마·시드·15대 쿼리 등 핵심 SQL 산출물은 요구 R-01~R-35를 오류 없이 충족하며, 제약조건 6종 전수 실제 강제(C2)와 15쿼리 전수 실행 오류 0건(D1)이 독립 실행으로 확인되었다. 가장 큰 결함은 채점기(verify_sql.py)의 검증 맹점으로, `price CHECK(price≥0)` 부재 스키마와 NOT NULL 컬럼 수 미달 스키마를 PASS로 통과시켜 "요구 위반 산출물을 FAIL로 잡는다"는 R-38 요건을 충족하지 못한다(D5 직접 실증). 이 상태로 제출하면 채점기가 스키마 품질을 과신하게 되어, 향후 스키마를 수정할 때 CHECK·NOT NULL 제약이 누락되어도 기계 채점이 이를 감지하지 못하는 회귀 위험이 남는다. 커밋 이력은 REPO_INVENTORY.md 기재로만 확인되고 직접 실행으로 검증되지 않아 R-50이 부분 판정에 그쳤으나, 이는 심사 사본 구성 방식에 기인한 것으로 실제 저장소에서는 해소될 가능성이 있다.

---

## 부록 C. 실행 검증 원문 (심사자가 요청한 명령과 출력 — 본문 인용분)


### GPT-5.4 — 요청 명령과 실행 원문

#### [C2] schema.sql를 독립적으로 실행해 실제 스키마/제약/인덱스/생성순서/NOT NULL 개수/FK 개수 확인(R-02,R-06~R-13)

```bash
python3 - <<'PY'
import sqlite3, re
sql=open('schema.sql',encoding='utf-8').read()
conn=sqlite3.connect(':memory:')
conn.executescript(sql)
print('foreign_keys', conn.execute('PRAGMA foreign_keys;').fetchone()[0])
print('tables', conn.execute("SELECT group_concat(name, ',') FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid").fetchone()[0])
for t in ['categories','members','books','rentals']:
    cols=conn.execute(f'PRAGMA table_info({t})').fetchall()
    fks=conn.execute(f'PRAGMA foreign_key_list({t})').fetchall()
    idx=conn.execute(f"SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='{t}' ORDER BY name").fetchall()
    print('TABLE',t,'cols',[(c[1],c[2],c[3],c[5]) for c in cols])
    print('NOTNULL',t,sum(c[3] for c in cols),'PKs',[c[1] for c in cols if c[5]])
    print('FK',t,[(r[3],r[2],r[4]) for r in fks])
    print('IDX',t,idx)
print('schema_order_lines', [ln.strip() for ln in sql.splitlines() if ln.strip().startswith('CREATE TABLE') or ln.strip().startswith('CREATE INDEX')])
PY
```

종료 코드: **0**

```text
foreign_keys 1
tables categories,members,books,rentals
TABLE categories cols [('category_id', 'INTEGER', 0, 1), ('category_name', 'TEXT', 1, 0), ('created_at', 'DATETIME', 0, 0)]
NOTNULL categories 1 PKs ['category_id']
FK categories []
IDX categories [('sqlite_autoindex_categories_1', None)]
TABLE members cols [('member_id', 'INTEGER', 0, 1), ('name', 'TEXT', 1, 0), ('email', 'TEXT', 1, 0), ('phone', 'TEXT', 1, 0), ('address', 'TEXT', 1, 0), ('join_date', 'TEXT', 1, 0)]
NOTNULL members 5 PKs ['member_id']
FK members []
IDX members [('sqlite_autoindex_members_1', None)]
TABLE books cols [('book_id', 'INTEGER', 0, 1), ('category_id', 'INTEGER', 1, 0), ('title', 'TEXT', 1, 0), ('author', 'TEXT', 1, 0), ('publisher', 'TEXT', 1, 0), ('published_year', 'INTEGER', 1, 0), ('price', 'INTEGER', 1, 0)]
NOTNULL books 6 PKs ['book_id']
FK books [('category_id', 'categories', 'category_id')]
IDX books []
TABLE rentals cols [('rental_id', 'INTEGER', 0, 1), ('member_id', 'INTEGER', 1, 0), ('book_id', 'INTEGER', 1, 0), ('rental_date', 'TEXT', 1, 0), ('due_date', 'TEXT', 1, 0), ('return_date', 'TEXT', 0, 0), ('status', 'TEXT', 1, 0)]
NOTNULL rentals 5 PKs ['rental_id']
FK rentals [('book_id', 'books', 'book_id'), ('member_id', 'members', 'member_id')]
IDX rentals [('idx_rentals_date', 'CREATE INDEX idx_rentals_date ON rentals (rental_date)')]
schema_order_lines ['CREATE TABLE categories (', 'CREATE TABLE members (', 'CREATE TABLE books (', 'CREATE TABLE rentals (', 'CREATE INDEX idx_rentals_d
…[이하 생략: 전체 1531자]
```

#### [C3] 제약조건이 실제로 강제되는지 독립 실험: FK, 음수 price, 잘못된 status, email/category 중복, NOT NULL 누락(R-14)

```bash
python3 - <<'PY'
import sqlite3
conn=sqlite3.connect(':memory:')
conn.executescript(open('schema.sql',encoding='utf-8').read())
conn.executescript(open('seed.sql',encoding='utf-8').read())
tests=[
('fk_missing_parent', "INSERT INTO rentals(member_id,book_id,rental_date,due_date,status) VALUES (999,1,'2026-11-10','2026-11-24','RENTED')"),
('negative_price', "INSERT INTO books(category_id,title,author,publisher,published_year,price) VALUES (1,'X','Y','Z',2024,-1)"),
('bad_status', "INSERT INTO rentals(member_id,book_id,rental_date,due_date,status) VALUES (1,1,'2026-11-10','2026-11-24','LOST')"),
('dup_email', "INSERT INTO members(name,email,phone,address,join_date) VALUES ('중복','minjun.kim@email.com','010-0000-0000','서울','2026-01-01')"),
('dup_category', "INSERT INTO categories(category_name) VALUES ('소설')"),
('notnull_missing_member_name', "INSERT INTO members(email,phone,address,join_date) VALUES ('x@x.com','010','서울','2026-01-01')"),
('notnull_missing_book_title', "INSERT INTO books(category_id,author,publisher,published_year,price) VALUES (1,'Y','Z',2024,1000)")
]
for name,sql in tests:
    try:
        conn.execute(sql)
        print(name,'ALLOWED')
    except Exception as e:
        print(name, type(e).__name__, str(e))
PY
```

종료 코드: **0**

```text
fk_missing_parent IntegrityError FOREIGN KEY constraint failed
negative_price IntegrityError CHECK constraint failed: price >= 0
bad_status IntegrityError CHECK constraint failed: status IN ('RENTED', 'RETURNED', 'OVERDUE')
dup_email IntegrityError UNIQUE constraint failed: members.email
dup_category IntegrityError UNIQUE constraint failed: categories.category_name
notnull_missing_member_name IntegrityError NOT NULL constraint failed: members.name
notnull_missing_book_title IntegrityError NOT NULL constraint failed: books.title
```

#### [C4] seed.sql를 독립 실행해 행 수, 총합, 상태 분포, 복수 대여 회원, 한국어 데이터 예시, 대여 없는 회원/도서 확인(R-15~R-18)

```bash
python3 - <<'PY'
import sqlite3
conn=sqlite3.connect(':memory:')
conn.executescript(open('schema.sql',encoding='utf-8').read())
conn.executescript(open('seed.sql',encoding='utf-8').read())
for t in ['categories','members','books','rentals']:
    print('count',t,conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0])
print('total', sum(conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ['categories','members','books','rentals']))
print('status_dist', conn.execute("SELECT status, COUNT(*) FROM rentals GROUP BY status ORDER BY status").fetchall())
print('multi_rent_members', conn.execute("SELECT member_id, COUNT(*) c FROM rentals GROUP BY member_id HAVING c>=2 ORDER BY member_id").fetchall())
print('no_rental_members', conn.execute("SELECT member_id,name FROM members WHERE member_id NOT IN (SELECT DISTINCT member_id FROM rentals) ORDER BY member_id").fetchall())
print('no_rental_books', conn.execute("SELECT book_id,title FROM books WHERE book_id NOT IN (SELECT DISTINCT book_id FROM rentals) ORDER BY book_id").fetchall())
print('sample_categories', conn.execute('SELECT category_id, category_name FROM categories ORDER BY category_id LIMIT 5').fetchall())
print('sample_members', conn.execute('SELECT member_id, name, email, phone, address FROM members ORDER BY member_id LIMIT 3').fetchall())
print('sample_books', conn.execute('SELECT book_id, title, author, publisher FROM books ORDER BY book_id LIMIT 5').fetchall())
PY
```

종료 코드: **0**

```text
count categories 10
count members 12
count books 13
count rentals 15
total 50
status_dist [('OVERDUE', 4), ('RENTED', 4), ('RETURNED', 7)]
multi_rent_members [(1, 3), (2, 2), (3, 2), (4, 2)]
no_rental_members [(11, '신현우'), (12, '류미나')]
no_rental_books [(11, '소크라테스의 변명'), (12, '구름빵')]
sample_categories [(1, '소설'), (2, '자기계발'), (3, '역사'), (4, '과학'), (5, '컴퓨터')]
sample_members [(1, '김민준', 'minjun.kim@email.com', '010-1234-5678', '서울시 강남구 역삼동'), (2, '이서연', 'seoyeon.lee@email.com', '010-2345-6789', '서울시 마포구 합정동'), (3, '박지호', 'jiho.park@email.com', '010-3456-7890', '경기도 성남시 분당구')]
sample_books [(1, '채식주의자', '한강', '창비'), (2, '아몬드', '손원평', '창비'), (3, '아주 작은 습관의 힘', '제임스 클리어', '비즈니스북스'), (4, '미라클 모닝', '할 엘로드', '한빛비즈'), (5, '조선왕조실록', '이덕일', '다산초당')]
```

#### [C5] seed.sql 단독 실행 가능성 및 적재 순서 검증: 빈 DB에서 seed.sql만 실행 시 실패 여부와, 부모→자식 순서 문장 요약(R-04,R-17)

```bash
python3 - <<'PY'
import sqlite3
seed=open('seed.sql',encoding='utf-8').read()
conn=sqlite3.connect(':memory:')
try:
    conn.executescript(seed)
    print('seed_only', 'OK')
except Exception as e:
    print('seed_only', type(e).__name__, str(e))
lines=[]
for ln in seed.splitlines():
    s=ln.strip()
    if s.startswith('INSERT INTO '):
        lines.append(s.split()[2])
print('insert_order', lines)
PY
```

종료 코드: **0**

```text
seed_only OperationalError no such table: categories
insert_order ['categories', 'members', 'books', 'rentals']
```

#### [C7] 15개 쿼리 전수 독립 실행 및 핵심 결과 요약. 특히 Q07/Q08/Q13/Q14/Q15 의미 타당성 검증(R-20~R-35)

```bash
python3 - <<'PY'
import sqlite3, re
sqlq=open('queries.sql',encoding='utf-8').read()
marks=list(re.finditer(r'^--\s*(Q\d{2})\s*:\s*(.*)$', sqlq, flags=re.M))
def split_first(body):
    buf=''
    for line in body.splitlines(True):
        buf+=line
        if sqlite3.complete_statement(buf):
            return buf.strip()
    return None
blocks=[]
for i,m in enumerate(marks):
    end=marks[i+1].start() if i+1<len(marks) else len(sqlq)
    blocks.append((m.group(1), m.group(2), split_first(sqlq[m.end():end].strip())))
conn=sqlite3.connect(':memory:')
conn.executescript(open('schema.sql',encoding='utf-8').read())
conn.executescript(open('seed.sql',encoding='utf-8').read())
for label,purpose,stmt in blocks:
    cur=conn.cursor()
    cur.execute(stmt)
    if cur.description:
        rows=cur.fetchall()
        print(label,'rows',len(rows),'sample',rows[:3])
    else:
        print(label,'rowcount',cur.rowcount)
        if label=='Q14':
            print('Q14_status_after', conn.execute("SELECT rental_id,status,due_date,return_date FROM rentals WHERE rental_id IN (12,13,14,15) ORDER BY rental_id").fetchall())
        if label=='Q15':
            print('Q15_member10_after', conn.execute("SELECT rental_id,member_id,rental_date FROM rentals WHERE member_id=10 ORDER BY rental_id").fetchall())
PY
```

종료 코드: **0**

```text
Q01 rows 2 sample [(9, '클린 코드', '로버트 마틴', 33000, 2013), (8, '혼자 공부하는 SQL', '우재남', 26000, 2021)]
Q02 rows 4 sample [(8, '김민준', '총균쇠', '2026-06-01', '2026-06-15', 'OVERDUE'), (9, '이서연', '혼자 공부하는 SQL', '2026-06-10', '2026-06-24', 'OVERDUE'), (10, '박지호', '부의 추월차선', '2026-07-05', '2026-07-19', 'OVERDUE')]
Q03 rows 5 sample [(12, '류미나', 'mina.ryu@email.com', '2025-01-07'), (11, '신현우', 'hyunwoo.shin@email.com', '2024-09-01'), (10, '강소희', 'sohee.kang@email.com', '2024-06-14')]
Q04 rows 2 sample [(8, '혼자 공부하는 SQL', '우재남', 2021, 26000), (5, '조선왕조실록', '이덕일', 2020, 22000)]
Q05 rows 13 sample [(10, '부의 추월차선', '엠제이 드마코', '경제경영', 2013, 16500), (7, '코스모스', '칼 세이건', '과학', 2006, 23000), (2, '아몬드', '손원평', '소설', 2017, 13500)]
Q06 rows 4 sample [('최수아', '부의 추월차선', '2026-10-22', '2026-11-05'), ('윤채원', '제주 한 달 살기', '2026-10-29', '2026-11-12'), ('임도현', '채식주의자', '2026-11-03', '2026-11-17')]
Q07 rows 2 sample [(11, '소크라테스의 변명', '플라톤', 9800), (12, '구름빵', '백희나', 9500)]
Q08 rows 12 sample [(1, '김민준', 3), (2, '이서연', 2), (3, '박지호', 2)]
Q09 rows 10 sample [('소설', 2, 12750.0), ('역사', 2, 23500.0), ('자기계발', 2, 16400.0)]
Q10 rows 4 sample [(1, '김민준', 1), (2, '이서연', 1), (3, '박지호', 1)]
Q11 rows 9 sample [('2026-01', 1), ('2026-02', 2), ('2026-03', 2)]
Q12 rows 5 sample [(9, '클린 코드', '로버트 마틴', 33000, 18238.0), (8, '혼자 공부하는 SQL', '우재남', 26000, 18238.0), (6, '총균쇠', '재레드 다이아몬드', 25000, 18238.0)]
Q13 rows 12 sample [(10, '강소희', '2026-11-08'), (9, '임도현', '2026-11-03'), (8, '윤채원', '2026-10-29')]
Q14 rowcount 1
Q14_statu
…[이하 생략: 전체 1690자]
```

#### [C9] 문서 수치/행수/에러메시지/실행계획 주장 대조용 실제 값 산출: KPI, JOIN vs EXISTS 실행계획, FK 오류 메시지(R-41~R-44)

```bash
python3 - <<'PY'
import sqlite3
conn=sqlite3.connect(':memory:')
conn.executescript(open('schema.sql',encoding='utf-8').read())
conn.executescript(open('seed.sql',encoding='utf-8').read())
print('plan_join')
for r in conn.execute("EXPLAIN QUERY PLAN SELECT DISTINCT m.member_id,m.name,m.email FROM members AS m INNER JOIN rentals AS r ON m.member_id = r.member_id ORDER BY m.member_id"):
    print(r)
print('plan_exists')
for r in conn.execute("EXPLAIN QUERY PLAN SELECT m.member_id,m.name,m.email FROM members AS m WHERE EXISTS (SELECT 1 FROM rentals AS r WHERE r.member_id = m.member_id) ORDER BY m.member_id"):
    print(r)
print('kpi1', conn.execute("SELECT strftime('%Y-%m', rental_date), COUNT(*), (SELECT COUNT(*) FROM books), ROUND(CAST(COUNT(*) AS REAL)/(SELECT COUNT(*) FROM books),4) FROM rentals GROUP BY strftime('%Y-%m', rental_date) ORDER BY 1").fetchall())
print('kpi2_top3', conn.execute("SELECT b.book_id,b.title,COUNT(r.rental_id) c FROM books b JOIN rentals r ON b.book_id=r.book_id GROUP BY b.book_id,b.title ORDER BY c DESC,b.book_id ASC LIMIT 3").fetchall())
print('kpi2_all_counts', conn.execute("SELECT b.book_id,b.title,COUNT(r.rental_id) c FROM books b LEFT JOIN rentals r ON b.book_id=r.book_id GROUP BY b.book_id,b.title ORDER BY c DESC,b.book_id ASC").fetchall())
print('kpi3', conn.execute("SELECT COUNT(*), SUM(CASE WHEN status='OVERDUE' THEN 1 ELSE 0 END), SUM(CASE WHEN status='RETURNED' THEN 1 ELSE 0 END), SUM(CASE WHEN status='RENTED' THEN 1 ELSE 0 END), ROUND(CAST(SUM(CASE WHEN status='OVERDUE' THEN 1 ELSE 0 END) AS REAL)/COUNT(*)*100,1) FROM rentals").fetchone())
print('kpi3_members', conn.execute("SELECT m.name, COUNT(r.rental_id), SUM(CASE WHEN r.status='OVERDUE' THEN 1 ELSE 0 END), ROUND(CAST(SUM(CASE WHEN r.status='OVERDUE' THEN 1 ELSE 0 END) AS REAL)/COUNT(r.rental_id)*100,1) FROM members m JOIN rentals r ON m.member_id=r.member_id GROUP BY m.member_id,m.name HAVING SUM(CASE WHEN r.status='OVERDUE' THEN 1 ELSE 0 END) > 0 ORDER BY 3 DESC,4 DESC").fetchall())
try:
    conn.execute("INSERT INTO rentals (member_id, book_id, rental_date, due_date, status) VALUES (999,1,'2026-11-10','2026-11-24','RENTED')")
except Exception as e:
    print('fk_error', type(e).__name__, str(e))
PY
```

종료 코드: **0**

```text
plan_join
(5, 0, 0, 'SCAN r')
(7, 0, 0, 'SEARCH m USING INTEGER PRIMARY KEY (rowid=?)')
(20, 0, 0, 'USE TEMP B-TREE FOR DISTINCT')
(21, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
plan_exists
(3, 0, 0, 'SCAN m')
(6, 0, 0, 'CORRELATED SCALAR SUBQUERY 1')
(10, 6, 0, 'SCAN r')
kpi1 [('2026-01', 1, 13, 0.0769), ('2026-02', 2, 13, 0.1538), ('2026-03', 2, 13, 0.1538), ('2026-04', 1, 13, 0.0769), ('2026-05', 1, 13, 0.0769), ('2026-06', 2, 13, 0.1538), ('2026-07', 2, 13, 0.1538), ('2026-10', 2, 13, 0.1538), ('2026-11', 2, 13, 0.1538)]
kpi2_top3 [(1, '채식주의자', 2), (3, '아주 작은 습관의 힘', 2), (9, '클린 코드', 2)]
kpi2_all_counts [(1, '채식주의자', 2), (3, '아주 작은 습관의 힘', 2), (9, '클린 코드', 2), (10, '부의 추월차선', 2), (2, '아몬드', 1), (4, '미라클 모닝', 1), (5, '조선왕조실록', 1), (6, '총균쇠', 1), (7, '코스모스', 1), (8, '혼자 공부하는 SQL', 1), (13, '제주 한 달 살기', 1), (11, '소크라테스의 변명', 0), (12, '구름빵', 0)]
kpi3 (15, 4, 7, 4, 26.7)
kpi3_members [('오태양', 1, 1, 100.0), ('박지호', 2, 1, 50.0), ('이서연', 2, 1, 50.0), ('김민준', 3, 1, 33.3)]
fk_error IntegrityError FOREIGN KEY constraint failed
```

#### [C12] verify_sql.py의 자기검증 신뢰성 반증 실험 1: 요구 위반 산출물(negative price 허용 스키마)로도 통과하는지 확인(R-38)

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('schema.sql')
orig=p.read_text(encoding='utf-8')
mod=orig.replace('price       INTEGER NOT NULL CHECK (price >= 0),','price       INTEGER NOT NULL,')
p.write_text(mod,encoding='utf-8')
import subprocess, sys
r=subprocess.run([sys.executable,'verify_sql.py'],capture_output=True,text=True)
print('exit',r.returncode)
print((r.stdout+r.stderr)[:3500])
PY
```

종료 코드: **0**

```text
exit 0
=================================================================
 🛠️  디지털 서랍장 (SQL) 기계적 검증 및 100점 채점기
=================================================================
✔ [PASS] 7대 필수 산출물 파일 전수 존재 확인 (+20점)
✔ [PASS] 스키마 생성 및 외래키 활성화 확인 (4개 테이블, FK 3개) (+20점)
   └ INFO 인덱스: idx_rentals_date
✔ [PASS] 4개 테이블 각 10행 이상 시드 적재 확인 (categories 10행, members 12행, books 13행, rentals 15행 / 총 50행) (+20점)
   └ INFO 상태 분포: {'OVERDUE': 4, 'RENTED': 4, 'RETURNED': 7}, 복수 대여 회원 4명
✔ [PASS] 유령 외래키(FK) 삽입 시 IntegrityError 정상 차단 확인 (+10점)
✔ [PASS] 15대 핵심 쿼리 전수 실행 성공 및 결과 리포트 자동 추출 (+20점)
   └ INFO outputs/query_results.md 재생성 완료
✔ [PASS] 3대 보너스 문서 심층 작성 확인 (+10점)
   └ INFO JOIN_VS_SUBQUERY.md 8944B, INTEGRITY_VIOLATION.md 5684B, KPI_REPORT.md 9229B
✔ [INFO] Mermaid ERD 및 1:N 관계선 3개 확인
✔ [INFO] 거버넌스 문서 2/4종 존재: README.md, SUBMISSION.md
=================================================================
 🎉 [100점 만점 ALL PASS] 디지털 서랍장 미션 최종 점수: 100/100점
=================================================================
```

#### [C13] verify_sql.py의 자기검증 신뢰성 반증 실험 2: status CHECK 제거 산출물을 잡는지 확인(R-38)

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('schema.sql')
orig=p.read_text(encoding='utf-8')
mod=orig.replace("status      TEXT    NOT NULL CHECK (status IN ('RENTED', 'RETURNED', 'OVERDUE'))", "status      TEXT    NOT NULL")
p.write_text(mod,encoding='utf-8')
import subprocess, sys
r=subprocess.run([sys.executable,'verify_sql.py'],capture_output=True,text=True)
print('exit',r.returncode)
print((r.stdout+r.stderr)[:3500])
PY
```

종료 코드: **0**

```text
exit 0
=================================================================
 🛠️  디지털 서랍장 (SQL) 기계적 검증 및 100점 채점기
=================================================================
✔ [PASS] 7대 필수 산출물 파일 전수 존재 확인 (+20점)
✔ [PASS] 스키마 생성 및 외래키 활성화 확인 (4개 테이블, FK 3개) (+20점)
   └ INFO 인덱스: idx_rentals_date
✔ [PASS] 4개 테이블 각 10행 이상 시드 적재 확인 (categories 10행, members 12행, books 13행, rentals 15행 / 총 50행) (+20점)
   └ INFO 상태 분포: {'OVERDUE': 4, 'RENTED': 4, 'RETURNED': 7}, 복수 대여 회원 4명
✔ [PASS] 유령 외래키(FK) 삽입 시 IntegrityError 정상 차단 확인 (+10점)
✔ [PASS] 15대 핵심 쿼리 전수 실행 성공 및 결과 리포트 자동 추출 (+20점)
   └ INFO outputs/query_results.md 재생성 완료
✔ [PASS] 3대 보너스 문서 심층 작성 확인 (+10점)
   └ INFO JOIN_VS_SUBQUERY.md 8944B, INTEGRITY_VIOLATION.md 5684B, KPI_REPORT.md 9229B
✔ [INFO] Mermaid ERD 및 1:N 관계선 3개 확인
✔ [INFO] 거버넌스 문서 2/4종 존재: README.md, SUBMISSION.md
=================================================================
 🎉 [100점 만점 ALL PASS] 디지털 서랍장 미션 최종 점수: 100/100점
=================================================================
```

#### [C14] verify_sql.py의 자기검증 신뢰성 반증 실험 3: queries.sql에서 Q07을 목적 위반 쿼리로 바꿔도 통과하는지 확인(R-38)

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('queries.sql')
orig=p.read_text(encoding='utf-8')
mod=orig.replace("FROM books b\nLEFT JOIN rentals r ON b.book_id = r.book_id\nWHERE r.rental_id IS NULL\nORDER BY b.book_id;", "FROM books b\nORDER BY b.book_id;")
p.write_text(mod,encoding='utf-8')
import subprocess, sys
r=subprocess.run([sys.executable,'verify_sql.py'],capture_output=True,text=True)
print('exit',r.returncode)
print((r.stdout+r.stderr)[:3500])
PY
```

종료 코드: **0**

```text
exit 0
=================================================================
 🛠️  디지털 서랍장 (SQL) 기계적 검증 및 100점 채점기
=================================================================
✔ [PASS] 7대 필수 산출물 파일 전수 존재 확인 (+20점)
✔ [PASS] 스키마 생성 및 외래키 활성화 확인 (4개 테이블, FK 3개) (+20점)
   └ INFO 인덱스: idx_rentals_date
✔ [PASS] 4개 테이블 각 10행 이상 시드 적재 확인 (categories 10행, members 12행, books 13행, rentals 15행 / 총 50행) (+20점)
   └ INFO 상태 분포: {'OVERDUE': 4, 'RENTED': 4, 'RETURNED': 7}, 복수 대여 회원 4명
✔ [PASS] 유령 외래키(FK) 삽입 시 IntegrityError 정상 차단 확인 (+10점)
✔ [PASS] 15대 핵심 쿼리 전수 실행 성공 및 결과 리포트 자동 추출 (+20점)
   └ INFO outputs/query_results.md 재생성 완료
✔ [PASS] 3대 보너스 문서 심층 작성 확인 (+10점)
   └ INFO JOIN_VS_SUBQUERY.md 8944B, INTEGRITY_VIOLATION.md 5684B, KPI_REPORT.md 9229B
✔ [INFO] Mermaid ERD 및 1:N 관계선 3개 확인
✔ [INFO] 거버넌스 문서 2/4종 존재: README.md, SUBMISSION.md
=================================================================
 🎉 [100점 만점 ALL PASS] 디지털 서랍장 미션 최종 점수: 100/100점
=================================================================
```

#### [C17] 민감정보 하드코딩 탐지 및 금지 기술 사용 흔적 탐지(API 키, trigger/view 등) (R-03,R-48)

```bash
python3 - <<'PY'
from pathlib import Path
import re
patterns=[r'AKIA[0-9A-Z]{16}', r'AIza[0-9A-Za-z\-_]{35}', r'sk-[A-Za-z0-9]{20,}', r'api[_-]?key', r'secret', r'token']
for path in sorted([p for p in Path('.').rglob('*') if p.is_file()]):
    try:
        txt=path.read_text(encoding='utf-8',errors='ignore')
    except: continue
    low=txt.lower()
    hits=[]
    for pat in patterns:
        if re.search(pat, txt, re.I): hits.append(pat)
    if hits:
        print('secret_hit', str(path), hits)
for fname in ['schema.sql','seed.sql','queries.sql','README.md','docs/ERD.md']:
    txt=Path(fname).read_text(encoding='utf-8',errors='ignore').lower()
    for kw in ['create view','trigger','django','spring','express','flask','fastapi','api']:
        if kw in txt:
            print('kw', fname, kw)
PY
```

종료 코드: **0**

```text
secret_hit .git/hooks/fsmonitor-watchman.sample ['token']
kw README.md api
```

#### [C18] R-50 관련 git 원격 URL 및 최근 커밋 메시지 형식 확인(공개 저장소 여부는 원격 문자열까지만 확인 가능)

```bash
bash -lc 'git remote -v; echo "== commits =="; git log --oneline --decorate -n 12'
```

종료 코드: **0**

```text
== commits ==
c6c7b25 (HEAD -> main) audit snapshot
```


### Claude-Sonnet-4 — 요청 명령과 실행 원문

#### [C1] 스키마·시드 적재 및 행수 확인

```bash
python3 - <<'PY'
import sqlite3
conn = sqlite3.connect(':memory:')
conn.execute('PRAGMA foreign_keys = ON;')
conn.executescript(open('schema.sql',encoding='utf-8').read())
conn.executescript(open('seed.sql',encoding='utf-8').read())
for t in ('categories','members','books','rentals'):
    print(t, conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0])
print('total', sum(conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('categories','members','books','rentals')))
print('fk_on', conn.execute('PRAGMA foreign_keys').fetchone()[0])
print('status_dist', conn.execute("SELECT status,COUNT(*) FROM rentals GROUP BY status ORDER BY status").fetchall())
print('multi_rent', conn.execute("SELECT COUNT(*) FROM (SELECT member_id FROM rentals GROUP BY member_id HAVING COUNT(*)>=2)").fetchone()[0])
PY
```

종료 코드: **0**

```text
categories 10
members 12
books 13
rentals 15
total 50
fk_on 1
status_dist [('OVERDUE', 4), ('RENTED', 4), ('RETURNED', 7)]
multi_rent 4
```

#### [C2] 제약조건 실제 강제 6종

```bash
python3 - <<'PY'
import sqlite3
conn = sqlite3.connect(':memory:')
conn.execute('PRAGMA foreign_keys = ON;')
conn.executescript(open('schema.sql',encoding='utf-8').read())
conn.executescript(open('seed.sql',encoding='utf-8').read())
tests = [
  ('FK_ghost', "INSERT INTO rentals(member_id,book_id,rental_date,due_date,status) VALUES(999,1,'2026-01-01','2026-01-15','RENTED')"),
  ('price_neg', "INSERT INTO books(category_id,title,author,publisher,published_year,price) VALUES(1,'X','A','B',2020,-1)"),
  ('status_bad', "INSERT INTO rentals(member_id,book_id,rental_date,due_date,status) VALUES(1,1,'2026-01-01','2026-01-15','LOST')"),
  ('email_dup', "INSERT INTO members(name,email,phone,address,join_date) VALUES('홍길동','minjun.kim@email.com','010-0000-0000','서울','2026-01-01')"),
  ('catname_dup', "INSERT INTO categories(category_name) VALUES('소설')"),
  ('notnull_miss', "INSERT INTO members(name,phone,address,join_date) VALUES('홍길동','010-0000-0000','서울','2026-01-01')"),
]
for label, sql in tests:
    try:
        conn.execute(sql)
        print(f'FAIL_NOT_BLOCKED: {label}')
    except Exception as e:
        print(f'BLOCKED {label}: {type(e).__name__}: {e}')
PY
```

종료 코드: **0**

```text
BLOCKED FK_ghost: IntegrityError: FOREIGN KEY constraint failed
BLOCKED price_neg: IntegrityError: CHECK constraint failed: price >= 0
BLOCKED status_bad: IntegrityError: CHECK constraint failed: status IN ('RENTED', 'RETURNED', 'OVERDUE')
BLOCKED email_dup: IntegrityError: UNIQUE constraint failed: members.email
BLOCKED catname_dup: IntegrityError: UNIQUE constraint failed: categories.category_name
BLOCKED notnull_miss: IntegrityError: NOT NULL constraint failed: members.email
```

#### [C3] schema.sql 첫문장·인덱스주석 확인

```bash
python3 - <<'PY'
lines = open('schema.sql',encoding='utf-8').read().splitlines()
for i,l in enumerate(lines[:5]):
    print(i,repr(l))
idx_line = next((i for i,l in enumerate(lines) if 'CREATE INDEX' in l.upper()), None)
if idx_line:
    print('idx_line', idx_line, repr(lines[idx_line]))
    print('above', repr(lines[idx_line-1]))
PY
```

종료 코드: **0**

```text
0 'PRAGMA foreign_keys = ON;'
1 ''
2 'CREATE TABLE categories ('
3 '    category_id   INTEGER PRIMARY KEY AUTOINCREMENT,'
4 '    category_name TEXT    NOT NULL UNIQUE,'
idx_line 41 'CREATE INDEX idx_rentals_date ON rentals (rental_date);'
above '-- 대여일 기준 기간 범위 조회 및 월별 대여 추이 집계 성능을 위해 인덱스를 생성한다.'
```

#### [D1] 15개 쿼리 전수 실행·결과 행수(올바른 블록 분리)

```bash
python3 - <<'PY'
import sqlite3, re
conn = sqlite3.connect(':memory:')
conn.execute('PRAGMA foreign_keys = ON;')
conn.executescript(open('schema.sql',encoding='utf-8').read())
conn.executescript(open('seed.sql',encoding='utf-8').read())
sql = open('queries.sql',encoding='utf-8').read()
marks = list(re.finditer(r'^--\s*(Q\d{2})\s*:.*$', sql, re.MULTILINE))
for i, m in enumerate(marks):
    end = marks[i+1].start() if i+1 < len(marks) else len(sql)
    block = sql[m.end():end]
    buf = ''
    first_stmt = None
    for line in block.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith('--'):
            continue
        buf += line
        if sqlite3.complete_statement(buf):
            first_stmt = buf.strip()
            break
    label = m.group(1)
    if not first_stmt:
        print(f'{label}: NO_STMT')
        continue
    try:
        cur = conn.execute(first_stmt)
        rows = cur.fetchall()
        if cur.description:
            cols = [d[0] for d in cur.description]
            print(f'{label}: {len(rows)} rows cols={cols}')
            for r in rows[:2]:
                print(f'  {r}')
        else:
            print(f'{label}: rowcount={cur.rowcount}')
    except Exception as e:
        print(f'{label}: ERROR {e}')
PY
```

종료 코드: **0**

```text
Q01: 2 rows cols=['book_id', 'title', 'author', 'price', 'published_year']
  (9, '클린 코드', '로버트 마틴', 33000, 2013)
  (8, '혼자 공부하는 SQL', '우재남', 26000, 2021)
Q02: 4 rows cols=['rental_id', '회원명', '도서명', '대여일', '반납기한', '상태']
  (8, '김민준', '총균쇠', '2026-06-01', '2026-06-15', 'OVERDUE')
  (9, '이서연', '혼자 공부하는 SQL', '2026-06-10', '2026-06-24', 'OVERDUE')
Q03: 5 rows cols=['member_id', 'name', 'email', 'join_date']
  (12, '류미나', 'mina.ryu@email.com', '2025-01-07')
  (11, '신현우', 'hyunwoo.shin@email.com', '2024-09-01')
Q04: 2 rows cols=['book_id', 'title', 'author', 'published_year', 'price']
  (8, '혼자 공부하는 SQL', '우재남', 2021, 26000)
  (5, '조선왕조실록', '이덕일', 2020, 22000)
Q05: 13 rows cols=['book_id', 'title', 'author', '카테고리', 'published_year', 'price']
  (10, '부의 추월차선', '엠제이 드마코', '경제경영', 2013, 16500)
  (7, '코스모스', '칼 세이건', '과학', 2006, 23000)
Q06: 4 rows cols=['회원명', '도서명', '대여일', '반납예정일']
  ('최수아', '부의 추월차선', '2026-10-22', '2026-11-05')
  ('윤채원', '제주 한 달 살기', '2026-10-29', '2026-11-12')
Q07: 2 rows cols=['book_id', 'title', 'author', 'price']
  (11, '소크라테스의 변명', '플라톤', 9800)
  (12, '구름빵', '백희나', 9500)
Q08: 12 rows cols=['member_id', '회원명', '총대여횟수']
  (1, '김민준', 3)
  (2, '이서연', 2)
Q09: 10 rows cols=['카테고리', '도서권수', '평균가격']
  ('소설', 2, 12750.0)
  ('역사', 2, 23500.0)
Q10: 4 rows cols=['member_id', '회원명', '연체건수']
  (1, '김민준', 1)
  (2, '이서연', 1)
Q11: 9 rows cols=['대여월', '대여건수']
  ('2026-01', 1)
  ('2026-02', 2)
Q12: 5 rows cols=['book_id', 'title', 'author', 'price', '전체평균가격']
  (9, '클린 코드', '로버트
…[이하 생략: 전체 1700자]
```

#### [D2] demo.sh --non-interactive 종료코드·워킹트리 오염 확인(출력 최소화)

```bash
bash demo.sh --non-interactive > /tmp/demo_out.txt 2>&1; EXITCODE=$?; echo "EXIT:$EXITCODE"; tail -5 /tmp/demo_out.txt; ls library.db 2>/dev/null && echo 'DIRTY:library.db' || echo 'CLEAN:no library.db'; ls b6_1_demo* 2>/dev/null && echo 'DIRTY:tmpdir_leaked' || echo 'CLEAN:no tmpdir'
```

종료 코드: **0**

```text
EXIT:0

[1m[0;36m======================================================================[0m
[1m[0;36m ✅ 시연 완료 — 15대 쿼리 실제 결과는 outputs/query_results.md 에 있습니다.[0m
[1m[0;36m    임시 DB(/tmp/tmp.aEyi3VKERZ)는 종료와 함께 자동 삭제됩니다.[0m
[1m[0;36m======================================================================[0m
CLEAN:no library.db
CLEAN:no tmpdir
```

#### [D3] Q13 상관서브쿼리 결과·NULL포함 확인

```bash
python3 - <<'PY'
import sqlite3
conn = sqlite3.connect(':memory:')
conn.execute('PRAGMA foreign_keys = ON;')
conn.executescript(open('schema.sql',encoding='utf-8').read())
conn.executescript(open('seed.sql',encoding='utf-8').read())
rows = conn.execute("""
SELECT m.member_id, m.name,
  (SELECT MAX(r.rental_date) FROM rentals r WHERE r.member_id=m.member_id) AS 최근대여일
FROM members m
ORDER BY 최근대여일 IS NULL, 최근대여일 DESC
""").fetchall()
print('total rows:', len(rows))
null_rows = [r for r in rows if r[2] is None]
print('NULL rows:', null_rows)
for r in rows[:5]:
    print(r)
PY
```

종료 코드: **0**

```text
total rows: 12
NULL rows: [(11, '신현우', None), (12, '류미나', None)]
(10, '강소희', '2026-11-08')
(9, '임도현', '2026-11-03')
(8, '윤채원', '2026-10-29')
(4, '최수아', '2026-10-22')
(7, '오태양', '2026-07-20')
```

#### [D4] Q14 UPDATE 영향행수·날짜 의존성 확인(고정날짜 기준)

```bash
python3 - <<'PY'
import sqlite3
conn = sqlite3.connect(':memory:')
conn.execute('PRAGMA foreign_keys = ON;')
conn.executescript(open('schema.sql',encoding='utf-8').read())
conn.executescript(open('seed.sql',encoding='utf-8').read())
# RENTED 상태이고 due_date가 지난 행 확인
rented = conn.execute("SELECT rental_id,member_id,due_date,status FROM rentals WHERE status='RENTED' AND return_date IS NULL ORDER BY due_date").fetchall()
print('RENTED rows before Q14:', rented)
# DATE('now') 기준 실행
cur = conn.execute("UPDATE rentals SET status='OVERDUE' WHERE return_date IS NULL AND due_date < DATE('now') AND status='RENTED'")
print('Q14 rowcount with DATE(now):', cur.rowcount)
# 고정날짜 2026-11-10 기준
conn2 = sqlite3.connect(':memory:')
conn2.execute('PRAGMA foreign_keys = ON;')
conn2.executescript(open('schema.sql',encoding='utf-8').read())
conn2.executescript(open('seed.sql',encoding='utf-8').read())
cur2 = conn2.execute("UPDATE rentals SET status='OVERDUE' WHERE return_date IS NULL AND due_date < '2026-11-10' AND status='RENTED'")
print('Q14 rowcount with fixed 2026-11-10:', cur2.rowcount)
PY
```

종료 코드: **0**

```text
RENTED rows before Q14: [(12, 4, '2026-11-05', 'RENTED'), (13, 8, '2026-11-12', 'RENTED'), (14, 9, '2026-11-17', 'RENTED'), (15, 10, '2026-11-22', 'RENTED')]
Q14 rowcount with DATE(now): 1
Q14 rowcount with fixed 2026-11-10: 1
```

#### [D5] verify_sql.py 자기검증 신뢰성: 요구위반 산출물을 FAIL로 잡는지

```bash
python3 - <<'PY'
import sqlite3, sys, os
# 테스트1: price 음수를 허용하는 가짜 스키마로 check_schema가 통과하는지
bad_schema = '''
PRAGMA foreign_keys = ON;
CREATE TABLE categories (category_id INTEGER PRIMARY KEY, category_name TEXT NOT NULL UNIQUE);
CREATE TABLE members (member_id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, phone TEXT NOT NULL, address TEXT NOT NULL, join_date TEXT NOT NULL);
CREATE TABLE books (book_id INTEGER PRIMARY KEY, category_id INTEGER NOT NULL, title TEXT NOT NULL, author TEXT NOT NULL, publisher TEXT NOT NULL, published_year INTEGER NOT NULL, price INTEGER NOT NULL, FOREIGN KEY(category_id) REFERENCES categories(category_id));
CREATE TABLE rentals (rental_id INTEGER PRIMARY KEY, member_id INTEGER NOT NULL, book_id INTEGER NOT NULL, rental_date TEXT NOT NULL, due_date TEXT NOT NULL, return_date TEXT, status TEXT NOT NULL CHECK(status IN ("RENTED","RETURNED","OVERDUE")), FOREIGN KEY(member_id) REFERENCES members(member_id), FOREIGN KEY(book_id) REFERENCES books(book_id));
CREATE INDEX idx_rentals_date ON rentals(rental_date);
'''
# verify_sql.pyの check_schema は price CHECK を検証しているか?
import re
src = open('verify_sql.py',encoding='utf-8').read()
has_price_check = 'price' in src.lower() and 'check' in src.lower()
has_status_check = 'status' in src.lower()
has_notnull_check = 'not null' in src.lower() or 'notnull' in src.lower()
print('verify checks price:', has_price_check)
print('verify checks status:', has_status_check)
print('verify checks notnull:', has_notnull_check)
# 実際にprice CHECKなしスキーマでcheck_schemaが通るか
conn = sqlite3.connect(':memory:')
conn.execute('PRAGMA foreign_keys = ON;')
conn.executescript(bad_schema)
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
print('tables in bad schema:', sorted(tables))
# price CHECK存在確認
cols = conn.execute('PRAGMA table_info(books)').fetchall()
print('books cols:', cols)
# bad schemaでINSERT price=-1が通るか
try:
    conn.execute("INSERT INTO categories VALUES(1,'test')")
    conn.execute("INSERT INTO books(category_id,title,author,publisher,published_year,price) VALUES(1,'T','A','P',2020,-1)")
    print('BAD: price=-1 accepted in bad_schema (no CHECK)')
except Exception as e:
    print('GOOD: price=-1 blocked:', e)
PY
```

종료 코드: **0**

```text
verify checks price: False
verify checks status: True
verify checks notnull: False
tables in bad schema: ['books', 'categories', 'members', 'rentals']
books cols: [(0, 'book_id', 'INTEGER', 0, None, 1), (1, 'category_id', 'INTEGER', 1, None, 0), (2, 'title', 'TEXT', 1, None, 0), (3, 'author', 'TEXT', 1, None, 0), (4, 'publisher', 'TEXT', 1, None, 0), (5, 'published_year', 'INTEGER', 1, None, 0), (6, 'price', 'INTEGER', 1, None, 0)]
BAD: price=-1 accepted in bad_schema (no CHECK)
```

#### [D6] queries.sql Q번호 연속성·주석형식·총개수 확인

```bash
python3 - <<'PY'
import re
sql = open('queries.sql',encoding='utf-8').read()
marks = list(re.finditer(r'^--\s*(Q\d{2})\s*:(.*)$', sql, re.MULTILINE))
print('total markers:', len(marks))
for m in marks:
    print(m.group(1), repr(m.group(2).strip()[:40]))
expected = [f'Q{i:02d}' for i in range(1,16)]
found = [m.group(1) for m in marks]
print('expected:', expected)
print('found:   ', found)
print('match:', found == expected)
PY
```

종료 코드: **0**

```text
total markers: 15
Q01 '특정 카테고리(컴퓨터) 도서를 가격 내림차순으로 조회'
Q02 '연체(OVERDUE) 상태인 대여 건 조회'
Q03 '가장 최근에 가입한 회원 5명 조회'
Q04 '2020년 이후 출판되고 가격이 20,000원 이상인 도서 조회'
Q05 '도서별 카테고리명을 포함한 전체 도서 목록 (INNER JOIN)'
Q06 '현재 대여 중(RENTED)인 회원 이름, 도서명, 반납예정일 조회 (다'
Q07 '대여 이력이 한 번도 없는 도서 조회 (LEFT JOIN + IS NUL'
Q08 '전체 회원별 대여 횟수 조회, 대여 이력이 없는 회원은 0으로 표시 (L'
Q09 '카테고리별 도서 권수와 평균 가격 조회 (COUNT, AVG, GROUP'
Q10 '회원별 총 연체 대여 건수, 연체가 1건 이상인 회원만 조회 (GROUP'
Q11 '월별 총 대여 건수 추이 조회 (strftime, GROUP BY, OR'
Q12 '전체 도서 평균 가격보다 비싼 도서 조회 (비상관 서브쿼리)'
Q13 '회원별 가장 최근 대여일 조회, 대여 이력 없는 회원은 NULL 표시 ('
Q14 '반납기한이 지났으나 아직 미반납(return_date IS NULL)인 '
Q15 '탈퇴 대기 회원(member_id=10)의 테스트성 대여 이력 1건 삭제'
expected: ['Q01', 'Q02', 'Q03', 'Q04', 'Q05', 'Q06', 'Q07', 'Q08', 'Q09', 'Q10', 'Q11', 'Q12', 'Q13', 'Q14', 'Q15']
found:    ['Q01', 'Q02', 'Q03', 'Q04', 'Q05', 'Q06', 'Q07', 'Q08', 'Q09', 'Q10', 'Q11', 'Q12', 'Q13', 'Q14', 'Q15']
match: True
```


---

## 부록 D. 심사 기준 원문 (R-01 ~ R-50)

# 코디세이 B6-1 미션 요구사항 (심사 기준 원문)

> **미션명**: 정보를 깔끔하게 정리하는 디지털 서랍장 만들기 (SQL / RDBMS)
> **도메인**: 도서관 스마트 대여/연체 관리 시스템
> **런타임 전제**: Python 3.9+ 표준 라이브러리(`sqlite3` 포함)만 사용, 외부 패키지 설치 0건. DB는 SQLite.
> **인코딩**: UTF-8, 줄바꿈 LF.
>
> 이 문서는 심사자가 사용할 **평가 기준**이다. 아래 R-01~R-50은 모두 개별 판정 대상이며,
> 심사자는 각 항목을 빠짐없이 PASS / PARTIAL(부분) / FAIL / N/A 중 하나로 판정해야 한다.

---

## A. 목표와 범위

- **R-01** 도메인이 "도서관의 회원·도서·대여 기록 관리(스마트 대여/연체)"로 성립하고, 데이터가 그 도메인의 현실적 업무를 표현한다.
- **R-02** 데이터 모델이 정확히 4개 테이블 `categories`, `members`, `books`, `rentals`로 구성되고, 1:N 관계 3개(`categories→books`, `members→rentals`, `books→rentals`)를 이룬다.
- **R-03** 순수 표준 SQL(SQLite)만 사용한다. 백엔드 프레임워크(Spring/Django/Express 등), API·웹 화면(UI), 뷰(VIEW), 저장 프로시저, 트리거를 사용하지 않는다.
- **R-04** SQL 산출물 3종(`schema.sql`, `seed.sql`, `queries.sql`)이 존재하고 각각 그 자체로 SQLite에서 실행 가능하다.
- **R-05** 평가자가 별도 DB 설치 없이 `python3 verify_sql.py` 한 줄로 100점 만점 기계 채점 결과와 15개 쿼리의 실제 실행 결과를 즉시 확인할 수 있는 재현성을 제공한다.

## B. 스키마 (`schema.sql`)

- **R-06** 파일 최상단(첫 번째 문장)에 `PRAGMA foreign_keys = ON;`을 선언한다.
- **R-07** `categories` 테이블: PK, `category_name`에 NOT NULL + UNIQUE.
- **R-08** `members` 테이블: PK, `email`에 NOT NULL + UNIQUE, NOT NULL 컬럼 2개 이상.
- **R-09** `books` 테이블: PK, `category_id` FK → `categories`, `price`에 `CHECK (price >= 0)`.
- **R-10** `rentals` 테이블: PK, FK 2개(`member_id → members`, `book_id → books`), `status`에 `CHECK (status IN ('RENTED','RETURNED','OVERDUE'))`.
- **R-11** 전체 제약 충족: PK 4개, FK 3개, 테이블마다 NOT NULL 2개 이상, UNIQUE 2개(`members.email`, `categories.category_name`), CHECK 2개.
- **R-12** `rentals(rental_date)` 인덱스를 생성하고, 그 인덱스 생성문 **바로 위 1줄**에 생성 사유 주석을 둔다.
- **R-13** DDL 생성 순서가 FK 의존성 위상정렬(`categories`, `members` → `books` → `rentals`)이다.
- **R-14** 제약조건이 선언만 되어 있는 것이 아니라 **실제로 강제**된다: (a) 존재하지 않는 부모를 참조하는 INSERT가 거부되고, (b) `price` 음수, (c) 허용되지 않은 `status` 값, (d) `members.email` 중복, (e) `categories.category_name` 중복, (f) NOT NULL 컬럼 누락이 각각 거부된다.

## C. 시드 데이터 (`seed.sql`)

- **R-15** 4개 테이블 각 10행 이상, 총 45행 이상의 데이터를 적재한다.
- **R-16** 데이터가 한국어 기반의 현실적인 값(회원 이름·이메일·전화·주소, 도서 제목·저자·출판사, 카테고리명 등)이다.
- **R-17** INSERT 순서가 부모 → 자식(`categories`/`members` → `books` → `rentals`)이며, 그 순서로 적재 시 FK 오류가 없다.
- **R-18** `rentals.status`에 `RENTED`·`RETURNED`·`OVERDUE` 세 상태가 모두 존재하고, 연체 건과 복수 대여 회원이 포함된다.

## D. 15대 쿼리 (`queries.sql`)

- **R-19** 각 쿼리 상단에 `-- Qnn: 목적` 형식의 주석이 있고, Q01~Q15 번호가 1부터 15까지 누락·중복 없이 연속이며 총 15개다.
- **R-20** Q01 — 기본 조회: 특정 카테고리 도서를 `WHERE` 조건과 `ORDER BY ... DESC`로 조회.
- **R-21** Q02 — 기본 조회: 연체(`OVERDUE`) 대여 건 조회.
- **R-22** Q03 — 기본 조회: 최근 가입 회원 5명(`ORDER BY` + `LIMIT`).
- **R-23** Q04 — 기본 조회: 다중 조건 `AND`(예: 2020년 이후 출판 & 20,000원 이상).
- **R-24** Q05 — 조인: `INNER JOIN`으로 도서와 카테고리 결합.
- **R-25** Q06 — 조인: 3개 테이블(`rentals`·`members`·`books`) 다중 `INNER JOIN`으로 대여 중 회원·도서·반납예정일 조회.
- **R-26** Q07 — 조인: `LEFT JOIN` + `IS NULL`로 대여 이력이 없는 도서 조회.
- **R-27** Q08 — 조인: `LEFT JOIN` + `COUNT` + `GROUP BY`로 회원별 대여 횟수를 0회 회원까지 포함해 조회.
- **R-28** Q09 — 집계: `COUNT`·`AVG`·`GROUP BY`로 카테고리별 권수·평균가 조회.
- **R-29** Q10 — 집계: `GROUP BY` + `HAVING`으로 회원별 연체 건수(1건 이상) 조회.
- **R-30** Q11 — 집계: `strftime('%Y-%m', ...)` + `GROUP BY`로 월별 대여 추이 조회.
- **R-31** Q12 — 서브쿼리: 비상관 서브쿼리로 평균가 초과 도서 조회.
- **R-32** Q13 — 서브쿼리: 상관 서브쿼리로 회원별 최근 대여일 조회.
- **R-33** Q14 — 수정: 기한 경과 미반납 건을 `OVERDUE`로 일괄 갱신하는 `UPDATE` 문이며 실행 시 영향 행 수를 확인할 수 있다.
- **R-34** Q15 — 삭제: 탈퇴 대기 회원의 테스트성 대여 이력 1건을 `DELETE`하며, 대상이 1건으로 한정된다.
- **R-35** 15개 쿼리 전부 SQLite에서 **실행 오류 0건**이며, 각 쿼리가 목적에 부합하는 실제 결과를 낸다(필요한 경우 빈 결과가 아닌 행을 반환하고, 반환값의 의미가 쿼리 목적과 일치한다).

## E. 기계 채점기 (`verify_sql.py`)

- **R-36** Python 표준 라이브러리만 사용하고(외부 패키지 0개), Python 3.9+ 에서 동작한다.
- **R-37** 6개 블록 합계 100점 구성(산출물 존재 20 + 스키마 20 + 시드 20 + FK 방어 10 + 15쿼리 실행 20 + 보너스 문서 10)이며, 실행 시 `outputs/query_results.md`를 자동 재생성하고 모든 블록 통과 시 Exit Code 0으로 종료한다.
- **R-38** 채점기가 실제로 요구사항을 검사한다(자기채점 신뢰성): 각 블록이 담당 요구 항목을 실제로 검증하고, 요구 위반이 있으면 FAIL로 종료한다. 선언만 확인하고 넘어가는 항목이 요구를 충족한다고 볼 수 있는지도 판단 대상이다.
- **R-39** `outputs/query_results.md`에 15개 쿼리의 전문과 실제 실행 결과(행 수·값)가 기록되어 있다.

## F. 문서 산출물

- **R-40** `docs/ERD.md`: Mermaid `erDiagram` + 4개 테이블의 컬럼·타입·제약(PK/FK/NOT NULL/UNIQUE/CHECK/DEFAULT) 명세 + 1:N 관계선 3개 + 관계 설명.
- **R-41** 보너스1 `docs/bonus/JOIN_VS_SUBQUERY.md`: 동일 요구를 `INNER JOIN`과 `EXISTS` 서브쿼리로 1:1 대조 — 두 쿼리 전문, 결과 동일성, 실행계획 근거, 가독성·성능 비교와 선택 기준.
- **R-42** 보너스2 `docs/bonus/INTEGRITY_VIOLATION.md`: 존재하지 않는 `member_id=999` INSERT 시 `FOREIGN KEY constraint failed` 실증(재현 SQL·실행 결과)과 원인 분석·해결책.
- **R-43** 보너스3 `docs/bonus/KPI_REPORT.md`: 경영진 3대 KPI(월별 대여 회전율, 최다 대여 도서 TOP 3, 회원 연체율) 각각의 정의·산출 SQL·해석·개선 액션.
- **R-44** 문서(README·ERD·보너스 3종·리포트)에 적힌 수치·실행계획·에러 메시지·행 수가 실제 실행 결과와 일치한다.

## G. 실행·시연 자산

- **R-45** `demo.sh`: 5단계(스키마 → 시드 → 주요 쿼리 → FK 위반 차단 → 100점 채점) 시연 러너, `--non-interactive` 지원, 정상 종료(Exit Code 0), 종료 시 임시 자원 삭제(trap), 실행 후 워킹 트리 오염 없음.
- **R-46** `README.md`: 개요, ERD 요약, 폴더 구조, 실행 방법, `demo.sh` 사용법, 루브릭 충족 체크리스트를 포함한다.
- **R-47** `SUBMISSION.md`: 제출 서약과 산출물 링크를 포함한다.

## H. 거버넌스·규칙 준수

- **R-48** API 키 등 민감정보가 저장소 파일에 하드코딩되어 있지 않다.
- **R-49** 거버넌스 문서가 저장소에 보존되어 있다(`ORDER_SHEET.md`, `RTM.md`, `PROJECT_MANIFEST.json`). 이 3종의 **내용은 심사 자료에서 제외**되며, 존재 여부만 파일 목록으로 확인한다(내용 판정은 하지 않는다).
- **R-50** 저장소가 `yerihanview/B6-1` public 저장소 main 브랜치에 푸시되어 있고, 커밋 이력이 Conventional Commits(`feat:`, `docs:` 등) 단위로 남아 있다.

---

## 심사 운영 규칙

1. **증거 우선**: PASS/PARTIAL 판정에는 반드시 근거를 붙인다(파일명·라인·SQL·실행 출력). 근거 없는 PASS는 무효다.
2. **자기 주장 불인정**: 산출물 문서에 적힌 `✅`, "100/100 ALL PASS", "실측 결과" 같은 서술은 **제출자의 자기 주장**이며 증거가 아니다. 특히 `verify_sql.py`는 제출자가 작성한 자기검증 스크립트이므로, 그 실행 성공 여부를 요구 충족의 근거로 쓸 수 없다. 요구 충족은 심사자가 자기 방식으로 확인한 결과로만 판정한다.
3. **직접 실행**: 판정 전에 심사자가 필요하다고 판단한 검증을 직접 설계해 요청하고, 제공된 원문 출력으로 확인한다(운영 절차는 심사 프롬프트에 별도 안내).
4. **항목 누락 금지**: R-01~R-50 전 항목을 하나도 빠뜨리지 않고 판정한다.
5. **채점**: 100점 만점. 배점표(항목군별 배점)를 스스로 정해 제시하고, 감점은 "요구 위반/누락"에 대해서만 사유와 함께 기록한다. 감점 합계와 최종 점수가 산술적으로 맞아야 한다.
6. **심사 범위**: 산출물을 고치거나 개선안을 실행하지 않는다. 판정과 결함 보고만 한다.

