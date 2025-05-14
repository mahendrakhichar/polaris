import sqlite3
from datetime import datetime

class Order:
    def __init__(self, order_id, user_id, restaurant_id, rider_id, items, total_price, status, order_time):
        """
        Initialize an Order object.

        Args:
            order_id (int): Unique identifier for the order
            user_id (int): ID of the user who placed the order
            restaurant_id (int): ID of the restaurant
            rider_id (int): ID of the assigned rider (or None)
            items (str): Comma-separated list of item names
            total_price (float): Total price of the order
            status (str): Order status (e.g., 'placed', 'assigned')
            order_time (str): Timestamp of when the order was placed
        """
        self.order_id = order_id
        self.user_id = user_id
        self.restaurant_id = restaurant_id
        self.rider_id = rider_id
        self.items = items
        self.total_price = total_price
        self.status = status
        self.order_time = order_time

    @staticmethod
    def place_order(user_id, restaurant_id, items, total_price):
        """
        Create a new order in the database.

        Args:
            user_id (int): ID of the user
            restaurant_id (int): ID of the restaurant
            items (str): Comma-separated list of item names
            total_price (float): Total price of the order

        Returns:
            Order: Newly created Order object

        Raises:
            ValueError: If inputs are invalid
            sqlite3.Error: If database operation fails
        """
        if not user_id or not restaurant_id or not items or total_price <= 0:
            raise ValueError("Invalid order details")

        try:
            now = datetime.now()
            with sqlite3.connect('food_delivery.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO orders (user_id, restaurant_id, items, total_price, status, order_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, restaurant_id, items, total_price, 'placed', now)
                )
                conn.commit()
                order_id = cursor.lastrowid
                return Order(order_id, user_id, restaurant_id, None, items, total_price, 'placed', now)
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

    @staticmethod
    def get_user_orders(user_id):
        """
        Retrieve all orders for a user.

        Args:
            user_id (int): User's ID

        Returns:
            list: List of Order objects
        """
        try:
            with sqlite3.connect('food_delivery.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT o.order_id, o.user_id, o.restaurant_id, o.rider_id, o.items,
                           o.total_price, o.status, o.order_time
                    FROM orders o
                    WHERE o.user_id = ?
                    """,
                    (user_id,)
                )
                results = cursor.fetchall()
                return [Order(*result) for result in results]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

    @staticmethod
    def get_rider_orders(rider_id):
        """
        Retrieve all orders assigned to a rider.

        Args:
            rider_id (int): Rider's ID

        Returns:
            list: List of Order objects
        """
        try:
            with sqlite3.connect('food_delivery.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT o.order_id, o.user_id, o.restaurant_id, o.rider_id, o.items,
                           o.total_price, o.status, o.order_time
                    FROM orders o
                    WHERE o.rider_id = ?
                    """,
                    (rider_id,)
                )
                results = cursor.fetchall()
                return [Order(*result) for result in results]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

    @staticmethod
    def assign_rider(order_id, rider_id):
        """
        Assign a rider to an order.

        Args:
            order_id (int): Order's ID
            rider_id (int): Rider's ID

        Returns:
            bool: True if successful
        """
        try:
            with sqlite3.connect('food_delivery.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE orders
                    SET rider_id = ?, status = 'assigned'
                    WHERE order_id = ?
                    """,
                    (rider_id, order_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

    @staticmethod
    def get_by_id(order_id):
        """
        Retrieve an order by its ID.

        Args:
            order_id (int): Order's ID

        Returns:
            Order: Order object if found, None otherwise
        """
        try:
            with sqlite3.connect('food_delivery.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT order_id, user_id, restaurant_id, rider_id, items,
                           total_price, status, order_time
                    FROM orders
                    WHERE order_id = ?
                    """,
                    (order_id,)
                )
                result = cursor.fetchone()
                if result:
                    return Order(*result)
                return None
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

@staticmethod
def mark_as_completed(order_id):
    """
    Mark an order as completed.
    
    Args:
        order_id (int): Order's ID
        
    Returns:
        bool: True if update was successful
    """
    try:
        with sqlite3.connect('food_delivery.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE orders
                SET status = 'completed'
                WHERE order_id = ?
                """,
                (order_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Database error: {str(e)}")
