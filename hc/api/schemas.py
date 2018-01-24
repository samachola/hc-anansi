check = {
    "properties": {
        "name": {"type": "string"},
        "tags": {"type": "string"},
        "timeout": {"type": "number", "minimum": 60, "maximum": 5184000},
        "grace": {"type": "number", "minimum": 60, "maximum": 5184000},
        "channels": {"type": "string"}
    }
}
