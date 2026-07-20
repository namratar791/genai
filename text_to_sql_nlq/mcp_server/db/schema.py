"""
db/schema.py
Pure DDL — just table creation. No data here (see seed_data.py).
12 light tables covering a simple e-commerce domain.
"""

TABLES = {
    "customers": """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT UNIQUE,
            city        TEXT,
            country     TEXT,
            signup_date TEXT
        );""",

    "departments": """
        CREATE TABLE IF NOT EXISTS departments (
            department_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT NOT NULL
        );""",

    "employees": """
        CREATE TABLE IF NOT EXISTS employees (
            employee_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT UNIQUE,
            department_id INTEGER,
            job_title     TEXT,
            hire_date     TEXT,
            FOREIGN KEY (department_id) REFERENCES departments(department_id)
        );""",

    "suppliers": """
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            contact_email TEXT,
            country       TEXT
        );""",

    "categories": """
        CREATE TABLE IF NOT EXISTS categories (
            category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL
        );""",

    "products": """
        CREATE TABLE IF NOT EXISTS products (
            product_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name   TEXT NOT NULL,
            category_id    INTEGER,
            supplier_id    INTEGER,
            unit_price     REAL,
            stock_quantity INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories(category_id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        );""",

    "warehouses": """
        CREATE TABLE IF NOT EXISTS warehouses (
            warehouse_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_name TEXT NOT NULL,
            city           TEXT,
            country        TEXT
        );""",

    "inventory": """
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_id       INTEGER,
            product_id         INTEGER,
            quantity_available INTEGER,
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );""",

    "orders": """
        CREATE TABLE IF NOT EXISTS orders (
            order_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            employee_id INTEGER,
            order_date  TEXT,
            status      TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        );""",

    "order_items": """
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id      INTEGER,
            product_id    INTEGER,
            quantity      INTEGER,
            unit_price    REAL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );""",

    "payments": """
        CREATE TABLE IF NOT EXISTS payments (
            payment_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id       INTEGER,
            amount         REAL,
            payment_method TEXT,
            payment_status TEXT,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );""",

    "reviews": """
        CREATE TABLE IF NOT EXISTS reviews (
            review_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id  INTEGER,
            customer_id INTEGER,
            rating      INTEGER,
            review_date TEXT,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );""",

    # ---- wide / detail tables (1:1 extensions of existing entities) ----

    "order_details": """
        CREATE TABLE IF NOT EXISTS order_details (
            order_detail_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id              INTEGER UNIQUE,
            shipping_method       TEXT,
            shipping_cost         REAL,
            tax_amount            REAL,
            discount_amount       REAL,
            total_amount          REAL,
            currency              TEXT,
            priority               TEXT,     -- 'Standard','Express','Same Day'
            gift_wrap             INTEGER,  -- 0/1
            delivery_instructions TEXT,
            tracking_number       TEXT,
            estimated_delivery_date TEXT,
            actual_delivery_date  TEXT,
            return_status         TEXT,     -- 'None','Requested','Returned','Refunded'
            order_notes           TEXT,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );""",

    "product_details": """
        CREATE TABLE IF NOT EXISTS product_details (
            product_detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id        INTEGER UNIQUE,
            brand             TEXT,
            model_number      TEXT,
            sku               TEXT UNIQUE,
            barcode           TEXT,
            color             TEXT,
            material          TEXT,
            weight_kg         REAL,
            dimensions_cm     TEXT,     -- e.g. '20x10x5'
            warranty_months   INTEGER,
            manufacture_date  TEXT,
            expiry_date       TEXT,
            is_active         INTEGER,  -- 0/1
            long_description  TEXT,
            tags              TEXT,     -- comma-separated
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );""",

    "transaction_history": """
        CREATE TABLE IF NOT EXISTS transaction_history (
            transaction_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id           INTEGER,
            customer_id        INTEGER,
            payment_id         INTEGER,
            transaction_type   TEXT,     -- 'Purchase','Refund','Chargeback','Adjustment'
            transaction_date   TEXT,
            amount             REAL,
            currency           TEXT,
            payment_gateway    TEXT,     -- 'Stripe','PayPal','Bank','Internal'
            gateway_reference  TEXT,
            status             TEXT,     -- 'Success','Failed','Pending','Reversed'
            notes              TEXT,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (payment_id) REFERENCES payments(payment_id)
        );""",

    "person_details": """
        CREATE TABLE IF NOT EXISTS person_details (
            person_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            person_type    TEXT,     -- 'Customer','Employee','Supplier Contact'
            linked_id      INTEGER,  -- id in the corresponding customers/employees/suppliers table
            first_name     TEXT,
            last_name      TEXT,
            date_of_birth  TEXT,
            gender         TEXT,
            phone          TEXT,
            email          TEXT,
            address_line1  TEXT,
            address_line2  TEXT,
            city           TEXT,
            state          TEXT,
            country        TEXT,
            postal_code    TEXT,
            occupation     TEXT,
            company_name   TEXT,
            notes          TEXT,
            created_at     TEXT
        );""",
    "table_descriptions": """
        CREATE TABLE IF NOT EXISTS table_descriptions (
            table_name TEXT PRIMARY KEY,
            description TEXT,
            business_terms TEXT
        );"""

}


def create_all_tables(conn):
    """Create all tables on the given sqlite3 connection."""
    cur = conn.cursor()
    for ddl in TABLES.values():
        cur.execute(ddl)
    conn.commit()


if __name__ == "__main__":
    import sqlite3
    conn = sqlite3.connect(":memory:")
    create_all_tables(conn)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables created:", [r[0] for r in cur.fetchall()])