# Generated from src/content/chapters (chapter 5) by `npm run labs`. Edit the chapter, not this file.
tools = [
    {
        "name": "get_order_status",
        "description": (
            "Look up the current shipping status of a customer order. "
            "Use this whenever the user asks where an order is or when it will arrive. "
            "Returns status, carrier and estimated delivery date."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Order number, e.g. '1182'"},
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    }
]
