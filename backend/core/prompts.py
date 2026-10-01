import tomllib
from pathlib import Path


# --------------- PATHS ---------------

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BACKEND_DIR / "prompts"


# --------------- LOADING ---------------

def load_prompt(name: str) -> dict[str, str]:
    path = PROMPTS_DIR / f"{name}.toml"

    if not path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {path}"
        )

    with path.open("rb") as file:
        return tomllib.load(file)
