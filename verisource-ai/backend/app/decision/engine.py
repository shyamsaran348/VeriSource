# app/decision/engine.py

from typing import List, Dict
from app.decision.confidence import compute_confidence, scale_confidence_for_ui
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
    Central Governance Hub: Implements a multi-stage deterministic decision gate.
    
    This function decides whether to 'approve' or 'refuse' a query based on
    statistical signal strength and model-level uncertainty markers.

    Args:
        mode: Policy (Strict) or Research (Tolerant)
        query_str: The raw user query
        similarities: List of cosine similarity scores from retrieved chunks
        conflict_flag: Boolean indicating if retrieved chunks contradict each other
        model_flag_insufficient: Boolean indicating if LLM signaled a lack of evidence

    Returns:
        Dict containing decision, score, and grounded reasoning.
    """

    # 1. Edge Case: No evidence retrieved at all
    if not similarities:
        reason = "No retrievable evidence found in selected document."
        return {
            "decision": "refused",
            "confidence_score": 0.0,
            "reason": reason,
            "explanation": generate_refusal_explanation(query_str, mode, reason)
        }

    # 2. Statistical Signal Filtering (Signal-to-Noise Gating)
    # Technical documents often contain noise. We calculate 'Signal Strength' 
    # based ONLY on positive technical matches.
    positive_sims = [s for s in similarities if s > 0]
    avg_positive_sim = sum(positive_sims) / len(positive_sims) if positive_sims else 0.0

    # 3. Calculate Core Confidence
    # This involves statistical variance check and model signal processing.
    raw_confidence = compute_confidence(
        similarities=similarities,
        conflict_flag=conflict_flag,
        model_flag_insufficient=model_flag_insufficient,
        mode=mode
    )

    # 4. Mode-Aware Gating Logic
    
    # ── POLICY MODE (STRICT) ──────────────────────────────────────────────────
    if mode == "policy":
        # Strict Conflict Check: Evidence must be harmonious
        if conflict_flag:
            reason = get_refusal_reason(mode, avg_positive_sim, conflict_flag, model_flag_insufficient)
            return {
                "decision": "refused",
                "confidence_score": round(raw_confidence, 4),
                "reason": reason,
                "explanation": generate_refusal_explanation(query_str, mode, reason)
            }

        # Strict Signal Gate: Must meet minimum precision threshold
        if avg_positive_sim < 0.05:  
            reason = get_refusal_reason(mode, avg_positive_sim, conflict_flag, model_flag_insufficient)
            return {
                "decision": "refused",
                "confidence_score": round(raw_confidence, 4),
                "reason": reason,
                "explanation": generate_refusal_explanation(query_str, mode, reason)
            }

        return {
            "decision": "approved",
            "confidence_score": scale_confidence_for_ui(raw_confidence),
            "reason": "Evidence sufficiently supports answer.",
            "explanation": None
        }

    # ── RESEARCH MODE (TOLERANT) ──────────────────────────────────────────────
    elif mode == "research":
        # Research mode allows for weaker signals to explore technical nuances
        if avg_positive_sim < 0.03:  
            reason = get_refusal_reason(mode, avg_positive_sim, conflict_flag, model_flag_insufficient)
            return {
                "decision": "refused",
                "confidence_score": round(raw_confidence, 4),
                "reason": reason,
                "explanation": generate_refusal_explanation(query_str, mode, reason)
            }

        return {
            "decision": "approved",
            "confidence_score": scale_confidence_for_ui(raw_confidence),
            "reason": "Evidence supports answer (research tolerance applied).",
            "explanation": None
        }

    # Fallback safety (Default to Refusal)
    reason = "Invalid mode or governance condition."
    return {
        "decision": "refused",
        "confidence_score": round(raw_confidence, 4),
        "reason": reason,
        "explanation": generate_refusal_explanation(query_str, mode, reason)
    }