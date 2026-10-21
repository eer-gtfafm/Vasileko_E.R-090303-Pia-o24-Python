from flask import Blueprint, jsonify, request

from schemas import parse_filters, parse_id
from service import BookingService, RoomService


def create_blueprint(room_service: RoomService, booking_service: BookingService,
                     cache=None) -> Blueprint:
    bp = Blueprint("hotel", __name__)

    # --- специализированный endpoint (объявлен раньше /rooms/<id>) ---
    @bp.get("/rooms/available")
    def available_rooms():
        capacity = request.args.get("capacity")
        capacity_value = int(capacity) if capacity not in (None, "") else None
        rooms = room_service.available_rooms(
            capacity=capacity_value,
            date_from=request.args.get("date_from"),
            date_to=request.args.get("date_to"),
        )
        return jsonify(rooms), 200

    @bp.get("/rooms")
    def list_rooms():
        return jsonify(room_service.list_rooms(parse_filters(request.args))), 200

    @bp.get("/rooms/<room_id>")
    def get_room(room_id: str):
        return jsonify(room_service.get_room(parse_id(room_id))), 200

    @bp.post("/rooms")
    def create_room():
        room = room_service.create_room(request.get_json(silent=True))
        response = jsonify(room)
        response.headers["Location"] = f"/rooms/{room['id']}"
        return response, 201

    @bp.put("/rooms/<room_id>")
    def replace_room(room_id: str):
        return jsonify(room_service.replace_room(parse_id(room_id), request.get_json(silent=True))), 200

    @bp.patch("/rooms/<room_id>")
    def patch_room(room_id: str):
        return jsonify(room_service.patch_room(parse_id(room_id), request.get_json(silent=True))), 200

    @bp.delete("/rooms/<room_id>")
    def delete_room(room_id: str):
        room_service.delete_room(parse_id(room_id))
        return "", 204

    # --- бронирование: транзакция с услугами (связь N:M) ---
    @bp.get("/bookings")
    def list_bookings():
        return jsonify(booking_service.list_bookings()), 200

    @bp.get("/bookings/<booking_id>")
    def get_booking(booking_id: str):
        return jsonify(booking_service.get_booking(parse_id(booking_id))), 200

    @bp.post("/bookings")
    def create_booking():
        booking = booking_service.create_booking(request.get_json(silent=True))
        response = jsonify(booking)
        response.headers["Location"] = f"/bookings/{booking['id']}"
        return response, 201

    # --- диагностика кэша (для демонстрации cache-aside) ---
    @bp.get("/cache/stats")
    def cache_stats():
        if cache is None:
            return jsonify({"enabled": False}), 200
        return jsonify({
            "enabled": True,
            "hits": cache.hits,
            "misses": cache.misses,
            "ttl": cache.ttl(1) if cache.get(1) is not None else 0,
        }), 200

    return bp
