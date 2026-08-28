import hashlib
import math


def embed(text: str, dimensions: int = 384) -> list[float]:
    # Deterministic local embedding for development/testing only.
    raw = hashlib.sha256(text.encode()).digest()
    values = [
        (raw[index % len(raw)] / 255.0) * 2 - 1 for index in range(dimensions)
    ]
    norm = math.sqrt(sum(value * value for value in values)) or 1
    return [value / norm for value in values]


def generate_answer(question: str, contexts: list[dict[str, object]]) -> str:
    """Produce the deterministic MVP answer from retrieved document chunks."""
    if not contexts:
        return "I could not find relevant information in the indexed knowledge base."
    snippets = "\n".join(
        f"[{index + 1}] {context['content']}"
        for index, context in enumerate(contexts)
    )
    return (
        "Based on the indexed knowledge, here are the most relevant findings:\n\n"
        f"{snippets}\n\nSources are shown below."
    )
