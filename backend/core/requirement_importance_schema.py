REQUIREMENT_IMPORTANCE_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "requirement": {
                        "type": "string",
                    },
                    "importance": {
                        "type": "string",
                        "enum": [
                            "MANDATORY",
                            "HIGH_PRIORITY",
                            "PREFERRED",
                            "OPTIONAL",
                        ],
                    },
                    "category": {
                        "type": "string",
                        "enum": [
                            "SKILL",
                            "EXPERIENCE",
                            "EDUCATION",
                            "CERTIFICATION",
                            "RESPONSIBILITY",
                            "OTHER",
                        ],
                    },
                    "jd_signal": {
                        "type": "string",
                    },
                    "reason": {
                        "type": "string",
                    },
                },
                "required": [
                    "requirement",
                    "importance",
                    "category",
                    "jd_signal",
                    "reason",
                ],
            },
        },
    },
    "required": [
        "requirements",
    ],
}
