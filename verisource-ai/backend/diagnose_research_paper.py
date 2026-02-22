from app.rag.retriever import retrieve
from app.rag.evidence import extract_evidence
from app.rag.conflict import detect_conflict
from app.decision.engine import make_decision

# Use the ID we know exists in the vector store
doc_id = "864f7efb-25f6-4f16-865d-cbffca462f46"
mode = "research"

queries = [
    "What techniques are combined in the proposed BDLSS scheme?",
    "What hashing algorithm is used to generate the genesis block?",
    "What threshold values are used for keyframe extraction?"
]

for q in queries:
    print(f"\n--- Testing Query: {q} ---")
    raw_results = retrieve(doc_id, q, mode)
    evidence_dicts = extract_evidence(raw_results, q)
    similarities = [e["similarity"] for e in evidence_dicts]
    conflict = detect_conflict(evidence_dicts, mode)
    
    # Use the actual engine logic
    decision_obj = make_decision(
        mode=mode,
        query_str=q,
        similarities=similarities,
        conflict_flag=conflict,
        model_flag_insufficient=False 
    )
    
    print(f"Top 3 Similarities (Scaled): {similarities[:3]}")
    print(f"Decision: {decision_obj['decision'].upper()}")
    print(f"Confidence (Scaled): {decision_obj['confidence_score']:.4f}")
    print(f"Reason: {decision_obj['reason']}")
