PROJECT_RELEVANCE_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "projects_relevance_score": {
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
        "project_fit_risk": {
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
        "strongest_projects": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "partially_relevant_projects": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "missing_project_evidence": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "projects_relevance_score",
        "rating",
        "project_fit_risk",
        "summary",
        "primary_factors",
        "strongest_projects",
        "partially_relevant_projects",
        "missing_project_evidence",
    ],
}
