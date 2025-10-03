
import re
from typing import List


def clean_text(text: str) -> str:
    if not text:
        return ""
    
    # Replace non-breaking spaces
    text = text.replace('\xa0', ' ')

    # normalize newlines
    text = re.sub(r"\r\n|\r", "\n", text)

    # collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # trim spaces per line
    text = '\n'.join(line.strip() for line in text.splitlines())

    # collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    text = clean_text(text)
    if not text:
        return []

    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""

    for s in sentences:
        if len(current) + len(s) <= chunk_size:
            current = (current + " " + s).strip()
        else:
            if current:
                chunks.append(current)
            # If the sentence itself is too long, split by characters
            if len(s) > chunk_size:
                for i in range(0, len(s), chunk_size - overlap):
                    part = s[i:i + (chunk_size - overlap)].strip()
                    if part:
                        chunks.append(part)
                current = ""
            else:
                current = s
    if current:
        chunks.append(current)

    # ensuring minimal overlap between subsequent chunks
    final = []
    for i, c in enumerate(chunks):
        if i == 0:
            final.append(c)
        else:
            # creating overlap from previous
            overlap_text = final[-1][-overlap:] if overlap and len(final[-1]) >= overlap else ""
            if overlap_text:
                final.append((overlap_text + " " + c).strip())
            else:
                final.append(c)
    return final
