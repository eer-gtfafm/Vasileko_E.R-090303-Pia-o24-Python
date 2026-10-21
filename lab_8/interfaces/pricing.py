from typing import Protocol
from models.entities import Room
from models.enums import TariffType


# Общий интерфейс стратегии расчёта стоимости проживания.
class PricingStrategy(Protocol):
    tariff: TariffType

    def calculate(self, room: Room, days: int) -> float: ...
