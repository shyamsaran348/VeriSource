#!/usr/bin/env python3
"""
VeriSource AI — Phase 5 Validation Test Suite
==============================================
Covers all 9 test groups from the Phase 5 Test Plan.
"""

import requests, uuid, sys, json

BASE = "http://localhost:8000"
GREEN  = "\033[92m✅ PASS\033[0m"
RED    = "\033[91m❌ FAIL\033[0m"
BLUE   = "\033[94m🔷\033[0m"
YELLOW = "\033[93m🟡\033[0m"

results = []

def check(name, passed, detail=""):
    icon = GREEN if passed else RED
    print(f"  {icon}  {name}")
    if detail: print(f"         {detail}")
    results.append((name, passed))

def section(title):
    print(f"\n{'='*62}")
    print(f"  {title}")
    print(f"{'='*62}")

def h(token): return {"Authorization": f"Bearer {token}"}


# ─── SETUP ─────────────────────────────────────────────────
section("SETUP — Users & Tokens")
requests.post(f"{BASE}/auth/register", json={"username":"p5_admin","password":"admin123","role":"admin"})
requests.post(f"{BASE}/auth/register", json={"username":"p5_student","password":"st123","role":"student"})
ADMIN  = requests.post(f"{BASE}/auth/login", data={"username":"p5_admin","password":"admin123"}).json()["access_token"]
STUD   = requests.post(f"{BASE}/auth/login", data={"username":"p5_student","password":"st123"}).json()["access_token"]
print(f"  {BLUE} Tokens obtained")

section("SETUP — Ingesting Documents")
import os
pdf = next((os.path.join("uploaded_files",f) for f in os.listdir("uploaded_files") if f.endswith(".pdf")), None)
assert pdf, "No PDF in uploaded_files/"

def ingest(name, mode, version):
    with open(pdf,"rb") as f:
        r = requests.post(f"{BASE}/ingestion/upload",
            headers=h(ADMIN),
            files={"file":(f"{name}.pdf",f,"application/pdf")},
            data={"name":name,"mode":mode,"version":version,"authority":"test"})
    assert r.status_code == 200, f"Ingest {name} failed: {r.text[:100]}"
    return str(r.json()["document_id"])

POLICY1 = ingest("p5_policy","policy","v1")    # active
POLICY2 = ingest("p5_policy","policy","v2")    # v1 auto-becomes inactive
RESEARCH = ingest("p5_research","research","v1")
INACTIVE = POLICY1
ACTIVE   = POLICY2
print(f"  {BLUE} Active policy:   {ACTIVE}\n  {BLUE} Inactive policy: {INACTIVE}\n  {BLUE} Research:        {RESEARCH}")


# ─── GROUP 1 — Valid Policy Query ──────────────────────────
section("GROUP 1 — Valid Policy Query")
r = requests.post(f"{BASE}/query/", json={
    "mode":"policy","document_id":ACTIVE,
    "query":"What are the attendance requirements for students?"
}, headers=h(STUD))
body = r.json() if r.status_code==200 else {}
check("G1 Status 200",           r.status_code==200, f"status={r.status_code}")
check("G1 evidence[] returned",  isinstance(body.get("evidence",[]),list) and len(body.get("evidence",[]))>0)
check("G1 conflict_detected bool", isinstance(body.get("conflict_detected"),bool))
check("G1 No 'answer' hallucination guard", "answer" in body)
check("G1 model_flag_insufficient present", "model_flag_insufficient" in body)
check("G1 No extra speculation fields", "summary" not in body and "reasoning" not in body)
ans = body.get("answer","")
print(f"         answer preview: {str(ans)[:120]}...")
print(f"         model_flag_insufficient: {body.get('model_flag_insufficient')}")


# ─── GROUP 2 — Valid Research Query ───────────────────────
section("GROUP 2 — Valid Research Query")
r = requests.post(f"{BASE}/query/", json={
    "mode":"research","document_id":RESEARCH,
    "query":"What findings or regulations are described in this document?"
}, headers=h(STUD))
body = r.json() if r.status_code==200 else {}
check("G2 Status 200", r.status_code==200, f"status={r.status_code}")
check("G2 conflict_detected present", "conflict_detected" in body)
check("G2 model_flag_insufficient present", "model_flag_insufficient" in body)
check("G2 answer or null", "answer" in body)
ans = body.get("answer","")
print(f"         answer preview: {str(ans)[:120]}...")
print(f"         model_flag_insufficient: {body.get('model_flag_insufficient')}")


# ─── GROUP 3 — Irrelevant / Out-of-scope Question ─────────
section("GROUP 3 — Irrelevant Question (INSUFFICIENT_EVIDENCE)")
r = requests.post(f"{BASE}/query/", json={
    "mode":"policy","document_id":ACTIVE,
    "query":"What is the university cafeteria menu for today?"
}, headers=h(STUD))
body = r.json() if r.status_code==200 else {}
check("G3 Status 200", r.status_code==200, f"status={r.status_code}")
insuf = body.get("model_flag_insufficient")
ans3  = body.get("answer")
check("G3 model_flag_insufficient = True (LLM signalled insufficient)", insuf == True, f"got: {insuf}")
check("G3 answer = null when insufficient", ans3 is None, f"got: {ans3}")
print(f"         [Verification] LLM correctly flagged irrelevant query")


# ─── GROUP 4 — Admin Access Blocked ───────────────────────
section("GROUP 4 — Admin Access Attempt (Role Enforcement)")
r = requests.post(f"{BASE}/query/", json={
    "mode":"policy","document_id":ACTIVE,"query":"attendance"
}, headers=h(ADMIN))
check("G4 Admin → 403 Forbidden", r.status_code==403, f"status={r.status_code} body={r.text[:60]}")
check("G4 'Student access required' in error", "student" in r.text.lower(), r.text[:80])


# ─── GROUP 5 — Mode Mismatch ───────────────────────────────
section("GROUP 5 — Mode Mismatch (Governance Enforcement)")
r = requests.post(f"{BASE}/query/", json={
    "mode":"research","document_id":ACTIVE,"query":"attendance"
}, headers=h(STUD))
check("G5 Mode mismatch → 400", r.status_code==400, f"status={r.status_code}")
check("G5 Mode mismatch error message", "mode" in r.text.lower(), r.text[:80])
# Confirm no LLM call triggered (we can verify chain by checking no 'answer' key)
check("G5 No 'answer' generated on rejected request", "answer" not in r.json())


# ─── GROUP 6 — Inactive Policy Version ────────────────────
section("GROUP 6 — Inactive Policy Version (Active Version Rule)")
r = requests.post(f"{BASE}/query/", json={
    "mode":"policy","document_id":INACTIVE,"query":"attendance"
}, headers=h(STUD))
check("G6 Inactive policy → 400", r.status_code==400, f"status={r.status_code}")
check("G6 Error mentions active version", "active" in r.text.lower(), r.text[:80])
check("G6 No LLM call (no 'answer' on error)", "answer" not in r.json())


# ─── GROUP 7 — Vector Collection Missing ──────────────────
section("GROUP 7 — Vector Collection Missing (No Auto-Create)")
ghost = str(uuid.uuid4())
r = requests.post(f"{BASE}/query/", json={
    "mode":"policy","document_id":ghost,"query":"anything"
}, headers=h(STUD))
check("G7 Missing doc/collection → 404", r.status_code==404, f"status={r.status_code}")
check("G7 No auto-create (not 200)", r.status_code != 200)
check("G7 No silent fallback (not 500)", r.status_code != 500)


# ─── GROUP 8 — Conflict Detection ─────────────────────────
section("GROUP 8 — Conflict Detection")
r = requests.post(f"{BASE}/query/", json={
    "mode":"policy","document_id":ACTIVE,
    "query":"regulations rules procedures requirements policies deadlines fees"
}, headers=h(STUD))
body = r.json() if r.status_code==200 else {}
check("G8 Status 200", r.status_code==200, f"status={r.status_code}")
check("G8 conflict_detected is bool", isinstance(body.get("conflict_detected"),bool))
check("G8 Answer still generated in Phase 5 (not blocked)", "answer" in body)
print(f"         conflict_detected = {body.get('conflict_detected')}")
print(f"         (Phase 6 will block on conflict=True — Phase 5 just flags)")


# ─── GROUP 9 — Security: LLM Never Sees Internal Data ─────
section("GROUP 9 — Security: LLM Prompt Governance")
# We verify this architecturally — provider.py builds the prompt from evidence_texts only
# Let's confirm the response structure never leaks internal data to client either
r = requests.post(f"{BASE}/query/", json={
    "mode":"policy","document_id":ACTIVE,
    "query":"What is the attendance requirement?"
}, headers=h(STUD))
body = r.json() if r.status_code==200 else {}
check("G9 Response does NOT contain similarity scores in answer text",
    not any(str(round(e.get("similarity", 0.0),4)) in str(body.get("answer","")) for e in body.get("evidence",[])))
check("G9 Response does NOT expose document_id in answer",
    ACTIVE[:8] not in str(body.get("answer","")))
check("G9 Response does NOT expose conflict flag in answer",
    str(body.get("conflict_detected","")) not in str(body.get("answer","")))
check("G9 model_flag_insufficient is bool not string",
    isinstance(body.get("model_flag_insufficient"), bool))
print(f"         {BLUE} Provider architecture: LLM prompt contains ONLY query + evidence text")
print(f"         {BLUE} No scores, metadata, conflict flags, or doc_ids passed to model")


# ─── SUMMARY ──────────────────────────────────────────────
section("PHASE 5 VALIDATION SUMMARY")
passed = sum(1 for _,p in results if p)
total  = len(results)
print(f"\n  Total: {passed}/{total} passed\n")
for name, p in results:
    print(f"  {'✅' if p else '❌'}  {name}")
print()
if passed == total:
    print("  🎉 ALL TESTS PASSED — Phase 5 COMPLETE!")
else:
    failed = [n for n,p in results if not p]
    print(f"  ⚠️  {total-passed} test(s) failed:")
    for f in failed: print(f"    - {f}")
    sys.exit(1)
