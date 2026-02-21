#!/usr/bin/env python3
"""
VeriSource AI — Phase 6 Similarity Threshold Calibration Experiment
=====================================================================
Runs 20 supported + 20 unsupported CBCS queries, collects similarity
statistics, and derives a safe separation threshold empirically.

Usage:
    cd backend/
    python calibrate_thresholds.py

Requirements:
    - Server running on localhost:8000
    - CBCS regulation PDF present in uploaded_files/
    - [CALIBRATE] debug prints active in router.py

Output:
    - calibration_results.json   (raw per-query data)
    - Printed statistics + threshold recommendation
"""

import requests, sys, os, time, json, math

BASE  = "http://localhost:8000"
CYAN  = "\033[96m"
GREEN = "\033[92m"
RED   = "\033[91m"
BOLD  = "\033[1m"
RESET = "\033[0m"
YELLOW = "\033[93m"

# ──────────────────────────────────────────────────────────────
# 20 SUPPORTED — clearly answerable from the CBCS R2021 document
# ──────────────────────────────────────────────────────────────
SUPPORTED_QUERIES = [
    "What is the minimum attendance required to appear for end semester examination?",
    "What CGPA is required for First Class with Distinction?",
    "What is the maximum duration allowed to complete the B.E. or B.Tech program?",
    "What is the minimum CGPA required for First Class?",
    "What is the definition of a credit unit in the CBCS framework?",
    "What is the maximum break of study allowed for a student?",
    "What are the eligibility criteria for supplementary examination?",
    "What is the attendence exemption percentage range?",
    "How is CGPA calculated under the CBCS regulation?",
    "What is the mark distribution for project viva voce?",
    "What is the minimum GPA required to pass a course?",
    "What are the grading letters and corresponding grade points?",
    "What is the minimum total credit requirement to be awarded the B.E./B.Tech degree?",
    "What happens when a student obtains an F grade in a subject?",
    "How many attempts are allowed for a student to clear a failed subject?",
    "What is the regulation for lateral entry students regarding credit requirements?",
    "What is the re-admission procedure after an approved break of study?",
    "What is the maximum number of subjects a student can register in a semester?",
    "What is the difference between CGPA and GPA under CBCS?",
    "What is the condition for a student to be declared passed in an arrear subject?",
]

# ──────────────────────────────────────────────────────────────
# 20 UNSUPPORTED — not in CBCS R2021 regulation document
# ──────────────────────────────────────────────────────────────
UNSUPPORTED_QUERIES = [
    "What is the hostel fee structure for students?",
    "What is the college placement record this year?",
    "What is the dress code prescribed for students?",
    "What is the cost of lab equipment for electronics students?",
    "Who is the dean of placements at the college?",
    "What is the campus WiFi speed and coverage?",
    "What is the college bus route fee per semester?",
    "What is the mess menu for this week?",
    "What is the average salary of alumni from this college?",
    "What are the library timings during examination season?",
    "What is the sports and gymnasium fee for students?",
    "Who is the current principal or head of institution?",
    "What is the fee refund policy for students who withdraw mid-semester?",
    "Does the college have an R&D center or innovation lab?",
    "What is the anti-ragging policy and its penalties?",
    "What is the NAAC accreditation grade of the college?",
    "What are the extracurricular activity credit points system?",
    "What are the machine learning course syllabus details?",
    "What is the admission cut-off mark for the CSE department?",
    "What medical and health facilities are available on campus?",
]


def banner(text, color=CYAN):
    print(f"\n{color}{BOLD}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{RESET}")


def setup_server():
    """Register users and ingest a CBCS PDF. Returns (student_token, doc_id)."""
    banner("SETUP — Registering users")

    requests.post(f"{BASE}/auth/register", json={"username": "cal_admin",   "password": "admin123", "role": "admin"})
    requests.post(f"{BASE}/auth/register", json={"username": "cal_student", "password": "st123",    "role": "student"})

    admin_resp = requests.post(f"{BASE}/auth/login", data={"username": "cal_admin",   "password": "admin123"})
    stud_resp  = requests.post(f"{BASE}/auth/login", data={"username": "cal_student", "password": "st123"})

    if admin_resp.status_code != 200 or stud_resp.status_code != 200:
        print(f"{RED}❌ Login failed. Is the server running on {BASE}?{RESET}")
        sys.exit(1)

    ADMIN = admin_resp.json()["access_token"]
    STUD  = stud_resp.json()["access_token"]
    print(f"  ✅ Tokens obtained")

    banner("SETUP — Ingesting CBCS PDF")

    pdf_path = None
    for fname in os.listdir("uploaded_files"):
        if fname.lower().endswith(".pdf"):
            pdf_path = os.path.join("uploaded_files", fname)
            break

    if not pdf_path:
        print(f"{RED}❌ No PDF found in uploaded_files/{RESET}")
        sys.exit(1)

    print(f"  📄 Using: {pdf_path}")

    with open(pdf_path, "rb") as f:
        r = requests.post(
            f"{BASE}/ingestion/upload",
            headers={"Authorization": f"Bearer {ADMIN}"},
            files={"file": ("cbcs_calibration.pdf", f, "application/pdf")},
            data={"name": "CBCS_Calibration", "mode": "policy", "version": "v1", "authority": "SSN College"}
        )

    if r.status_code != 200:
        print(f"{RED}❌ Ingestion failed: {r.text}{RESET}")
        sys.exit(1)

    doc_id = str(r.json()["document_id"])
    print(f"  ✅ Ingested — doc_id = {doc_id}")
    time.sleep(1)

    return STUD, doc_id


def run_query(token, doc_id, question):
    """Fire a single policy-mode query and return the response body + timing."""
    t0 = time.time()
    resp = requests.post(
        f"{BASE}/query/",
        json={"mode": "policy", "document_id": doc_id, "query": question},
        headers={"Authorization": f"Bearer {token}"},
    )
    elapsed = time.time() - t0

    if resp.status_code != 200:
        return None, elapsed

    body = resp.json()

    # Extract similarity stats from evidence blocks
    evidence = body.get("evidence", [])
    sims = [e["similarity"] for e in evidence if "similarity" in e]

    return {
        "query": question,
        "decision": body.get("decision"),
        "confidence_score": body.get("confidence_score"),
        "conflict_detected": body.get("conflict_detected"),
        "model_flag_insufficient": body.get("model_flag_insufficient"),
        "avg_similarity": round(sum(sims) / len(sims), 4) if sims else None,
        "max_similarity": round(max(sims), 4) if sims else None,
        "min_similarity": round(min(sims), 4) if sims else None,
        "weighted_confidence": round(0.7 * max(sims) + 0.3 * (sum(sims)/len(sims)), 4) if sims else None,
        "num_chunks": len(sims),
        "elapsed_s": round(elapsed, 2),
    }, elapsed


def collect(token, doc_id, queries, label):
    """Run a batch of queries and return records."""
    banner(f"EXPERIMENT — {label} ({len(queries)} queries)")
    records = []
    for i, q in enumerate(queries, 1):
        result, elapsed = run_query(token, doc_id, q)
        if result is None:
            print(f"  [{i:02d}] {RED}HTTP ERROR{RESET}  {q[:60]}")
            continue
        sym = GREEN + "✅ approved" if result["decision"] == "approved" else RED + "🚫 refused "
        print(
            f"  [{i:02d}] {sym}{RESET}  "
            f"avg={result['avg_similarity']:.4f}  "
            f"max={result['max_similarity']:.4f}  "
            f"conf={result['confidence_score']:.4f}  "
            f"conflict={int(result['conflict_detected'] or 0)}  "
            f"({elapsed:.1f}s)  {q[:55]}…"
        )
        records.append(result)
    return records


def stats(records, key="avg_similarity"):
    """Return (mean, minimum, maximum, stdev) for a numeric key across records."""
    vals = [r[key] for r in records if r.get(key) is not None]
    if not vals:
        return None, None, None, None
    mean = sum(vals) / len(vals)
    mn   = min(vals)
    mx   = max(vals)
    var  = sum((v - mean) ** 2 for v in vals) / len(vals)
    sd   = math.sqrt(var)
    return round(mean, 4), round(mn, 4), round(mx, 4), round(sd, 4)


def print_stats_table(sup_records, unsup_records):
    banner("SIMILARITY DISTRIBUTION STATISTICS", YELLOW)

    headers = ["Metric", "Supported (n=20)", "Unsupported (n=20)"]
    col_w = [26, 22, 22]

    def row(label, s_vals, u_vals):
        print(f"  {label:<{col_w[0]}} {str(s_vals):<{col_w[1]}} {str(u_vals):<{col_w[2]}}")

    print()
    print(f"  {'─'*72}")
    print(f"  {'Metric':<{col_w[0]}} {'Supported (n=20)':<{col_w[1]}} {'Unsupported (n=20)':<{col_w[2]}}")
    print(f"  {'─'*72}")

    for key, label in [
        ("avg_similarity", "avg_similarity"),
        ("max_similarity", "max_similarity"),
        ("min_similarity", "min_similarity"),
        ("weighted_confidence", "weighted (0.7*max+0.3*avg)"),
        ("confidence_score", "system confidence_score"),
    ]:
        sm, sn, sx, ss = stats(sup_records, key)
        um, un, ux, us = stats(unsup_records, key)
        print(f"  {'─'*72}")
        print(f"  {label:<{col_w[0]}} {'─'*20} {'─'*20}")
        print(f"  {'  mean':<{col_w[0]}} {str(sm):<{col_w[1]}} {str(um):<{col_w[2]}}")
        print(f"  {'  min (lowest)':<{col_w[0]}} {str(sn):<{col_w[1]}} {str(un):<{col_w[2]}}")
        print(f"  {'  max (highest)':<{col_w[0]}} {str(sx):<{col_w[1]}} {str(ux):<{col_w[2]}}")
        print(f"  {'  stdev':<{col_w[0]}} {str(ss):<{col_w[1]}} {str(us):<{col_w[2]}}")

    print(f"  {'─'*72}")


def print_threshold_recommendation(sup_records, unsup_records):
    banner("THRESHOLD RECOMMENDATION", GREEN)

    _, s_min, _, _ = stats(sup_records, "avg_similarity")
    _, _, u_max, _ = stats(unsup_records, "avg_similarity")

    if s_min is None or u_max is None:
        print(f"  {RED}Not enough data to compute recommendation{RESET}")
        return

    print(f"\n  Lowest avg_similarity among SUPPORTED  : {GREEN}{s_min:.4f}{RESET}")
    print(f"  Highest avg_similarity among UNSUPPORTED: {RED}{u_max:.4f}{RESET}")

    gap = s_min - u_max
    print(f"\n  Separation gap : {BOLD}{gap:.4f}{RESET}")

    if gap <= 0:
        print(f"\n  {RED}⚠️  OVERLAP DETECTED — distributions overlap by {abs(gap):.4f}.")
        print(f"  avg_similarity alone may not be a reliable separator.{RESET}")
        print(f"  → Consider using weighted formula: 0.7 * max_similarity + 0.3 * avg_similarity")

        _, sw_min, _, _ = stats(sup_records, "weighted_confidence")
        _, _, uw_max, _ = stats(unsup_records, "weighted_confidence")
        if sw_min and uw_max:
            w_gap = sw_min - uw_max
            if w_gap > 0:
                w_thresh = round((sw_min + uw_max) / 2, 3)
                print(f"  → Weighted gap: {w_gap:.4f}  →  Recommended weighted threshold: {BOLD}{YELLOW}{w_thresh}{RESET}")
    else:
        recommended = round((s_min + u_max) / 2, 3)
        safe_policy   = recommended
        safe_research = round(recommended * 0.6, 3)

        print(f"\n  {BOLD}✅ CLEAR SEPARATION FOUND{RESET}")
        print(f"\n  Recommended threshold (avg_similarity, policy mode)  : {GREEN}{BOLD}{safe_policy}{RESET}")
        print(f"  Recommended threshold (avg_similarity, research mode): {GREEN}{BOLD}{safe_research}{RESET}")
        print()
        print(f"  To apply — update these constants:")
        print(f"    engine.py  →  policy  threshold : {safe_policy}")
        print(f"    engine.py  →  research threshold: {safe_research}")
        print(f"    refusal.py →  mirror same values")

    # Check decision accuracy
    sup_approved   = sum(1 for r in sup_records   if r["decision"] == "approved")
    unsup_refused  = sum(1 for r in unsup_records if r["decision"] == "refused")
    total = len(sup_records) + len(unsup_records)
    correct = sup_approved + unsup_refused
    print(f"\n  Decision accuracy with CURRENT thresholds:")
    print(f"    Supported approved   : {sup_approved}/{len(sup_records)}")
    print(f"    Unsupported refused  : {unsup_refused}/{len(unsup_records)}")
    print(f"    Overall accuracy     : {BOLD}{correct}/{total} ({100*correct/total:.1f}%){RESET}")


def save_results(sup_records, unsup_records):
    output = {
        "experiment": "Phase 6 Similarity Threshold Calibration",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": "fastembed (MiniLM ONNX)",
        "supported": sup_records,
        "unsupported": unsup_records,
    }
    with open("calibration_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  💾 Raw results saved → calibration_results.json")


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{BOLD}{CYAN}VeriSource AI — Phase 6 Threshold Calibration Experiment{RESET}")
    print(f"  Embedding model : fastembed (MiniLM ONNX via ChromaDB)")
    print(f"  Target          : 20 supported + 20 unsupported CBCS queries")

    token, doc_id = setup_server()

    sup_records   = collect(token, doc_id, SUPPORTED_QUERIES,   "SUPPORTED Queries")
    unsup_records = collect(token, doc_id, UNSUPPORTED_QUERIES, "UNSUPPORTED Queries")

    print_stats_table(sup_records, unsup_records)
    print_threshold_recommendation(sup_records, unsup_records)
    save_results(sup_records, unsup_records)

    banner("CALIBRATION COMPLETE", GREEN)
    print(f"  Next steps:")
    print(f"  1. Review the recommendation above")
    print(f"  2. Update constants in engine.py and refusal.py")
    print(f"  3. Run: python test_phase6.py")
    print(f"  4. Remove [CALIBRATE] debug prints from router.py")
    print()
