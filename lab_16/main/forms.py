from django import forms

from .models import Booking, Guest, Room


class RoomForm(forms.ModelForm):
    """ModelForm для номера: валидация цены и вместимости."""

    class Meta:
        model = Room
        fields = ["number", "room_type", "floor", "capacity", "price", "status", "amenities"]
        widgets = {
            "amenities": forms.Textarea(attrs={"rows": 2}),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Цена должна быть положительной")
        return price

    def clean_capacity(self):
        capacity = self.cleaned_data["capacity"]
        if capacity <= 0:
            raise forms.ValidationError("Вместимость должна быть больше нуля")
        return capacity


class BookingForm(forms.ModelForm):
    """ModelForm для бронирования: гость, номер, даты."""

    class Meta:
        model = Booking
        fields = ["room", "guest", "check_in", "check_out"]
        widgets = {
            "check_in": forms.DateInput(attrs={"type": "date"}),
            "check_out": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get("check_in")
        check_out = cleaned.get("check_out")
        if check_in and check_out and check_out <= check_in:
            raise forms.ValidationError("Дата выезда должна быть позже даты заезда")
        room = cleaned.get("room")
        if room and check_in and check_out:
            overlaps = Booking.objects.filter(
                room=room, check_in__lt=check_out, check_out__gt=check_in
            )
            if self.instance.pk:
                overlaps = overlaps.exclude(pk=self.instance.pk)
            if overlaps.exists():
                raise forms.ValidationError("Номер уже забронирован на эти даты")
        return cleaned


class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ["full_name", "email", "phone"]