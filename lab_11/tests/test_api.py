ROOM = {"number": "401", "room_type": "стандартный", "price_per_night": 3000, "capacity": 2}


def test_get_rooms(client):
    response = client.get("/rooms")

    assert response.status_code == 200
    assert len(response.get_json()) == 10


def test_get_room_and_cache(client):
    first = client.get("/rooms/1")
    second = client.get("/rooms/1")

    assert first.status_code == 200
    assert first.get_json() == second.get_json()
    stats = client.get("/cache/stats").get_json()
    assert stats["enabled"] is True
    assert stats["hits"] >= 1


def test_get_room_not_found(client):
    response = client.get("/rooms/999")

    assert response.status_code == 404
    assert response.get_json()["code"] == "ROOM_NOT_FOUND"


def test_create_room(client):
    response = client.post("/rooms", json=ROOM)

    assert response.status_code == 201
    assert response.headers["Location"] == "/rooms/11"
    assert response.get_json()["price_per_night"] == 3000


def test_patch_room(client):
    response = client.patch("/rooms/1", json={"price_per_night": 2800})

    assert response.status_code == 200
    assert response.get_json()["price_per_night"] == 2800
    assert client.get("/rooms/1").get_json()["price_per_night"] == 2800


def test_delete_room(client):
    created = client.post("/rooms", json=ROOM).get_json()

    response = client.delete(f"/rooms/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/rooms/{created['id']}").status_code == 404


def test_delete_room_in_use(client):
    response = client.delete("/rooms/1")

    assert response.status_code == 409
    assert response.get_json()["code"] == "ROOM_IN_USE"


def test_available_rooms(client):
    response = client.get("/rooms/available?capacity=4")

    assert response.status_code == 200
    assert [room["number"] for room in response.get_json()] == ["301", "304"]


def test_create_booking(client):
    response = client.post("/bookings", json={
        "room_id": 1,
        "guest_id": 1,
        "check_in": "2026-12-01",
        "check_out": "2026-12-03",
        "services": [{"service_id": 2, "quantity": 1}],
    })

    assert response.status_code == 201
    assert response.get_json()["total_price"] == 5300.0
    assert client.get("/rooms/1").get_json()["status"] == "занят"


def test_get_bookings(client):
    response = client.get("/bookings")

    assert response.status_code == 200
    assert len(response.get_json()) == 6
    assert response.get_json()[0]["room_number"]
