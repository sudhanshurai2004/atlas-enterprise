from google.adk.agents import Agent

from app.agents.tools import rag_retrieve_tool


rag_agent = Agent(
    name="rag_agent",
    model="gemini-3.8-flash",
    instruction=(
        "Retrieve enterprise knowledge with the rag_retrieve tool. "
        "Answer only from retrieved citations. "
        'Return JSON: {"answer": string, "citations": array, '
        '"confidence": number}.'
    ),
    tools=[rag_retrieve_tool],
)
