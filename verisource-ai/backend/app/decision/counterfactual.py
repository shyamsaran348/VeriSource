# app/decision/counterfactual.py

from typing import Dict, List

# Define a mapping of query keywords to "evidence requirements" 
# This is used to explain what the system would have needed for approval.
CONCEPT_REQUIREMENTS = {
    "attendance": [
        "A clear statement defining minimum attendance percentage (e.g., 75%)",
        "A clause specifying eligibility conditions for examination appearance",
        "Section documentation on attendance condonation policies"
    ],
    "duration": [
        "Explicit definition of minimum/maximum time for program completion",
        "Clauses regarding 'break of study' or 'lateral entry' duration",
        "Specific year-range data for B.E. / B.Tech graduation"
    ],
    "degree": [
        "Formal classification criteria (Distinction, First Class, Pass)",
        "Minimum CGPA requirements for award categories",
        "Policy on backlog clearance and its effect on degree honors"
    ],
    "fee": [
        "Structured fee tables or official currency figures",
        "Refund policy timelines and percentage brackets",
        "Hostel or transport specific financial amendments"
    ],
    "exam": [
        "Eligibility criteria for appearing in end-semester assessments",
        "Rules regarding malpractice and disciplinary actions",
        "Valuation or re-totaling procedure clauses"
    ],
    "admission": [
        "Eligibility criteria for entry-level enrollment",
        "Document requirements for seat allotment",
        "Selection process descriptions and cut-off mechanisms"
    ]
}

def generate_refusal_explanation(query: str, mode: str, reason: str) -> Dict:
    """
    Analyzes the query and refusal reason to generate counterfactual elements.
    Aligns with 'What if' / 'Why not' Explainable AI (XAI) research.
    """
    query_lower = query.lower()
    missing_elements = []
    
    # 1. Identify concepts from the query
    found_concepts = []
    for concept, requirements in CONCEPT_REQUIREMENTS.items():
        if concept in query_lower:
            found_concepts.append(concept)
            missing_elements.extend(requirements)
            
    # 2. Add technical/governance requirements based on the reason
    if "conflict" in reason.lower():
        missing_elements.insert(0, "A non-contradictory, singular resolution of policy clauses")
    elif "similarity" in reason.lower() or "insufficient" in reason.lower():
        if not found_concepts:
            missing_elements.append("A relevant section matching the specific subject of your query")
            
    # Deduplicate while preserving order
    unique_elements = []
    for e in missing_elements:
        if e not in unique_elements:
            unique_elements.append(e)

    # Limit to top 4 for UI clarity
    final_elements = unique_elements[:4]

    return {
        "missing_evidence_requirements": final_elements,
        "mode_threshold_context": {
            "mode": mode,
            "calibrated_gate": "0.05" if mode == "policy" else "0.03",
            "condition": "High similarity + Minimal conflict"
        }
    }
