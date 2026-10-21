import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database import Base, SessionLocal, engine
from app.routers.rooms import router as rooms_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("hotel_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_rooms()
    yield


SEED = [
    ("101", "стандартный", 1, 2, 2500.0, True, "wi-fi,tv"),
    ("102", "стандартный", 1, 2, 2700.0, True, "wi-fi,tv,кондиционер"),
    ("103", "стандартный", 1, 1, 2400.0, False, "wi-fi"),
    ("201", "люкс", 2, 2, 6000.0, True, "wi-fi,tv,кондиционер,мини-бар"),
    ("202", "люкс", 2, 3, 6500.0, False, "wi-fi,tv,кондиционер,джакузи"),
    ("203", "люкс", 2, 2, 6200.0, True, "wi-fi,tv,кондиционер,мини-бар"),
    ("301", "семейный", 3, 4, 4200.0, True, "wi-fi,tv,кухня"),
    ("302", "семейный", 3, 4, 4400.0, True, "wi-fi,tv,кухня,кондиционер"),
    ("303", "семейный", 3, 3, 4100.0, False, "wi-fi,кухня"),
    ("304", "семейный", 3, 5, 4500.0, True, "wi-fi,tv,кухня,кондиционер"),
    ("401", "стандартный", 4, 2, 2800.0, True, "wi-fi,tv"),
    ("402", "стандартный", 4, 2, 2900.0, True, "wi-fi,tv"),
]


def seed_rooms() -> None:
    """Заполняет базу тестовыми данными при первом запуске."""
    db = SessionLocal()
    try:
        from app.repositories.room import RoomRepository

        repository = RoomRepository(db)
        if repository.count() == 0:
            for number, room_type, floor, capacity, price, available, amenities in SEED:
                repository.create(number, room_type, floor, capacity, price, available, amenities.split(","))
            logger.info("База заполнена тестовыми номерами: %d шт.", len(SEED))
    finally:
        db.close()


app = FastAPI(
    title="Отель — REST API",
    description="REST API гостиницы (вариант 5): номера, фильтрация, сортировка, пагинация, статистика.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(rooms_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирование запросов: метод, URL, статус, время выполнения."""
    start = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start) * 1000
    logger.info("%s %s -> %s (%.1f мс)", request.method, request.url.path, response.status_code, duration)
    return response


@app.get("/", summary="Корневой endpoint")
async def root():
    return {"service": "Отель REST API", "docs": "/docs", "redoc": "/redoc"}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})