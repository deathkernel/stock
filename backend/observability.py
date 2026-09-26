"""Lightweight in-process observability helpers."""
from __future__ import annotations

import logging
import time
import uuid
from collections import Counter

from fastapi import Request

logger = logging.getLogger("stock_intelligence")
REQUEST_COUNTS: Counter[str] = Counter()
STATUS_COUNTS: Counter[str] = Counter()
TOTAL_REQUESTS = 0
TOTAL_ERRORS = 0
TOTAL_LATENCY_MS = 0.0


async def observe_request(request: Request, call_next):
    global TOTAL_REQUESTS, TOTAL_ERRORS, TOTAL_LATENCY_MS
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    started = time.perf_counter()
    try:
        response = await call_next(request)
        status = response.status_code
    except Exception:
        status = 500
        TOTAL_ERRORS += 1
        raise
    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000
        TOTAL_REQUESTS += 1
        TOTAL_LATENCY_MS += elapsed_ms
        route = request.url.path
        REQUEST_COUNTS[request.method + " " + route] += 1
        STATUS_COUNTS[str(status)] += 1
        logger.info(
            "request method=%s path=%s status=%s duration_ms=%.2f request_id=%s",
            request.method, route, status, elapsed_ms, request_id,
        )

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
    return response


def metrics() -> dict:
    average = TOTAL_LATENCY_MS / TOTAL_REQUESTS if TOTAL_REQUESTS else 0.0
    return {
        "requests_total": TOTAL_REQUESTS,
        "errors_total": TOTAL_ERRORS,
        "average_latency_ms": round(average, 2),
        "status_codes": dict(STATUS_COUNTS),
        "routes": dict(REQUEST_COUNTS),
    }
