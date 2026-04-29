import sqlite3


class CafeDB:
    def __init__(self, db_name="cafe.db"):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS dishes (
            dish_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            order_date TEXT,
            total_price INTEGER DEFAULT 0,
            status TEXT DEFAULT 'new',
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            dish_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (dish_id) REFERENCES dishes(dish_id)
        )
        """)

        self.conn.commit()


    def customer_exists(self, customer_id):
        self.cur.execute("SELECT 1 FROM customers WHERE customer_id = ?", (customer_id,))
        return self.cur.fetchone() is not None

    def dish_exists(self, dish_id):
        self.cur.execute("SELECT 1 FROM dishes WHERE dish_id = ?", (dish_id,))
        return self.cur.fetchone() is not None


    def add_customer(self, name, phone):
        try:
            with self.conn:
                self.cur.execute(
                    "INSERT INTO customers (name, phone) VALUES (?, ?)",
                    (name, phone)
                )
                print("Клиент добавлен!")
        except sqlite3.IntegrityError:
            print("Такой телефон уже существует")

    def get_customers(self):
        self.cur.execute("SELECT * FROM customers")
        return self.cur.fetchall()


    def add_dish(self, name, price):
        with self.conn:
            self.cur.execute(
                "INSERT INTO dishes (name, price) VALUES (?, ?)",
                (name, price)
            )
            print("Блюдо добавлено!")

    def get_dishes(self):
        self.cur.execute("SELECT * FROM dishes")
        return self.cur.fetchall()


    def add_order(self, customer_id):
        with self.conn:
            self.cur.execute(
                "INSERT INTO orders (customer_id, order_date) VALUES (?, DATETIME('now'))",
                (customer_id,)
            )
            return self.cur.lastrowid

    def add_order_item(self, order_id, dish_id, quantity):
        with self.conn:
            self.cur.execute(
                "INSERT INTO order_items (order_id, dish_id, quantity) VALUES (?, ?, ?)",
                (order_id, dish_id, quantity)
            )
        self.update_total(order_id)

    def update_total(self, order_id):
        self.cur.execute("""
        SELECT SUM(d.price * oi.quantity)
        FROM order_items oi
        JOIN dishes d ON d.dish_id = oi.dish_id
        WHERE oi.order_id = ?
        """, (order_id,))

        total = self.cur.fetchone()[0] or 0

        with self.conn:
            self.cur.execute(
                "UPDATE orders SET total_price = ? WHERE order_id = ?",
                (total, order_id)
            )

    def get_all_orders(self):
        self.cur.execute("""
        SELECT order_id, customer_id, order_date, total_price, status
        FROM orders
        """)
        return self.cur.fetchall()

    def get_order_details(self, order_id):
        self.cur.execute("""
        SELECT 
            o.order_id,
            c.name,
            d.name,
            oi.quantity,
            d.price,
            (d.price * oi.quantity),
            o.status
        FROM orders o
        JOIN customers c ON c.customer_id = o.customer_id
        JOIN order_items oi ON oi.order_id = o.order_id
        JOIN dishes d ON d.dish_id = oi.dish_id
        WHERE o.order_id = ?
        """, (order_id,))
        return self.cur.fetchall()

    def delete_order(self, order_id):
        with self.conn:
            self.cur.execute(
                "DELETE FROM orders WHERE order_id = ?",
                (order_id,)
            )
            print("Заказ удалён")

    def most_popular_dish(self):
        self.cur.execute("""
        SELECT d.name, SUM(oi.quantity) as total
        FROM order_items oi
        JOIN dishes d ON d.dish_id = oi.dish_id
        GROUP BY d.name
        ORDER BY total DESC
        LIMIT 1
        """)
        return self.cur.fetchone()

    def close(self):
        self.conn.close()


def safe_int_input(text):
    try:
        return int(input(text))
    except ValueError:
        print("Введите число!")
        return None


def print_list(title, data):
    print(f"\n--- {title} ---")
    for row in data:
        print(row)


def menu():
    print("\nМеню:")
    print("1. Добавить клиента")
    print("2. Показать клиентов")
    print("3. Добавить блюдо")
    print("4. Показать блюда")
    print("5. Создать заказ")
    print("6. Показать заказы")
    print("7. Детали заказа")
    print("8. Удалить заказ")
    print("9. Популярное блюдо")
    print("0. Выход")


if __name__ == "__main__":
    db = CafeDB()

    try:
        while True:
            menu()
            choice = input("Выбери действие: ")

            if choice == "1":
                name = input("Имя: ")
                phone = input("Телефон: ")
                db.add_customer(name, phone)

            elif choice == "2":
                print_list("Клиенты", db.get_customers())

            elif choice == "3":
                name = input("Название блюда: ")
                price = safe_int_input("Цена: ")
                if price is not None:
                    db.add_dish(name, price)

            elif choice == "4":
                print_list("Блюда", db.get_dishes())

            elif choice == "5":
                print_list("Клиенты", db.get_customers())
                customer_id = safe_int_input("ID клиента: ")

                if customer_id is None or not db.customer_exists(customer_id):
                    print("Клиент не найден")
                    continue

                order_id = db.add_order(customer_id)
                print(f"Создан заказ №{order_id}")

                while True:
                    print_list("Блюда", db.get_dishes())
                    dish_id = safe_int_input("ID блюда (0 - закончить): ")

                    if dish_id is None:
                        continue
                    if dish_id == 0:
                        break
                    if not db.dish_exists(dish_id):
                        print("Блюдо не найдено")
                        continue

                    qty = safe_int_input("Количество: ")
                    if qty is None or qty <= 0:
                        print("Некорректное количество")
                        continue

                    db.add_order_item(order_id, dish_id, qty)

            elif choice == "6":
                print_list("Заказы", db.get_all_orders())

            elif choice == "7":
                order_id = safe_int_input("ID заказа: ")
                if order_id is not None:
                    details = db.get_order_details(order_id)
                    if details:
                        print_list("Детали заказа", details)
                    else:
                        print("Заказ не найден")

            elif choice == "8":
                order_id = safe_int_input("ID заказа: ")
                if order_id is not None:
                    db.delete_order(order_id)

            elif choice == "9":
                result = db.most_popular_dish()
                if result:
                    print(f"Популярное блюдо: {result[0]} (продано {result[1]})")
                else:
                    print("Нет данных")

            elif choice == "0":
                print("Выход...")
                break

            else:
                print("Неверный выбор")

    finally:
        db.close()