import sqlite3
import random
from datetime import datetime, timedelta

def create_mock_db():
    conn = sqlite3.connect('retail.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        join_date TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL,
        stock_quantity INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        sale_date TEXT,
        total_amount REAL,
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        customer_id INTEGER,
        rating INTEGER,
        comment TEXT,
        review_date TEXT,
        FOREIGN KEY (product_id) REFERENCES products (id),
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    ''')

    # Clear existing data
    cursor.execute('DELETE FROM reviews')
    cursor.execute('DELETE FROM sales')
    cursor.execute('DELETE FROM products')
    cursor.execute('DELETE FROM customers')

    # Seed Customers
    customers = [
        (1, 'Alice Johnson', 'alice@example.com', '2023-01-15'),
        (2, 'Bob Smith', 'bob@example.com', '2023-02-20'),
        (3, 'Charlie Brown', 'charlie@example.com', '2023-03-10'),
        (4, 'Diana Prince', 'diana@example.com', '2023-04-05'),
        (5, 'Evan Wright', 'evan@example.com', '2023-05-12')
    ]
    cursor.executemany('INSERT INTO customers VALUES (?,?,?,?)', customers)

    # Seed Products
    products = [
        (1, 'Laptop Pro', 'Electronics', 1200.00, 50),
        (2, 'Smartphone X', 'Electronics', 800.00, 100),
        (3, 'Running Shoes', 'Apparel', 120.00, 200),
        (4, 'Coffee Maker', 'Home', 80.00, 75),
        (5, 'Bluetooth Headphones', 'Electronics', 150.00, 150)
    ]
    cursor.executemany('INSERT INTO products VALUES (?,?,?,?,?)', products)

    # Seed Sales
    sales = []
    for i in range(1, 21):
        customer_id = random.randint(1, 5)
        product_id = random.randint(1, 5)
        quantity = random.randint(1, 3)
        price = next(p[3] for p in products if p[0] == product_id)
        total_amount = price * quantity
        sale_date = (datetime.now() - timedelta(days=random.randint(0, 60))).strftime('%Y-%m-%d')
        sales.append((i, customer_id, product_id, quantity, sale_date, total_amount))
    
    cursor.executemany('INSERT INTO sales VALUES (?,?,?,?,?,?)', sales)

    # Seed Reviews
    reviews = [
        (1, 1, 1, 5, 'Great laptop, very fast!', '2023-06-01'),
        (2, 2, 2, 4, 'Good phone but battery life could be better.', '2023-06-05'),
        (3, 3, 3, 5, 'Very comfortable shoes.', '2023-06-10'),
        (4, 4, 4, 3, 'Makes okay coffee, a bit noisy.', '2023-06-15'),
        (5, 5, 5, 4, 'Sound quality is amazing.', '2023-06-20')
    ]
    cursor.executemany('INSERT INTO reviews VALUES (?,?,?,?,?,?)', reviews)

    conn.commit()
    conn.close()
    print("Database 'retail.db' created and populated successfully.")

if __name__ == "__main__":
    create_mock_db()
