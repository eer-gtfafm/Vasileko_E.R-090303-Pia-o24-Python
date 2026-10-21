def test_get_list(client):
    response = client.get("/rooms")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 12
    assert len(data["items"]) == data["total"]


def test_get_existing_room(client):
    response = client.get("/rooms/1")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["number"]
    assert body["price"] > 0


def test_get_missing_room(client):
    response = client.get("/rooms/99999")

    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


def test_post_correct_room(client, sample_room):
    response = client.post("/rooms", json=sample_room)

    assert response.status_code == 201
    body = response.json()
    assert body["number"] == "705"
    assert body["price"] == 8000.0
    assert body["amenities"] == ["wi-fi", "мини-бар"]


def test_post_duplicate_room_conflict(client, sample_room):
    client.post("/rooms", json=sample_room)
    response = client.post("/rooms", json=sample_room)

    assert response.status_code == 409


def test_post_invalid_room(client):
    response = client.post("/rooms", json={
        "number": "1", "room_type": "люкс", "floor": 1,
        "capacity": 2, "price": -100, "available": True, "amenities": [],
    })

    assert response.status_code == 422


def test_post_missing_field(client):
    response = client.post("/rooms", json={"number": "111", "price": 100})

    assert response.status_code == 422


def test_put_room(client, sample_room):
    payload_create = {**sample_room, "number": "706"}
    created = client.post("/rooms", json=payload_create).json()
    payload = {**payload_create, "price": 9000.0}
    response = client.put(f"/rooms/{created['id']}", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["number"] == "706"
    assert body["price"] == 9000.0


def test_put_missing_room(client, sample_room):
    response = client.put("/rooms/99999", json=sample_room)

    assert response.status_code == 404


def test_patch_room(client, sample_room):
    created = client.post("/rooms", json={**sample_room, "number": "707"}).json()
    response = client.patch(f"/rooms/{created['id']}", json={"price": 8500.0})

    assert response.status_code == 200
    body = response.json()
    assert body["price"] == 8500.0
    assert body["number"] == created["number"]


def test_delete_room(client, sample_room):
    created = client.post("/rooms", json={**sample_room, "number": "708"}).json()
    response = client.delete(f"/rooms/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/rooms/{created['id']}").status_code == 404


def test_delete_missing_room(client):
    response = client.delete("/rooms/99999")

    assert response.status_code == 404


def test_filter_by_type(client):
    response = client.get("/rooms", params={"room_type": "люкс"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert all(item["room_type"] == "люкс" for item in data["items"])


def test_filter_by_price_range(client):
    response = client.get("/rooms", params={"min_price": 5000, "max_price": 7000})

    data = response.json()
    assert all(5000 <= item["price"] <= 7000 for item in data["items"])


def test_sort_desc(client):
    ascending = client.get("/rooms", params={"sort": "price", "order": "asc"}).json()["items"]
    descending = client.get("/rooms", params={"sort": "price", "order": "desc"}).json()["items"]

    assert [r["price"] for r in ascending] == sorted(r["price"] for r in ascending)
    assert [r["price"] for r in descending] == sorted((r["price"] for r in descending), reverse=True)


def test_pagination(client):
    page1 = client.get("/rooms", params={"skip": 0, "limit": 5}).json()
    page2 = client.get("/rooms", params={"skip": 5, "limit": 5}).json()

    assert len(page1["items"]) == 5
    assert len(page2["items"]) == 5
    assert page1["items"][0]["id"] != page2["items"][0]["id"]


def test_search(client):
    response = client.get("/rooms/search", params={"q": "201"})

    assert response.status_code == 200
    assert any(room["number"] == "201" for room in response.json())


def test_statistics(client):
    response = client.get("/rooms/statistics")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 12
    assert body["average_price"] > 0
    assert body["min_price"] <= body["max_price"]


def test_cache_hit_after_get(client):
    first = client.get("/rooms/1")
    second = client.get("/rooms/1")

    assert first.json() == second.json()
    assert first.status_code == 200


def test_cache_invalidated_after_patch(client, sample_room):
    created = client.post("/rooms", json={**sample_room, "number": "709"}).json()
    client.get(f"/rooms/{created['id']}")

    client.patch(f"/rooms/{created['id']}", json={"price": 9999.0})
    fresh = client.get(f"/rooms/{created['id']}")

    assert fresh.json()["price"] == 9999.0


def test_invalid_query_order(client):
    response = client.get("/rooms", params={"order": "sideways"})

    assert response.status_code == 422


def test_validation_error_body(client):
    response = client.post("/rooms", json={"number": "", "room_type": "люкс", "floor": 1,
                                           "capacity": 2, "price": 100, "available": True,
                                           "amenities": []})

    assert response.status_code == 422