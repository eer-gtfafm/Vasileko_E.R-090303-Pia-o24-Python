from flask import Blueprint, jsonify, request

from schemas import parse_filters, parse_id
from service import RoomService


# HTTP-уровень: разбор запроса, вызов сервиса, формирование ответа.
# Бизнес-логика находится в RoomService.
def create_blueprint(service: RoomService) -> Blueprint:
    bp = Blueprint("rooms", __name__)

    # Специализированный endpoint объявлен раньше динамического,
    # чтобы слово available не воспринималось как идентификатор.
    @bp.get("/rooms/available")
    def available_rooms():
        filters = parse_filters(request.args)
        rooms = service.get_available_rooms(filters)
        return jsonify([room.to_dict() for room in rooms]), 200

    @bp.get("/rooms")
    def list_rooms():
        filters = parse_filters(request.args)
        rooms = service.list_rooms(filters)
        return jsonify([room.to_dict() for room in rooms]), 200

    @bp.get("/rooms/<room_id>")
    def get_room(room_id: str):
        room = service.get_room(parse_id(room_id))
        return jsonify(room.to_dict()), 200

    @bp.post("/rooms")
    def create_room():
        room = service.create_room(request.get_json(silent=True))
        response = jsonify(room.to_dict())
        response.headers["Location"] = f"/rooms/{room.id}"
        return response, 201

    @bp.put("/rooms/<room_id>")
    def replace_room(room_id: str):
        room = service.replace_room(parse_id(room_id), request.get_json(silent=True))
        return jsonify(room.to_dict()), 200

    @bp.patch("/rooms/<room_id>")
    def patch_room(room_id: str):
        room = service.patch_room(parse_id(room_id), request.get_json(silent=True))
        return jsonify(room.to_dict()), 200

    @bp.delete("/rooms/<room_id>")
    def delete_room(room_id: str):
        service.delete_room(parse_id(room_id))
        return "", 204

    return bp
