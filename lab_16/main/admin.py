from django.contrib import admin

from .models import Booking, Guest, Room, RoomType


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("number", "room_type", "floor", "capacity", "price", "status")
    list_filter = ("status", "room_type", "floor")
    search_fields = ("number", "amenities")
    list_editable = ("status", "price")
    ordering = ("number",)


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone")
    search_fields = ("full_name", "email")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("room", "guest", "check_in", "check_out", "nights", "total_price")
    list_filter = ("check_in", "room")
    search_fields = ("guest__full_name", "room__number")
    autocomplete_fields = ("room", "guest")

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct