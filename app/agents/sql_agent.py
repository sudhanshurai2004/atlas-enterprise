from google.adk.agents import Agent

from app.agents.tools import sql_query_tool


sql_agent = Agent(
    name="sql_agent",
    model="gemini-2.5-flash",
    instruction=(
        "Use the sql_query tool for structured customer billing questions. "
        "Only use returned SQL rows as evidence. "
        'Return JSON: {"answer": string, "citations": array, '
        '"confidence": number}.'
    ),
    tools=[sql_query_tool],
)
