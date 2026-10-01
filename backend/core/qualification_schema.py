QUALIFICATION_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "qualification_score": {
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
        "qualification_risk": {
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
        "satisfied_qualifications": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "partial_qualifications": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "missing_critical_qualifications": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "qualification_score",
        "rating",
        "qualification_risk",
        "summary",
        "primary_factors",
        "satisfied_qualifications",
        "partial_qualifications",
        "missing_critical_qualifications",
    ],
}
