import re
SPEAKER_RE = re.compile(r'^(\w+):\s', re.M)

def has_speakers(text: str) -> bool:
    return bool(SPEAKER_RE.search(text))

def split_by_speakers(text: str) -> list[str]:
    blocks, current = [], []
    for line in text.splitlines():
        if re.match(r'^\w+:', line):
            if current:
                blocks.append('\n'.join(current).strip())
                current = []
        current.append(line)
    if current:
        blocks.append('\n'.join(current).strip())
    return [b for b in blocks if b]
