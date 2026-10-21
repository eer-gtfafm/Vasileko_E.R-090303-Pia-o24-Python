import logging
import os
import time

from flask import Flask, jsonify, request

from app.database import Dish, db, init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("restaurant")


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://app:password@db:5432/restaurant",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        init_db()

    @app.before_request
    def log_request():
        request.environ["_start_time"] = time.perf_counter()

    @app.after_request
    def log_response(response):
        duration = (time.perf_counter() - request.environ.get("_start_time", time.perf_counter())) * 1000
        logger.info("%s %s -> %s (%.1f ms)", request.method, request.path,
                    response.status_code, duration)
        return response

    @app.get("/health")
    def health():
        return jsonify({"status": "healthy", "service": "restaurant"})

    @app.get("/")
    def root():
        return jsonify({
            "service": "Restaurant API",
            "endpoints": ["/health", "/dishes", "/api/dishes"],
        })

    @app.get("/dishes")
    @app.get("/api/dishes")
    def list_dishes():
        dishes = Dish.query.order_by(Dish.name).all()
        return jsonify([d.to_dict() for d in dishes])

    @app.get("/dishes/<int:dish_id>")
    @app.get("/api/dishes/<int:dish_id>")
    def get_dish(dish_id: int):
        dish = db.session.get(Dish, dish_id)
        if dish is None:
            return jsonify({"error": "Блюдо не найдено"}), 404
        return jsonify(dish.to_dict())

    @app.post("/dishes")
    @app.post("/api/dishes")
    def create_dish():
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        try:
            price = float(data.get("price", 0))
        except (TypeError, ValueError):
            return jsonify({"error": "Цена должна быть числом"}), 400
        if not name:
            return jsonify({"error": "Название блюда не может быть пустым"}), 400
        if price <= 0:
            return jsonify({"error": "Цена должна быть положительной"}), 400
        dish = Dish(name=name, price=price)
        db.session.add(dish)
        db.session.commit()
        logger.info("Создано блюдо %s (ID %s)", dish.name, dish.id)
        return jsonify(dish.to_dict()), 201

    @app.delete("/dishes/<int:dish_id>")
    @app.delete("/api/dishes/<int:dish_id>")
    def delete_dish(dish_id: int):
        dish = db.session.get(Dish, dish_id)
        if dish is None:
            return jsonify({"error": "Блюдо не найдено"}), 404
        db.session.delete(dish)
        db.session.commit()
        logger.info("Удалено блюдо ID %s", dish_id)
        return "", 204

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))