"""
db/seed_data.py
Inserts light sample/random data into the 12 tables defined in schema.py.
Kept intentionally small (a few dozen rows per table) so the demo stays fast.
"""

import random
from datetime import datetime, timedelta

random.seed(42)

NAMES = ["James Smith", "Maria Garcia", "Wei Chen", "Priya Patel", "Ahmed Khan",
         "Sofia Rossi", "Liam Muller", "Emma Kim", "Noah Silva", "Olivia Brown",
         "Carlos Nguyen", "Aisha Hassan", "Yuki Sato", "Ivan Petrov", "Grace Lee"]
CITIES = [("New York", "USA"), ("Los Angeles", "USA"), ("Toronto", "Canada"),
          ("London", "UK"), ("Berlin", "Germany"), ("Mumbai", "India"),
          ("Tokyo", "Japan"), ("Sydney", "Australia")]
DEPARTMENTS = ["Sales", "Marketing", "Engineering", "Support", "Finance"]
JOB_TITLES = ["Sales Rep", "Support Agent", "Engineer", "Analyst", "Manager"]
SUPPLIERS = ["Global Textiles", "NorthPeak Electronics", "GreenLeaf Foods", "Alpine Hardware"]
CATEGORIES = ["Electronics", "Apparel", "Home & Kitchen", "Sports", "Groceries"]
PRODUCT_NAMES = ["Wireless Earbuds", "Bluetooth Speaker", "Cotton T-Shirt", "Blender",
                  "Yoga Mat", "Running Shoes", "Coffee Maker", "Green Tea Pack",
                  "Desk Organizer", "Camping Tent"]
WAREHOUSES = [("Central Warehouse", "New York", "USA"), ("EU Hub", "Berlin", "Germany")]
ORDER_STATUS = ["Pending", "Shipped", "Delivered", "Cancelled"]
PAYMENT_METHODS = ["Credit Card", "PayPal", "Bank Transfer"]
PAYMENT_STATUS = ["Success", "Failed", "Refunded"]

SHIPPING_METHODS = ["Standard", "Express", "Same Day", "Economy"]
PRIORITIES = ["Standard", "Express", "Same Day"]
RETURN_STATUSES = ["None", "None", "None", "Requested", "Returned", "Refunded"]
CURRENCIES = ["USD", "EUR", "GBP"]
BRANDS = ["Nimbus", "Vertex", "Aurora", "Pioneer", "Zenith"]
COLORS = ["Black", "White", "Blue", "Red", "Silver"]
MATERIALS = ["Plastic", "Aluminum", "Cotton", "Stainless Steel", "Leather"]
TXN_TYPES = ["Purchase", "Refund", "Chargeback", "Adjustment"]
GATEWAYS = ["Stripe", "PayPal", "Bank", "Internal"]
TXN_STATUS = ["Success", "Failed", "Pending", "Reversed"]
GENDERS = ["Male", "Female", "Other"]
OCCUPATIONS = ["Engineer", "Teacher", "Designer", "Consultant", "Manager", "Analyst"]
TABLE_DESCRIPTIONS = [
    ("customers", "Stores customer profile and registration information including name, email and location.", "customer,buyer,user,client"),
    ("departments", "Stores company departments such as Sales, Marketing and Engineering.", "department,team,business unit"),
    ("employees", "Stores employee information including department, role and hiring details.", "employee,staff,worker,associate"),
    ("suppliers", "Stores supplier and vendor information for products.", "supplier,vendor,manufacturer,seller"),
    ("categories", "Stores product categories and classifications.", "category,product type,classification"),
    ("products", "Stores product catalog information including pricing and stock quantity.", "product,item,goods,catalog,inventory"),
    ("warehouses", "Stores warehouse locations used for inventory management.", "warehouse,storage center,distribution center"),
    ("inventory", "Tracks available inventory quantities of products in warehouses.", "inventory,stock,availability,quantity"),
    ("orders", "Stores customer orders and order status information.", "order,purchase,sale,transaction"),
    ("order_items", "Stores individual products purchased within each order.", "line item,ordered products,purchased items"),
    ("payments", "Stores payment details and payment status for orders.", "payment,billing,revenue,transaction"),
    ("reviews", "Stores customer ratings and reviews for products.", "review,rating,feedback,customer opinion"),
    ("order_details", "Stores shipping, delivery, tax, discount and return information for orders.", "shipping,delivery,tracking,returns,fulfillment"),
    ("product_details", "Stores detailed product specifications including brand, SKU, dimensions and warranty information.", "product specification,sku,brand,attributes,product metadata"),
    ("transaction_history", "Stores financial transaction history including purchases, refunds and chargebacks.", "transaction,payment history,refund,chargeback,financial activity"),
    ("person_details", "Stores detailed personal information for customers and employees including address and demographic information.", "person,profile,contact information,personal details")
]

def rand_date(start_year=2023, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return (start + timedelta(days=random.randint(0, (end - start).days))).strftime("%Y-%m-%d")


def seed_all(conn):
    cur = conn.cursor()

    # customers (15)
    for i in range(15):
        name = random.choice(NAMES)
        city, country = random.choice(CITIES)
        cur.execute(
            "INSERT INTO customers (name, email, city, country, signup_date) VALUES (?,?,?,?,?)",
            (name, f"{name.split()[0].lower()}{i}@customermail.com", city, country, rand_date(2022, 2024)),
        )

    # departments (5)
    for d in DEPARTMENTS:
        cur.execute("INSERT INTO departments (department_name) VALUES (?)", (d,))

    # employees (8)
    for i in range(8):
        name = random.choice(NAMES)
        cur.execute(
            "INSERT INTO employees (name, email, department_id, job_title, hire_date) VALUES (?,?,?,?,?)",
            (name, f"{name.split()[0].lower()}{i}@company.com", random.randint(1, 5),
             random.choice(JOB_TITLES), rand_date(2020, 2023)),
        )

    # suppliers (4)
    for s in SUPPLIERS:
        cur.execute(
            "INSERT INTO suppliers (name, contact_email, country) VALUES (?,?,?)",
            (s, f"contact@{s.lower().replace(' ', '')}.com", random.choice(["USA", "Germany", "China"])),
        )

    # categories (5)
    for c in CATEGORIES:
        cur.execute("INSERT INTO categories (category_name) VALUES (?)", (c,))

    # products (10)
    for i, p in enumerate(PRODUCT_NAMES):
        cur.execute(
            "INSERT INTO products (product_name, category_id, supplier_id, unit_price, stock_quantity) VALUES (?,?,?,?,?)",
            (p, random.randint(1, 5), random.randint(1, 4), round(random.uniform(5, 300), 2), random.randint(0, 200)),
        )

    # warehouses (2)
    for w, city, country in WAREHOUSES:
        cur.execute("INSERT INTO warehouses (warehouse_name, city, country) VALUES (?,?,?)", (w, city, country))

    # inventory (~15)
    for wid in range(1, 3):
        for pid in range(1, 11):
            if random.random() < 0.7:
                cur.execute(
                    "INSERT INTO inventory (warehouse_id, product_id, quantity_available) VALUES (?,?,?)",
                    (wid, pid, random.randint(0, 300)),
                )

    # orders (25)
    for i in range(25):
        cur.execute(
            "INSERT INTO orders (customer_id, employee_id, order_date, status) VALUES (?,?,?,?)",
            (random.randint(1, 15), random.randint(1, 8), rand_date(), random.choice(ORDER_STATUS)),
        )

    # order_items (~50)
    for oid in range(1, 26):
        for _ in range(random.randint(1, 3)):
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?,?,?,?)",
                (oid, random.randint(1, 10), random.randint(1, 5), round(random.uniform(5, 300), 2)),
            )

    # payments (25)
    for oid in range(1, 26):
        cur.execute(
            "INSERT INTO payments (order_id, amount, payment_method, payment_status) VALUES (?,?,?,?)",
            (oid, round(random.uniform(20, 800), 2), random.choice(PAYMENT_METHODS), random.choice(PAYMENT_STATUS)),
        )

    # reviews (~20)
    for _ in range(20):
        cur.execute(
            "INSERT INTO reviews (product_id, customer_id, rating, review_date) VALUES (?,?,?,?)",
            (random.randint(1, 10), random.randint(1, 15), random.randint(1, 5), rand_date()),
        )

    # order_details (one row per order, 25) — wide table with shipping/billing/return info
    for oid in range(1, 26):
        shipping_cost = round(random.uniform(0, 25), 2)
        tax_amount = round(random.uniform(2, 40), 2)
        discount_amount = round(random.choice([0, 0, 0, 5, 10, 15]), 2)
        # rough total: a few line items worth, just for demo realism (not recomputed from order_items)
        total_amount = round(random.uniform(30, 900) + shipping_cost + tax_amount - discount_amount, 2)
        order_date = rand_date()
        cur.execute(
            """INSERT INTO order_details
               (order_id, shipping_method, shipping_cost, tax_amount, discount_amount, total_amount,
                currency, priority, gift_wrap, delivery_instructions, tracking_number,
                estimated_delivery_date, actual_delivery_date, return_status, order_notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (oid, random.choice(SHIPPING_METHODS), shipping_cost, tax_amount, discount_amount, total_amount,
             random.choice(CURRENCIES), random.choice(PRIORITIES), random.choice([0, 1]),
             random.choice(["Leave at front door", "Signature required", "Call on arrival", None]),
             f"TRK{random.randint(100000,999999)}", rand_date(), rand_date(),
             random.choice(RETURN_STATUSES), random.choice(["", "Gift order", "Repeat customer", ""])),
        )

    # product_details (one row per product, 10) — wide table with specs
    for pid in range(1, 11):
        brand = random.choice(BRANDS)
        cur.execute(
            """INSERT INTO product_details
               (product_id, brand, model_number, sku, barcode, color, material, weight_kg,
                dimensions_cm, warranty_months, manufacture_date, expiry_date, is_active,
                long_description, tags)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (pid, brand, f"MDL-{random.randint(1000,9999)}", f"SKU-{pid:04d}-{brand[:3].upper()}",
             f"{random.randint(100000000000, 999999999999)}", random.choice(COLORS), random.choice(MATERIALS),
             round(random.uniform(0.1, 15), 2), f"{random.randint(5,50)}x{random.randint(5,50)}x{random.randint(2,30)}",
             random.choice([6, 12, 24, 36]), rand_date(2022, 2023), rand_date(2025, 2027),
             random.choice([1, 1, 1, 0]), f"Detailed spec sheet and long-form description for product {pid}.",
             ",".join(random.sample(["bestseller", "new", "eco-friendly", "sale", "limited"], k=2))),
        )

    # transaction_history (~30) — broader log than payments, includes refunds/chargebacks
    for i in range(30):
        oid = random.randint(1, 25)
        cur.execute(
            """INSERT INTO transaction_history
               (order_id, customer_id, payment_id, transaction_type, transaction_date, amount,
                currency, payment_gateway, gateway_reference, status, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (oid, random.randint(1, 15), oid, random.choice(TXN_TYPES), rand_date(),
             round(random.uniform(10, 900), 2), random.choice(CURRENCIES), random.choice(GATEWAYS),
             f"GW-{random.randint(100000,999999)}", random.choice(TXN_STATUS),
             random.choice(["", "Customer requested", "Auto-retry succeeded", ""])),
        )

    # person_details (~20) — generic wide people table, linked back to customers/employees
    for i in range(15):
        fn, ln = random.choice(NAMES).split()
        city, country = random.choice(CITIES)
        cur.execute(
            """INSERT INTO person_details
               (person_type, linked_id, first_name, last_name, date_of_birth, gender, phone, email,
                address_line1, address_line2, city, state, country, postal_code, occupation,
                company_name, notes, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ("Customer", i + 1, fn, ln, rand_date(1970, 2000), random.choice(GENDERS),
             f"+1-555-{random.randint(1000,9999)}", f"{fn.lower()}.{ln.lower()}@personmail.com",
             f"{random.randint(1,999)} Main St", random.choice(["Apt 2B", "Suite 100", None]),
             city, "", country, f"{random.randint(10000,99999)}", random.choice(OCCUPATIONS),
             None, "", rand_date(2022, 2024)),
        )
    for i in range(8):
        fn, ln = random.choice(NAMES).split()
        city, country = random.choice(CITIES)
        cur.execute(
            """INSERT INTO person_details
               (person_type, linked_id, first_name, last_name, date_of_birth, gender, phone, email,
                address_line1, address_line2, city, state, country, postal_code, occupation,
                company_name, notes, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ("Employee", i + 1, fn, ln, rand_date(1975, 2002), random.choice(GENDERS),
             f"+1-555-{random.randint(1000,9999)}", f"{fn.lower()}.{ln.lower()}@company.com",
             f"{random.randint(1,999)} Corporate Ave", None, city, "", country,
             f"{random.randint(10000,99999)}", random.choice(OCCUPATIONS), "Our Company",
             "", rand_date(2020, 2023)),
        )

    conn.commit()

def seed_table_descriptions(conn):
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO table_descriptions
        (table_name,description,business_terms)
        VALUES
        (?, ?, ?)
        """,
        TABLE_DESCRIPTIONS
    )
    conn.commit()


if __name__ == "__main__":
    import sqlite3
    from schema import create_all_tables

    conn = sqlite3.connect(":memory:")
    create_all_tables(conn)
    seed_all(conn)
    seed_table_descriptions(conn)
    cur = conn.cursor()
    for t in ["customers", "departments", "employees", "suppliers", "categories",
              "products", "warehouses", "inventory", "orders", "order_items",
              "payments", "reviews", "order_details", "product_details",
              "transaction_history", "person_details"]:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"{t:15s} -> {cur.fetchone()[0]} rows")