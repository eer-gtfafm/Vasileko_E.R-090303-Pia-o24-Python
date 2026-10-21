import sys

import requests

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 5
ROOM_TYPES = ("стандартный", "люкс", "семейный")
ROOM_STATUSES = ("свободен", "занят", "на обслуживании")


def print_rooms(rooms) -> None:
    if not rooms:
        print("Номеров нет.")
        return
    print(f"{'ID':>3}  {'Номер':<6} {'Тип':<12} {'Цена':>9} {'Мест':>4}  Статус")
    for room in rooms:
        print(f"{room['id']:>3}  {room['number']:<6} {room['room_type']:<12} "
              f"{room['price_per_night']:>9.2f} {room['capacity']:>4}  {room['status']}")


def print_bookings(bookings) -> None:
    if not bookings:
        print("Бронирований нет.")
        return
    for booking in bookings:
        print(f"№{booking['id']}: номер {booking['room_number']}, гость {booking['guest_name']}, "
              f"{booking['check_in']} - {booking['check_out']}, {booking['total_price']:.2f} руб., "
              f"статус: {booking['status']}")


def show(response: requests.Response) -> None:
    if response.status_code == 204:
        print(f"HTTP {response.status_code}: запрос выполнен, тело ответа отсутствует.")
        return
    try:
        payload = response.json()
    except ValueError:
        print(f"HTTP {response.status_code}: некорректный ответ сервера")
        return

    if response.status_code >= 400:
        print(f"HTTP {response.status_code}: {payload.get('error')} (код {payload.get('code')})")
        return

    print(f"HTTP {response.status_code}:")
    if isinstance(payload, list):
        if payload and "room_number" in payload[0]:
            print_bookings(payload)
        else:
            print_rooms(payload)
    elif "room_number" in payload:
        print_bookings([payload])
    else:
        print_rooms([payload])


def read_room_payload(partial: bool = False) -> dict:
    payload = {}
    number = input("Номер комнаты: ").strip()
    if number or not partial:
        payload["number"] = number
    room_type = input(f"Тип ({'/'.join(ROOM_TYPES)}): ").strip()
    if room_type or not partial:
        payload["room_type"] = room_type
    price = input("Цена за ночь: ").strip()
    if price or not partial:
        payload["price_per_night"] = price
    capacity = input("Количество мест: ").strip()
    if capacity or not partial:
        payload["capacity"] = capacity
    status = input(f"Статус ({'/'.join(ROOM_STATUSES)}), Enter — не менять: ").strip()
    if status:
        payload["status"] = status
    return {key: value for key, value in payload.items() if value != ""}


def main() -> None:
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})

    while True:
        print("\n=========================")
        print("   REST CLIENT + SQL DB")
        print("=========================")
        print("1. Получить список номеров")
        print("2. Получить номер по ID (кэш)")
        print("3. Создать номер")
        print("4. Изменить (PUT)")
        print("5. Частично изменить (PATCH)")
        print("6. Удалить")
        print("7. Фильтрация")
        print("8. Сортировка")
        print("9. Свободные номера")
        print("10. Создать бронирование")
        print("11. Список бронирований")
        print("12. Статистика кэша")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "0":
            print("Работа клиента завершена.")
            break

        try:
            if choice == "1":
                show(session.get(f"{BASE_URL}/rooms", timeout=TIMEOUT))
            elif choice == "2":
                room_id = input("ID номера: ").strip()
                show(session.get(f"{BASE_URL}/rooms/{room_id}", timeout=TIMEOUT))
            elif choice == "3":
                show(session.post(f"{BASE_URL}/rooms", json=read_room_payload(), timeout=TIMEOUT))
            elif choice == "4":
                room_id = input("ID номера: ").strip()
                show(session.put(f"{BASE_URL}/rooms/{room_id}", json=read_room_payload(), timeout=TIMEOUT))
            elif choice == "5":
                room_id = input("ID номера: ").strip()
                show(session.patch(f"{BASE_URL}/rooms/{room_id}",
                                   json=read_room_payload(partial=True), timeout=TIMEOUT))
            elif choice == "6":
                room_id = input("ID номера: ").strip()
                show(session.delete(f"{BASE_URL}/rooms/{room_id}", timeout=TIMEOUT))
            elif choice == "7":
                params = {}
                room_type = input(f"Тип ({'/'.join(ROOM_TYPES)}), Enter — любой: ").strip()
                if room_type:
                    params["type"] = room_type
                min_price = input("Минимальная цена, Enter — без ограничения: ").strip()
                if min_price:
                    params["min_price"] = min_price
                max_price = input("Максимальная цена, Enter — без ограничения: ").strip()
                if max_price:
                    params["max_price"] = max_price
                show(session.get(f"{BASE_URL}/rooms", params=params, timeout=TIMEOUT))
            elif choice == "8":
                sort = input("Поле сортировки (price/number/capacity): ").strip()
                order = input("Порядок (asc/desc): ").strip()
                show(session.get(f"{BASE_URL}/rooms", params={"sort": sort, "order": order}, timeout=TIMEOUT))
            elif choice == "9":
                capacity = input("Минимальная вместимость, Enter — любая: ").strip()
                params = {"capacity": capacity} if capacity else {}
                show(session.get(f"{BASE_URL}/rooms/available", params=params, timeout=TIMEOUT))
            elif choice == "10":
                payload = {
                    "room_id": int(input("ID номера: ")),
                    "guest_id": int(input("ID гостя: ")),
                    "check_in": input("Дата заезда (YYYY-MM-DD): ").strip(),
                    "check_out": input("Дата выезда (YYYY-MM-DD): ").strip(),
                }
                services = input("ID услуг через запятую, Enter — без услуг: ").strip()
                payload["services"] = [
                    {"service_id": int(item), "quantity": 1}
                    for item in services.split(",") if item.strip()
                ]
                show(session.post(f"{BASE_URL}/bookings", json=payload, timeout=TIMEOUT))
            elif choice == "11":
                show(session.get(f"{BASE_URL}/bookings", timeout=TIMEOUT))
            elif choice == "12":
                show(session.get(f"{BASE_URL}/cache/stats", timeout=TIMEOUT))
            else:
                print("Неизвестный пункт меню.")
        except requests.ConnectionError:
            print("Сервер недоступен: сначала запустите app.py")
        except requests.Timeout:
            print("Тайм-аут ожидания ответа от сервера")
        except ValueError as error:
            print(f"Ошибка ввода: {error}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nКлиент остановлен.")
        sys.exit(0)
