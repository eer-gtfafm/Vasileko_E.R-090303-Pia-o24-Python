from fastapi import FastAPI, HTTPException

from app.client import ServiceClient

app = FastAPI(title="API Gateway")

MENU_URL = "http://127.0.0.1:8001"
ORDER_URL = "http://127.0.0.1:8002"
DELIVERY_URL = "http://127.0.0.1:8003"

menu = ServiceClient(MENU_URL, retries=2, backoff=0.05)
orders = ServiceClient(ORDER_URL, retries=2, backoff=0.05)
delivery = ServiceClient(DELIVERY_URL, retries=1)


@app.get("/")
def root() -> dict:
    return {
        "service": "API Gateway",
        "endpoints": ["/health", "/dishes", "/orders", "/deliveries", "/order"],
    }


@app.get("/health")
def health() -> dict:
    """Агрегированный health-check по всем сервисам."""
    statuses = {}
    for name, client in [("menu", menu), ("orders", orders), ("delivery", delivery)]:
        try:
            client.get("/health")
            statuses[name] = "ok"
        except Exception:
            statuses[name] = "unavailable"
    overall = "healthy" if all(v == "ok" for v in statuses.values()) else "degraded"
    return {"status": overall, "services": statuses}


@app.get("/dishes")
def proxy_dishes() -> list:
    try:
        return menu.get("/dishes")
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))


@app.get("/orders")
def proxy_orders() -> list:
    try:
        return orders.get("/orders")
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))


@app.get("/deliveries")
def proxy_deliveries() -> list:
    try:
        return delivery.get("/deliveries")
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))


@app.post("/order")
def create_order(payload: dict) -> dict:
    """Агрегация: заказ через order-service (с проверкой menu-service)."""
    try:
        result = orders.get(f"/create?dish_id={payload['dish_id']}&client_name="
                            f"{payload.get('client_name', 'client').replace(' ', '%20')}")
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))
    return result