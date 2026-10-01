EXPERIENCE_FIT_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "experience_fit_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
        },
        "rating": {
            "type": "string",
            "enum": [
                "excellent",
                "strong",
                "good",
                "fair",
                "weak",
            ],
        },
        "experience_risk": {
            "type": "string",
            "enum": [
                "low",
                "moderate",
                "high",
                "severe",
            ],
        },
        "summary": {
            "type": "string",
        },
        "primary_factors": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "factor": {
                        "type": "string",
                    },
                    "impact": {
                        "type": "string",
                        "enum": [
                            "positive",
                            "negative",
                            "neutral",
                        ],
                    },
                    "impact_strength": {
                        "type": "string",
                        "enum": [
                            "low",
                            "medium",
                            "high",
                        ],
                    },
                    "reason": {
                        "type": "string",
                    },
                },
                "required": [
                    "factor",
                    "impact",
                    "impact_strength",
                    "reason",
                ],
            },
        },
        "core_experience_satisfied": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "partial_experience_requirements": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "missing_critical_experience": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "experience_fit_score",
        "rating",
        "experience_risk",
        "summary",
        "primary_factors",
        "core_experience_satisfied",
        "partial_experience_requirements",
        "missing_critical_experience",
    ],
}
