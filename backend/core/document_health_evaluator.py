import json
import os
from pathlib import Path
import tomllib

from dotenv import load_dotenv
from groq import Groq

from core.document_health_schema import (
    DOCUMENT_HEALTH_RESPONSE_SCHEMA,
)
from core.schemas import (
    DocumentHealthAssessment,
    ResumeDiagnosticsReport,
)


# --------------- PATHS ---------------

BACKEND_ROOT = Path(
    __file__
).resolve().parents[1]

CONFIG_PATH = (
    BACKEND_ROOT
    / "config.toml"
)

PROMPT_PATH = (
    BACKEND_ROOT
    / "prompts"
    / "document_health.toml"
)


# --------------- CONFIG ---------------

load_dotenv(
    BACKEND_ROOT
    / ".env"
)

with CONFIG_PATH.open(
    "rb"
) as file:
    config = tomllib.load(file)

with PROMPT_PATH.open(
    "rb"
) as file:
    prompt_config = tomllib.load(file)

llm_config = config[
    "llm"
][
    "document_health"
]

LLM_MODEL = llm_config[
    "model"
]

LLM_TEMPERATURE = llm_config[
    "temperature"
]

LLM_REASONING_EFFORT = llm_config[
    "reasoning_effort"
]

LLM_INCLUDE_REASONING = llm_config[
    "include_reasoning"
]

LLM_MAX_COMPLETION_TOKENS = llm_config[
    "max_completion_tokens"
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


# --------------- EVALUATION ---------------

def evaluate_document_health(
    diagnostics: ResumeDiagnosticsReport,
) -> DocumentHealthAssessment:
    diagnostics_json = json.dumps(
        diagnostics.model_dump(
            mode="json"
        ),
        indent=2,
    )

    system_prompt = prompt_config[
        "system_prompt"
    ]

    user_prompt = (
        prompt_config[
            "user_prompt"
        ]
        .replace(
            "{diagnostics_json}",
            diagnostics_json,
        )
    )

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=LLM_TEMPERATURE,
        reasoning_effort=LLM_REASONING_EFFORT,
        include_reasoning=LLM_INCLUDE_REASONING,
        max_completion_tokens=LLM_MAX_COMPLETION_TOKENS,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "document_health_assessment",
                "strict": True,
                "schema": DOCUMENT_HEALTH_RESPONSE_SCHEMA,
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
            "Document-health evaluator returned an empty response."
        )

    return (
        DocumentHealthAssessment
        .model_validate_json(
            content
        )
    )
