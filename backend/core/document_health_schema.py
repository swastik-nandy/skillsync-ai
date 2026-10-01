DOCUMENT_HEALTH_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "document_health_score": {
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
        "processing_risk": {
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
        "critical_issues": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "document_health_score",
        "rating",
        "processing_risk",
        "summary",
        "primary_factors",
        "critical_issues",
    ],
}
