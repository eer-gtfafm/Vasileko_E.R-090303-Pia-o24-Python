PAYLOAD = {"number": "101", "room_type": "стандартный", "price_per_night": 2500, "capacity": 2}


def create_room(client, **overrides):
    response = client.post("/rooms", json={**PAYLOAD, **overrides})
    assert response.status_code == 201
    return response.get_json()


def test_get_rooms_list(client):
    create_room(client)

    response = client.get("/rooms")

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["number"] == "101"


def test_get_room_by_id(client):
    room = create_room(client)

    response = client.get(f"/rooms/{room['id']}")

    assert response.status_code == 200
    assert response.get_json()["id"] == room["id"]


def test_get_room_not_found(client):
    response = client.get("/rooms/999")

    assert response.status_code == 404
    assert response.get_json()["code"] == "ROOM_NOT_FOUND"


def test_get_room_invalid_id(client):
    response = client.get("/rooms/abc")

    assert response.status_code == 400
    assert response.get_json()["code"] == "INVALID_ID"


def test_create_room(client):
    response = client.post("/rooms", json=PAYLOAD)

    assert response.status_code == 201
    assert response.headers["Location"] == "/rooms/1"
    assert response.get_json()["status"] == "свободен"


def test_create_room_validation_error(client):
    response = client.post("/rooms", json={**PAYLOAD, "price_per_night": -100})

    assert response.status_code == 400
    assert response.get_json()["code"] == "VALIDATION_ERROR"


def test_replace_room(client):
    room = create_room(client)

    response = client.put(f"/rooms/{room['id']}", json={**PAYLOAD, "number": "202", "capacity": 3})

    assert response.status_code == 200
    assert response.get_json()["number"] == "202"
    assert response.get_json()["capacity"] == 3


def test_patch_room(client):
    room = create_room(client)

    response = client.patch(f"/rooms/{room['id']}", json={"price_per_night": 2800})

    assert response.status_code == 200
    assert response.get_json()["price_per_night"] == 2800
    assert response.get_json()["number"] == "101"


def test_delete_room(client):
    room = create_room(client)

    response = client.delete(f"/rooms/{room['id']}")

    assert response.status_code == 204
    assert client.get(f"/rooms/{room['id']}").status_code == 404


def test_filter_rooms(client):
    create_room(client, number="101", room_type="стандартный")
    create_room(client, number="102", room_type="люкс", price_per_night=6000)

    response = client.get("/rooms?type=люкс")

    assert response.status_code == 200
    assert [room["number"] for room in response.get_json()] == ["102"]


def test_sort_rooms(client):
    create_room(client, number="101", price_per_night=2500)
    create_room(client, number="102", price_per_night=6000)

    response = client.get("/rooms?sort=price&order=desc")

    assert [room["price_per_night"] for room in response.get_json()] == [6000, 2500]


def test_available_rooms_endpoint(client):
    create_room(client, number="101")
    create_room(client, number="102", status="занят")

    response = client.get("/rooms/available")

    assert response.status_code == 200
    assert [room["number"] for room in response.get_json()] == ["101"]


def test_method_not_allowed(client):
    response = client.put("/rooms")

    assert response.status_code == 405
    assert response.get_json()["code"] == "METHOD_NOT_ALLOWED"
