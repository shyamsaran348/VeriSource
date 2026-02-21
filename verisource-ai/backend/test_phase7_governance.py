#!/usr/bin/env python3
"""
VeriSource AI — Phase 7 Governance + Audit Validation Suite
=============================================================
Validates ALL governance rules (Phase 6) AND confirms audit logging (Phase 7).

Groups:
  TEST 1 — Policy Mode: Strong evidence → approved
  TEST 2 — Policy Mode: Conflict detected → refused
  TEST 3 — Policy Mode: Low similarity / off-topic → refused
  TEST 4 — Research Mode: Conflict tolerant (if applicable)
  TEST 5 — Governance wall: LLM cannot override refused decision
  TEST 6 — Admin Access Blocked from query endpoint (403)
  TEST 7 — Audit Log: entries written for both approved and refused
  TEST 8 — Regression: Phase 6 decision engine unchanged after logging addition
  TEST 9 — Audit: failed logging does NOT crash query flow

Usage:
    cd backend/
    python3 test_phase7_governance.py

Requirements:
    - Server running on localhost:8000
    - CBCS PDF present in uploaded_files/
"""

import requests, sys, os, time, hashlib, json

BASE   = "http://localhost:8000"
GREEN  = "\033[92m✅ PASS\033[0m"
RED    = "\033[91m❌ FAIL\033[0m"
BLUE   = "\033[94m🔷\033[0m"
YELLOW = "\033[93m🟡\033[0m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

results = []


def check(name, passed, detail=""):
    icon = GREEN if passed else RED
    print(f"  {icon}  {name}")
    if detail:
        print(f"         {detail}")
    results.append((name, passed))


def section(title, color=CYAN):
    print(f"\n{color}{BOLD}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{RESET}")


def h(token):
    return {"Authorization": f"Bearer {token}"}


# ─── SETUP ─────────────────────────────────────────────────────────────────────
section("SETUP — Users & Tokens")

requests.post(f"{BASE}/auth/register", json={"username": "p7_admin",   "password": "adm123", "role": "admin"})
requests.post(f"{BASE}/auth/register", json={"username": "p7_student", "password": "stu123", "role": "student"})

admin_r = requests.post(f"{BASE}/auth/login", data={"username": "p7_admin",   "password": "adm123"})
stud_r  = requests.post(f"{BASE}/auth/login", data={"username": "p7_student", "password": "stu123"})

if admin_r.status_code != 200 or stud_r.status_code != 200:
    print(f"  {RED}Login failed. Is the server running on {BASE}?")
    sys.exit(1)

ADMIN = admin_r.json()["access_token"]
STUD  = stud_r.json()["access_token"]
print(f"  {BLUE} Admin + Student tokens obtained")

# ─── INGEST POLICY DOCUMENT ────────────────────────────────────────────────────
section("SETUP — Ingesting CBCS Policy Document")

pdf_path = None
for f in os.listdir("uploaded_files"):
    if f.lower().endswith(".pdf"):
        pdf_path = os.path.join("uploaded_files", f)
        break

if not pdf_path:
    print(f"  {RED}No PDF in uploaded_files/")
    sys.exit(1)

print(f"  {BLUE} PDF: {pdf_path}")

with open(pdf_path, "rb") as fh:
    r = requests.post(
        f"{BASE}/ingestion/upload",
        headers=h(ADMIN),
        files={"file": ("cbcs_p7.pdf", fh, "application/pdf")},
        data={"name": "CBCS_P7_Test", "mode": "policy", "version": "v1", "authority": "SSN"}
    )

if r.status_code != 200:
    print(f"  {RED}Ingestion failed: {r.text}")
    sys.exit(1)

POLICY_DOC_ID = str(r.json()["document_id"])
print(f"  {BLUE} doc_id = {POLICY_DOC_ID}")
time.sleep(1)


def query(doc_id, mode, question, token=None):
    token = token or STUD
    resp = requests.post(
        f"{BASE}/query/",
        json={"mode": mode, "document_id": doc_id, "query": question},
        headers=h(token),
    )
    body = resp.json() if resp.status_code in (200, 403) else {}
    return resp, body


# ──────────────────────────────────────────────────────────────
# TEST 1 — Policy mode: Strong evidence → APPROVED
# ──────────────────────────────────────────────────────────────
section("TEST 1 — Policy Mode: Strong Evidence → Approved")

print(f"\n  {YELLOW} Query: minimum attendance requirement")
resp, body = query(POLICY_DOC_ID, "policy", "What is the minimum attendance required to appear for end semester examination?")
check("T1 HTTP 200",             resp.status_code == 200,                         f"status={resp.status_code}")
check("T1 decision = approved",  body.get("decision") == "approved",              f"decision={body.get('decision')}")
check("T1 answer not null",      body.get("answer") is not None,                  f"answer={(body.get('answer') or '')[:80]}")
check("T1 confidence > 0.10",    body.get("confidence_score", 0) > 0.10,         f"score={body.get('confidence_score')}")
check("T1 reason present",       bool(body.get("reason")),                        f"reason={body.get('reason')}")
check("T1 model_flag exposed",   "model_flag_insufficient" in body,               "field present in response")
print(f"  Decision   : {body.get('decision')}  |  Confidence: {body.get('confidence_score')}")
print(f"  Answer     : {str(body.get('answer') or '')[:150]}")

print(f"\n  {YELLOW} Query: duration of B.E./B.Tech program")
resp2, body2 = query(POLICY_DOC_ID, "policy", "What is the maximum duration allowed to complete the B.E. or B.Tech program?")
check("T1b decision = approved", body2.get("decision") == "approved",             f"decision={body2.get('decision')}")
check("T1b answer not null",     body2.get("answer") is not None,                 f"answer={(body2.get('answer') or '')[:80]}")
print(f"  Decision   : {body2.get('decision')}  |  Confidence: {body2.get('confidence_score')}")


# ──────────────────────────────────────────────────────────────
# TEST 2 — Policy mode: Off-topic query (low similarity) → REFUSED
# ──────────────────────────────────────────────────────────────
section("TEST 2 — Policy Mode: Off-topic / Low Similarity → Refused")

for q_label, question in [
    ("Capital of France",  "What is the capital of France?"),
    ("Hostel fee",         "What is the hostel fee structure?"),
    ("WiFi password",      "What is the campus WiFi password?"),
    ("Mess menu",          "What is on the mess menu today?"),
]:
    print(f"\n  {YELLOW} {q_label}")
    resp, body = query(POLICY_DOC_ID, "policy", question)
    check(f"T2 [{q_label}] HTTP 200",          resp.status_code == 200,                f"status={resp.status_code}")
    check(f"T2 [{q_label}] decision = refused", body.get("decision") == "refused",     f"decision={body.get('decision')}")
    check(f"T2 [{q_label}] answer = null",      body.get("answer") is None,            f"answer={body.get('answer')}")
    check(f"T2 [{q_label}] reason present",     bool(body.get("reason")),              f"reason={body.get('reason')}")
    print(f"     Decision: {body.get('decision')}  |  Reason: {body.get('reason')}")


# ──────────────────────────────────────────────────────────────
# TEST 3 — Policy mode: Broad multi-clause query (conflict test)
# ──────────────────────────────────────────────────────────────
section("TEST 3 — Policy Mode: Conflict Detection Integration")

print(f"\n  {YELLOW} Query: broad award criteria (may trigger conflict)")
resp, body = query(
    POLICY_DOC_ID, "policy",
    "What are the conditions and criteria for award of degree with distinction, first class, and pass class?"
)
check("T3 HTTP 200",                resp.status_code == 200,                              f"status={resp.status_code}")
check("T3 decision present",        body.get("decision") in ("approved", "refused"),      f"decision={body.get('decision')}")
check("T3 conflict_detected bool",  isinstance(body.get("conflict_detected"), bool),      f"conflict={body.get('conflict_detected')}")
check("T3 confidence present",      body.get("confidence_score") is not None,             f"score={body.get('confidence_score')}")
if body.get("conflict_detected"):
    check("T3 conflict → refused (policy mode)", body.get("decision") == "refused",       f"decision={body.get('decision')}")
    check("T3 conflict → answer null",           body.get("answer") is None,              f"answer={body.get('answer')}")
else:
    check("T3 no conflict → valid decision",     body.get("decision") in ("approved","refused"))
print(f"  Decision: {body.get('decision')}  |  Conflict: {body.get('conflict_detected')}  |  Confidence: {body.get('confidence_score')}")


# ──────────────────────────────────────────────────────────────
# TEST 4 — Research mode: Tolerance applied
# ──────────────────────────────────────────────────────────────
section("TEST 4 — Research Mode: Conflict Tolerance (uses policy doc as research proxy)")

# Upload the same PDF as research mode to test research logic
with open(pdf_path, "rb") as fh:
    r = requests.post(
        f"{BASE}/ingestion/upload",
        headers=h(ADMIN),
        files={"file": ("cbcs_research.pdf", fh, "application/pdf")},
        data={"name": "CBCS_Research", "mode": "research", "version": "v1", "authority": "SSN"}
    )

if r.status_code == 200:
    RESEARCH_DOC_ID = str(r.json()["document_id"])
    print(f"  {BLUE} Research doc_id = {RESEARCH_DOC_ID}")
    time.sleep(1)

    resp, body = query(
        RESEARCH_DOC_ID, "research",
        "What does the regulation say about CGPA requirements?"
    )
    check("T4 HTTP 200",            resp.status_code == 200,                              f"status={resp.status_code}")
    check("T4 decision present",    body.get("decision") in ("approved", "refused"),      f"decision={body.get('decision')}")
    check("T4 confidence present",  body.get("confidence_score") is not None,            f"score={body.get('confidence_score')}")
    check("T4 mode = research",     body.get("mode") == "research",                       f"mode={body.get('mode')}")
    print(f"  Decision: {body.get('decision')}  |  Confidence: {body.get('confidence_score')}")
    print(f"  Conflict: {body.get('conflict_detected')}  |  Answer: {str(body.get('answer') or '')[:100]}")
else:
    check("T4 research doc ingested", False, f"status={r.status_code}: {r.text[:100]}")


# ──────────────────────────────────────────────────────────────
# TEST 5 — Governance wall: LLM cannot override refusal
# ──────────────────────────────────────────────────────────────
section("TEST 5 — Governance Wall: LLM Cannot Override Refusal")

print(f"\n  {BLUE} Verifying that ALL refused responses have answer=null...")

gov_queries = [
    ("who is the principal",   "Who is the current principal of the college?"),
    ("FIFA world cup",         "Who won the FIFA World Cup in 2022?"),
    ("campus wifi",            "What is the WiFi speed in the campus labs?"),
    ("fee refund",             "What is the fee refund policy for withdrawn students?"),
]

bypass_violations = []
for label, q in gov_queries:
    resp, body = query(POLICY_DOC_ID, "policy", q)
    if body.get("decision") == "refused" and body.get("answer") is not None:
        bypass_violations.append(label)
    check(
        f"GOV [{label}] refused → answer=null",
        not (body.get("decision") == "refused" and body.get("answer") is not None),
        f"decision={body.get('decision')} answer={body.get('answer')}"
    )

if bypass_violations:
    print(f"\n  🚨 LLM BYPASS DETECTED in: {bypass_violations}")
else:
    print(f"\n  {GREEN}  No LLM bypass — governance wall holding correctly")


# ──────────────────────────────────────────────────────────────
# TEST 6 — Admin blocked from query endpoint (403)
# ──────────────────────────────────────────────────────────────
section("TEST 6 — Access Control: Admin Blocked from Query Endpoint")

resp, body = query(POLICY_DOC_ID, "policy", "What is the minimum attendance?", token=ADMIN)
check("T6 Admin → 403",      resp.status_code == 403,    f"status={resp.status_code}")
check("T6 detail present",   "detail" in body,           f"body={body}")
print(f"  Status: {resp.status_code}  |  Detail: {body.get('detail','')}")


# ──────────────────────────────────────────────────────────────
# TEST 7 — Audit Logs Written (Phase 7 Core Validation)
# ──────────────────────────────────────────────────────────────
section("TEST 7 — Phase 7: Audit Logs Are Written After Each Query")

audit_resp = requests.get(f"{BASE}/audit/logs", headers=h(ADMIN), params={"limit": 20})
check("T7 GET /audit/logs HTTP 200", audit_resp.status_code == 200, f"status={audit_resp.status_code}")

if audit_resp.status_code == 200:
    logs = audit_resp.json()
    check("T7 logs list returned",           isinstance(logs, list),        f"type={type(logs)}")
    check("T7 at least 1 log entry",         len(logs) > 0,                 f"count={len(logs)}")

    if logs:
        sample = logs[0]
        check("T7 log has user_id",          "user_id"          in sample,  f"keys={list(sample.keys())}")
        check("T7 log has document_id",      "document_id"      in sample,  f"keys={list(sample.keys())}")
        check("T7 log has mode",             "mode"             in sample,  f"mode={sample.get('mode')}")
        check("T7 log has query_hash",       "query_hash"       in sample,  f"hash_len={len(sample.get('query_hash',''))}")
        check("T7 log has decision",         "decision"         in sample,  f"decision={sample.get('decision')}")
        check("T7 log has confidence_score", "confidence_score" in sample,  f"score={sample.get('confidence_score')}")
        check("T7 log has timestamp",        "timestamp"        in sample,  f"ts={sample.get('timestamp')}")
        check("T7 query_hash is SHA-256",    len(sample.get("query_hash", "")) == 64, f"hash={sample.get('query_hash','')[:16]}...")
        check("T7 raw query NOT stored",     "query" not in sample,         "Privacy: raw text must not appear in log")

        # Verify approved + refused both logged
        decisions_logged = {log["decision"] for log in logs}
        check("T7 approved decisions logged",  "approved" in decisions_logged, f"decisions seen: {decisions_logged}")
        check("T7 refused decisions logged",   "refused"  in decisions_logged, f"decisions seen: {decisions_logged}")

        print(f"\n  Most recent {len(logs)} log entries:")
        for log in logs[:5]:
            print(f"    id={log['id']}  decision={log['decision']:<8}  "
                  f"mode={log['mode']:<8}  score={log['confidence_score']:.4f}  "
                  f"ts={str(log['timestamp'])[:19]}")
else:
    print(f"  Skipping audit field checks — endpoint returned {audit_resp.status_code}")


# ──────────────────────────────────────────────────────────────
# TEST 8 — Regression: Phase 6 logic unchanged
# ──────────────────────────────────────────────────────────────
section("TEST 8 — Regression: Phase 6 Governance Unchanged After Phase 7 Integration")

# Re-run the canonical Phase 6 checks to confirm no regression
reg_tests = [
    ("attendance",     "What is the minimum attendance required to appear for end semester examination?", "approved"),
    ("hostel fee",     "What is the hostel fee structure?",       "refused"),
    ("placement",      "What is the college placement record?",   "refused"),
]

for label, question, expected in reg_tests:
    resp, body = query(POLICY_DOC_ID, "policy", question)
    check(
        f"REG [{label}] decision={expected}",
        body.get("decision") == expected,
        f"decision={body.get('decision')}"
    )
    if expected == "refused":
        check(f"REG [{label}] answer=null", body.get("answer") is None, f"answer={body.get('answer')}")


# ──────────────────────────────────────────────────────────────
# TEST 9 — Audit Student blocked from /audit/logs
# ──────────────────────────────────────────────────────────────
section("TEST 9 — Access Control: Student Cannot Access Audit Logs")

audit_stud = requests.get(f"{BASE}/audit/logs", headers=h(STUD))
check("T9 Student → 403 on audit logs", audit_stud.status_code == 403, f"status={audit_stud.status_code}")
print(f"  Status: {audit_stud.status_code}")


# ──────────────────────────────────────────────────────────────
# STRUCTURAL CHECKS — Code-level validation
# ──────────────────────────────────────────────────────────────
section("STRUCTURAL CHECKS — Code-Level Validation")

import importlib, inspect

try:
    engine_mod = importlib.import_module("app.decision.engine")
    make_decision = getattr(engine_mod, "make_decision")
    sig = inspect.signature(make_decision)
    params = list(sig.parameters.keys())
    check("STRUCT engine.make_decision exists",             True)
    check("STRUCT engine params: mode",                     "mode"                    in params, f"params={params}")
    check("STRUCT engine params: similarities",             "similarities"            in params, f"params={params}")
    check("STRUCT engine params: conflict_flag",            "conflict_flag"           in params, f"params={params}")
    check("STRUCT engine params: model_flag_insufficient",  "model_flag_insufficient" in params, f"params={params}")
except Exception as e:
    check("STRUCT engine module importable", False, str(e))

try:
    conf_mod = importlib.import_module("app.decision.confidence")
    compute_confidence = getattr(conf_mod, "compute_confidence")
    src = inspect.getsource(compute_confidence)
    check("STRUCT confidence uses max_similarity",   "max_similarity"        in src, "weighted formula present")
    check("STRUCT confidence uses avg_similarity",   "avg_similarity"        in src)
    check("STRUCT confidence clamps 0-1",            "max(0.0" in src or "min(1.0" in src or "clamp" in src.lower())
    check("STRUCT confidence applies model penalty", "model_flag_insufficient" in src)
except Exception as e:
    check("STRUCT confidence module importable", False, str(e))

try:
    refusal_mod = importlib.import_module("app.decision.refusal")
    get_reason = getattr(refusal_mod, "get_refusal_reason")
    src = inspect.getsource(get_reason)
    check("STRUCT refusal has policy branch",   '"policy"'   in src)
    check("STRUCT refusal has research branch", '"research"' in src)
    check("STRUCT refusal different thresholds", src.count("avg_similarity <") >= 2 or src.count("< 0.") >= 2)
except Exception as e:
    check("STRUCT refusal module importable", False, str(e))

try:
    logger_mod = importlib.import_module("app.audit.logger")
    log_fn = getattr(logger_mod, "log_query_interaction")
    src = inspect.getsource(log_fn)
    check("STRUCT audit hashes query",  "hash_query" in src or "sha256" in src.lower())
    check("STRUCT audit fail-safe",     "SQLAlchemyError" in src or "except" in src)
    check("STRUCT audit no raw query stored", "query_hash" in src and "query=query" not in src)
except Exception as e:
    check("STRUCT audit logger importable", False, str(e))


# ──────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ──────────────────────────────────────────────────────────────
section("PHASE 7 GOVERNANCE + AUDIT VALIDATION SUMMARY")

passed = sum(1 for _, p in results if p)
total  = len(results)
pct    = 100 * passed // total if total else 0

print(f"\n  {BOLD}Total: {passed}/{total} passed ({pct}%){RESET}\n")

for name, p in results:
    icon = "✅" if p else "❌"
    print(f"  {icon}  {name}")

print()
if passed == total:
    print(f"  🎉 {BOLD}ALL TESTS PASSED — Phase 7 VALIDATED!{RESET}")
    print(f"  ✅ Governance: working  ✅ Audit log: working  ✅ No LLM bypass  ✅ No regression")
else:
    failed = [n for n, p in results if not p]
    print(f"  ⚠️  {total - passed} test(s) failed:")
    for f in failed:
        print(f"    ❌ {f}")
    sys.exit(1)
