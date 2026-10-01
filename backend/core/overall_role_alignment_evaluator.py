import json
import os
from pathlib import Path
import tomllib

from dotenv import load_dotenv
from groq import Groq

from core.overall_role_alignment_schema import (
    OVERALL_ROLE_ALIGNMENT_RESPONSE_SCHEMA,
)
from core.schemas import (
    OverallRoleAlignmentAssessment,
    OverallRoleAlignmentContext,
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
    / "overall_role_alignment.toml"
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
    "overall_role_alignment"
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

def evaluate_overall_role_alignment(
    context: OverallRoleAlignmentContext,
) -> OverallRoleAlignmentAssessment:
    context_json = json.dumps(
        context.model_dump(
            mode="json"
        ),
        indent=2,
    )

    user_prompt = (
        prompt_config[
            "user_prompt"
        ]
        .replace(
            "{context_json}",
            context_json,
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
                "name": "overall_role_alignment",
                "strict": True,
                "schema": (
                    OVERALL_ROLE_ALIGNMENT_RESPONSE_SCHEMA
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
            "Overall role-alignment evaluator "
            "returned an empty response."
        )

    return (
        OverallRoleAlignmentAssessment
        .model_validate_json(
            content
        )
    )
