from typing import List, Optional

from pydantic import BaseModel, Field


class RoomBase(BaseModel):
    number: str = Field(min_length=1, max_length=10, description="Номер комнаты")
    room_type: str = Field(min_length=1, description="Тип: стандартный / люкс / семейный")
    floor: int = Field(ge=1, le=100, description="Этаж")
    capacity: int = Field(ge=1, description="Вместимость, человек")
    price: float = Field(gt=0, description="Цена за ночь, руб.")
    available: bool = True
    amenities: List[str] = Field(default_factory=list, description="Удобства")


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    number: Optional[str] = Field(default=None, min_length=1, max_length=10)
    room_type: Optional[str] = Field(default=None, min_length=1)
    floor: Optional[int] = Field(default=None, ge=1, le=100)
    capacity: Optional[int] = Field(default=None, ge=1)
    price: Optional[float] = Field(default=None, gt=0)
    available: Optional[bool] = None
    amenities: Optional[List[str]] = None


class RoomResponse(RoomBase):
    id: int

    class Config:
        from_attributes = True


class RoomListResponse(BaseModel):
    items: List[RoomResponse]
    total: int
    skip: int
    limit: int


class RoomStatistics(BaseModel):
    total: int
    available_count: int
    average_price: float
    min_price: float
    max_price: float