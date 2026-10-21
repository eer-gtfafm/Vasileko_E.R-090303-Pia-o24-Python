from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import get_db
from database.models import Database
from keyboards.menu import main_menu
from services.hotel import HotelService

router = Router()


def service(db: Database) -> HotelService:
    return HotelService(db.session())


HELP_TEXT = (
    "🏨 <b>Бот гостиницы</b>\n\n"
    "Команды:\n"
    "/start — главное меню\n"
    "/help — помощь\n"
    "/cancel — отменить текущую операцию\n"
    "/rooms — список всех номеров\n"
    "/stats — статистика (админ)\n\n"
    "Возможности меню:\n"
    "— поиск свободных номеров\n"
    "— бронирование номера\n"
    "— отмена бронирования\n"
    "— история бронирований\n"
    "— добавление номера (админ)"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    db = get_db()
    svc = HotelService(db.session())
    svc.get_or_create_client(
        message.from_user.id,
        message.from_user.full_name or "Клиент",
    )
    await message.answer(
        f"Здравствуйте, {message.from_user.full_name or 'гость'}! "
        "Добро пожаловать в бот гостиницы. Выберите действие:",
        reply_markup=main_menu(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu())


@router.message(Command("cancel"), StateFilter("*"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        await message.answer("Сейчас нет активной операции.", reply_markup=main_menu())
        return
    await state.clear()
    await message.answer("Операция отменена.", reply_markup=main_menu())


@router.message(Command("rooms"))
async def cmd_rooms(message: Message) -> None:
    db = get_db()
    rooms = HotelService(db.session()).list_rooms()
    if not rooms:
        await message.answer("Номеров в базе нет.")
        return
    lines = [f"{r.id}. Номер {r.number} — {r.room_type.name}, {r.price} ₽/ночь, "
             f"{r.capacity} мест, статус: {r.status}" for r in rooms]
    await message.answer("\n".join(lines), reply_markup=main_menu())


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if not message.from_user or message.from_user.id != 0:
        db = get_db()
        stats = HotelService(db.session()).statistics()
        await message.answer(
            f"📊 <b>Статистика</b>\n"
            f"Номеров в базе: {stats['rooms']}\n"
            f"Клиентов: {stats['clients']}\n"
            f"Бронирований: {stats['bookings']}"
        )


@router.message(F.text == "ℹ️ Помощь")
async def menu_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu())