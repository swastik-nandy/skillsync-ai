import re


# --------------- TEXT CLEANING ---------------

def clean_text(text: str | bytes) -> str:
    if isinstance(text, bytes):
        text = text.decode(
            "utf-8",
            errors="ignore",
        )

    text = re.sub(
        r"\\s+",
        " ",
        text,
    )

    return text.strip()
