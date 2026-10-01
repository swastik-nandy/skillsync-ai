import json
import os
from pathlib import Path
import tomllib

from dotenv import load_dotenv
from groq import Groq

from core.project_relevance_schema import (
    PROJECT_RELEVANCE_RESPONSE_SCHEMA,
)
from core.schemas import (
    ProjectRelevanceAssessment,
    ProjectRelevanceDiagnostics,
    RequirementImportanceItem,
    ResumeProject,
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
    / "project_relevance.toml"
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
    "project_relevance"
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

def evaluate_project_relevance(
    projects: list[ResumeProject],
    diagnostics: ProjectRelevanceDiagnostics,
    requirement_profile: list[RequirementImportanceItem],
) -> ProjectRelevanceAssessment:
    projects_json = json.dumps(
        [
            item.model_dump(
                mode="json"
            )
            for item in projects
        ],
        indent=2,
    )

    diagnostics_json = json.dumps(
        diagnostics.model_dump(
            mode="json"
        ),
        indent=2,
    )

    requirements_json = json.dumps(
        [
            item.model_dump(
                mode="json"
            )
            for item in requirement_profile
        ],
        indent=2,
    )

    user_prompt = (
        prompt_config[
            "user_prompt"
        ]
        .replace(
            "{projects_json}",
            projects_json,
        )
        .replace(
            "{diagnostics_json}",
            diagnostics_json,
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
                "name": "project_relevance_assessment",
                "strict": True,
                "schema": (
                    PROJECT_RELEVANCE_RESPONSE_SCHEMA
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
            "Project relevance evaluator returned "
            "an empty response."
        )

    return (
        ProjectRelevanceAssessment
        .model_validate_json(
            content
        )
    )
