class Movie:
    def __init__(self, name, genre, year, rating):
        self.name = name
        self.genre = genre
        self.year = year
        self.rating = rating  # вызовет сеттер для проверки рейтинга
    @property
    def rating(self):
        return self._rating
    @rating.setter
    def rating(self, value):
        from exceptions import InvalidRatingError
        if value < 0 or value > 10:
            raise InvalidRatingError("рейтинг должен быть строго от 0 до 10!") # выбрасываем наше личное исключение, если рейтинг не тот
        self._rating = value
    def to_dict(self):
        """Переводим объект фильма в обычный словарь для сохранения в JSON"""
        return {
            "name": self.name,
            "genre": self.genre,
            "year": self.year,
            "rating": self.rating,
        }
    @classmethod
    def from_dict(cls, data):
        """Собираем объект фильма обратно из словаря JSON"""
        return cls(
            name=data["name"],
            genre=data["genre"],
            year=data["year"],
            rating=data["rating"],
        )
    def __str__(self):
        return f"'{self.name}' | Жанр: {self.genre} | Год: {self.year} | Рейтинг: {self.rating}"
