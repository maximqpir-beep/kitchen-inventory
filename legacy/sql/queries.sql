-- name: rooms
-- 01. Список помещений; /rooms/.
SELECT id, name, description FROM rooms ORDER BY name, id;

-- name: categories
-- 02. Список категорий; фильтры /items/.
SELECT id, name FROM categories ORDER BY name, id;

-- name: conditions
-- 03. Список состояний; фильтры /items/.
SELECT id, name, usable FROM conditions ORDER BY id;

-- name: items
-- 04. WHERE, JOIN: поиск, помещение, состояние, категория.
-- Параметры: шаблон имени, room дважды, state дважды, category дважды.
SELECT i.id, i.name, i.category_id, c.name AS category_name,
    i.state_id, s.name AS state_name, s.usable,
    i.room_id, r.name AS room_name, i.quantity, i.unit_price,
    i.quantity * i.unit_price AS total
FROM items AS i
JOIN categories AS c ON c.id = i.category_id
JOIN conditions AS s ON s.id = i.state_id
JOIN rooms AS r ON r.id = i.room_id
WHERE i.name_search LIKE ? ESCAPE '\'
  AND (? = 0 OR i.room_id = ?)
  AND (? = 0 OR i.state_id = ?)
  AND (? = 0 OR i.category_id = ?)
ORDER BY i.name_search, i.id;

-- name: available_items
-- 05. WHERE: исправные предметы по помещению.
-- Параметры: room дважды (0 означает все помещения).
SELECT i.id, i.name, i.category_id, c.name AS category_name,
    i.state_id, s.name AS state_name, s.usable,
    i.room_id, r.name AS room_name, i.quantity, i.unit_price,
    i.quantity * i.unit_price AS total
FROM items AS i
JOIN categories AS c ON c.id = i.category_id
JOIN conditions AS s ON s.id = i.state_id
JOIN rooms AS r ON r.id = i.room_id
WHERE s.usable = 1 AND (? = 0 OR i.room_id = ?)
ORDER BY r.name, i.name_search, i.id;

-- name: item_detail
-- 06. JOIN: карточка предмета, параметр ID.
SELECT i.id, i.name, i.category_id, c.name AS category_name,
    i.state_id, s.name AS state_name, s.usable,
    i.room_id, r.name AS room_name, i.quantity, i.unit_price,
    i.quantity * i.unit_price AS total
FROM items AS i
JOIN categories AS c ON c.id = i.category_id
JOIN conditions AS s ON s.id = i.state_id
JOIN rooms AS r ON r.id = i.room_id
WHERE i.id = ?;

-- name: movements
-- 07. JOIN, WHERE, ORDER BY, LIMIT/OFFSET: история.
-- Параметры: date дважды, status дважды (-1 все, 0 выполнено, 1 отменено),
-- limit, offset. Дата YYYY-MM-DD; пустая строка означает все даты.
SELECT m.id, m.item_id, i.name AS item_name,
    m.from_room, f.name AS source_name, m.to_room, t.name AS target_name,
    m.created_at, m.cancelled
FROM movements AS m
JOIN items AS i ON i.id = m.item_id
JOIN rooms AS f ON f.id = m.from_room
JOIN rooms AS t ON t.id = m.to_room
WHERE (? = '' OR date(m.created_at) = ?)
  AND (? = -1 OR m.cancelled = ?)
ORDER BY m.created_at DESC, m.id DESC LIMIT ? OFFSET ?;

-- name: movement_detail
-- 08. JOIN: карточка перемещения, параметр ID.
SELECT m.id, m.item_id, i.name AS item_name,
    m.from_room, f.name AS source_name, m.to_room, t.name AS target_name,
    m.created_at, m.cancelled
FROM movements AS m
JOIN items AS i ON i.id = m.item_id
JOIN rooms AS f ON f.id = m.from_room
JOIN rooms AS t ON t.id = m.to_room
WHERE m.id = ?;

-- name: inventory_totals
-- 09. Агрегаты COUNT/SUM: обзор и статистика.
SELECT COUNT(*) AS batches, COALESCE(SUM(i.quantity), 0) AS units,
    COALESCE(SUM(i.quantity * i.unit_price), 0) AS total,
    COALESCE(SUM(CASE WHEN s.usable = 1 THEN i.quantity ELSE 0 END), 0)
        AS usable
FROM items AS i
JOIN conditions AS s ON s.id = i.state_id;

-- name: movement_totals
-- 10. Агрегаты COUNT/SUM: выполненные и отмененные записи.
SELECT COUNT(*) AS total,
    COALESCE(SUM(CASE WHEN cancelled = 0 THEN 1 ELSE 0 END), 0) AS done,
    COALESCE(SUM(cancelled), 0) AS cancelled FROM movements;

-- name: price_bounds
-- 11. MIN/MAX/AVG: цены за штуку, не стоимость партий.
SELECT MIN(unit_price) AS minimum, MAX(unit_price) AS maximum,
    CAST(ROUND(AVG(unit_price)) AS INTEGER) AS average FROM items;

-- name: category_statistics
-- 12. GROUP BY: партии и количество по категориям.
SELECT c.id, c.name, COUNT(i.id) AS batches,
    COALESCE(SUM(i.quantity), 0) AS units,
    COALESCE(SUM(i.quantity * i.unit_price), 0) AS total
FROM categories AS c LEFT JOIN items AS i ON i.category_id = c.id
GROUP BY c.id, c.name ORDER BY units DESC, c.id;

-- name: room_statistics
-- 13. GROUP BY: все помещения, включая пустые.
SELECT r.id, r.name, COUNT(i.id) AS batches,
    COALESCE(SUM(i.quantity), 0) AS units,
    COALESCE(SUM(i.quantity * i.unit_price), 0) AS total
FROM rooms AS r LEFT JOIN items AS i ON i.room_id = r.id
GROUP BY r.id, r.name ORDER BY r.id;

-- name: condition_statistics
-- 14. GROUP BY: количество по состояниям.
SELECT s.id, s.name, COUNT(i.id) AS batches,
    COALESCE(SUM(i.quantity), 0) AS units
FROM conditions AS s LEFT JOIN items AS i ON i.state_id = s.id
GROUP BY s.id, s.name ORDER BY s.id;

-- name: heavy_rooms
-- 15. HAVING: помещения с количеством предметов >= порога.
SELECT r.id, r.name, COUNT(i.id) AS batches,
    COALESCE(SUM(i.quantity), 0) AS units
FROM rooms AS r LEFT JOIN items AS i ON i.room_id = r.id
GROUP BY r.id, r.name
HAVING COALESCE(SUM(i.quantity), 0) >= ?
ORDER BY units DESC, r.id;

-- name: expensive_items
-- 16. ORDER BY DESC, LIMIT/OFFSET: три дорогие партии на главной.
-- Параметры: limit, offset.
SELECT i.id, i.name, i.category_id, c.name AS category_name,
    i.state_id, s.name AS state_name, s.usable,
    i.room_id, r.name AS room_name, i.quantity, i.unit_price,
    i.quantity * i.unit_price AS total
FROM items AS i
JOIN categories AS c ON c.id = i.category_id
JOIN conditions AS s ON s.id = i.state_id
JOIN rooms AS r ON r.id = i.room_id
ORDER BY total DESC, i.id LIMIT ? OFFSET ?;
