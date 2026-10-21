def get_num_input(prompt, is_float=False): #проверка на правильно введенные символы (цифры)
    while True:
        try:
            return float(input(prompt)) if is_float else int(input(prompt))
        except ValueError:
            print("ошибка. введите числовое значение")


class vehicle: #родительский класс "транспортное средство"
    def __init__(self, brand, model, price): #конструктор класса для слздания объекта
        self.brand, self.model, self.price  = brand, model, price  #сохраняем 
    @property #декоратор, который превращает обычный метод класса в свойство
    def price(self):
        return self._price
    @price.setter # сеттер: метод для инкапсуляции и проверки цены при ее записи/изменении
    def price(self, value):
        if value < 0:
            raise ValueError("цена не может быть отрицательной!")
        self._price = value
    def get_performance(self): # базовый метод для расчета эффективности (общий интерфейс для полиморфизма)
        return 0 # по умолчанию для абстрактного транспорта возвращает ноль


class car(vehicle):  # создаем класс "легковой авто", который наследует всё от класса vehicle
    def __init__(self, brand, model, price, passengers):  # конструктор, принимает общие параметры и уникальное количество мест
        super().__init__(brand, model, price)  # super() вызывает конструктор родителя, чтобы записать марку, модель и цену
        self.passengers = passengers  # сохраняем количество пассажиров в уникальное свойство объекта
    def get_performance(self):  # переопределяем метод: теперь он считает показатель именно для легковой машины
        return round(self.price / self.passengers, 2)  # вычисляем, сколько рублей стоимости машины приходится на одно место
    def __str__(self):  # специальный метод для автоматического превращения объекта в текст при печати через print()
        return f"легковой: {self.brand} {self.model} ; цена: {self.price} руб. ; мест: {self.passengers}"  # возвращаем строку данных


class truck(vehicle):  # создаем класс "грузовик", также наследующий класс vehicle
    def __init__(self, brand, model, price, capacity):  # конструктор, принимает общие параметры и уникальную грузоподъемность
        super().__init__(brand, model, price)  # передаем марку, модель и цену на обработку в родительский класс
        self.capacity = capacity  # сохраняем грузоподъемность (в тоннах) в свойство объекта
    def get_performance(self):  # переопределяем метод под логику грузовика (полиморфизм)
        return round(self.price / self.capacity, 2)  # вычисляем стоимость машины на одну тонну ее веса
    def __str__(self):  # специальный метод для текстового представления грузовика в консоли
        return f"грузовой: {self.brand} {self.model} ; цена: {self.price} руб. ; грузоподъемность: {self.capacity} т."  # возвращаем строку данных


class fleet:  # объявляем класс "автопарк", который будет управлять всеми машинами
    def __init__(self, name):  # конструктор, принимает только название парка
        self.name, self.vehicles = name, []  # записываем имя, а в self.vehicles создаем пустой список для хранения будущих объектов (композиция)


def main():
    my_fleet = fleet("автопарк")
    my_fleet.vehicles = [
        car("toyota", "camry", 2000000, 5),
        truck("KAMAZ", "65115", 5000000, 15),
        car("lada", "vesta", 1200000, 5),
    ]
    while True:
        print(f"\n===== МЕНЮ АВТОПАРКА '{my_fleet.name}' =====")
        print("1. добавить | 2. показать все | 3. действие | 4. изменить цену | 5. удалить | 6. статистика | 0. выход")
        choice = input("выберите действие: ").strip()
        if choice == "1":
            t_type = input("тип (1 - легковой, 2 - грузовой): ").strip()
            if t_type not in ("1", "2"):
                print("неверный тип!")
                continue
            brand, model = input("марка: ").strip(), input("модель: ").strip()
            price = get_num_input("цена (руб.): ", is_float=True)
            if t_type == "1":
                p = get_num_input("количество пассажиров: ")
                my_fleet.vehicles.append(car(brand, model, price, p))
            else:
                c = get_num_input("грузоподъемность (тонн): ", is_float=True)
                my_fleet.vehicles.append(truck(brand, model, price, c))
            print("транспорт добавлен!")
        elif choice == "2":
            if not my_fleet.vehicles:
                print("автопарк пуст.")
            for idx, v in enumerate(my_fleet.vehicles, 1):
                print(f"{idx}. {v}")
        elif choice == "3":  
            print("\n--- транспортные показатели (стоимость единицы емкости): ---")
            for v in my_fleet.vehicles:
                print(
                    f"- {v.brand} {v.model}  показатель: {v.get_performance()} руб."
                )
        elif choice == "4":  
            try:
                idx = get_num_input("введите номер транспорта: ") - 1
                if 0 <= idx < len(my_fleet.vehicles):
                    my_fleet.vehicles[idx].price = get_num_input(
                        "новая цена: ", is_float=True
                    )
                    print("цена успешно изменена!")
                else:
                    print("неверный номер!")
            except ValueError as e:
                print(f"ошибка изменения: {e}")
        elif choice == "5":
            idx = get_num_input("введите номер для удаления: ") - 1
            if 0 <= idx < len(my_fleet.vehicles):
                print(
                    f"удален: {my_fleet.vehicles.pop(idx).brand} {my_fleet.vehicles[idx].model}"
                )
            else:
                print("неверный номер!")
        elif choice == "6":
            if not my_fleet.vehicles:
                continue
            prices = [v.price for v in my_fleet.vehicles]  
            print(
                f"\nвсего техники: {len(my_fleet.vehicles)} ед.\nобщая стоимость: {sum(prices)} руб.\nсредняя цена: {round(sum(prices)/len(prices), 2)} руб."
            )
        elif choice == "0":
            print("работа программы завершена")
            break


if __name__ == "__main__":
    main()