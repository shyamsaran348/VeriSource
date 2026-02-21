"""
LLM Provider — Phase 5 Controlled Generation.

Architecture constraints (enforced here):
  ✅ LLM receives ONLY: user query + extracted evidence text
  ❌ LLM NEVER receives: similarity scores, conflict flags, document_id,
                          metadata, authority, version, other documents

Groq API is used (gsk_... key from .env).
Temperature = 0 for deterministic, evidence-grounded output.
No streaming.

Special output protocol:
  If the evidence does not support the query, the model must output exactly:
      INSUFFICIENT_EVIDENCE
  This is parsed by response_parser.py — NOT decided by the model autonomously.
"""

import os
from groq import Groq

_client = None


def _get_groq_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set in environment.")
        _client = Groq(api_key=api_key)
    return _client


# ──────────────────────────────────────────────────────────────
# Mode-specific prompts
# ──────────────────────────────────────────────────────────────

POLICY_SYSTEM_PROMPT = """You are a strict policy verification assistant.

Your ONLY job is to answer questions using the provided policy document excerpts.

Rules you MUST follow:
1. Use ONLY the evidence provided. Do NOT use outside knowledge.
2. The extracted evidence may be messy, incomplete, or lack context due to PDF parsing. You must synthesize the core rule clearly into a professional, formal response.
3. Use deterministic language: "must", "shall", "is required", "is prohibited".
4. Do NOT summarize or add external context. State only the rules found in the text.
5. Do NOT mention the evidence process, document IDs, scores, or internal system details."""

RESEARCH_SYSTEM_PROMPT = """You are a research evidence synthesis assistant.

Your ONLY job is to synthesize findings from the provided research document excerpts.

Rules you MUST follow:
1. Use ONLY the evidence provided. Do NOT use outside knowledge.
2. The extracted evidence may be messy or incomplete. You must synthesize the core findings clearly into a professional, formal response.
3. Use probabilistic language: "suggests", "indicates", "may imply", "the evidence shows".
4. Do NOT present uncertain findings as facts.
5. Do NOT mention the evidence process, document IDs, scores, or internal system details."""


def generate_answer(
    mode: str,
    query: str,
    evidence_blocks: list[str],
) -> str:
    """
    Call Groq API with ONLY query + evidence text.
    Returns raw model output string.

    Args:
        mode:            "policy" or "research" (selects system prompt)
        query:           The user's question
        evidence_blocks: List of raw evidence text strings (NO scores, NO metadata)

    Returns:
        raw string from model — either an answer or "INSUFFICIENT_EVIDENCE"
    """
    system_prompt = POLICY_SYSTEM_PROMPT if mode == "policy" else RESEARCH_SYSTEM_PROMPT

    # Build evidence block text — ONLY text, nothing else
    if evidence_blocks:
        evidence_text = "\n\n---\n\n".join(
            f"[Evidence {i+1}]\n{text.strip()}"
            for i, text in enumerate(evidence_blocks)
        )
    else:
        evidence_text = "(No evidence retrieved)"

    user_message = f"""Question: {query}

Evidence from document:
{evidence_text}

Answer (use ONLY the evidence above):"""

    client = _get_groq_client()

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0,          # Deterministic
        max_tokens=512,
        stream=False,           # No streaming
    )

    return response.choices[0].message.content.strip()