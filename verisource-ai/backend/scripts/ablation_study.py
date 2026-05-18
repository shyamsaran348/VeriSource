# scripts/ablation_study.py

import sys
import os
import json
from typing import List, Dict

# Add the root backend directory to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(BACKEND_DIR)

from app.decision.engine import make_decision

def run_experiment(dataset: List[Dict], **kwargs) -> Dict:
    stats = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    for entry in dataset:
        expected = entry['expected_decision']
        mock = entry['mock_input']
        
        dec = make_decision(
            mode="policy",
            query_str=entry['query'],
            similarities=mock['similarities'],
            conflict_flag=mock['conflict_flag'],
            model_flag_insufficient=mock['model_flag_insufficient'],
            **kwargs
        )
        
        actual = dec['decision']
        if expected == "refused":
            if actual == "refused":
                stats["tp"] += 1
            else:
                stats["fn"] += 1 # Unsafe Approval
        else: # approved
            if actual == "approved":
                stats["tn"] += 1
            else:
                stats["fp"] += 1
                
    # Calculate Unsafe Approval Rate (UAR)
    unsafe_cases = len([e for e in dataset if e['expected_decision'] == 'refused'])
    uar = stats["fn"] / unsafe_cases if unsafe_cases > 0 else 0
    return {"uar": uar, "stats": stats}

def main():
    dataset_path = os.path.join(SCRIPT_DIR, 'eval_dataset.json')
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)

    print("====================================================")
    print("VERISOURCE AI: GOVERNANCE ABLATION STUDY")
    print("====================================================\n")
    print(f"{'Condition':<30} | {'Unsafe Approval Rate':<20}")
    print("-" * 55)

    experiments = [
        ("Full Governance (VeriSource)", {}),
        ("Ablation: No Entropy Penalty", {"bypass_entropy": True}),
        ("Ablation: No Conflict Detection", {"bypass_conflict": True}),
        ("Ablation: No LLM Veto", {"bypass_veto": True}),
        ("Vanilla RAG (No Governance)", {"bypass_governance": True})
    ]

    for name, params in experiments:
        results = run_experiment(dataset, **params)
        print(f"{name:<30} | {results['uar']:>19.2%}")

    print("\n[RESEARCH CONCLUSION]")
    print("The ablation study quantifies the safety contribution of each governance signal.")
    print("Lower Unsafe Approval Rate indicates higher reliability.")
    print("====================================================")

if __name__ == "__main__":
    main()
