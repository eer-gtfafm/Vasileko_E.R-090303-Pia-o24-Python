import logging
from typing import Optional

from flask import Flask, jsonify

from cache import RoomCache, create_cache_client
from database import Database, init_db
from exceptions import ApiError
from repository import BookingRepository, GuestRepository, RoomRepository, ServiceRepository
from routes import create_blueprint
from service import BookingService, RoomService


def create_app(db_path: str = "hotel.db", seed: bool = True,
               cache_client=None, init: bool = True) -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False

    database = Database(db_path)
    if init:
        init_db(database, seed=seed)

    if cache_client is None:
        cache_client, cache_backend = create_cache_client()
    else:
        cache_backend = "custom"
    cache = RoomCache(cache_client)

    room_repository = RoomRepository(database)
    room_service = RoomService(room_repository, cache)
    booking_service = BookingService(
        room_repository,
        GuestRepository(database),
        ServiceRepository(database),
        BookingRepository(database),
        cache,
    )

    app.extensions["database"] = database
    app.extensions["room_service"] = room_service
    app.extensions["booking_service"] = booking_service
    app.extensions["room_cache"] = cache
    app.extensions["cache_backend"] = cache_backend

    app.register_blueprint(create_blueprint(room_service, booking_service, cache))

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
        logging.getLogger("hotel_api").exception("Unhandled error: %s", error)
        return jsonify({"error": "Внутренняя ошибка сервера", "code": "INTERNAL_ERROR"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    print("База данных: SQLite (hotel.db), кэш:", app.extensions["cache_backend"])
    app.run(host="127.0.0.1", port=5000)
