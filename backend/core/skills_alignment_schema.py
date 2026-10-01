SKILLS_ALIGNMENT_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "skills_alignment_score": {
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
        "alignment_risk": {
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
        "core_requirements_satisfied": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "partial_requirements": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "missing_critical_requirements": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "skills_alignment_score",
        "rating",
        "alignment_risk",
        "summary",
        "primary_factors",
        "core_requirements_satisfied",
        "partial_requirements",
        "missing_critical_requirements",
    ],
}
