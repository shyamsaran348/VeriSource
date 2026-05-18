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
    model_flag_insufficient: bool,
    bypass_governance: bool = False,
    bypass_entropy: bool = False,
    bypass_conflict: bool = False,
    bypass_veto: bool = False
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

    # 0. Baseline Comparison Logic (Vanilla RAG Simulation)
    if bypass_governance:
        return {
            "decision": "approved",
            "confidence_score": 1.0,
            "reason": "Governance Bypassed (Baseline Mode)",
            "explanation": None,
            "diagnostics": {"focus_score": 1.0, "consensus_score": 1.0}
        }

    # 1. Edge Case: No evidence retrieved at all
    if not similarities:
        reason = "No retrievable evidence found in selected document."
        return {
            "decision": "refused",
            "confidence_score": 0.0,
            "reason": reason,
            "explanation": generate_refusal_explanation(query_str, mode, reason),
            "diagnostics": {"focus_score": 0.0, "consensus_score": 0.0}
        }

    # 2. Statistical Signal Filtering (Signal-to-Noise Gating)
    # Technical documents often contain noise. We calculate 'Signal Strength' 
    # based ONLY on positive technical matches.
    positive_sims = [s for s in similarities if s > 0]
    avg_positive_sim = sum(positive_sims) / len(positive_sims) if positive_sims else 0.0

    # 3. Calculate Core Confidence
    # This involves statistical variance check and model signal processing.
    try:
        raw_confidence, diagnostics = compute_confidence(
            similarities=similarities,
            conflict_flag=conflict_flag if not bypass_conflict else False,
            model_flag_insufficient=model_flag_insufficient if not bypass_veto else False,
            mode=mode,
            bypass_entropy=bypass_entropy
        )
    except Exception as e:
        # 🛡️ ARCHITECTURAL SELF-HEALING
        # If ML engine fails, fail SAFE (Refusal)
        print(f"[CRITICAL] ML Engine Error: {e}")
        return {
            "decision": "refused",
            "confidence_score": 0.0,
            "reason": "Internal Governance Error: Uncertainty too high to proceed.",
            "explanation": {"missing_evidence_requirements": ["System stability check (ML Executor failed)"]},
            "diagnostics": {"focus_score": 0.0, "consensus_score": 0.0}
        }

    # 4. Mode-Aware Gating Logic
    
    # ── POLICY MODE (STRICT) ──────────────────────────────────────────────────
    if mode == "policy":
        # Stage 2 Check: Did the LLM flag missing evidence?
        if model_flag_insufficient and not bypass_veto:
            reason = get_refusal_reason(mode, avg_positive_sim, conflict_flag, model_flag_insufficient)
            return {
                "decision": "refused",
                "confidence_score": round(raw_confidence, 4),
                "reason": reason,
                "explanation": generate_refusal_explanation(query_str, mode, reason),
                "diagnostics": diagnostics
            }

        # Strict Conflict Check: Evidence must be harmonious
        if conflict_flag and not bypass_conflict:
            reason = get_refusal_reason(mode, avg_positive_sim, conflict_flag, model_flag_insufficient)
            return {
                "decision": "refused",
                "confidence_score": round(raw_confidence, 4),
                "reason": reason,
                "explanation": generate_refusal_explanation(query_str, mode, reason),
                "diagnostics": diagnostics
            }

        # Strict Signal Gate: Must meet minimum precision threshold
        if avg_positive_sim < 0.05:  
            reason = get_refusal_reason(mode, avg_positive_sim, conflict_flag, model_flag_insufficient)
            return {
                "decision": "refused",
                "confidence_score": round(raw_confidence, 4),
                "reason": reason,
                "explanation": generate_refusal_explanation(query_str, mode, reason),
                "diagnostics": diagnostics
            }

        return {
            "decision": "approved",
            "confidence_score": scale_confidence_for_ui(raw_confidence),
            "reason": "Evidence sufficiently supports answer.",
            "explanation": None,
            "diagnostics": diagnostics
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
                "explanation": generate_refusal_explanation(query_str, mode, reason),
                "diagnostics": diagnostics
            }

        return {
            "decision": "approved",
            "confidence_score": scale_confidence_for_ui(raw_confidence),
            "reason": "Evidence supports answer (research tolerance applied).",
            "explanation": None,
            "diagnostics": diagnostics
        }

    # Fallback safety (Default to Refusal)
    reason = "Invalid mode or governance condition."
    return {
        "decision": "refused",
        "confidence_score": round(raw_confidence, 4),
        "reason": reason,
        "explanation": generate_refusal_explanation(query_str, mode, reason),
        "diagnostics": diagnostics
    }