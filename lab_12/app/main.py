import sys
from typing import List, Tuple

from app.database import Database
from app.repositories.order_repository import OrderRepository
from app.repositories.repositories import CustomerRepository, DishRepository
from app.services.services import (
    CustomerService,
    DishService,
    DuplicateError,
    NotFoundError,
    OrderError,
    OrderService,
)


def print_customers(customers) -> None:
    if not customers:
        print("Клиентов нет.")
        return
    print(f"{'ID':>3}  {'ФИО':<28}  Телефон")
    for c in customers:
        print(f"{c.id:>3}  {c.full_name:<28}  {c.phone}")


def print_dishes(dishes) -> None:
    if not dishes:
        print("Блюд нет.")
        return
    print(f"{'ID':>3}  {'Название':<28} {'Категория':<14} {'Цена':>9}")
    for d in dishes:
        print(f"{d.id:>3}  {d.name:<28} {d.category:<14} {float(d.price):>9.2f}")


def print_orders(orders) -> None:
    if not orders:
        print("Заказов нет.")
        return
    for order in orders:
        items = ", ".join(
            f"{item.dish.name} x{item.quantity}" for item in order.items
        ) or "—"
        print(
            f"№{order.id}: {order.customer.full_name} | {order.status} | "
            f"{items} | итого {order.total():.2f} руб."
        )


def read_dish_ids(prompt: str) -> List[Tuple[int, int]]:
    items: List[Tuple[int, int]] = []
    print(prompt)
    while True:
        raw = input("  ID блюда (Enter — закончить): ").strip()
        if not raw:
            break
        try:
            dish_id = int(raw)
        except ValueError:
            print("  Ошибка: ID должен быть целым числом")
            continue
        qty_raw = input("  Количество: ").strip()
        try:
            quantity = int(qty_raw or "1")
        except ValueError:
            print("  Ошибка: количество должно быть целым числом")
            continue
        items.append((dish_id, quantity))
    return items


def main(db_url: str = "sqlite:///restaurant.db", seed: bool = True) -> None:
    database = Database(db_url)
    database.create_tables()
    session = database.session()

    customers = CustomerService(CustomerRepository(session))
    dishes = DishService(DishRepository(session))
    orders = OrderService(OrderRepository(session), DishRepository(session), CustomerRepository(session))

    if seed and not dishes.list():
        for name, category, price in [
            ("Борщ", "супы", 350.0),
            ("Оливье", "салаты", 280.0),
            ("Цезарь", "салаты", 420.0),
            ("Стейк", "горячее", 890.0),
            ("Паста", "горячее", 450.0),
            ("Чизкейк", "десерты", 320.0),
        ]:
            dishes.create(name, category, price)
        customers.create("Иванов Иван", "+7 900 111-11-11")
        customers.create("Петрова Анна", "+7 900 222-22-22")

    while True:
        print("\n=========== РЕСТОРАН (SQLAlchemy ORM) ===========")
        print("1. Список клиентов")
        print("2. Добавить клиента")
        print("3. Список блюд")
        print("4. Найти блюда (категория / часть названия)")
        print("5. Сортировка блюд по цене")
        print("6. Добавить блюдо")
        print("7. Список заказов")
        print("8. Создать заказ (транзакция)")
        print("9. Заказы клиента (связь)")
        print("10. Изменить количество в заказе")
        print("11. Изменить статус заказа")
        print("12. Статистика заказов")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "0":
                print("Работа завершена.")
                break
            elif choice == "1":
                print_customers(customers.list())
            elif choice == "2":
                name = input("ФИО клиента: ").strip()
                phone = input("Телефон: ").strip()
                customer = customers.create(name, phone)
                print(f"Добавлен клиент ID {customer.id}: {customer.full_name}")
            elif choice == "3":
                print_dishes(dishes.list())
            elif choice == "4":
                category = input("Категория (Enter — любая): ").strip() or None
                search = input("Часть названия (Enter — любая): ").strip() or None
                found = dishes.find(category=category, search=search)
                print(f"Найдено блюд: {len(found)}")
                print_dishes(found)
            elif choice == "5":
                print_dishes(dishes.find(sort_by_price=True))
            elif choice == "6":
                name = input("Название блюда: ").strip()
                category = input("Категория: ").strip()
                try:
                    price = float(input("Цена: ").strip())
                except ValueError:
                    raise OrderError("Цена должна быть числом")
                dish = dishes.create(name, category, price)
                print(f"Добавлено блюдо ID {dish.id}: {dish.name}")
            elif choice == "7":
                print_orders(orders.list())
            elif choice == "8":
                customer_id = int(input("ID клиента: "))
                items = read_dish_ids("Введите позиции заказа:")
                comment = input("Комментарий (Enter — без): ").strip() or None
                order = orders.create_order(customer_id, items, comment)
                print(f"Создан заказ №{order.id} на сумму {order.total():.2f} руб.")
            elif choice == "9":
                customer_id = int(input("ID клиента: "))
                print_orders(orders.orders_of_customer(customer_id))
            elif choice == "10":
                item_id = int(input("ID позиции: "))
                quantity = int(input("Новое количество: "))
                orders.change_quantity(item_id, quantity)
                print("Количество обновлено.")
            elif choice == "11":
                order_id = int(input("ID заказа: "))
                status = input("Статус (принят/готовится/выполнен/отменён): ").strip()
                orders.set_status(order_id, status)
                print("Статус обновлён.")
            elif choice == "12":
                stats = orders.stats()
                print(f"Заказов: {stats['count']}; сумма: {stats['total']:.2f} руб.; "
                      f"средний чек: {stats['average']:.2f} руб.")
            else:
                print("Неизвестный пункт меню.")
        except (NotFoundError, DuplicateError, OrderError) as error:
            print("Ошибка:", error)
        except ValueError:
            print("Ошибка: введите корректное число")
        except KeyboardInterrupt:
            print("\nКлиент остановлен.")
            break

    session.close()
    database.engine.dispose()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sqlite:///restaurant.db")