# app/decision/refusal.py

def get_refusal_reason(
    mode: str,
    avg_similarity: float,
    conflict_flag: bool,
    model_flag_insufficient: bool
) -> str:
    """
    Returns structured refusal reason based on governance logic.
    """

    if model_flag_insufficient:
        return "Model indicated insufficient evidence in selected document."

    if mode == "policy":
        if conflict_flag:
            return "Conflicting sections detected in policy document."
        if avg_similarity < 0.05:  # Calibrated 2026-02-21: fastembed MiniLM ONNX, 20+20 query experiment
            return "Insufficient supporting evidence in selected policy document."

    elif mode == "research":
        if avg_similarity < 0.03:  # Calibrated 2026-02-21: fastembed MiniLM ONNX, 20+20 query experiment
            return "Insufficient supporting evidence in selected research paper."

    return "Confidence threshold not satisfied."