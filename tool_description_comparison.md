# WEAK — LLM will misuse this

{
"name": "search",
"description": "Search for things",
"input_schema": {
"type": "object",
"properties": {
"q": {"type": "string"}
},
"required": ["q"]
}
}

# STRONG — LLM uses this correctly

{
"name": "web_search",
"description": """Search the web for current information.
Use this when the user asks about recent events, facts you are unsure about,
prices, news, or anything that requires up-to-date information.
Do NOT use for general knowledge questions you already know the answer to.""",
"input_schema": {
"type": "object",
"properties": {
"query": {
"type": "string",
"description": "A focused search query. Be specific. E.g. 'Python 3.12 new features' not just 'Python'"
},
"max_results": {
"type": "integer",
"description": "Number of results to return. Default 5, max 10."
}
},
"required": ["query"]
}
}
