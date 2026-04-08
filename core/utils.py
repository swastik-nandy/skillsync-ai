import re
from typing import Union

def clean_text(text: Union[str, bytes]) -> str:
    """Clean text by normalizing whitespace and decoding bytes."""
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="ignore")
    text = re.sub(r"\s+", " ", text)
    return text.strip()
