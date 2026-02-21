"""
LLM Response Parser — Phase 5.

Detects the INSUFFICIENT_EVIDENCE sentinel from model output.
The model SIGNALS lack of evidence using this token; it does NOT decide refusal.
Refusal enforcement is handled in Phase 6.
"""


INSUFFICIENT_SENTINEL = "INSUFFICIENT_EVIDENCE"


def parse_llm_response(raw_output: str) -> dict:
    """
    Parse raw model output into structured components.

    Returns:
        {
            "answer": str | None,
            "model_flag_insufficient": bool
        }

    If the model output contains INSUFFICIENT_EVIDENCE (case-insensitive):
        answer = None
        model_flag_insufficient = True
    Else:
        answer = cleaned output text
        model_flag_insufficient = False
    """
    if not raw_output or not raw_output.strip():
        return {
            "answer": None,
            "model_flag_insufficient": True,
        }

    if INSUFFICIENT_SENTINEL in raw_output.upper():
        return {
            "answer": None,
            "model_flag_insufficient": True,
        }

    return {
        "answer": raw_output.strip(),
        "model_flag_insufficient": False,
    }