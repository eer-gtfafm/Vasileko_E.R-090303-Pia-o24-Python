def test_index_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Ресторан" in response.get_data(as_text=True)


def test_list_page(client):
    response = client.get("/dishes")

    assert response.status_code == 200
    assert "Меню" in response.get_data(as_text=True)
    assert "Борщ" in response.get_data(as_text=True)


def test_list_page_search(client):
    response = client.get("/dishes?search=Цезарь")

    text = response.get_data(as_text=True)
    assert "Цезарь" in text
    assert "Солянка" not in text


def test_list_page_filter_by_category(client):
    response = client.get("/dishes?category_id=1")

    text = response.get_data(as_text=True)
    assert "Борщ" in text
    assert "Чизкейк" not in text


def test_list_page_sort_by_price(client):
    response = client.get("/dishes?sort=price&order=desc")

    text = response.get_data(as_text=True)
    assert text.index("Стейк") < text.index("Кофе")


def test_detail_page(client):
    response = client.get("/dishes/1")

    assert response.status_code == 200
    assert "Борщ" in response.get_data(as_text=True)


def test_detail_page_missing(client):
    response = client.get("/dishes/9999")

    assert response.status_code == 404
    assert "not found" not in response.get_data(as_text=True).lower() or "404" in response.get_data(as_text=True)


def test_404_page(client):
    response = client.get("/no-such-page")

    assert response.status_code == 404


def test_create_dish_form(client):
    response = client.post("/dishes/create", data={
        "name": "Пельмени", "description": "С мясом", "price": "380",
        "calories": "520", "available": "1", "category_id": "3",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Пельмени" in response.get_data(as_text=True)


def test_create_dish_invalid_price(client):
    response = client.post("/dishes/create", data={
        "name": "Бесплатное", "description": "", "price": "0",
        "calories": "10", "available": "1", "category_id": "1",
    }, follow_redirects=True)

    assert "Цена должна быть положительной" in response.get_data(as_text=True)


def test_edit_dish(client, dish_id):
    response = client.post(f"/dishes/{dish_id}/edit", data={
        "name": "Обновлённое", "description": "изменено", "price": "300",
        "calories": "150", "available": "1", "category_id": "1",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Обновлённое" in response.get_data(as_text=True)


def test_delete_dish(client, dish_id):
    client.post(f"/dishes/{dish_id}/delete", follow_redirects=True)

    detail = client.get(f"/dishes/{dish_id}")
    assert detail.status_code == 404


def test_create_order_page(client):
    response = client.post("/orders/create", data={
        "customer_name": "Иванов Иван", "dish_ids": ["1", "4"],
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Иванов Иван" in response.get_data(as_text=True)


def test_order_without_dishes(client):
    response = client.post("/orders/create", data={
        "customer_name": "Иванов Иван", "dish_ids": [],
    }, follow_redirects=True)

    assert "хотя бы одно блюдо" in response.get_data(as_text=True)


def test_update_order_status(client):
    client.post("/orders/create", data={"customer_name": "Петров", "dish_ids": ["2"]})
    response = client.post("/orders/1/status", data={"status": "выполнен"},
                           follow_redirects=True)

    assert response.status_code == 200
    assert "выполнен" in response.get_data(as_text=True)


def test_api_list_dishes(client):
    response = client.get("/api/dishes")

    assert response.status_code == 200
    items = response.get_json()
    assert isinstance(items, list)
    assert len(items) >= 5


def test_api_get_dish(client):
    response = client.get("/api/dishes/1")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Борщ"


def test_api_create_dish(client):
    response = client.post("/api/dishes", json={
        "name": "API-блюдо", "description": "создано через API",
        "price": 150.0, "calories": 100, "available": True, "category_id": 1,
    })

    assert response.status_code == 201
    assert response.get_json()["id"] is not None


def test_api_create_dish_bad_price(client):
    response = client.post("/api/dishes", json={
        "name": "X", "description": "", "price": -50.0,
        "calories": 10, "available": True, "category_id": 1,
    })

    assert response.status_code == 400


def test_api_update_dish(client, dish_id):
    response = client.put(f"/api/dishes/{dish_id}", json={"price": 999.0})

    assert response.status_code == 200
    assert response.get_json()["price"] == 999.0


def test_api_update_missing_dish(client):
    response = client.put("/api/dishes/9999", json={"price": 100.0})

    assert response.status_code == 404


def test_api_delete_dish(client, dish_id):
    response = client.delete(f"/api/dishes/{dish_id}")

    assert response.status_code == 204
    assert client.get(f"/api/dishes/{dish_id}").status_code == 404


def test_api_delete_missing_dish(client):
    response = client.delete("/api/dishes/9999")

    assert response.status_code == 404


def test_api_categories(client):
    response = client.get("/api/categories")

    assert response.status_code == 200
    names = [c["name"] for c in response.get_json()]
    assert "супы" in names


def test_api_create_order(client):
    response = client.post("/api/orders", json={
        "customer_name": "API-клиент", "dish_ids": [1, 2],
    })

    assert response.status_code == 201
    body = response.get_json()
    assert body["total"] == 350.0 + 420.0


def test_api_order_missing_dish(client):
    response = client.post("/api/orders", json={
        "customer_name": "API-клиент", "dish_ids": [9999],
    })

    assert response.status_code == 400