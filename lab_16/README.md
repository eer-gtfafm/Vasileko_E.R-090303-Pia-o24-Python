# Лабораторная работа №16 — веб-приложение на Django

Вариант 5 — предметная область «Отель» (Room, RoomType, Guest, Booking).

## Технологии

Django 6, Django ORM, миграции, Django Admin, аутентификация, Class-Based и Function-Based views, шаблоны Django Template Language, SQLite (по умолчанию).

## Структура проекта

```
lab_16/
├── manage.py
├── config/                # settings, urls проекта
├── main/                  # приложение
│   ├── models.py          # Room, RoomType, Guest, Booking
│   ├── forms.py           # ModelForm-ы с валидацией
│   ├── views.py           # FVB + CBV, логика прав доступа
│   ├── urls.py            # маршруты приложения
│   ├── admin.py           # регистрация моделей в Admin
│   ├── management/commands/seed.py  # заполнение тестовыми данными
│   ├── templates/         # base, index, списки, формы, статистика
│   └── static/main/style.css
└── requirements.txt
```

## Установка и запуск

```bash
cd lab_16
../venv/bin/pip install django            # если ещё не установлен
../venv/bin/python manage.py migrate
../venv/bin/python manage.py seed          # 4 типа, 16 номеров, 6 гостей, 8 бронирований
../venv/bin/python manage.py runserver     # http://127.0.0.1:8000
```

Админ: http://127.0.0.1:8000/admin — пользователь `admin`, пароль `admin123` (создаётся командой seed).

## Страницы

- `/` — главная (счётчики, ссылки)
- `/rooms/` — список номеров (поиск, фильтр по типу/статусу, сортировка, пагинация)
- `/rooms/<pk>/` — карточка номера
- `/rooms/create/`, `/rooms/<pk>/edit/`, `/rooms/<pk>/delete/` — CRUD (только администратор)
- `/bookings/`, `/bookings/create/` — бронирования (проверка пересечения дат)
- `/guests/` — гости
- `/statistics/` — статистика (ORM aggregate/annotate)

## Тесты

```bash
../venv/bin/python manage.py test
```