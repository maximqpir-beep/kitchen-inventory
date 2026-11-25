PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0)
);
CREATE TABLE IF NOT EXISTS conditions (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    name TEXT NOT NULL UNIQUE,
    usable INTEGER NOT NULL CHECK (usable IN (0, 1))
);
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    name TEXT NOT NULL UNIQUE,
    description TEXT
);
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    name_search TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    state_id INTEGER NOT NULL REFERENCES conditions(id),
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price INTEGER NOT NULL CHECK (unit_price > 0)
);
CREATE TABLE IF NOT EXISTS movements (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    item_id INTEGER NOT NULL REFERENCES items(id),
    from_room INTEGER NOT NULL REFERENCES rooms(id),
    to_room INTEGER NOT NULL REFERENCES rooms(id),
    created_at TEXT NOT NULL CHECK (datetime(created_at) IS NOT NULL),
    cancelled INTEGER NOT NULL DEFAULT 0 CHECK (cancelled IN (0, 1)),
    CHECK (from_room <> to_room)
);
CREATE INDEX IF NOT EXISTS items_room_idx ON items(room_id);
CREATE INDEX IF NOT EXISTS items_category_idx ON items(category_id);
CREATE INDEX IF NOT EXISTS movements_item_idx ON movements(item_id);
CREATE INDEX IF NOT EXISTS movements_date_idx ON movements(created_at);
