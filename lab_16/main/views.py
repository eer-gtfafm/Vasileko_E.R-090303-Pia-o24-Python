from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import BookingForm, GuestForm, RoomForm
from .models import Booking, Guest, Room, RoomType


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ---------- главная и статистика ----------
def index(request):
    rooms_total = Room.objects.count()
    rooms_free = Room.objects.filter(status=Room.STATUS_FREE).count()
    guests_total = Guest.objects.count()
    bookings_total = Booking.objects.count()
    return render(request, "main/index.html", {
        "rooms_total": rooms_total,
        "rooms_free": rooms_free,
        "guests_total": guests_total,
        "bookings_total": bookings_total,
    })


def statistics(request):
    stats = {
        "rooms_total": Room.objects.count(),
        "rooms_free": Room.objects.filter(status=Room.STATUS_FREE).count(),
        "rooms_booked": Room.objects.filter(status=Room.STATUS_BOOKED).count(),
        "avg_price": Room.objects.aggregate(avg=Avg("price"))["avg"] or 0,
        "max_price": Room.objects.aggregate(max=Max("price"))["max"] or 0,
        "min_price": Room.objects.aggregate(min=Min("price"))["min"] or 0,
        "bookings_total": Booking.objects.count(),
        "revenue": Booking.objects.aggregate(total=Sum("total_price"))["total"] or 0,
        "guests_total": Guest.objects.count(),
    }
    by_type = (
        RoomType.objects.annotate(count=Count("rooms"), avg_price=Avg("rooms__price"))
        .order_by("-count")
    )
    return render(request, "main/statistics.html", {"stats": stats, "by_type": by_type})


# ---------- CRUD номеров (FVB) ----------
def room_list(request):
    query = request.GET.get("q", "")
    room_type = request.GET.get("type", "")
    status = request.GET.get("status", "")
    sort = request.GET.get("sort", "number")

    rooms = Room.objects.select_related("room_type")
    if query:
        rooms = rooms.filter(Q(number__icontains=query) | Q(amenities__icontains=query))
    if room_type:
        rooms = rooms.filter(room_type_id=room_type)
    if status:
        rooms = rooms.filter(status=status)

    allowed_sort = {"number", "price", "capacity", "floor", "-price", "-capacity", "-floor", "-number"}
    if sort in allowed_sort:
        rooms = rooms.order_by(sort)

    paginator = Paginator(rooms, 5)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "main/room_list.html", {
        "rooms": page,
        "types": RoomType.objects.all(),
        "q": query,
        "type_selected": room_type,
        "status_selected": status,
        "sort": sort,
    })


def room_detail(request, pk):
    room = get_object_or_404(Room.objects.select_related("room_type").prefetch_related("bookings__guest"), pk=pk)
    return render(request, "main/room_detail.html", {"room": room})


@login_required
def room_create(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Только администратор может создавать номера")
    form = RoomForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        room = form.save()
        messages.success(request, f"Номер {room.number} создан")
        return redirect("room_detail", pk=room.pk)
    return render(request, "main/room_form.html", {"form": form, "title": "Добавить номер"})


@login_required
def room_update(request, pk):
    if not is_admin(request.user):
        return HttpResponseForbidden("Только администратор может изменять номера")
    room = get_object_or_404(Room, pk=pk)
    form = RoomForm(request.POST or None, instance=room)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Номер обновлён")
        return redirect("room_detail", pk=room.pk)
    return render(request, "main/room_form.html", {"form": form, "title": "Изменить номер"})


class RoomDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Room
    success_url = reverse_lazy("room_list")

    def test_func(self):
        return is_admin(self.request.user)

    def handle_no_permission(self):
        return HttpResponseForbidden("Только администратор может удалять номера")


# ---------- бронирования (CBV) ----------
class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "main/booking_form.html"

    def get_success_url(self):
        return reverse_lazy("booking_list")

    def form_valid(self, form):
        messages.success(self.request, "Бронирование создано")
        return super().form_valid(form)


class BookingListView(ListView):
    model = Booking
    template_name = "main/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10
    ordering = ["-check_in"]


class BookingDetailView(DetailView):
    model = Booking
    template_name = "main/booking_detail.html"
    context_object_name = "booking"


class BookingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Booking
    success_url = reverse_lazy("booking_list")

    def test_func(self):
        return is_admin(self.request.user)

    def handle_no_permission(self):
        return HttpResponseForbidden("Только администратор может удалять бронирования")


# ---------- гости ----------
class GuestCreateView(LoginRequiredMixin, CreateView):
    model = Guest
    form_class = GuestForm

    def get_success_url(self):
        return reverse_lazy("guest_list")


class GuestListView(ListView):
    model = Guest
    context_object_name = "guests"
    paginate_by = 10


class GuestDetailView(DetailView):
    model = Guest
    context_object_name = "guest"

    def get_queryset(self):
        return Guest.objects.prefetch_related("bookings__room")