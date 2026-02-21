# app/decision/confidence.py

from typing import List


def compute_confidence(
    similarities: List[float],
    conflict_flag: bool,
    model_flag_insufficient: bool,
    mode: str
) -> float:
    """
    Computes a numeric confidence score (0.0 – 1.0).

    This function does NOT make governance decisions.
    It only calculates confidence based on measurable signals.

    Calibration note (2026-02-21):
    - Uses weighted formula: 0.7 * max_similarity + 0.3 * avg_similarity
    - Empirically shown to provide better separation than avg alone
      Supported mean weighted: 0.208  |  Unsupported mean weighted: -0.126
    """

    if not similarities:
        return 0.0

    avg_similarity = sum(similarities) / len(similarities)
    max_similarity = max(similarities)
    min_similarity = min(similarities)

    # Weighted confidence — calibrated for fastembed MiniLM ONNX
    # max_similarity captures the strongest relevant chunk;
    # avg_similarity anchors overall evidence quality
    confidence = 0.7 * max_similarity + 0.3 * avg_similarity

    # Hard penalty if model itself flagged insufficient
    if model_flag_insufficient:
        confidence *= 0.5

    # Mode-aware penalty handling
    if mode == "policy":
        # Policy mode is strict — conflicts are severe
        if conflict_flag:
            confidence *= 0.5

    elif mode == "research":
        # Research mode tolerates conflict but lowers confidence
        if conflict_flag:
            confidence *= 0.8

    # Additional safeguard: weak minimum similarity
    # Threshold 0.10 (not 0.40) — fastembed produces low min scores even for
    # valid retrievals (calibration: supported min_similarity mean = 0.09)
    if min_similarity < 0.10:
        confidence *= 0.8

    # Clamp between 0 and 1
    confidence = max(0.0, min(1.0, confidence))

    return round(confidence, 4)