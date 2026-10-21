PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS booking_services;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS guests;
DROP TABLE IF EXISTS rooms;

-- Основная сущность: гостиничный номер
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT NOT NULL UNIQUE,
    room_type TEXT NOT NULL CHECK (room_type IN ('стандартный', 'люкс', 'семейный')),
    price_per_night REAL NOT NULL CHECK (price_per_night > 0),
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    status TEXT NOT NULL DEFAULT 'свободен'
        CHECK (status IN ('свободен', 'занят', 'на обслуживании'))
);

CREATE TABLE guests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL CHECK (length(full_name) > 0),
    email TEXT NOT NULL UNIQUE,
    phone TEXT
);

CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    price REAL NOT NULL CHECK (price >= 0)
);

-- Бронирование: связь 1:N с номерами и гостями
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE RESTRICT,
    guest_id INTEGER NOT NULL REFERENCES guests(id) ON DELETE RESTRICT,
    check_in TEXT NOT NULL,
    check_out TEXT NOT NULL,
    total_price REAL NOT NULL CHECK (total_price >= 0),
    status TEXT NOT NULL DEFAULT 'активно'
        CHECK (status IN ('активно', 'отменено', 'завершено')),
    CHECK (check_out > check_in)
);

-- Промежуточная таблица связи N:M: бронирование и дополнительные услуги
CREATE TABLE booking_services (
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    PRIMARY KEY (booking_id, service_id)
);

-- Индекс для поиска свободных номеров и фильтра по статусу
CREATE INDEX idx_rooms_status ON rooms(status);

-- Индекс для JOIN бронирований с номерами и проверки занятости
CREATE INDEX idx_bookings_room ON bookings(room_id);

-- Индекс для выборки бронирований гостя
CREATE INDEX idx_bookings_guest ON bookings(guest_id);

-- Индекс для сортировки и фильтрации по цене
CREATE INDEX idx_rooms_price ON rooms(price_per_night);
