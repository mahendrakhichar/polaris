from contextlib import contextmanager
import sqlite3

@contextmanager
def db_cursor():
    conn = sqlite3.connect('food_delivery.db')
    conn.row_factory = sqlite3.Row  # Set BEFORE creating the cursor!
    cursor = conn.cursor()

    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def init_db():
    """
    Initialize the SQLite database with required tables.
    """
    try:
        with sqlite3.connect('food_delivery.db') as conn:
            cursor = conn.cursor()

            # Optional: enable column access by name
            conn.row_factory = sqlite3.Row

            # Drop old tables if they exist
            cursor.execute('DROP TABLE IF EXISTS users')
            cursor.execute('DROP TABLE IF EXISTS riders')
            cursor.execute('DROP TABLE IF EXISTS restaurants')
            cursor.execute('DROP TABLE IF EXISTS menus')
            cursor.execute('DROP TABLE IF EXISTS orders')
            cursor.execute('DROP TABLE IF EXISTS notifications')

            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL
                )
            ''')

            # Create riders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS riders (
                    rider_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    is_available BOOLEAN DEFAULT TRUE
                )
            ''')

            # Create restaurants table with additional fields (food_type, prep_time)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS restaurants (
                    restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    food_type TEXT DEFAULT 'Mixed',
                    prep_time INTEGER DEFAULT 10,
                    opening_time TIME DEFAULT '09:00:00',
                    closing_time TIME DEFAULT '22:00:00',
                    serves_breakfast BOOLEAN DEFAULT 1,
                    serves_lunch BOOLEAN DEFAULT 1,
                    serves_dinner BOOLEAN DEFAULT 1
                )
            ''')

            # Create menus table (linked to restaurants)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS menus (
                    menu_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    restaurant_id INTEGER,
                    item_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id)
                )
            ''')

            # Create orders table (linked to users, restaurants, and riders)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    restaurant_id INTEGER,
                    rider_id INTEGER,
                    items TEXT NOT NULL,
                    total_price REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estimated_delivery_time INTEGER,
                    delivery_location TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id),
                    FOREIGN KEY (rider_id) REFERENCES riders (rider_id)
                )
            ''')

            # Create notifications table (linked to users and orders)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    order_id INTEGER,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (order_id) REFERENCES orders (order_id)
                )
            ''')

            # Create indexes for performance improvement
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders (user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_rider_id ON orders (rider_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_menus_restaurant_id ON menus (restaurant_id)')

            conn.commit()
            populate_sample_data()

            print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")


def populate_sample_data():
    try:
        with db_cursor() as cursor:
            restaurants = [
                ("Pizza Palace", "123 Main St", "Italian", 20, "00:00", "23:00", 0, 1, 1),
                ("Sushi Wave", "456 Oak Ave", "Japanese", 15, "11:00", "22:00", 0, 1, 1),
                ("Breakfast Club", "789 Pine Rd", "American", 15, "06:00", "15:00", 1, 1, 0),
                ("24/7 Diner", "321 Elm St", "American", 15, "00:00", "23:59", 1, 1, 1),
                ("Lunch Box", "654 Maple Dr", "Mixed", 12, "10:00", "16:00", 0, 1, 0),
                ("Dinner Palace", "987 Cedar Ln", "Fine Dining", 30, "16:00", "23:00", 0, 0, 1),
                ("All Day Cafe", "147 Olive St", "Cafe", 10, "07:00", "20:00", 1, 1, 1),
                ("Evening Bistro", "258 Cherry Ave", "French", 25, "16:00", "23:00", 0, 0, 1),
                ("Morning Glory", "369 Bamboo Rd", "Breakfast", 15, "06:00", "14:00", 1, 1, 0),
                ("Late Night Eats", "741 Vine St", "Mixed", 20, "18:00", "03:00", 0, 0, 1)
            ]
            cursor.executemany("""
                INSERT INTO restaurants (
                    name, location, food_type, prep_time,
                    opening_time, closing_time,
                    serves_breakfast, serves_lunch, serves_dinner
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, restaurants)
            # Sample Menu Items for each restaurant
            menus = [
                # 1. Pizza Palace
                (1, "Margherita Pizza", 12.99),
                (1, "Pepperoni Pizza", 14.99),
                (1, "Garlic Bread", 4.99),
                (1, "Caesar Salad", 8.99),
                # 2. Sushi Wave
                (2, "California Roll", 8.99),
                (2, "Salmon Nigiri", 12.99),
                (2, "Miso Soup", 3.99),
                (2, "Tempura Udon", 14.99),
                # 3. Taco Fiesta
                (3, "Street Tacos", 9.99),
                (3, "Burrito Supreme", 11.99),
                (3, "Guacamole & Chips", 6.99),
                (3, "Mexican Rice", 3.99),
                # 4. Dragon Wok
                (4, "Kung Pao Chicken", 13.99),
                (4, "Fried Rice", 10.99),
                (4, "Spring Rolls", 5.99),
                (4, "Mapo Tofu", 12.99),
                # 5. Burger Barn
                (5, "Classic Burger", 10.99),
                (5, "Cheese Fries", 5.99),
                (5, "Milkshake", 4.99),
                (5, "Onion Rings", 4.99),
                # 6. Curry House
                (6, "Butter Chicken", 14.99),
                (6, "Naan Bread", 2.99),
                (6, "Vegetable Biryani", 12.99),
                (6, "Samosas", 5.99),
                # 7. Mediterranean Delight
                (7, "Hummus Plate", 7.99),
                (7, "Falafel Wrap", 9.99),
                (7, "Greek Salad", 8.99),
                (7, "Shawarma Plate", 13.99),
                # 8. Seoul Kitchen
                (8, "Bibimbap", 13.99),
                (8, "Kimchi Jjigae", 11.99),
                (8, "Korean BBQ", 15.99),
                (8, "Japchae", 10.99),
                # 9. Thai Spice
                (9, "Pad Thai", 12.99),
                (9, "Green Curry", 13.99),
                (9, "Tom Yum Soup", 6.99),
                (9, "Mango Sticky Rice", 5.99),
                # 10. Pasta Paradise
                (10, "Spaghetti Carbonara", 13.99),
                (10, "Fettuccine Alfredo", 12.99),
                (10, "Garlic Knots", 4.99),
                (10, "Tiramisu", 6.99)
            ]
            cursor.executemany("INSERT INTO menus (restaurant_id, item_name, price) VALUES (?, ?, ?)", menus)

            # Sample Riders
            riders = [
                ("John Rider", "Downtown Area", True),
                ("Sarah Delivery", "Uptown Area", True),
                ("Mike Speed", "Westside", True),
                ("Lisa Quick", "Eastside", True),
                ("Tom Swift", "Central Area", True)
            ]
            cursor.executemany("INSERT INTO riders (name, location, is_available) VALUES (?, ?, ?)", riders)

            # Sample Users
            users = [
                ("Alice Johnson", "123 Park Ave"),
                ("Bob Smith", "456 Lake St"),
                ("Carol Wilson", "789 River Rd"),
                ("David Brown", "321 Hill Dr"),
                ("Eva Davis", "654 Forest Ln"),
                ("Frank Miller", "987 Beach Rd"),
                ("Grace Taylor", "147 Mountain Ave"),
                ("Henry Clark", "258 Valley St"),
                ("Iris White", "369 Ocean Dr"),
                ("Jack Green", "741 Desert Rd")
            ]


            cursor.executemany("INSERT INTO users (name, location) VALUES (?, ?)", users)

            sample_orders = [
                (1, 1, None, '[{"name":"Margherita Pizza","price":12.99}]', 12.99, 'pending', '123 Park Ave'),
                (2, 2, None, '[{"name":"California Roll","price":8.99}]', 8.99, 'pending', '456 Lake St'),
                (3, 3, None, '[{"name":"Butter Chicken","price":14.99}]', 14.99, 'pending', '789 River Rd')
            ]

            cursor.executemany("""
                INSERT INTO orders (
                    user_id, restaurant_id, rider_id, items,
                    total_price, status, delivery_location
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, sample_orders)
            print("Sample data populated successfully.")
    except sqlite3.Error as e:
        print(f"Error populating sample data: {e}")
