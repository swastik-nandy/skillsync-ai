OVERALL_ROLE_ALIGNMENT_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "overall_role_alignment_score": {
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
        "screening_risk": {
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
                    "section": {
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
                    "section",
                    "impact",
                    "impact_strength",
                    "reason",
                ],
            },
        },
        "strongest_alignment_areas": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "critical_gaps": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "priority_improvements": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "overall_role_alignment_score",
        "rating",
        "screening_risk",
        "summary",
        "primary_factors",
        "strongest_alignment_areas",
        "critical_gaps",
        "priority_improvements",
    ],
}
