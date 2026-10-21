import logging

from flask import Blueprint, jsonify, request

from app.repositories.repositories import CategoryRepository, DishRepository, OrderRepository
from app.services.services import (
    CategoryService,
    ConflictError,
    DishService,
    NotFoundError,
    OrderService,
    ValidationError,
)

logger = logging.getLogger("restaurant")
api_bp = Blueprint("api", __name__)


@api_bp.errorhandler(NotFoundError)
def not_found(error):
    return jsonify({"error": str(error)}), 404


@api_bp.errorhandler(ValidationError)
def validation_error(error):
    return jsonify({"error": str(error)}), 400


@api_bp.errorhandler(ConflictError)
def conflict(error):
    return jsonify({"error": str(error)}), 409


@api_bp.get("/dishes")
def api_list_dishes():
    """Список блюд с поиском, фильтрацией и сортировкой (JSON)."""
    search = request.args.get("search") or None
    category_id = request.args.get("category_id") or None
    available_raw = request.args.get("available")
    available = (available_raw == "1") if available_raw in ("0", "1") else None
    sort = request.args.get("sort", "name")
    order = request.args.get("order", "asc")
    dishes = DishService(DishRepository(), CategoryRepository()).list(
        search, int(category_id) if category_id else None, available, sort, order)
    return jsonify([dish.to_dict() for dish in dishes])


@api_bp.get("/dishes/<int:dish_id>")
def api_get_dish(dish_id):
    dish = DishService(DishRepository(), CategoryRepository()).get(dish_id)
    return jsonify(dish.to_dict())


@api_bp.post("/dishes")
def api_create_dish():
    data = request.get_json(silent=True) or {}
    try:
        dish = DishService(DishRepository(), CategoryRepository()).create(
            name=data.get("name", ""),
            description=data.get("description", ""),
            price=float(data.get("price", 0) or 0),
            calories=int(data.get("calories", 0) or 0),
            available=bool(data.get("available", True)),
            category_id=int(data.get("category_id", 0) or 0),
        )
        logger.info("API: создано блюдо %s", dish.name)
        return jsonify(dish.to_dict()), 201
    except (ValidationError, ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


@api_bp.put("/dishes/<int:dish_id>")
def api_update_dish(dish_id):
    data = request.get_json(silent=True) or {}
    fields = {}
    for key in ("name", "description", "available"):
        if key in data:
            fields[key] = data[key]
    for key in ("price", "calories", "category_id"):
        if key in data:
            fields[key] = float(data[key]) if key == "price" else int(data[key])
    try:
        dish = DishService(DishRepository(), CategoryRepository()).update(dish_id, fields)
        return jsonify(dish.to_dict())
    except NotFoundError:
        return jsonify({"error": f"Блюдо с ID {dish_id} не найдено"}), 404
    except (ValidationError, ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


@api_bp.delete("/dishes/<int:dish_id>")
def api_delete_dish(dish_id):
    try:
        DishService(DishRepository(), CategoryRepository()).delete(dish_id)
        logger.info("API: удалено блюдо ID %s", dish_id)
        return "", 204
    except NotFoundError:
        return jsonify({"error": f"Блюдо с ID {dish_id} не найдено"}), 404


@api_bp.get("/categories")
def api_list_categories():
    return jsonify([c.to_dict() if hasattr(c, "to_dict") else {"id": c.id, "name": c.name}
                    for c in CategoryService(CategoryRepository()).list()])


@api_bp.get("/orders")
def api_list_orders():
    orders = OrderService(OrderRepository(), DishRepository()).list()
    return jsonify([order.to_dict() for order in orders])


@api_bp.post("/orders")
def api_create_order():
    data = request.get_json(silent=True) or {}
    try:
        order = OrderService(OrderRepository(), DishRepository()).create(
            customer_name=data.get("customer_name", ""),
            dish_ids=[int(x) for x in data.get("dish_ids", [])],
        )
        logger.info("API: создан заказ №%s", order.id)
        return jsonify(order.to_dict()), 201
    except (NotFoundError, ValidationError, ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400