import logging

from flask import Flask, jsonify

from exceptions import ApiError
from repository import RoomRepository
from routes import create_blueprint
from service import RoomService

SEED_ROOMS = [
    {"number": "101", "room_type": "стандартный", "price_per_night": 2500, "capacity": 2},
    {"number": "102", "room_type": "люкс", "price_per_night": 6000, "capacity": 2},
    {"number": "103", "room_type": "семейный", "price_per_night": 4200, "capacity": 4, "status": "занят"},
    {"number": "104", "room_type": "стандартный", "price_per_night": 2200, "capacity": 2, "status": "на обслуживании"},
]


def create_app(repository: RoomRepository = None, seed: bool = True) -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False

    repository = repository or RoomRepository()
    service = RoomService(repository)
    app.extensions["room_service"] = service
    app.register_blueprint(create_blueprint(service))

    if seed and not repository.get_all():
        for payload in SEED_ROOMS:
            service.create_room(payload)

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Ресурс не найден", "code": "NOT_FOUND"}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"error": "Метод не поддерживается", "code": "METHOD_NOT_ALLOWED"}), 405

    @app.errorhandler(Exception)
    def handle_internal_error(error: Exception):
        logging.getLogger("room_api").exception("Unhandled error: %s", error)
        return jsonify({"error": "Внутренняя ошибка сервера", "code": "INTERNAL_ERROR"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
