# app/decision/engine.py

from typing import List, Dict
from app.decision.confidence import compute_confidence
from app.decision.refusal import get_refusal_reason


def make_decision(
    mode: str,
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
        reason: str
    }
    """

    if not similarities:
        return {
            "decision": "refused",
            "confidence_score": 0.0,
            "reason": "No retrievable evidence found in selected document."
        }

    avg_similarity = sum(similarities) / len(similarities)

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
            return {
                "decision": "refused",
                "confidence_score": confidence_score,
                "reason": get_refusal_reason(
                    mode, avg_similarity, conflict_flag, model_flag_insufficient
                )
            }

        # Similarity gate — empirically calibrated via 20+20 CBCS query experiment:
        #   Supported avg range  : -0.17 – 0.36  (mean 0.145)
        #   Unsupported avg range: -0.78 – 0.05  (mean -0.198)
        #   Safe boundary        : 0.05  (midpoint between 0.0457 and 0.058)
        if avg_similarity < 0.05:  # Calibrated 2026-02-21 — fastembed MiniLM ONNX
            return {
                "decision": "refused",
                "confidence_score": confidence_score,
                "reason": get_refusal_reason(
                    mode, avg_similarity, conflict_flag, model_flag_insufficient
                )
            }

        # model_flag_insufficient: ADVISORY ONLY in policy mode.
        # Calibration experiment (2026-02-21, 20+20 CBCS queries) showed
        # an ~80% false-positive rate — the LLM outputs INSUFFICIENT_EVIDENCE
        # even for questions clearly answerable from the CBCS document.
        # This flag already reduces confidence_score by 50% in confidence.py.
        # We do NOT let it make a hard governance decision here.

        return {
            "decision": "approved",
            "confidence_score": confidence_score,
            "reason": "Evidence sufficiently supports answer."
        }

    # ------------------------
    # RESEARCH MODE (TOLERANT)
    # ------------------------
    elif mode == "research":

        # Research mode: similarity gate only — model flag is purely advisory
        # Calibrated threshold: 0.03 (60% of policy threshold, research tolerates ambiguity)
        if avg_similarity < 0.03:  # Calibrated 2026-02-21 — fastembed MiniLM ONNX
            return {
                "decision": "refused",
                "confidence_score": confidence_score,
                "reason": get_refusal_reason(
                    mode, avg_similarity, conflict_flag, model_flag_insufficient
                )
            }

        return {
            "decision": "approved",
            "confidence_score": confidence_score,
            "reason": "Evidence supports answer (research tolerance applied)."
        }

    # Fallback safety
    return {
        "decision": "refused",
        "confidence_score": confidence_score,
        "reason": "Invalid mode or governance condition."
    }