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
            return "Conflicting sections detected in policy document. Institutional governance requires a singular resolution."
        if avg_similarity < 0.05:  
            return "Insufficient supporting evidence in selected policy document. The query may fall outside official institutional scope."

    elif mode == "research":
        if avg_similarity < 0.03:  
            return "Insufficient supporting evidence in selected research paper. The query may involve variables not covered in this study's methodology."

    return "Confidence threshold not satisfied."