from google.adk.agents import Agent


summarizer_agent = Agent(
    name="summarizer_agent",
    model="gemini-2.5-flash",
    instruction=(
        "Synthesize RAG and SQL evidence into one concise answer. "
        "Preserve every citation and do not invent unsupported facts. "
        'Return JSON: {"answer": string, "citations": array, '
        '"confidence": number}.'
    ),
)
