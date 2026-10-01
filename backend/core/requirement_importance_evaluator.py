import json
import os
from pathlib import Path
import tomllib

from dotenv import load_dotenv
from groq import Groq

from core.requirement_importance_schema import (
    REQUIREMENT_IMPORTANCE_RESPONSE_SCHEMA,
)
from core.schemas import (
    RequirementImportanceEvaluation,
    RequirementImportanceReport,
    RequirementImportanceRequest,
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
    / "requirement_importance.toml"
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
    "requirement_importance"
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


# --------------- VALIDATION ---------------

def _validate_requirement_mapping(
    requested: list[str],
    returned: list[str],
) -> None:
    if len(requested) != len(returned):
        raise RuntimeError(
            "Requirement-importance evaluator returned "
            "a different number of requirements."
        )

    if len(set(returned)) != len(returned):
        raise RuntimeError(
            "Requirement-importance evaluator returned "
            "duplicate requirements."
        )

    if set(requested) != set(returned):
        raise RuntimeError(
            "Requirement-importance evaluator changed "
            "the supplied requirement set."
        )


# --------------- EVALUATION ---------------

def evaluate_requirement_importance(
    request: RequirementImportanceRequest,
) -> RequirementImportanceReport:
    if not request.jd_text.strip():
        raise ValueError(
            "Job description cannot be empty."
        )

    if not request.requirements:
        raise ValueError(
            "At least one requirement is required."
        )

    if len(set(request.requirements)) != len(
        request.requirements
    ):
        raise ValueError(
            "Requirements must not contain duplicates."
        )

    requirements_json = json.dumps(
        request.requirements,
        indent=2,
    )

    user_prompt = (
        prompt_config[
            "user_prompt"
        ]
        .replace(
            "{jd_text}",
            request.jd_text,
        )
        .replace(
            "{requirements_json}",
            requirements_json,
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
                "name": "requirement_importance",
                "strict": True,
                "schema": (
                    REQUIREMENT_IMPORTANCE_RESPONSE_SCHEMA
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
            "Requirement-importance evaluator "
            "returned an empty response."
        )

    evaluation = (
        RequirementImportanceEvaluation
        .model_validate_json(
            content
        )
    )

    returned_requirements = [
        item.requirement
        for item
        in evaluation.requirements
    ]

    _validate_requirement_mapping(
        request.requirements,
        returned_requirements,
    )

    mandatory = 0
    high_priority = 0
    preferred = 0
    optional = 0

    for item in evaluation.requirements:
        value = item.importance.value

        if value == "MANDATORY":
            mandatory += 1

        elif value == "HIGH_PRIORITY":
            high_priority += 1

        elif value == "PREFERRED":
            preferred += 1

        elif value == "OPTIONAL":
            optional += 1

    return RequirementImportanceReport(
        total_requirements=len(
            evaluation.requirements
        ),
        mandatory=mandatory,
        high_priority=high_priority,
        preferred=preferred,
        optional=optional,
        requirements=evaluation.requirements,
    )
