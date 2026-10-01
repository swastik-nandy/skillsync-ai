import json
import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from core.schemas import (
    FEEDBACK_RESPONSE_SCHEMA,
    FeedbackReport,
)


# --------------- PATHS ---------------

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BACKEND_DIR / ".env"
CONFIG_PATH = BACKEND_DIR / "config.toml"


# --------------- CONFIG ---------------

load_dotenv(ENV_PATH)

with CONFIG_PATH.open("rb") as file:
    config = tomllib.load(file)

feedback_config = config["llm"]["feedback_generation"]

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

LLM_PROVIDER = feedback_config["provider"]
LLM_MODEL = feedback_config["model"]
LLM_TEMPERATURE = feedback_config["temperature"]
LLM_REASONING_EFFORT = feedback_config["reasoning_effort"]
LLM_INCLUDE_REASONING = feedback_config["include_reasoning"]
LLM_MAX_COMPLETION_TOKENS = feedback_config["max_completion_tokens"]

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not configured")

if LLM_PROVIDER != "groq":
    raise ValueError(
        f"Unsupported LLM provider: {LLM_PROVIDER}"
    )


# --------------- CLIENT ---------------

client = Groq(
    api_key=GROQ_API_KEY,
)


# --------------- FEEDBACK GENERATION ---------------

def generate_feedback(
    system_prompt: str,
    user_prompt: str,
) -> FeedbackReport:
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
                "name": "feedback_report",
                "strict": True,
                "schema": FEEDBACK_RESPONSE_SCHEMA,
            },
        },
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("Groq returned an empty response")

    return FeedbackReport.model_validate(
        json.loads(content)
    )
