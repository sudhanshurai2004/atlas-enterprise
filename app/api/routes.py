import time
import uuid
from typing import Any

import psycopg
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.auth import get_current_user, issue_token, LoginRequest
from app.api.cache import get_cached_answer, set_cached_answer
from app.api.state import append_turn, get_history
from app.config import settings
from app.pricing import calculate_cost


router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    session_id: str


@router.post("/auth/token")
def auth_token(request: LoginRequest) -> dict[str, str]:
    return issue_token(request)


@router.post("/query")
def query(
    request: QueryRequest,
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    started = time.perf_counter()
    trace_id = str(uuid.uuid4())
    cached = get_cached_answer(request.question)

    if cached:
        answer = cached
        cache_hit = True
    else:
        answer = {
            "answer": (
                f"Atlas processed '{request.question}' with the multi-agent supervisor."
            ),
            "citations": [],
            "confidence": 0.5,
        }
        cache_hit = False
        set_cached_answer(request.question, answer)

    append_turn(request.session_id, request.question, answer["answer"])
    latency_ms = int((time.perf_counter() - started) * 1000)
    input_tokens = len(request.question.split())
    output_tokens = len(answer["answer"].split())
    cost_usd = calculate_cost(input_tokens, output_tokens)

    try:
        with psycopg.connect(settings.database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO query_logs
                        (question, answer, input_tokens, output_tokens,
                         latency_ms, cost_usd, trace_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        request.question,
                        answer["answer"],
                        input_tokens,
                        output_tokens,
                        latency_ms,
                        cost_usd,
                        trace_id,
                    ),
                )
    except psycopg.Error:
        pass

    return {
        **answer,
        "trace_id": trace_id,
        "cache_hit": cache_hit,
        "cost_usd": cost_usd,
        "latency_ms": latency_ms,
    }


@router.get("/history/{session_id}")
def history(
    session_id: str,
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    return {"session_id": session_id, "turns": get_history(session_id)}


@router.post("/query/stream")
def query_stream(
    request: QueryRequest,
    user: dict[str, str] = Depends(get_current_user),
) -> StreamingResponse:
    def events():
        response = query(request, user)
        words = response["answer"].split()
        for word in words:
            yield f"data: {word}\n\n"
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@router.get("/metrics")
def metrics(
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        with psycopg.connect(settings.database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        COALESCE(AVG(input_tokens + output_tokens), 0),
                        COALESCE(AVG(cost_usd), 0),
                        COALESCE(AVG(latency_ms), 0)
                    FROM (
                        SELECT * FROM query_logs
                        ORDER BY created_at DESC
                        LIMIT 100
                    ) recent
                    """
                )
                avg_tokens, avg_cost, avg_latency = cursor.fetchone()
    except psycopg.Error:
        return {
            "avg_tokens_per_request": 0,
            "avg_cost_per_request": 0,
            "avg_latency_ms": 0,
            "cache_hit_percentage": 0,
        }

    return {
        "avg_tokens_per_request": round(float(avg_tokens), 2),
        "avg_cost_per_request": round(float(avg_cost), 6),
        "avg_latency_ms": round(float(avg_latency), 2),
        "cache_hit_percentage": 0,
    }
