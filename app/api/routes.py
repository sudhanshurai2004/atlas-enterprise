import json
import logging
import time
import uuid
from typing import Any

import psycopg
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.auth import get_current_user, issue_token, LoginRequest
from app.api.cache import get_cached_answer, set_cached_answer
from app.api.state import append_turn, client, get_history, record_query
from app.config import settings
from app.pricing import calculate_cost
from app.agents.runtime import run_supervisor


router = APIRouter()
logger = logging.getLogger(__name__)


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
        answer = run_supervisor(
            request.question,
            user["username"],
            request.session_id,
        )
        cache_hit = False
        set_cached_answer(request.question, answer)

    append_turn(request.session_id, request.question, answer["answer"])
    total_queries, cache_hits = record_query(cache_hit)
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
    except psycopg.Error as exc:
        logger.exception("Could not write query log")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Query logging is unavailable",
        ) from exc

    return {
        **answer,
        "trace_id": trace_id,
        "cache_hit": cache_hit,
        "cache_hit_percentage": round(cache_hits * 100 / total_queries, 2),
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
        answer = response["answer"]
        words = answer.split()
        for index, word in enumerate(words):
            text = word if index == 0 else f" {word}"
            yield f"event: token\ndata: {json.dumps({'text': text})}\n\n"
        yield f"event: result\ndata: {json.dumps(response)}\n\n"
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
    except psycopg.Error as exc:
        logger.exception("Could not read query metrics")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Metrics are unavailable",
        ) from exc

    total_queries = int(client.get("atlas:metrics:queries") or 0)
    cache_hits = int(client.get("atlas:metrics:cache_hits") or 0)
    return {
        "avg_tokens_per_request": round(float(avg_tokens), 2),
        "avg_cost_per_request": round(float(avg_cost), 6),
        "avg_latency_ms": round(float(avg_latency), 2),
        "cache_hit_percentage": (
            round(cache_hits * 100 / total_queries, 2)
            if total_queries
            else 0
        ),
    }
