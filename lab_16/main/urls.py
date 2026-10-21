from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("statistics/", views.statistics, name="statistics"),

    # номера
    path("rooms/", views.room_list, name="room_list"),
    path("rooms/<int:pk>/", views.room_detail, name="room_detail"),
    path("rooms/create/", views.room_create, name="room_create"),
    path("rooms/<int:pk>/edit/", views.room_update, name="room_update"),
    path("rooms/<int:pk>/delete/", views.RoomDeleteView.as_view(), name="room_delete"),

    # бронирования
    path("bookings/", views.BookingListView.as_view(), name="booking_list"),
    path("bookings/create/", views.BookingCreateView.as_view(), name="booking_create"),
    path("bookings/<int:pk>/", views.BookingDetailView.as_view(), name="booking_detail"),
    path("bookings/<int:pk>/delete/", views.BookingDeleteView.as_view(), name="booking_delete"),

    # гости
    path("guests/", views.GuestListView.as_view(), name="guest_list"),
    path("guests/create/", views.GuestCreateView.as_view(), name="guest_create"),
    path("guests/<int:pk>/", views.GuestDetailView.as_view(), name="guest_detail"),
]