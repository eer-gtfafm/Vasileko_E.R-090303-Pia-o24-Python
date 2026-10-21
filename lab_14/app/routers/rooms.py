import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.room import RoomNotFoundError, RoomRepository
from app.schemas.room import RoomCreate, RoomListResponse, RoomResponse, RoomStatistics, RoomUpdate
from app.services.room import RoomCache, RoomService

logger = logging.getLogger("hotel_api")

router = APIRouter(prefix="/rooms", tags=["rooms"])


def get_service(db: Session = Depends(get_db)):
    """Dependency Injection: сервис с репозиторием и кэшем."""
    cache_client, _ = getattr(get_service, "_cache_client", (None, None))
    if cache_client is None:
        from app.services.room import create_cache_client

        cache_client, _ = create_cache_client()
        get_service._cache_client = (cache_client, _)
    return RoomService(RoomRepository(db), RoomCache(cache_client))


@router.get("", response_model=RoomListResponse,
            summary="Список номеров", description="Фильтрация, сортировка и пагинация")
def list_rooms(
    room_type: Optional[str] = Query(default=None, description="Тип номера"),
    min_price: Optional[float] = Query(default=None, description="Мин. цена"),
    max_price: Optional[float] = Query(default=None, description="Макс. цена"),
    available: Optional[bool] = Query(default=None, description="Только доступные"),
    sort: str = Query(default="price", description="Поле сортировки: price, number, capacity"),
    order: str = Query(default="asc", pattern="^(asc|desc)$", description="Направление"),
    skip: int = Query(default=0, ge=0, description="Сколько пропустить"),
    limit: int = Query(default=20, ge=1, le=100, description="Сколько вернуть"),
    service: RoomService = Depends(get_service),
):
    items, total = service.list_rooms(
        room_type=room_type, min_price=min_price, max_price=max_price, available=available,
        sort=sort, order=order, skip=skip, limit=limit,
    )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/search", response_model=List[RoomResponse], summary="Поиск по номеру/типу")
def search_rooms(
    q: str = Query(..., min_length=1, description="Строка поиска"),
    limit: int = Query(default=20, ge=1, le=100),
    service: RoomService = Depends(get_service),
):
    return service.search_rooms(q, limit=limit)


@router.get("/statistics", response_model=RoomStatistics, summary="Статистика")
def room_statistics(service: RoomService = Depends(get_service)):
    return service.statistics()


@router.get("/{room_id}", response_model=RoomResponse, summary="Номер по ID")
def get_room(room_id: int, service: RoomService = Depends(get_service)):
    try:
        return service.get_room(room_id)
    except RoomNotFoundError:
        raise HTTPException(status_code=404, detail=f"Номер с ID {room_id} не найден")


@router.post("", response_model=RoomResponse, status_code=201, summary="Создать номер")
def create_room(payload: RoomCreate, service: RoomService = Depends(get_service)):
    try:
        return service.create_room(payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error))


@router.put("/{room_id}", response_model=RoomResponse, summary="Полное изменение")
def replace_room(room_id: int, payload: RoomCreate, service: RoomService = Depends(get_service)):
    try:
        return service.replace_room(room_id, payload.model_dump())
    except RoomNotFoundError:
        raise HTTPException(status_code=404, detail=f"Номер с ID {room_id} не найден")


@router.patch("/{room_id}", response_model=RoomResponse, summary="Частичное изменение")
def patch_room(room_id: int, payload: RoomUpdate, service: RoomService = Depends(get_service)):
    try:
        return service.patch_room(room_id, payload.model_dump(exclude_unset=True))
    except RoomNotFoundError:
        raise HTTPException(status_code=404, detail=f"Номер с ID {room_id} не найден")


@router.delete("/{room_id}", status_code=204, summary="Удалить номер")
def delete_room(room_id: int, service: RoomService = Depends(get_service)):
    try:
        service.delete_room(room_id)
    except RoomNotFoundError:
        raise HTTPException(status_code=404, detail=f"Номер с ID {room_id} не найден")