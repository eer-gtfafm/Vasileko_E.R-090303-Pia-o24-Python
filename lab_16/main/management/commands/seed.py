from decimal import Decimal
from random import randint

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from main.models import Booking, Guest, Room, RoomType


class Command(BaseCommand):
    help = "Заполняет базу тестовыми данными: 4 типа, 16 номеров, 6 гостей, бронирования"

    def handle(self, *args, **options):
        if RoomType.objects.exists():
            self.stdout.write("База уже заполнена, пропускаю")
            return

        types = {}
        for name, desc in [
            ("Стандартный", "Однокомнатный номер с базовыми удобствами"),
            ("Люкс", "Просторный номер с мини-баром и джакузи"),
            ("Семейный", "Номер с кухней и двумя комнатами"),
            ("Студия", "Номер с мягкой мебелью и кофемашиной"),
        ]:
            types[name] = RoomType.objects.create(name=name, description=desc)

        seed_rooms = [
            ("101", "Стандартный", 1, 2, 2500), ("102", "Стандартный", 1, 2, 2700),
            ("103", "Стандартный", 1, 1, 2400), ("104", "Стандартный", 1, 3, 2900),
            ("201", "Люкс", 2, 2, 6000), ("202", "Люкс", 2, 3, 6500),
            ("203", "Люкс", 2, 2, 6200), ("204", "Люкс", 2, 2, 6800),
            ("301", "Семейный", 3, 4, 4200), ("302", "Семейный", 3, 4, 4400),
            ("303", "Семейный", 3, 5, 4500), ("304", "Семейный", 3, 6, 4800),
            ("401", "Студия", 4, 2, 3500), ("402", "Студия", 4, 2, 3700),
            ("403", "Студия", 4, 3, 3900), ("404", "Студия", 4, 3, 4100),
        ]
        for number, type_name, floor, capacity, price in seed_rooms:
            Room.objects.create(
                number=number, room_type=types[type_name], floor=floor, capacity=capacity,
                price=Decimal(str(price)), status=Room.STATUS_FREE,
                amenities="wi-fi, tv" if floor in (1, 4) else "wi-fi, tv, кондиционер, мини-бар",
            )

        guests = [
            ("Иванов Иван Иванович", "ivanov@example.com", "+7 900 111-11-11"),
            ("Петрова Анна Сергеевна", "petrova@example.com", "+7 900 222-22-22"),
            ("Сидоров Олег Петрович", "sidorov@example.com", "+7 900 333-33-33"),
            ("Кузнецова Мария Ивановна", "kuznetsova@example.com", "+7 900 444-44-44"),
            ("Смирнов Дмитрий Андреевич", "smirnov@example.com", "+7 900 555-55-55"),
            ("Волкова Елена Викторовна", "volkova@example.com", "+7 900 666-66-66"),
        ]
        guest_objs = [Guest.objects.create(full_name=name, email=email, phone=phone) for name, email, phone in guests]

        rooms = list(Room.objects.all())
        for i in range(8):
            room = rooms[i % len(rooms)]
            guest = guest_objs[i % len(guest_objs)]
            day_in = 10 + i
            day_out = day_in + randint(1, 4)
            month = 12 if i >= 7 else 11
            Booking.objects.create(
                room=room, guest=guest,
                check_in=f"2026-{month:02d}-{day_in:02d}",
                check_out=f"2026-{month:02d}-{day_out:02d}",
            )

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123")

        self.stdout.write(self.style.SUCCESS("База заполнена: 4 типа, 16 номеров, 6 гостей, 8 бронирований, админ admin/admin123"))