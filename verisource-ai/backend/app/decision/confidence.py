# app/decision/confidence.py

import math
from typing import List


def calculate_retrieval_entropy(similarities: List[float]) -> float:
    """
    Calculates the Shannon Entropy of the retrieval distribution.
    
    High Entropy (> 2.0): Scores are spread thin across many unrelated chunks. (Uncertain)
    Low Entropy (< 1.0): Retrieval is focused on a few high-precision matches. (Certain)
    """
    if not similarities:
        return 0.0
    
    # Softmax-style normalization to create a probability distribution
    # Using a small epsilon to avoid log(0)
    exp_sims = [math.exp(s * 10) for s in similarities] # Temperature scaling to sharpen signal
    total = sum(exp_sims)
    probs = [s / total for s in exp_sims]
    
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    return round(entropy, 4)


def compute_confidence(
    similarities: List[float],
    conflict_flag: bool,
    model_flag_insufficient: bool,
    mode: str,
    bypass_entropy: bool = False
) -> tuple[float, dict]:
    """
    Computes a numeric confidence score (0.0 – 1.0) and returns diagnostic signals.
    """

    if not similarities:
        return 0.0, {"focus_score": 0.0, "consensus_score": 0.0}

    # 1. RETRIEVAL FOCUS (Entropy)
    entropy = calculate_retrieval_entropy(similarities)
    entropy_penalty = 1.0
    if not bypass_entropy:
        if entropy > 1.8: # Threshold for high uncertainty/scattered results
            entropy_penalty = 0.7
        elif entropy > 1.2:
            entropy_penalty = 0.9

    # 2. EVIDENCE STABILITY (Consensus)
    # Inverse of Standard Deviation, scaled 0-1
    import numpy as np
    std_dev = float(np.std(similarities)) if len(similarities) > 1 else 0.0
    consensus_signal = max(0, 1.0 - (std_dev * 2.5)) # Sensitivity factor

    # 3. PRECISION-WEIGHTED SIGNAL
    max_sim = max(similarities)
    positive_sims = [s for s in similarities if s > 0]
    avg_positive_sim = sum(positive_sims) / len(positive_sims) if positive_sims else 0.0
    
    base_confidence = 0.8 * max_sim + 0.2 * avg_positive_sim
    confidence = base_confidence * entropy_penalty

    # 4. PENALTY HEURISTICS
    if model_flag_insufficient:
        confidence *= 0.4 

    if mode == "policy":
        if conflict_flag:
            confidence *= 0.5 
    elif mode == "research":
        if conflict_flag:
            confidence *= 0.8 

    diagnostics = {
        "focus_score": round(max(0, 1.0 - (entropy / 2.0)), 4), 
        "consensus_score": round(consensus_signal, 4),
        "entropy": round(entropy, 4),
        "std_dev": round(std_dev, 4)
    }

    return max(0.0, min(1.0, confidence)), diagnostics


def scale_confidence_for_ui(raw_confidence: float) -> float:
    """
    ⚖️ HUMANE PERCEPTION SCALING
    Maps technical vector distance to a 'Human Trust' percentage.
    """
    if raw_confidence <= 0:
        return 0.0

    # Sigmoid-style boost: Maps 0.05 technical score to ~70% perceived trust
    scaled = 1.0 - math.exp(-22 * raw_confidence)
    
    # Floor of 70% for anything passing the initial gate
    ui_confidence = 0.7 + (scaled * 0.29) 
    
    return round(max(0.0, min(0.99, ui_confidence)), 4)