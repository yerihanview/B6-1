PRAGMA foreign_keys = ON;

CREATE TABLE categories (
    category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT    NOT NULL UNIQUE,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE members (
    member_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    phone       TEXT    NOT NULL,
    address     TEXT    NOT NULL,
    join_date  TEXT    NOT NULL
);

CREATE TABLE books (
    book_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    title       TEXT    NOT NULL,
    author      TEXT    NOT NULL,
    publisher   TEXT    NOT NULL,
    published_year INTEGER NOT NULL,
    price       INTEGER NOT NULL CHECK (price >= 0),
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
);

CREATE TABLE rentals (
    rental_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id   INTEGER NOT NULL,
    book_id     INTEGER NOT NULL,
    rental_date TEXT    NOT NULL,
    due_date    TEXT    NOT NULL,
    return_date TEXT,
    status      TEXT    NOT NULL CHECK (status IN ('RENTED', 'RETURNED', 'OVERDUE')),
    FOREIGN KEY (member_id) REFERENCES members (member_id),
    FOREIGN KEY (book_id)   REFERENCES books   (book_id)
);

-- 대여일 기준 기간 범위 조회 및 월별 대여 추이 집계 성능을 위해 인덱스를 생성한다.
CREATE INDEX idx_rentals_date ON rentals (rental_date);
