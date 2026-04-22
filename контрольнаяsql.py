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



    def add_customer(self, name, phone):
        try:
            with self.conn:
                self.cur.execute(
                    "INSERT INTO customers (name, phone) VALUES (?, ?)",
                    (name, phone)
                )
                return self.cur.lastrowid
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
            return self.cur.lastrowid

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

    def update_status(self, order_id, status):
        with self.conn:
            self.cur.execute(
                "UPDATE orders SET status = ? WHERE order_id = ?",
                (status, order_id)
            )

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

    def get_all_orders(self):
        self.cur.execute("""
        SELECT order_id, customer_id, order_date, total_price, status
        FROM orders
        """)
        return self.cur.fetchall()

    def delete_order(self, order_id):
        with self.conn:
            self.cur.execute(
                "DELETE FROM orders WHERE order_id = ?",
                (order_id,)
            )

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

    while True:
        menu()
        choice = input("Выбери действие: ")

        if choice == "1":
            name = input("Имя: ")
            phone = input("Телефон: ")
            db.add_customer(name, phone)

        elif choice == "2":
            print(db.get_customers())

        elif choice == "3":
            name = input("Название блюда: ")
            price = int(input("Цена: "))
            db.add_dish(name, price)

        elif choice == "4":
            print(db.get_dishes())

        elif choice == "5":
            customer_id = int(input("ID клиента: "))
            order_id = db.add_order(customer_id)

            while True:
                dish_id = int(input("ID блюда (0 - закончить): "))
                if dish_id == 0:
                    break
                qty = int(input("Количество: "))
                db.add_order_item(order_id, dish_id, qty)

        elif choice == "6":
            print(db.get_all_orders())

        elif choice == "7":
            order_id = int(input("ID заказа: "))
            print(db.get_order_details(order_id))

        elif choice == "8":
            order_id = int(input("ID заказа: "))
            db.delete_order(order_id)

        elif choice == "9":
            print(db.most_popular_dish())

        elif choice == "0":
            db.close()
            break

        else:
            print("Неверный выбор")