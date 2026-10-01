EVIDENCE_QUALITY_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "evidence_quality_score": {
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
        "evidence_risk": {
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
                    "severity": {
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
                    "severity",
                    "reason",
                ],
            },
        },
        "weak_evidence_requirements": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "unevidenced_requirements": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "evidence_quality_score",
        "rating",
        "evidence_risk",
        "summary",
        "primary_factors",
        "weak_evidence_requirements",
        "unevidenced_requirements",
    ],
}
