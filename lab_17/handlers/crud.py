from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import get_db
from keyboards.menu import cancel_operation_keyboard, main_menu, room_types_keyboard
from services.hotel import BookingError, HotelService, NotFoundError
from states.registration import AddRoomStates

router = Router()

ADMIN_IDS = {0}  # по умолчанию доступ только из конфигурации


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("room_add"))
async def cmd_room_add(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("Добавление номеров доступно только администратору.",
                             reply_markup=main_menu())
        return
    await state.set_state(AddRoomStates.number)
    await message.answer(
        "Добавление номера. Шаг 1/5: введите номер комнаты (или /cancel):",
        reply_markup=cancel_operation_keyboard(),
    )


@router.message(AddRoomStates.number, F.text)
async def fsm_number(message: Message, state: FSMContext) -> None:
    if not message.text.strip():
        await message.answer("Номер не может быть пустым, повторите:")
        return
    await state.update_data(number=message.text.strip())
    await state.set_state(AddRoomStates.room_type)
    db = get_db()
    keyboard = room_types_keyboard(HotelService(db.session()).room_types())
    await message.answer("Шаг 2/5: выберите тип номера:", reply_markup=keyboard)


@router.callback_query(AddRoomStates.room_type, F.data.startswith("rtype:"))
async def fsm_room_type(callback: CallbackQuery, state: FSMContext) -> None:
    room_type_id = int(callback.data.split(":")[1])
    await state.update_data(room_type_id=room_type_id)
    await state.set_state(AddRoomStates.price)
    await callback.message.answer("Шаг 3/5: введите цену за ночь (число):")
    await callback.answer()


@router.message(AddRoomStates.price, F.text)
async def fsm_price(message: Message, state: FSMContext) -> None:
    try:
        price = float(message.text.strip())
    except ValueError:
        await message.answer("Цена должна быть числом (например 3500), повторите:")
        return
    if price <= 0:
        await message.answer("Цена должна быть положительной, повторите:")
        return
    await state.update_data(price=price)
    await state.set_state(AddRoomStates.capacity)
    await message.answer("Шаг 4/5: введите вместимость (человек):")


@router.message(AddRoomStates.capacity, F.text)
async def fsm_capacity(message: Message, state: FSMContext) -> None:
    try:
        capacity = int(message.text.strip())
    except ValueError:
        await message.answer("Вместимость должна быть целым числом, повторите:")
        return
    if capacity <= 0:
        await message.answer("Вместимость должна быть больше нуля, повторите:")
        return
    await state.update_data(capacity=capacity)
    data = await state.get_data()
    db = get_db()
    svc = HotelService(db.session())
    try:
        room_type = svc.get_room_type(data["room_type_id"])
    except NotFoundError:
        await state.clear()
        await message.answer("Тип номера не найден, операция отменена.", reply_markup=main_menu())
        return
    await state.set_state(AddRoomStates.confirm)
    await message.answer(
        f"Шаг 5/5: подтвердите данные\n"
        f"Номер: {data['number']}\n"
        f"Тип: {room_type.name}\n"
        f"Цена: {data['price']} ₽/ночь\n"
        f"Вместимость: {data['capacity']} чел.\n\n"
        f"Введите «да» для сохранения или /cancel:"
    )


@router.message(AddRoomStates.confirm, F.text.lower().in_({"да", "yes"}))
async def fsm_confirm_yes(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    db = get_db()
    try:
        room = HotelService(db.session()).create_room(
            data["number"], data["room_type_id"],
            data["price"], data["capacity"],
        )
    except BookingError as error:
        await state.clear()
        await message.answer(f"Ошибка: {error}", reply_markup=main_menu())
        return
    await state.clear()
    await message.answer(
        f"✅ Номер {room.number} добавлен: {room.room_type.name}, "
        f"{room.price} ₽/ночь, {room.capacity} мест.",
        reply_markup=main_menu(),
    )


@router.message(AddRoomStates.confirm)
async def fsm_confirm_no(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Добавление номера отменено.", reply_markup=main_menu())