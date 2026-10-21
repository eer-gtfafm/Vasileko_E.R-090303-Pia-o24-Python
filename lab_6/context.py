from contextlib import contextmanager

# Собственный контекстный менеджер 
@contextmanager
def hotel_operation(operation_name: str):
    print(f"\n--- Начало операции: {operation_name} ---")
    try:
        yield
    except Exception as e:
        print(f"!!! Ошибка в операции '{operation_name}': {e} !!!")
        raise
    finally:
        print(f"--- Завершение операции: {operation_name} ---\n")