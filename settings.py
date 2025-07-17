import os
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

TEMPERATURE = 0.2
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_aws_diagram",
            "description": "Generates an AWS architecture diagram from a given node/edge description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "object",
                        "properties": {
                            "nodes": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "type": {"type": "string"},
                                        "label": {"type": "string"},
                                        "group": {"type": "string"}
                                    },
                                    "required": ["id", "type", "label"]
                                }
                            },
                            "edges": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "from": {"type": "string"},
                                        "to": {"type": "string"}
                                    },
                                    "required": ["from", "to"]
                                }
                            }
                        },
                        "required": ["nodes", "edges"]
                    }
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ask_for_clarification",
            "description": "Asks the user a clarifying question to improve the architecture.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"}
                },
                "required": ["question"]
            }
        }
    }
]

