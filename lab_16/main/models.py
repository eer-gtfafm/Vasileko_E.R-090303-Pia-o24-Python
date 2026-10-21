from datetime import date

from django.db import models


def _as_date(value):
    if isinstance(value, str):
        return date.fromisoformat(value)
    return value


class RoomType(models.Model):
    """Тип номера (связь 1:N с номерами)."""

    name = models.CharField("Название", max_length=100, unique=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Тип номера"
        verbose_name_plural = "Типы номеров"

    def __str__(self):
        return self.name


class Room(models.Model):
    """Гостиничный номер — основная сущность."""

    STATUS_FREE = "free"
    STATUS_BOOKED = "booked"
    STATUS_MAINTENANCE = "maintenance"
    STATUS_CHOICES = [
        (STATUS_FREE, "Свободен"),
        (STATUS_BOOKED, "Занят"),
        (STATUS_MAINTENANCE, "На обслуживании"),
    ]

    number = models.CharField("Номер", max_length=10, unique=True)
    room_type = models.ForeignKey(
        RoomType, on_delete=models.CASCADE, related_name="rooms", verbose_name="Тип"
    )
    floor = models.PositiveIntegerField("Этаж")
    capacity = models.PositiveIntegerField("Вместимость")
    price = models.DecimalField("Цена за ночь", max_digits=10, decimal_places=2)
    status = models.CharField("Состояние", max_length=20, choices=STATUS_CHOICES, default=STATUS_FREE)
    amenities = models.TextField("Удобства", blank=True)

    class Meta:
        verbose_name = "Номер"
        verbose_name_plural = "Номера"
        ordering = ["number"]

    def __str__(self):
        return self.number


class Guest(models.Model):
    """Гость (связь 1:N с бронированиями)."""

    full_name = models.CharField("ФИО", max_length=200)
    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Телефон", max_length=30, blank=True)

    class Meta:
        verbose_name = "Гость"
        verbose_name_plural = "Гости"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Booking(models.Model):
    """Бронирование номера гостем."""

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings", verbose_name="Номер")
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name="bookings", verbose_name="Гость")
    check_in = models.DateField("Заезд")
    check_out = models.DateField("Выезд")
    nights = models.PositiveIntegerField("Ночей", default=1)
    total_price = models.DecimalField("Стоимость", max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-check_in"]

    def __str__(self):
        return f"{self.room.number} — {self.guest.full_name} ({self.check_in}…{self.check_out})"

    def save(self, *args, **kwargs):
        check_in = _as_date(self.check_in)
        check_out = _as_date(self.check_out)
        self.nights = max((check_out - check_in).days, 1)
        self.total_price = self.nights * self.room.price
        super().save(*args, **kwargs)