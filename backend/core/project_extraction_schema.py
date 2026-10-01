PROJECT_EXTRACTION_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {
                        "type": "string",
                    },
                    "description": {
                        "type": "string",
                    },
                    "technologies": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                    "responsibilities": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                    "outcomes": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                    "quantified_metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                    "production_signals": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                    "evidence": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
                "required": [
                    "name",
                    "description",
                    "technologies",
                    "responsibilities",
                    "outcomes",
                    "quantified_metrics",
                    "production_signals",
                    "evidence",
                ],
            },
        },
    },
    "required": [
        "projects",
    ],
}
