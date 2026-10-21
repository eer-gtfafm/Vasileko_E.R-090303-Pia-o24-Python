from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from database import get_db
from keyboards.menu import booking_cancel_keyboard, free_rooms_keyboard, main_menu
from services.hotel import BookingError, HotelService, NotFoundError

router = Router()


@router.message(F.text == "🏨 Свободные номера")
async def menu_free(message: Message) -> None:
    db = get_db()
    rooms = HotelService(db.session()).free_rooms()
    if not rooms:
        await message.answer("Свободных номеров нет.", reply_markup=main_menu())
        return
    keyboard = free_rooms_keyboard(rooms)
    await message.answer("Свободные номера (нажмите для бронирования):", reply_markup=keyboard)


@router.message(F.text == "🔍 Поиск номера")
async def menu_search_prompt(message: Message) -> None:
    await message.answer("Введите номер комнаты или часть типа (например: 101 или люкс):", reply_markup=main_menu())


@router.message(F.text == "📅 Мои бронирования")
async def menu_history(message: Message) -> None:
    db = get_db()
    bookings = HotelService(db.session()).history(message.from_user.id)
    if not bookings:
        await message.answer("У вас пока нет бронирований.", reply_markup=main_menu())
        return
    lines = [
        f"№{b.id}: номер {b.room.number} — {b.check_in}…{b.check_out} "
        f"({b.nights} ноч., {b.total} ₽)"
        for b in bookings
    ]
    await message.answer("📅 Ваши бронирования:\n" + "\n".join(lines), reply_markup=main_menu())


@router.message(F.text == "❌ Отменить бронирование")
async def menu_cancel_prompt(message: Message) -> None:
    db = get_db()
    bookings = HotelService(db.session()).history(message.from_user.id)
    if not bookings:
        await message.answer("У вас нет бронирований для отмены.", reply_markup=main_menu())
        return
    await message.answer("Выберите бронирование для отмены:",
                         reply_markup=booking_cancel_keyboard(bookings))


@router.callback_query(F.data.startswith("cancel:"))
async def cb_cancel_booking(callback: CallbackQuery) -> None:
    booking_id = int(callback.data.split(":")[1])
    db = get_db()
    try:
        booking = HotelService(db.session()).cancel_booking(callback.from_user.id, booking_id)
        await callback.message.answer(
            f"Бронирование №{booking.id} (номер {booking.room.number}) отменено. "
            "Номер снова свободен.",
            reply_markup=main_menu(),
        )
    except (NotFoundError, BookingError) as error:
        await callback.message.answer(f"Ошибка: {error}", reply_markup=main_menu())
    await callback.answer()


@router.message(F.text == "➕ Добавить номер")
async def menu_add_room(message: Message) -> None:
    await message.answer(
        "Команда /room_add запускает диалог добавления номера (доступна администратору). "
        "Введите /room_add для начала.",
        reply_markup=main_menu(),
    )