from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Menu Service")


class Dish(BaseModel):
    id: int
    name: str
    price: float
    available: bool = True


_DISHES: dict[int, Dish] = {}


@app.on_event("startup")
def seed() -> None:
    if not _DISHES:
        for i, (name, price) in enumerate([("Борщ", 350.0), ("Цезарь", 420.0),
                                           ("Стейк", 890.0), ("Паста", 450.0)],
                                          start=1):
            _DISHES[i] = Dish(id=i, name=name, price=price)


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}


@app.get("/dishes")
def list_dishes() -> list[Dish]:
    return list(_DISHES.values())


@app.get("/dishes/{dish_id}")
def get_dish(dish_id: int) -> Dish:
    from fastapi import HTTPException

    dish = _DISHES.get(dish_id)
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish