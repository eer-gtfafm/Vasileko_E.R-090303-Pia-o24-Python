from interfaces.pricing import PricingStrategy
from models.entities import Room
from models.enums import TariffType


# Обычный тариф: стоимость = цена за ночь * количество ночей.
class RegularTariff:
    tariff = TariffType.REGULAR

    def calculate(self, room: Room, days: int) -> float:
        return round(room.price_per_night * days, 2)


# Сезонный тариф: наценка 30% в высокий сезон.
class SeasonalTariff:
    tariff = TariffType.SEASONAL
    COEFFICIENT = 1.3

    def calculate(self, room: Room, days: int) -> float:
        return round(room.price_per_night * days * self.COEFFICIENT, 2)


# Тариф выходного дня: скидка 15% при проживании от двух ночей.
class WeekendTariff:
    tariff = TariffType.WEEKEND
    DISCOUNT = 0.15

    def calculate(self, room: Room, days: int) -> float:
        cost = room.price_per_night * days
        if days >= 2:
            cost *= 1 - self.DISCOUNT
        return round(cost, 2)
