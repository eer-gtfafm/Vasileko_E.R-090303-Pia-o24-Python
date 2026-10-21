"""Этап 1. Наивная реализация системы бронирования гостиницы.

Версия программы ДО применения паттернов проектирования:
тип номера, тариф и уведомления зашиты в виде цепочек if/elif,
а данные хранятся прямо в сервисе.

Проблемы такой реализации:
1. Чтобы добавить новый тип номера, нужно изменить calculate_price()
   и добавить ветку в add_room().
2. Чтобы добавить новый тариф, нужно снова править calculate_price().
3. Уведомления вызываются жёстко внутри book_room(), поэтому новый
   получатель события требует правки сервиса.
4. Хранение данных (список словарей) перемешано с бизнес-логикой,
   заменить его на файл или БД без правки сервиса невозможно.
5. Расчёт цены невозможно протестировать отдельно от меню.
"""

ROOMS = []
BOOKINGS = []


def calculate_price(room_type, base_price, days, tariff):
    # Тип номера "зашит" в условную конструкцию
    if room_type == "standard":
        price_per_night = base_price
    elif room_type == "suite":
        price_per_night = base_price * 2.5
    elif room_type == "family":
        price_per_night = base_price * 1.6
    else:
        raise ValueError("Неизвестный тип номера")

    # Тариф тоже "зашит" в условную конструкцию
    if tariff == "regular":
        total = price_per_night * days
    elif tariff == "seasonal":
        total = price_per_night * days * 1.3
    elif tariff == "weekend":
        total = price_per_night * days * (0.85 if days >= 2 else 1.0)
    else:
        raise ValueError("Неизвестный тариф")

    return round(total, 2)


def add_room(room_id, number, room_type, base_price):
    # Данные хранятся прямо в модуле в виде списка словарей
    if room_type not in ("standard", "suite", "family"):
        raise ValueError("Неизвестный тип номера")
    ROOMS.append({
        "id": room_id,
        "number": number,
        "room_type": room_type,
        "base_price": base_price,
        "status": "свободен",
    })


def book_room(room_id, guest_name, days, tariff):
    room = None
    for item in ROOMS:
        if item["id"] == room_id:
            room = item
            break

    if room is None:
        raise ValueError("Номер не найден")
    if room["status"] != "свободен":
        raise ValueError(f"Номер {room['number']} недоступен")
    if days <= 0:
        raise ValueError("Количество дней должно быть больше 0")

    total = calculate_price(room["room_type"], room["base_price"], days, tariff)
    room["status"] = "забронирован"

    booking = {
        "id": len(BOOKINGS) + 1,
        "room_id": room_id,
        "guest_name": guest_name,
        "days": days,
        "total_cost": total,
    }
    BOOKINGS.append(booking)

    # Уведомления вызываются жёстко: новый получатель = правка метода
    print(f"[УВЕДОМЛЕНИЕ] {guest_name}, номер {room['number']} забронирован.")
    print(f"[ЖУРНАЛ] Создано бронирование №{booking['id']} на {total} руб.")
    return booking


def main():
    add_room(1, "101", "standard", 2500)
    add_room(2, "201", "suite", 2500)
    add_room(3, "301", "family", 2500)

    print("--- НАИВНАЯ РЕАЛИЗАЦИЯ ---")
    for room in ROOMS:
        price = calculate_price(room["room_type"], room["base_price"], 3, "regular")
        print(f"Номер {room['number']} ({room['room_type']}): 3 ночи = {price} руб.")

    book_room(1, "Иванов И. И.", 3, "seasonal")


if __name__ == "__main__":
    main()
