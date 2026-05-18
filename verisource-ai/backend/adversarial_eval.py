# adversarial_eval.py

import sys
import os
from typing import List

# Add the app directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from app.decision.engine import make_decision
from app.rag.conflict import detect_conflict

def run_adversarial_test(name: str, mode: str, query: str, similarities: List[float], model_flag_insufficient: bool = False):
    print(f"\n--- Test: {name} ---")
    print(f"Query: {query}")
    print(f"Mode: {mode}")
    print(f"Similarities: {similarities}")
    
    # Mocking evidence blocks for conflict detection
    evidence_blocks = [{"similarity": s} for s in similarities]
    conflict = detect_conflict(evidence_blocks, mode)
    
    decision = make_decision(
        mode=mode,
        query_str=query,
        similarities=similarities,
        conflict_flag=conflict,
        model_flag_insufficient=model_flag_insufficient
    )
    
    print(f"Conflict Detected: {conflict}")
    print(f"Decision: {decision['decision'].upper()}")
    print(f"Confidence Score: {decision['confidence_score']}")
    print(f"Reason: {decision['reason']}")
    if decision.get('explanation'):
        missing = decision['explanation'].get('missing_evidence_requirements', [])
        print(f"Missing Requirements: {missing}")
    
    return decision

def main():
    print("====================================================")
    print("VERISOURCE AI: ADVERSARIAL GOVERNANCE EVALUATION")
    print("====================================================")

    # CASE 1: The Hallucination Trap (Low Relevance)
    run_adversarial_test(
        name="Hallucination Trap (Policy)",
        mode="policy",
        query="What is the secret code for free tuition?",
        similarities=[0.02, 0.01, 0.005, 0.001], # Extremely low relevance
    )

    # CASE 2: The Contradiction Test (Unstable Evidence)
    # High scores but very spread out (High SD)
    run_adversarial_test(
        name="Contradiction Test (Policy)",
        mode="policy",
        query="Is the deadline Monday or Friday?",
        similarities=[0.90, 0.10, 0.05, 0.02], # Large gap -> Unstable
    )

    # CASE 3: Ambiguous Research (Tolerant)
    run_adversarial_test(
        name="Ambiguous Research (Research)",
        mode="research",
        query="Evaluate the impact of the 2024 policy shift.",
        similarities=[0.15, 0.12, 0.10, 0.08], # Weak but distributed signal
    )

    # CASE 4: LLM Insufficiency Flag (Sentinel Detection)
    run_adversarial_test(
        name="LLM Refusal Sentinel",
        mode="policy",
        query="Find the hidden clause about AI ethics.",
        similarities=[0.45, 0.40, 0.35], # Good retrieval but...
        model_flag_insufficient=True     # ...LLM says "I can't find this"
    )

    # CASE 5: High-Precision Consensus (The Gold Standard)
    run_adversarial_test(
        name="High-Precision Consensus",
        mode="policy",
        query="What is the CGPA requirement?",
        similarities=[0.85, 0.82, 0.80, 0.78], # Focused, high-score retrieval
    )

if __name__ == "__main__":
    main()
