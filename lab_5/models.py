class Movie:  # создаем класс для фильма


    def __init__(
        self, name, genre, year, rating, duration
    ):  # конструктор, принимает название, жанр, год, рейтинг и длительность
        self.name = name  # записываем название фильма в объект
        self.genre = genre  # записываем жанр фильма
        self.year = year  # записываем год выпуска
        self.rating = rating  # записываем рейтинг фильма
        self.duration = duration  # продолжительность фильма в минутах


    def __str__(
        self,
    ):  # специальный метод для красивого вывода данных о фильме через print()
        return f"'{self.name}' [{self.genre}] | Год: {self.year} | Рейтинг: {self.rating} | Время: {self.duration} мин."  # возвращаем оформленную строку
