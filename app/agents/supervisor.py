from google.adk.agents import Agent

from app.agents.critic_agent import critic_agent
from app.agents.rag_agent import rag_agent
from app.agents.sql_agent import sql_agent
from app.agents.summarizer_agent import summarizer_agent


supervisor = Agent(
    name="atlas_supervisor",
    model="gemini-2.5-flash",
    instruction=(
        "Decompose the question. Delegate to exactly one sub-agent at a time "
        "using evidence needs: rag_agent for runbooks or documents, "
        "sql_agent for customer billing data, and summarizer_agent for synthesis. "
        "Evaluate evidence, repeat delegation when needed, and answer only "
        "with supported facts and citations. Critic weak answers for at most "
        "2 reflection rounds."
    ),
    sub_agents=[rag_agent, sql_agent, summarizer_agent, critic_agent],
)
