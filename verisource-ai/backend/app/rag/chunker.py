# app/rag/chunker.py

import re
from typing import List

CHUNK_SIZE   = 800   # Optimized for MiniLM's 256-token window
OVERLAP      = 200   # Ensures context continuity between adjacent chunks
MIN_CHUNK    = 80    # Discards noise/tiny fragments

# Regex: Detects regulatory section headings (e.g., '7.1', 'Article 5')
# This allows us to keep specific clauses together in one chunk.
_HEADING_RE = re.compile(
    r'^(?:'
    r'\d+\.\d*\s'           
    r'|(?:Clause|Article|Section|Chapter|Regulation|Rule)\s+\d'  
    r'|[A-Z][A-Z\s]{4,}:'  
    r')',
    re.MULTILINE
)

def _split_sentences(text: str) -> List[str]:
    """
    Splits text into sentences while preserving technical abbreviations.
    Prevents false splits on terms like 'Cl. 7.1' or 'Ref. No.'.
    """
    protected = re.sub(r'(Cl|Art|Sec|Reg|No|Para|vs|viz|etc|e\.g|i\.e)\.',
                       r'\1<DOT>', text)
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9\(])', protected)
    return [p.replace('<DOT>', '.').strip() for p in parts if p.strip()]

def chunk_text(text: str) -> List[str]:
    """
    Semantic Chunker: Section-aware and Sentence-boundary aligned.
    
    Strategy:
    1. Pre-split on section headings to preserve document structure.
    2. Within each section, split into sentences.
    3. Pack sentences into chunks of ~800 chars with ~200 chars overlap.
    """
    if not text or not text.strip():
        return []

    sections = []
    parts = _HEADING_RE.split(text)
    headings = _HEADING_RE.findall(text)
    
    if parts[0].strip():
        sections.append(parts[0].strip())
    for heading, body in zip(headings, parts[1:]):
        sections.append(f"{heading}{body}".strip())

    chunks: List[str] = []
    for section in sections:
        sentences = _split_sentences(section)
        current_chunk = ""

        for sentence in sentences:
            # Greedy packing with overlap
            if current_chunk and (len(current_chunk) + 1 + len(sentence)) > CHUNK_SIZE:
                chunks.append(current_chunk.strip())
                tail = current_chunk[-OVERLAP:] if len(current_chunk) > OVERLAP else current_chunk
                current_chunk = tail + " " + sentence
            else:
                current_chunk = (current_chunk + " " + sentence).strip() if current_chunk else sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

    # Final noise filtering and deduplication
    final_chunks = []
    seen = set()
    for c in chunks:
        if len(c) < MIN_CHUNK: continue
        key = c[:60] # Fast hash key
        if key not in seen:
            seen.add(key)
            final_chunks.append(c)

    return final_chunks