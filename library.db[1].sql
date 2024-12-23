CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    author_id INTEGER REFERENCES authors(id),
    year INTEGER,
    available BOOLEAN DEFAULT TRUE
);

CREATE TABLE readers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE book_history (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES books(id),
    reader_id INTEGER REFERENCES readers(id),
    issue_date DATE,
    return_date DATE
);
