import logging
import time
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from llmkit import configure, get_settings, request_id

from llmsvc.errors import register_error_handlers

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    configure()
    log.info("startup", extra={"ctx": {"service": "llmsvc"}})
    settings = get_settings()
    _app.state.settings = settings
    yield


app = FastAPI(lifespan=lifespan)
register_error_handlers(app)


@app.middleware("http")
async def add_request_id(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request_id.set(rid)
    started = time.perf_counter()
    response = await call_next(request)
    log.info(
        "request",
        extra={
            "ctx": {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 1),
            }
        },
    )
    response.headers["X-Request-ID"] = rid
    return response


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}
