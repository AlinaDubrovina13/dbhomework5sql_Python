import psycopg2


def delete_db(conn):
    cur.execute("""
        DROP TABLE client, phone_book
        CASCADE;
        """)


def create_db(conn):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS client(
            client_id SERIAL PRIMARY KEY,
            first_name VARCHAR(40) NOT NULL,
            last_name VARCHAR(40) NOT NULL,
            email TEXT UNIQUE
        );
        """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phone_book(
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES client(client_id),
            phone_number VARCHAR(10) UNIQUE
        );
        """)


def add_client(conn, first_name, last_name, email):
    cur.execute("""
        INSERT INTO client(first_name, last_name, email)
        VALUES(%s, %s, %s) RETURNING client_id;
        """, (first_name, last_name, email))
    conn.commit()
    print(f'Новый клиент добавлен: {cur.fetchone()[0]}')


def add_phone_number(conn, client_id, phone_number):
    cur.execute("""
        INSERT INTO phone_book(client_id, phone_number)
        VALUES(%s, %s);
        """, (client_id, phone_number))
    conn.commit()
    cur.execute("""
        SELECT first_name, last_name
        FROM client cl
        JOIN phone_book pb
        ON cl.client_id = pb.client_id
        WHERE cl.client_id=%s;
        """, (client_id,))
    print(f'Номер телефона клиента {cur.fetchone()[1]} добавлен.')


def change_client(conn, client_id, first_name=None, last_name=None, email=None):
    cur.execute("""
        SELECT *
        FROM client
        WHERE client_id=%s;
        """, (client_id,))
    client = cur.fetchone()
    if first_name is None:
        first_name = client[1]
    if last_name is None:
        last_name = client[2]
    if email is None:
        email = client[3]
    cur.execute("""
        UPDATE client SET first_name=%s, last_name=%s, email=%s
        WHERE client_id=%s;
        """, (first_name, last_name, email, client_id))
    print(f'Данные клиента {last_name} обновлены.')


def delete_phone(conn, client_id, phone_number):
    cur.execute("""
        SELECT EXISTS(
        SELECT *
        FROM client
        WHERE client_id=%s
        );
        """, (client_id,))
    client = cur.fetchone()[0]
    if client is False:
        print('Такого клиента нет.')
    else:
        cur.execute("""
            DELETE
            FROM phone_book
            WHERE phone_number=%s;
            """, (phone_number,))
        print(f'Телефон {phone_number} удален.')


def delete_client(conn, client_id):
    cur.execute("""
        DELETE
        FROM phone_book
        WHERE client_id=%s;
        """, (client_id,))
    cur.execute("""
        DELETE
        FROM client
        WHERE client_id=%s;
        """, (client_id,))
    conn.commit()
    print('Все данные о клиенте удалены.')


def find_client(conn, first_name=None, last_name=None, email=None, phone_number=None):
    if first_name is None:
        first_name = '%'
    else:
        first_name = '%' + first_name + '%'
    if last_name is None:
        last_name = '%'
    else:
        last_name = '%' + last_name + '%'
    if email is None:
        email = '%'
    else:
        email = '%' + email + '%'
    if phone_number is None:
        cur.execute("""
            SELECT client_id, first_name, last_name, email
            FROM client
            WHERE first_name LIKE %s
            AND last_name LIKE %s
            AND email LIKE %s;
            """, (first_name, last_name, email))
    else:
        cur.execute("""
            SELECT cl.client_id, cl.first_name, cl.last_name, cl.email
            FROM client cl
            JOIN phone_book pb
            ON cl.client_id = pb.client_id
            WHERE cl.first_name LIKE %s
            AND cl.last_name LIKE %s
            AND cl.email LIKE %s
            AND pb.phone_number LIKE %s;
            """, (first_name, last_name, email, phone_number))
    print(cur.fetchall())


if __name__ == '__main__':
    with psycopg2.connect(database="netology_db", user="postgres",
                          password="postgres") as conn:
        with conn.cursor() as cur:
            delete_db(conn)
            create_db(conn)
            add_client(conn, 'Kirill', 'Ivanov', 'Kirya777@mail.ru')
            add_client(conn, 'Denis', 'Fedorov', 'car870212@mail.ru')
            add_client(conn, 'Andrey', 'Andreev', 'Dron@yandex.ru')
            add_phone_number(conn, 1, '7851247130')
            add_phone_number(conn, 2, '3367741159')
            add_phone_number(conn, 2, '7779998547')
            change_client(conn, 1, 'Kirill', 'Kirillov')
            change_client(conn, 2, None, None, 'Fedora117@mail.ru')
            delete_phone(conn, 1, '7851247130')
            delete_client(conn, 2)
            find_client(conn, 'Denis')
            find_client(conn, None, 'Andreev')
            find_client(conn, None, None, 'Dron@yandex.ru')
            find_client(conn, None, None, None, '3367741159')

conn.close()