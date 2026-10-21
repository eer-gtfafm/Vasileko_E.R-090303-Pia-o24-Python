import logging

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

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
web_bp = Blueprint("web", __name__)


def dish_service():
    return DishService(DishRepository(), CategoryRepository())


def category_service():
    return CategoryService(CategoryRepository())


def order_service():
    return OrderService(OrderRepository(), DishRepository())


@web_bp.route("/")
def index():
    """Главная страница: ссылки на разделы и статистика."""
    stats = order_service().stats()
    return render_template("index.html", stats=stats)


@web_bp.route("/dishes")
def list_dishes():
    """Список блюд с поиском, фильтрацией и сортировкой."""
    search = request.args.get("search") or None
    category_id = request.args.get("category_id") or None
    available_raw = request.args.get("available")
    available = (available_raw == "1") if available_raw in ("0", "1") else None
    sort = request.args.get("sort", "name")
    order = request.args.get("order", "asc")

    dishes = dish_service().list(search, int(category_id) if category_id else None,
                                 available, sort, order)
    categories = category_service().list()
    return render_template("list.html", dishes=dishes, categories=categories,
                           search=search or "", category_id=category_id or "",
                           available=available_raw or "", sort=sort, order=order)


@web_bp.route("/dishes/<int:dish_id>")
def dish_detail(dish_id):
    try:
        dish = dish_service().get(dish_id)
    except NotFoundError:
        return render_template("404.html"), 404
    return render_template("detail.html", dish=dish)


@web_bp.route("/dishes/create", methods=["GET", "POST"])
def create_dish():
    if request.method == "POST":
        try:
            dish = dish_service().create(
                name=request.form.get("name", ""),
                description=request.form.get("description", ""),
                price=float(request.form.get("price", 0) or 0),
                calories=int(request.form.get("calories", 0) or 0),
                available=request.form.get("available") == "1",
                category_id=int(request.form.get("category_id", 0) or 0),
            )
            flash("Блюдо успешно добавлено", "success")
            logger.info("Создано блюдо %s (ID %s)", dish.name, dish.id)
            return redirect(url_for("web.dish_detail", dish_id=dish.id))
        except (ValidationError, ValueError) as error:
            flash(f"Ошибка: {error}", "danger")
    return render_template("create.html", categories=category_service().list())


@web_bp.route("/dishes/<int:dish_id>/edit", methods=["GET", "POST"])
def edit_dish(dish_id):
    try:
        dish = dish_service().get(dish_id)
    except NotFoundError:
        return render_template("404.html"), 404

    if request.method == "POST":
        try:
            fields = {
                "name": request.form.get("name", "").strip(),
                "description": request.form.get("description", ""),
                "category_id": int(request.form.get("category_id", 0) or 0),
                "available": request.form.get("available") == "1",
            }
            price_raw = request.form.get("price", "").strip()
            calories_raw = request.form.get("calories", "").strip()
            if price_raw:
                fields["price"] = float(price_raw)
            if calories_raw:
                fields["calories"] = int(calories_raw)
            updated = dish_service().update(dish_id, fields)
            flash("Изменения сохранены", "success")
            logger.info("Изменено блюдо ID %s", dish_id)
            return redirect(url_for("web.dish_detail", dish_id=updated.id))
        except (ValidationError, ValueError) as error:
            flash(f"Ошибка: {error}", "danger")
    return render_template("edit.html", dish=dish, categories=category_service().list())


@web_bp.route("/dishes/<int:dish_id>/delete", methods=["POST"])
def delete_dish(dish_id):
    try:
        dish_service().delete(dish_id)
        flash("Блюдо удалено", "success")
        logger.info("Удалено блюдо ID %s", dish_id)
    except NotFoundError as error:
        flash(str(error), "danger")
    return redirect(url_for("web.list_dishes"))


@web_bp.route("/orders")
def list_orders():
    return render_template("orders.html", orders=order_service().list())


@web_bp.route("/orders/create", methods=["GET", "POST"])
def create_order():
    if request.method == "POST":
        try:
            dish_ids = [int(x) for x in request.form.getlist("dish_ids")]
            order = order_service().create(request.form.get("customer_name", ""), dish_ids)
            flash(f"Заказ №{order.id} создан", "success")
            logger.info("Создан заказ №%s", order.id)
            return redirect(url_for("web.list_orders"))
        except (NotFoundError, ValidationError, ValueError) as error:
            flash(f"Ошибка: {error}", "danger")
    return render_template("order_create.html", dishes=dish_service().list())


@web_bp.route("/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    try:
        order_service().set_status(order_id, request.form.get("status", ""))
        flash("Статус заказа обновлён", "success")
    except (NotFoundError, ValidationError) as error:
        flash(str(error), "danger")
    return redirect(url_for("web.list_orders"))