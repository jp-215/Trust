QUERY_GOLD_TOOL = {
    "name": "query_gold_table",
    "description": "Fetch the aggregated story record (claim matrix, outlet coverage) for a given story_id from the gold Delta table. Returns details about which outlets reported which claims.",
    "parameters": {
        "type": "object",
        "properties": {
            "story_id": {
                "type": "string",
                "description": "The unique story identifier to query",
            }
        },
        "required": ["story_id"],
    },
}


def dispatch(name: str, args: dict, gold_client) -> dict:
    if name == "query_gold_table":
        story_id = args.get("story_id")
        if not story_id:
            return {"error": "story_id is required"}
        result = gold_client.query_gold_table(story_id)
        if result is None:
            return {"error": f"no story_record found for story_id={story_id}"}
        return {"success": True, "story_record": result}
    raise ValueError(f"unknown tool: {name}")
