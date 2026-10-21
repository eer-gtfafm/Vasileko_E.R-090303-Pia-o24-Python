from aiogram.fsm.state import State, StatesGroup


class AddRoomStates(StatesGroup):
    """Многошаговый FSM-сценарий добавления номера: 5 состояний."""

    number = State()
    room_type = State()
    price = State()
    capacity = State()
    confirm = State()


class BookingStates(StatesGroup):
    """FSM-сценарий бронирования номера."""

    select_room = State()
    check_in = State()
    check_out = State()