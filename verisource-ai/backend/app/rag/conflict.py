# app/rag/conflict.py

import statistics
from typing import List


# Calibrated thresholds for Standard Deviation of Top-K results
# High SD (> 0.20) indicates erratic evidence distribution
STABILITY_THRESHOLD_POLICY = 0.20
STABILITY_THRESHOLD_RESEARCH = 0.30


def detect_conflict(evidence_blocks: List[dict], mode: str) -> bool:
    """
    Detects semantic instability or evidence conflict using Top-K Standard Deviation.

    Instead of simple range, we measure the 'Consensus' among the top retrieved chunks.
    High Deviation = Erratically distributed evidence (Conflict-prone).
    Low Deviation = Harmonious, focused evidence (Stable).
    """

    if not evidence_blocks or len(evidence_blocks) < 3:
        # Not enough evidence to calculate statistical stability
        return False

    # Extract similarities for the top chunks
    # Note: 'evidence_blocks' passed here are dicts with 'similarity' keys
    scores = [block["similarity"] for block in evidence_blocks]
    
    # Calculate Standard Deviation to measure 'Evidence Consensus'
    try:
        sd = statistics.stdev(scores)
    except statistics.StatisticsError:
        return False

    # Policy mode requires tighter consensus
    if mode == "policy":
        return sd > STABILITY_THRESHOLD_POLICY

    # Research mode allows for more diverse/conflicting viewpoints
    if mode == "research":
        return sd > STABILITY_THRESHOLD_RESEARCH

    return False