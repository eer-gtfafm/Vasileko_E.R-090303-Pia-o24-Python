from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import get_db
from keyboards.menu import main_menu
from services.hotel import BookingError, HotelService, NotFoundError
from states.registration import BookingStates

router = Router()

DATE_HINT = "Введите дату в формате ГГГГ-ММ-ДД, например 2026-12-01 (или /cancel для отмены):"


@router.callback_query(F.data.startswith("book:"))
async def cb_select_room(callback: CallbackQuery, state: FSMContext) -> None:
    room_id = int(callback.data.split(":")[1])
    await state.set_state(BookingStates.check_in)
    await state.update_data(room_id=room_id)
    await callback.message.answer(f"Вы выбрали бронирование номера. {DATE_HINT}")
    await callback.answer()


@router.message(BookingStates.check_in, F.text)
async def booking_check_in(message: Message, state: FSMContext) -> None:
    check_in = message.text.strip()
    from datetime import date
    try:
        date.fromisoformat(check_in)
    except ValueError:
        await message.answer("Некорректная дата, повторите (ГГГГ-ММ-ДД):")
        return
    await state.update_data(check_in=check_in)
    await state.set_state(BookingStates.check_out)
    await message.answer("Дата выезда. " + DATE_HINT)


@router.message(BookingStates.check_out, F.text)
async def booking_check_out(message: Message, state: FSMContext) -> None:
    check_out = message.text.strip()
    data = await state.get_data()
    from datetime import date
    try:
        end = date.fromisoformat(check_out)
        start = date.fromisoformat(data["check_in"])
    except ValueError:
        await message.answer("Некорректная дата, повторите (ГГГГ-ММ-ДД):")
        return
    if (end - start).days <= 0:
        await message.answer("Дата выезда должна быть позже даты заезда, повторите:")
        return

    db = get_db()
    try:
        booking = HotelService(db.session()).create_booking(
            message.from_user.id, data["room_id"],
            data["check_in"], check_out,
        )
    except (NotFoundError, BookingError) as error:
        await state.clear()
        await message.answer(f"Ошибка бронирования: {error}", reply_markup=main_menu())
        return

    await state.clear()
    await message.answer(
        f"✅ Бронирование №{booking.id} оформлено!\n"
        f"Номер: {booking.room.number}\n"
        f"Период: {booking.check_in} — {booking.check_out} "
        f"({booking.nights} ноч.)\n"
        f"Стоимость: {booking.total} ₽",
        reply_markup=main_menu(),
    )


@router.message(BookingStates.check_in, StateFilter("*"))
@router.message(BookingStates.check_out, StateFilter("*"))
async def booking_invalid_input(message: Message) -> None:
    await message.answer("Пожалуйста, введите дату текстом (ГГГГ-ММ-ДД) или /cancel.")