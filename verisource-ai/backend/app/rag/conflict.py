from typing import List


POLICY_VARIANCE_THRESHOLD = 0.35
RESEARCH_VARIANCE_THRESHOLD = 0.60


def detect_conflict(evidence_blocks: List[dict], mode: str) -> bool:
    """
    Detects semantic inconsistency based on similarity variance.

    Policy mode:
        Strict threshold (low tolerance)

    Research mode:
        Higher tolerance for ambiguity
    """

    if not evidence_blocks or len(evidence_blocks) < 2:
        return False

    scores = [block["score"] for block in evidence_blocks]

    max_score = max(scores)
    min_score = min(scores)
    variance = max_score - min_score

    if mode == "policy":
        return variance > POLICY_VARIANCE_THRESHOLD

    if mode == "research":
        return variance > RESEARCH_VARIANCE_THRESHOLD

    return False