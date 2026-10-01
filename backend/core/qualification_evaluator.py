import json
import os
from pathlib import Path
import tomllib

from dotenv import load_dotenv
from groq import Groq

from core.qualification_schema import (
    QUALIFICATION_RESPONSE_SCHEMA,
)
from core.schemas import (
    QualificationAssessment,
    QualificationDiagnostics,
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
    / "qualification_alignment.toml"
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
    "qualification_alignment"
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

def evaluate_qualification_alignment(
    diagnostics: QualificationDiagnostics,
) -> QualificationAssessment:
    diagnostics_json = json.dumps(
        diagnostics.model_dump(
            mode="json"
        ),
        indent=2,
    )

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
                "name": "qualification_assessment",
                "strict": True,
                "schema": QUALIFICATION_RESPONSE_SCHEMA,
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
            "Qualification evaluator returned "
            "an empty response."
        )

    return (
        QualificationAssessment
        .model_validate_json(
            content
        )
    )
