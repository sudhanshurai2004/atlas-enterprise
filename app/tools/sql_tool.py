import re
import sys
from typing import Any

import psycopg
import sqlglot
from sqlglot import exp
import vertexai
from vertexai.generative_models import GenerativeModel

from app.config import settings
from app.tools.schema_context import FEW_SHOT_EXAMPLES, TABLE_DDL


ALLOWED_TABLES = {"billing_customers"}
ALLOWED_COLUMNS = {
    "id",
    "name",
    "plan",
    "error_code",
    "error_at",
    "mrr_usd",
}


def generate_sql(question: str) -> str:
    examples = "\n".join(
        f"Question: {example_question}\nSQL: {example_sql}"
        for example_question, example_sql in FEW_SHOT_EXAMPLES
    )
    prompt = (
        "Generate exactly one PostgreSQL SELECT statement for this question.\n"
        "Use only the billing_customers table and its listed columns.\n"
        "Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, "
        "GRANT, REVOKE, COPY, CALL, or multiple statements.\n"
        f"{TABLE_DDL}\nExamples:\n{examples}\n"
        f"Question: {question}\nSQL:"
    )

    vertexai.init(
        project=settings.gcp_project_id,
        location=settings.gcp_region,
    )
    model = GenerativeModel("gemini-3.8-flash")
    response = model.generate_content(prompt)
    sql = response.text.strip().strip("`")
    sql = re.sub(r"^sql\s*", "", sql, flags=re.IGNORECASE)
    return sql.strip()


def validate_select(sql: str) -> tuple[bool, str]:
    try:
        expressions = sqlglot.parse(sql, read="postgres")
    except Exception as exc:
        return False, f"SQL parse error: {exc}"

    if len(expressions) != 1 or expressions[0] is None:
        return False, "Exactly one SQL statement is required"

    statement = expressions[0]
    if not isinstance(statement, exp.Select):
        return False, "Only SELECT statements are allowed"

    tables = {table.name.lower() for table in statement.find_all(exp.Table)}
    if not tables.issubset(ALLOWED_TABLES):
        return False, "Query references a table outside the allowlist"

    for column in statement.find_all(exp.Column):
        if column.name.lower() not in ALLOWED_COLUMNS:
            return False, f"Column '{column.name}' is outside the allowlist"

    return True, "valid"


def run_sql(question: str) -> dict[str, Any]:
    try:
        sql = generate_sql(question)
    except Exception as exc:
        return {"error": f"SQL generation failed: {type(exc).__name__}"}

    valid, message = validate_select(sql)
    if not valid:
        return {"error": message, "sql": sql}

    try:
        with psycopg.connect(
            settings.database_url,
            options="-c default_transaction_read_only=on",
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL statement_timeout = '5s'")
                cursor.execute(sql)
                columns = [
                    column.name
                    for column in cursor.description
                ] if cursor.description else []
                rows = cursor.fetchall()
    except Exception as exc:
        return {"error": f"Query execution failed: {type(exc).__name__}"}

    return {
        "sql": sql,
        "columns": columns,
        "rows": [
            [str(value) if value is not None else None for value in row]
            for row in rows
        ],
    }


if __name__ == "__main__":
    question_args = sys.argv[1:]
    if question_args[:1] == ["--q"]:
        question_args = question_args[1:]
    question = " ".join(question_args)
    print(run_sql(question))
