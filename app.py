from flask import Flask, render_template, request, redirect
import psycopg2
from config import host, user, password, db_name

app = Flask(__name__)

try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    connection.autocommit = True

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT version();"
        )

        print(f"Server version: {cursor.fetchone()}")
    

    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         "SELECT version();"
    #     )

    #     print(f"Server version: {cursor.fetchone()}")


    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """CREATE TABLE authors (
    #             id serial PRIMARY KEY,
    #             name varchar(100));"""
    #     )


    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """CREATE TABLE books (
    #             id SERIAL PRIMARY KEY,
    #             title varchar(100),
    #             author_id INTEGER REFERENCES authors(id),
    #             year int,
    #             available boolean DEFAULT TRUE,
    #     )


    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """CREATE TABLE readers (
    #             id serial PRIMARY KEY,
    #             name varchar(100),
    #             registration_date DATE DEFAULT CURRENT_DATE,
    #             phone varchar(15));"""
    #     )

    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """CREATE TABLE loan_history (
    #             id serial PRIMARY KEY,
    #             book_id INTEGER REFERENCES books(id),
    #             reader_id INTEGER REFERENCES readers(id),
    #             issue_date DATE DEFAULT CURRENT_DATE,
    #             return_date DATE,
    #             status varchar(20) DEFAULT 'issued');"""
    #     )

except Exception as ex:
    print("[INFO] Error while working with PostgreSQL:", ex)
finally:
    if connection:
        connection.close()
        print("[INFO] PostgreSQL connection closed")

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books')
def books():
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )

        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, author_id, year, available FROM BOOKS;"
                )
            
            books = cursor.fetchall()

        return render_template('books.html', books=books)
    except Exception as ex:
        print("[INFO] Error while working with PostgreSQL:", ex)
    finally:
        if connection:
            connection.close()

@app.route('/sorted_books', methods=['GET'])
def sorted_books():
    sort_by = request.args.get('sort_by', 'title')

    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )

        connection.autocommit = True

        with connection.cursor() as cursor:
            if sort_by == 'year':
                cursor.execute("SELECT id, title, author_id, year, available FROM books ORDER BY year;")
            else: 
                cursor.execute("SELECT id, title, author_id, year, available FROM books ORDER BY title;")
            
            books = cursor.fetchall()

        return render_template('sorted_books.html', books=books, sort_by=sort_by)

    except Exception as ex:
        print("[INFO] Error while working with PostgreSQL:", ex)
    finally:
        if connection:
            connection.close()



@app.route('/search_books', methods=['GET'])
def search_books():
    book_title = request.args.get('book_title', '')

    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )

        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, author_id, year, available FROM books WHERE title ILIKE %s;",  
                ('%' + book_title + '%',) 
            )
            books = cursor.fetchall()

        return render_template('search_books.html', books=books, query=book_title)

    except Exception as ex:
        print("[INFO] Error while working with PostgreSQL:", ex)
    finally:
        if connection:
            connection.close()

# Страница для обновления книги
@app.route('/update_book', methods=['POST', 'GET'])
def update_book():
    if request.method == 'POST':
        book_id = request.form['book_id']
        title = request.form['title']
        year = request.form['year']

        try:
            # Подключаемся к базе данных
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            connection.autocommit = True

            with connection.cursor() as cursor:
                # Обновляем данные книги по ID
                cursor.execute(
                    "UPDATE books SET title = %s, year = %s WHERE id = %s;",
                    (title, year, book_id)
                )

        except Exception as ex:
            print("[INFO] Error while working with PostgreSQL:", ex)
        finally:
            if connection:
                connection.close()

        return redirect('/books')
    else:
        return render_template('update_book.html')

@app.route('/add_book', methods=['POST', 'GET'])
def add_book():
    if request.method == 'POST':
        author_name = request.form['author_name']
        title = request.form['title']
        year = request.form['year']

        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            
            connection.autocommit = True

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM authors WHERE name = %s;",
                    (author_name,)
                )
                author_id = cursor.fetchone()

                if author_id is None:
                    cursor.execute(
                        "INSERT INTO authors (name) VALUES (%s) RETURNING id;",
                        (author_name,)
                    )
                    author_id = cursor.fetchone()[0] 

                cursor.execute(
                    """
                    INSERT INTO books (title, year, author_id)
                    VALUES (%s, %s, %s);
                    """,
                    (title, year, author_id)
                )

        except Exception as ex:
            print("[INFO] Error while working with PostgreSQL:", ex)
        finally:
            if connection:
                connection.close()
        
        return redirect('/')
    else:
        return render_template('add_book.html')

@app.route('/total_books', methods=['GET'])
def total_books():
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )

        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM books;")
            total_books = cursor.fetchone()[0]

        return render_template('total_books.html', total_books=total_books)

    except Exception as ex:
        print("[INFO] Error while working with PostgreSQL:", ex)
    finally:
        if connection:
            connection.close()

@app.route('/search_books_by_author', methods=['GET', 'POST'])
def search_books_by_author():
    if request.method == 'POST':
        author_name = request.form['author_name']  # Получаем имя автора из формы
        
        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )

            connection.autocommit = True

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM books
                    JOIN authors ON books.author_id = authors.id
                    WHERE authors.name ILIKE %s;
                    """, ('%' + author_name + '%',)
                )
                book_count = cursor.fetchone()[0]

            return render_template('books_by_author_count.html', book_count=book_count, author_name=author_name)

        except Exception as ex:
            print("[INFO] Error while working with PostgreSQL:", ex)
        finally:
            if connection:
                connection.close()
    
    return render_template('search_books_by_author.html')

@app.route('/delete_book/<int:book_id>', methods=['GET'])
def delete_book(book_id):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )

        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM books WHERE id = %s;", 
                (book_id,)
            )

    except Exception as ex:
        print("[INFO] Error while working with PostgreSQL:", ex)
    finally:
        if connection:
            connection.close()

    return redirect('/books')

@app.route('/book_reader_pairs', methods=['GET'])
def book_reader_pairs():
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )

        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT b.title, r.name, lh.issue_date, lh.return_date
                FROM loan_history lh
                JOIN books b ON lh.book_id = b.id
                JOIN readers r ON lh.reader_id = r.id
                WHERE lh.status = 'issued';  -- We only want books that are currently issued
            """)
            book_reader_data = cursor.fetchall()

        return render_template('book_reader_pairs.html', book_reader_data=book_reader_data)

    except Exception as ex:
        print("[INFO] Error while working with PostgreSQL:", ex)
    finally:
        if connection:
            connection.close()


@app.route('/add_reader', methods=['POST', 'GET'])
def add_reader():
    if request.method == 'POST':
        reader_name = request.form['reader_name']
        reader_phone = request.form['reader_phone']
        book_id = request.form['book_id']

        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            connection.autocommit = True

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO readers (name, phone) VALUES (%s, %s) RETURNING id;",
                    (reader_name, reader_phone)
                )
                reader_id = cursor.fetchone()[0] 

                cursor.execute(
                    "UPDATE books SET available = FALSE WHERE id = %s;",
                    (book_id,)
                )

                cursor.execute(
                    """
                    INSERT INTO loan_history (book_id, reader_id, issue_date, status)
                    VALUES (%s, %s, CURRENT_DATE, 'issued');
                    """,
                    (book_id, reader_id)
                )

        except Exception as ex:
            print("[INFO] Error while working with PostgreSQL:", ex)
        finally:
            if connection:
                connection.close()

        return redirect('/books')
    else:
        return render_template('add_reader.html')
    

@app.route('/log', methods=['GET'])
def book_logs():
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM book_log ORDER BY change_date DESC;")
            logs = cursor.fetchall()

        return render_template('trigger_log.html', logs=logs)

    except Exception as ex:
        print("[INFO] Error while working with PostgreSQL:", ex)
    finally:
        if connection:
            connection.close()


if __name__ == '__main__':
    app.run(debug=True)
