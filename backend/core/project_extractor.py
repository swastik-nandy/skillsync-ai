import os
from pathlib import Path
import tomllib

from dotenv import load_dotenv
from groq import Groq

from core.project_extraction_schema import (
    PROJECT_EXTRACTION_RESPONSE_SCHEMA,
)
from core.schemas import ProjectExtractionResult


# --------------- PATHS ---------------

BACKEND_ROOT = Path(
    __file__
).resolve().parents[1]

CONFIG_PATH = BACKEND_ROOT / "config.toml"

PROMPT_PATH = (
    BACKEND_ROOT
    / "prompts"
    / "project_extraction.toml"
)


# --------------- CONFIG ---------------

load_dotenv(
    BACKEND_ROOT
    / ".env"
)

with CONFIG_PATH.open("rb") as file:
    config = tomllib.load(file)

with PROMPT_PATH.open("rb") as file:
    prompt_config = tomllib.load(file)

llm_config = config[
    "llm"
][
    "project_extraction"
]


# --------------- CLIENT ---------------

api_key = os.getenv(
    "GROQ_API_KEY"
)

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is not configured."
    )

client = Groq(
    api_key=api_key
)


# --------------- EXTRACTION ---------------

def extract_projects(
    resume_text: str,
) -> ProjectExtractionResult:
    if not resume_text.strip():
        raise ValueError(
            "Resume text cannot be empty."
        )

    user_prompt = (
        prompt_config[
            "user_prompt"
        ]
        .replace(
            "{resume_text}",
            resume_text,
        )
    )

    response = client.chat.completions.create(
        model=llm_config[
            "model"
        ],
        messages=[
            {
                "role": "system",
                "content": prompt_config[
                    "system_prompt"
                ],
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=llm_config[
            "temperature"
        ],
        reasoning_effort=llm_config[
            "reasoning_effort"
        ],
        include_reasoning=llm_config[
            "include_reasoning"
        ],
        max_completion_tokens=llm_config[
            "max_completion_tokens"
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "project_extraction",
                "strict": True,
                "schema": (
                    PROJECT_EXTRACTION_RESPONSE_SCHEMA
                ),
            },
        },
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    if not content:
        raise RuntimeError(
            "Project extractor returned an empty response."
        )

    return (
        ProjectExtractionResult
        .model_validate_json(
            content
        )
    )
