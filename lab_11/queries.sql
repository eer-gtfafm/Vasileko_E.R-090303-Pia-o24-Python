-- 15 обязательных SQL-запросов по базе гостиницы.
-- Файл используется демонстрационным скриптом sql_demo.py.

-- 1. SELECT: все номера
SELECT * FROM rooms;

-- 2. WHERE: свободные номера
SELECT id, number, price_per_night
FROM rooms
WHERE status = 'свободен';

-- 3. ORDER BY: номера по убыванию цены
SELECT number, room_type, price_per_night
FROM rooms
ORDER BY price_per_night DESC;

-- 4. JOIN: бронирования с гостем и номером
SELECT b.id, r.number, g.full_name, b.check_in, b.check_out, b.total_price
FROM bookings b
JOIN rooms r ON r.id = b.room_id
JOIN guests g ON g.id = b.guest_id;

-- 5. LEFT JOIN: все номера и их бронирования (в том числе без броней)
SELECT r.number, b.id AS booking_id, b.status
FROM rooms r
LEFT JOIN bookings b ON b.room_id = r.id;

-- 6. GROUP BY: количество бронирований по типу номера
SELECT r.room_type, COUNT(b.id) AS bookings_count
FROM rooms r
LEFT JOIN bookings b ON b.room_id = r.id
GROUP BY r.room_type;

-- 7. HAVING: гости с двумя и более бронированиями
SELECT g.full_name, COUNT(b.id) AS bookings_count
FROM guests g
JOIN bookings b ON b.guest_id = g.id
GROUP BY g.id, g.full_name
HAVING COUNT(b.id) >= 2;

-- 8. COUNT: общее количество номеров
SELECT COUNT(*) AS rooms_count FROM rooms;

-- 9. AVG и SUM: средняя цена номера и сумма всех бронирований
SELECT AVG(price_per_night) AS avg_price, SUM(total_price) AS total_revenue
FROM rooms
JOIN bookings ON bookings.room_id = rooms.id;

-- 10. INSERT: новая услуга
INSERT INTO services (name, price) VALUES ('Химчистка', 800.0);

-- 11. UPDATE: изменение цены номера
UPDATE rooms
SET price_per_night = price_per_night * 1.05
WHERE room_type = 'люкс';

-- 12. DELETE: удаление услуги, которая ещё не используется
DELETE FROM services
WHERE name = 'Химчистка'
  AND id NOT IN (SELECT service_id FROM booking_services);

-- 13. Подзапрос: номера дороже средней цены
SELECT number, price_per_night
FROM rooms
WHERE price_per_night > (SELECT AVG(price_per_night) FROM rooms)
ORDER BY price_per_night DESC;

-- 14. Несколько условий: свободные семейные номера вместимостью от 4 человек
SELECT number, capacity, price_per_night
FROM rooms
WHERE status = 'свободен'
  AND room_type = 'семейный'
  AND capacity >= 4;

-- 15. Несколько таблиц: бронирования с услугами (N:M через промежуточную таблицу)
SELECT b.id AS booking_id,
       r.number AS room,
       g.full_name AS guest,
       s.name AS service,
       bs.quantity,
       s.price * bs.quantity AS service_total
FROM bookings b
JOIN rooms r ON r.id = b.room_id
JOIN guests g ON g.id = b.guest_id
JOIN booking_services bs ON bs.booking_id = b.id
JOIN services s ON s.id = bs.service_id
ORDER BY b.id, s.name;
