# app/decision/engine.py

from typing import List, Dict
from app.decision.confidence import compute_confidence
from app.decision.refusal import get_refusal_reason
from app.decision.counterfactual import generate_refusal_explanation


def make_decision(
    mode: str,
    query_str: str,
    similarities: List[float],
    conflict_flag: bool,
    model_flag_insufficient: bool
) -> Dict:
    """
    System-level governance decision.

    Returns:
    {
        decision: "approved" | "refused",
        confidence_score: float,
        reason: str,
        explanation: Dict | None
    }
    """

    if not similarities:
        reason = "No retrievable evidence found in selected document."
        return {
            "decision": "refused",
            "confidence_score": 0.0,
            "reason": reason,
            "explanation": generate_refusal_explanation(query_str, mode, reason)
        }

    avg_similarity = sum(similarities) / len(similarities)
    
    # 🔹 CALIBRATION: Signal-to-Noise Gating
    # For technical technical papers, irrelevant chunks (negative similarity) drown out
    # a single high-precision match. We calculate signal strength from positives only.
    positive_sims = [s for s in similarities if s > 0]
    avg_positive_sim = sum(positive_sims) / len(positive_sims) if positive_sims else avg_similarity

    confidence_score = compute_confidence(
        similarities=similarities,
        conflict_flag=conflict_flag,
        model_flag_insufficient=model_flag_insufficient,
        mode=mode
    )

    # ------------------------
    # POLICY MODE (STRICT)
    # ------------------------
    if mode == "policy":
        # Conflict = hard refusal (evidence contradicts itself)
        if conflict_flag:
            reason = get_refusal_reason(
                mode, avg_positive_sim, conflict_flag, model_flag_insufficient
            )
            return {
                "decision": "refused",
                "confidence_score": confidence_score,
                "reason": reason,
                "explanation": generate_refusal_explanation(query_str, mode, reason)
            }

        # Similarity gate (Using signal strength)
        if avg_positive_sim < 0.05:  
            reason = get_refusal_reason(
                mode, avg_positive_sim, conflict_flag, model_flag_insufficient
            )
            return {
                "decision": "refused",
                "confidence_score": confidence_score,
                "reason": reason,
                "explanation": generate_refusal_explanation(query_str, mode, reason)
            }

        return {
            "decision": "approved",
            "confidence_score": confidence_score,
            "reason": "Evidence sufficiently supports answer.",
            "explanation": None
        }

    # ------------------------
    # RESEARCH MODE (TOLERANT)
    # ------------------------
    elif mode == "research":
        # Research mode is highly sensitive to signal strength in large technical docs
        if avg_positive_sim < 0.03:  
            reason = get_refusal_reason(
                mode, avg_positive_sim, conflict_flag, model_flag_insufficient
            )
            return {
                "decision": "refused",
                "confidence_score": confidence_score,
                "reason": reason,
                "explanation": generate_refusal_explanation(query_str, mode, reason)
            }

        return {
            "decision": "approved",
            "confidence_score": confidence_score,
            "reason": "Evidence supports answer (research tolerance applied).",
            "explanation": None
        }

    # Fallback safety
    reason = "Invalid mode or governance condition."
    return {
        "decision": "refused",
        "confidence_score": confidence_score,
        "reason": reason,
        "explanation": generate_refusal_explanation(query_str, mode, reason)
    }