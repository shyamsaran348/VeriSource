# app/llm/prompt_policy.py

def build_policy_prompt(query: str, evidence_blocks: list[str]) -> str:
    evidence_text = "\n\n".join(evidence_blocks)

    return f"""
You are answering a university policy question.

Rules:
- Use ONLY the provided evidence.
- If evidence does not clearly support an answer, say: INSUFFICIENT_EVIDENCE
- Do NOT guess.
- Do NOT assume.
- Do NOT add external knowledge.
- Language must be deterministic (must, shall, required).

Question:
{query}

Evidence:
{evidence_text}

Provide a clear and direct answer.
"""