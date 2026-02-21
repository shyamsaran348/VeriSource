# app/llm/prompt_research.py

def build_research_prompt(query: str, evidence_blocks: list[str]) -> str:
    evidence_text = "\n\n".join(evidence_blocks)

    return f"""
You are analyzing a research paper.

Rules:
- Use ONLY the provided evidence.
- If evidence is insufficient, say: INSUFFICIENT_EVIDENCE
- You may express uncertainty.
- Do NOT invent conclusions.
- Do NOT add outside knowledge.

Question:
{query}

Evidence:
{evidence_text}

Provide an evidence-grounded explanation.
"""