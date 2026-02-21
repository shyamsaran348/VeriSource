"""
chunker.py — Sentence-aware, section-preserving text chunker.

Improvements over the naive character-split approach:
- Respects sentence boundaries (never splits mid-sentence)
- Larger chunk size (800 chars) to use more of MiniLM's 256-token window
- Larger overlap (200 chars) for better context continuity between chunks
- Section-heading detection: splits on regulatory headings so each clause
  stays together rather than being split across two chunks
- Deduplication: skips chunks that are identical to the previous

MiniLM token budget: 256 tokens ≈ 1,000 characters max.
Optimal chunk: 800 chars ≈ 150–180 tokens — well within budget,
leaving room for the query tokens during retrieval.
"""

import re
from typing import List


# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────

CHUNK_SIZE   = 800   # target characters per chunk (was 500)
OVERLAP      = 200   # overlap between chunks (was 100)
MIN_CHUNK    = 80    # discard chunks shorter than this (noise)

# Regex: detect regulatory-style section headings
# Matches lines that look like: "7.", "7.1", "Clause 7.1", "ARTICLE 5", etc.
_HEADING_RE = re.compile(
    r'^(?:'
    r'\d+\.\d*\s'           # "7.1 " or "7. "
    r'|(?:Clause|Article|Section|Chapter|Regulation|Rule)\s+\d'  # "Clause 7"
    r'|[A-Z][A-Z\s]{4,}:'  # ALL CAPS heading ending with ":"
    r')',
    re.MULTILINE
)


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _split_sentences(text: str) -> List[str]:
    """
    Split text into sentences, keeping the delimiter attached.
    Handles common abbreviations to avoid false splits on e.g. "Cl. 7.1".
    """
    # Protect common abbreviations from being split
    protected = re.sub(r'(Cl|Art|Sec|Reg|No|Para|vs|viz|etc|e\.g|i\.e)\.',
                       r'\1<DOT>', text)
    # Split on sentence-ending punctuation followed by whitespace + capital
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9\(])', protected)
    # Restore protected dots
    return [p.replace('<DOT>', '.').strip() for p in parts if p.strip()]


def _split_on_headings(text: str) -> List[str]:
    """
    Pre-split the document at regulatory section headings so that
    each section starts a fresh chunk boundary.
    """
    parts = _HEADING_RE.split(text)
    headings = _HEADING_RE.findall(text)

    # Re-attach heading to its section body
    sections = []
    if parts[0].strip():
        sections.append(parts[0].strip())
    for heading, body in zip(headings, parts[1:]):
        combined = f"{heading}{body}".strip()
        if combined:
            sections.append(combined)

    return sections if sections else [text]


# ──────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────

def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = OVERLAP,
) -> List[str]:
    """
    Split document text into overlapping, sentence-boundary-aligned chunks.

    Strategy:
    1. Pre-split on section headings (regulatory structure preservation)
    2. Within each section, split into sentences
    3. Greedily pack sentences into chunks of ≤ chunk_size characters
    4. Add overlap by prepending last N chars of the previous chunk

    Args:
        text:       Full document text
        chunk_size: Target max characters per chunk (default 800)
        overlap:    Characters of overlap between consecutive chunks (default 200)

    Returns:
        List of non-empty, deduplicated text chunks
    """
    if not text or not text.strip():
        return []

    # Step 1 — section-level pre-split
    sections = _split_on_headings(text)

    raw_chunks: List[str] = []

    for section in sections:
        sentences = _split_sentences(section)
        if not sentences:
            continue

        current_chunk = ""

        for sentence in sentences:
            # If adding this sentence would exceed chunk_size, flush
            if current_chunk and (len(current_chunk) + 1 + len(sentence)) > chunk_size:
                raw_chunks.append(current_chunk.strip())
                # Start new chunk with overlap from end of previous
                tail = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = tail + " " + sentence
            else:
                current_chunk = (current_chunk + " " + sentence).strip() if current_chunk else sentence

        # Flush remaining
        if current_chunk.strip():
            raw_chunks.append(current_chunk.strip())

    # Step 2 — filter noise and deduplicate
    seen = set()
    chunks: List[str] = []
    for chunk in raw_chunks:
        if len(chunk) < MIN_CHUNK:
            continue
        key = chunk[:60]  # fast dedup key on first 60 chars
        if key in seen:
            continue
        seen.add(key)
        chunks.append(chunk)

    return chunks