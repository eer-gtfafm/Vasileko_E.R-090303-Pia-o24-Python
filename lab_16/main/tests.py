from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.test import TestCase
from django.urls import reverse

from .models import Booking, Guest, Room, RoomType


class BaseTest(TestCase):
    def setUp(self):
        self.type_std = RoomType.objects.create(name="Стандартный", description="обычный номер")
        self.type_lux = RoomType.objects.create(name="Люкс", description="улучшенный")
        self.room = Room.objects.create(
            number="101", room_type=self.type_std, floor=1, capacity=2,
            price=Decimal("2500.00"), status=Room.STATUS_FREE, amenities="wi-fi, tv",
        )
        self.room2 = Room.objects.create(
            number="201", room_type=self.type_lux, floor=2, capacity=3,
            price=Decimal("6000.00"), status=Room.STATUS_FREE, amenities="wi-fi, джакузи",
        )
        self.guest = Guest.objects.create(full_name="Иванов Иван", email="ivanov@example.com", phone="+79001112233")
        self.user = User.objects.create_user(username="admin", password="secret123", is_staff=True)


class ViewsTest(BaseTest):
    def test_index_page(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Отель")

    def test_room_list_page(self):
        response = self.client.get(reverse("room_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "101")

    def test_room_detail_page(self):
        response = self.client.get(reverse("room_detail", args=[self.room.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2500")

    def test_room_detail_missing(self):
        response = self.client.get(reverse("room_detail", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_statistics_page(self):
        response = self.client.get(reverse("statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Средняя цена")

    def test_search_room(self):
        response = self.client.get(reverse("room_list"), {"q": "джакузи"})
        self.assertContains(response, "201")
        self.assertNotContains(response, ">101<")

    def test_filter_by_type(self):
        response = self.client.get(reverse("room_list"), {"type": self.type_lux.pk})
        self.assertContains(response, "201")
        self.assertNotContains(response, ">101<")

    def test_sort_by_price_desc(self):
        response = self.client.get(reverse("room_list"), {"sort": "-price"})
        content = response.content.decode()
        self.assertLess(content.index("201"), content.index("101"))

    def test_pagination(self):
        for i in range(6):
            Room.objects.create(
                number=f"30{i}", room_type=self.type_std, floor=3, capacity=2,
                price=Decimal("2000.00"), status=Room.STATUS_FREE,
            )
        response = self.client.get(reverse("room_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Стр. 1")

    def test_guest_list(self):
        response = self.client.get(reverse("guest_list"))
        self.assertContains(response, "Иванов Иван")

    def test_booking_list_page(self):
        Booking.objects.create(room=self.room, guest=self.guest, check_in="2026-12-01", check_out="2026-12-03")
        response = self.client.get(reverse("booking_list"))
        self.assertContains(response, "101")


class AuthAndCrudTest(BaseTest):
    def test_create_room_requires_login(self):
        response = self.client.get(reverse("room_create"))
        self.assertEqual(response.status_code, 302)

    def test_create_room_as_admin(self):
        self.client.login(username="admin", password="secret123")
        response = self.client.post(reverse("room_create"), {
            "number": "300", "room_type": self.type_std.pk, "floor": 3,
            "capacity": 4, "price": "3500.00", "status": Room.STATUS_FREE, "amenities": "wi-fi",
        })
        self.assertRedirects(response, reverse("room_detail", args=[Room.objects.get(number="300").pk]))
        self.assertTrue(Room.objects.filter(number="300").exists())

    def test_create_room_invalid_price(self):
        self.client.login(username="admin", password="secret123")
        response = self.client.post(reverse("room_create"), {
            "number": "300", "room_type": self.type_std.pk, "floor": 3,
            "capacity": 4, "price": "-100", "status": Room.STATUS_FREE, "amenities": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Цена должна быть положительной")

    def test_regular_user_cannot_create_room(self):
        user = User.objects.create_user(username="guest", password="secret123", is_staff=False)
        self.client.login(username="guest", password="secret123")
        response = self.client.post(reverse("room_create"), {})
        self.assertEqual(response.status_code, 403)

    def test_update_room_as_admin(self):
        self.client.login(username="admin", password="secret123")
        response = self.client.post(reverse("room_update", args=[self.room.pk]), {
            "number": "101", "room_type": self.type_std.pk, "floor": 1,
            "capacity": 2, "price": "2700.00", "status": Room.STATUS_FREE, "amenities": "wi-fi",
        })
        self.assertRedirects(response, reverse("room_detail", args=[self.room.pk]))
        self.room.refresh_from_db()
        self.assertEqual(self.room.price, Decimal("2700.00"))

    def test_delete_room_as_admin(self):
        self.client.login(username="admin", password="secret123")
        response = self.client.post(reverse("room_delete", args=[self.room2.pk]))
        self.assertRedirects(response, reverse("room_list"))
        self.assertFalse(Room.objects.filter(pk=self.room2.pk).exists())

    def test_booking_creation(self):
        self.client.login(username="admin", password="secret123")
        response = self.client.post(reverse("booking_create"), {
            "room": self.room.pk, "guest": self.guest.pk,
            "check_in": "2026-12-01", "check_out": "2026-12-04",
        })
        self.assertRedirects(response, reverse("booking_list"))
        booking = Booking.objects.get(guest=self.guest, room=self.room)
        self.assertEqual(booking.nights, 3)
        self.assertEqual(booking.total_price, Decimal("7500.00"))

    def test_booking_overlap_rejected(self):
        Booking.objects.create(room=self.room, guest=self.guest, check_in="2026-12-01", check_out="2026-12-05")
        self.client.login(username="admin", password="secret123")
        response = self.client.post(reverse("booking_create"), {
            "room": self.room.pk, "guest": self.guest.pk,
            "check_in": "2026-12-03", "check_out": "2026-12-06",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже забронирован")


class OrmTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.booking = Booking.objects.create(
            room=self.room, guest=self.guest, check_in="2026-12-01", check_out="2026-12-03"
        )

    def test_filter_and_exclude(self):
        self.assertEqual(Room.objects.filter(status=Room.STATUS_FREE).count(), 2)
        self.assertEqual(Room.objects.exclude(status=Room.STATUS_BOOKED).count(), 2)

    def test_get_and_exists(self):
        room = Room.objects.get(number="101")
        self.assertEqual(room.price, Decimal("2500.00"))
        self.assertTrue(Room.objects.filter(number="201").exists())
        self.assertFalse(Room.objects.filter(number="999").exists())

    def test_order_by(self):
        rooms = list(Room.objects.order_by("-price"))
        self.assertEqual(rooms[0].number, "201")

    def test_aggregate_and_annotate(self):
        avg = Room.objects.aggregate(avg_price=Avg("price"))["avg_price"]
        self.assertIsNotNone(avg)
        by_type = (
            RoomType.objects.annotate(room_count=Count("rooms"))
            .order_by("-room_count")
        )
        self.assertGreaterEqual(len(by_type), 1)

    def test_related_objects(self):
        self.assertEqual(self.room.bookings.count(), 1)
        self.assertEqual(self.guest.bookings.count(), 1)
        self.assertEqual(self.room.room_type.name, "Стандартный")

    def test_select_related(self):
        room = Room.objects.select_related("room_type").get(pk=self.room.pk)
        self.assertEqual(room.room_type.name, "Стандартный")