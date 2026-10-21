import datetime
import logging

from flask import Flask

from app.config import Config
from app.database import db


def create_app(config: Config = None) -> Flask:
    """Application Factory: создание Flask-приложения с разными конфигурациями."""
    app = Flask(__name__)
    app.config.from_object(config or Config)

    db.init_app(app)

    from app.routes.api import api_bp
    from app.routes.web import web_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Логирование
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("restaurant").info("Приложение запущено")

    @app.errorhandler(404)
    def not_found(error):
        return render_404(), 404

    def render_404():
        from flask import render_template
        return render_template("404.html")

    # Создание таблиц и заполнение тестовыми данными выполняется при первом запуске
    with app.app_context():
        db.create_all()
        seed(app)

    return app


def seed(app: Flask) -> None:
    """Заполняет базу тестовыми данными при первом запуске."""
    from app.models.models import Category, Dish, Order
    from app.repositories.repositories import CategoryRepository, DishRepository

    categories_repo = CategoryRepository()
    dishes_repo = DishRepository()
    if categories_repo.get_all():
        return

    categories = {}
    for name in ("супы", "салаты", "горячее", "десерты", "напитки"):
        categories[name] = categories_repo.create(name)

    menu = [
        ("Борщ", "Свекольный суп со сметаной", 350.0, 210, categories["супы"]),
        ("Солянка", "Мясная сборная солянка", 420.0, 340, categories["супы"]),
        ("Оливье", "Классический салат", 280.0, 250, categories["салаты"]),
        ("Цезарь", "Салат с курицей и пармезаном", 420.0, 380, categories["салаты"]),
        ("Стейк", "Говяжий стейк с овощами", 890.0, 610, categories["горячее"]),
        ("Паста", "Паста карбонара", 450.0, 540, categories["горячее"]),
        ("Чизкейк", "Нью-Йорк чизкейк", 320.0, 430, categories["десерты"]),
        ("Кофе", "Эспрессо", 150.0, 5, categories["напитки"]),
    ]
    for name, description, price, calories, category in menu:
        dishes_repo.create(name, description, price, calories, True, category.id)


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)