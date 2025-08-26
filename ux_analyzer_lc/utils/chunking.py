from __future__ import annotations

def sliding_windows(text: str, window_size: int, overlap: int) -> list[str]:
    if window_size <= 0:
        return [text]
    chunks, start, n = [], 0, len(text)
    step = max(1, window_size - overlap)
    while start < n:
        end = min(n, start + window_size)
        chunks.append(text[start:end])
        if end == n:
            break
        start += step
    return chunks
