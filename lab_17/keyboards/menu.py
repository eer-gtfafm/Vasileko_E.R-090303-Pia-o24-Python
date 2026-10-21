from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def main_menu() -> ReplyKeyboardMarkup:
    """Reply Keyboard: главное меню бота."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏨 Свободные номера")],
            [KeyboardButton(text="🔍 Поиск номера")],
            [KeyboardButton(text="📅 Мои бронирования")],
            [KeyboardButton(text="➕ Добавить номер")],
            [KeyboardButton(text="❌ Отменить бронирование")],
            [KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
    )


def room_types_keyboard(room_types) -> InlineKeyboardMarkup:
    """Inline-клавиатура выбора типа номера (callback: rtype:<id>)."""
    buttons = [
        [InlineKeyboardButton(text=t.name, callback_data=f"rtype:{t.id}")]
        for t in room_types
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def free_rooms_keyboard(rooms) -> InlineKeyboardMarkup:
    """Inline-клавиатура свободных номеров (callback: book:<room_id>)."""
    buttons = [
        [InlineKeyboardButton(text=f"{r.number} — {r.price} ₽/ночь",
                              callback_data=f"book:{r.id}")]
        for r in rooms
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def booking_cancel_keyboard(bookings) -> InlineKeyboardMarkup:
    """Inline-клавиатура отмены бронирования (callback: cancel:<id>)."""
    buttons = [
        [InlineKeyboardButton(text=f"№{b.id}: {b.room.number} — {b.check_in}",
                              callback_data=f"cancel:{b.id}")]
        for b in bookings
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cancel_operation_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с командой отмены FSM."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/cancel")]],
        resize_keyboard=True,
    )