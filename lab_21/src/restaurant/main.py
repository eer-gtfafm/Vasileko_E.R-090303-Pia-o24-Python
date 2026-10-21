"""Точка входа FastAPI-приложения «Ресторан»."""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from restaurant.api import auth, deliveries, dishes, orders
from restaurant.config.database import create_all
from restaurant.exceptions.errors import AppError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("restaurant")

app = FastAPI(
    title="Restaurant API",
    description="Итоговый проект: REST API ресторана с авторизацией, заказами и доставкой.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(dishes.router)
app.include_router(orders.router)
app.include_router(deliveries.router)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    logger.warning("Business error: %s — %s", exc.error_code, exc.message)
    return JSONResponse(status_code=exc.status_code, content={"error": exc.error_code, "message": exc.message})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for err in exc.errors():
        loc = ".".join(str(part) for part in err["loc"] if part not in {"body", "query"})
        details.append({"field": loc or err["loc"][-1], "message": err["msg"]})
    return JSONResponse(status_code=422, content={"error": "VALIDATION_ERROR", "details": details})


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, duration_ms)
    return response


@app.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "healthy", "service": "restaurant"}


@app.on_event("startup")
def on_startup() -> None:
    create_all()
    logger.info("Приложение запущено, таблицы БД готовы")
