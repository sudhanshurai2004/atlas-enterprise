from google.adk.tools import FunctionTool

from app.retrieval.hybrid_retriever import retrieve
from app.tools.sql_tool import run_sql


rag_retrieve_tool = FunctionTool(
    func=retrieve,
)

sql_query_tool = FunctionTool(
    func=run_sql,
)
