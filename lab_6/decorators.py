import time
from functools import wraps
from exceptions import RoomNotAvailableError

# Декоратор №1 — журналирование 
def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Вызван метод {func.__name__}()")
        result = func(*args, **kwargs)
        print(f"[LOG] Результат: {result}")
        return result
    return wrapper

# Декоратор №2 — измерение времени 
def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"[PERFORMANCE] {func.__name__}: {end - start:.5f} сек")
        return result
    return wrapper

# Декоратор №3 — с параметрами 
def require_status(required_status):
    def decorator(func):
        @wraps(func)
        def wrapper(self, room, *args, **kwargs):
            if room.status != required_status:
                raise RoomNotAvailableError(
                    f"Номер {room.number} должен быть в статусе '{required_status.value}', "
                    f"а сейчас он '{room.status.value}'"
                )
            return func(self, room, *args, **kwargs)
        return wrapper
    return decorator