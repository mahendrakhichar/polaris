import sqlite3
from db import db_cursor

class Restaurant:
    def __init__(self, restaurant_id: int, name: str, location: str, food_type: str, prep_time: int):
        """
        Initialize a Restaurant object.
        
        Args:
            restaurant_id (int): Unique identifier for the restaurant
            name (str): Name of the restaurant
            location (str): Location of the restaurant
            food_type (str): Type of cuisine (e.g., Italian)
            prep_time (int): Food preparation time in minutes
        """
        self.restaurant_id = restaurant_id
        self.name = name
        self.location = location
        self.food_type = food_type
        self.prep_time = prep_time

    @staticmethod
    def register(name: str, location: str, food_type: str, prep_time: int = 10, menu_items: list = None) -> 'Restaurant':
        """
        Register a new restaurant with optional menu items.
        
        Args:
            name (str): Restaurant's name
            location (str): Restaurant's location
            food_type (str): Type of cuisine
            prep_time (int): Food preparation time in minutes
            menu_items (list): List of menu items, each with 'item_name' and 'price'
        
        Returns:
            Restaurant: Newly created Restaurant object
        
        Raises:
            ValueError: If name, location, or food_type is empty
            sqlite3.Error: If database operation fails
        """
        if not name or not location or not food_type:
            raise ValueError("Name, location, and food type are required")
        
        try:
            with db_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO restaurants (name, location, food_type, prep_time) VALUES (?, ?, ?, ?)",
                    (name, location, food_type, prep_time)
                )
                restaurant_id = cursor.lastrowid
                
                if menu_items:
                    for item in menu_items:
                        cursor.execute(
                            "INSERT INTO menus (restaurant_id, item_name, price) VALUES (?, ?, ?)",
                            (restaurant_id, item['item_name'], item['price'])
                        )
                
                return Restaurant(restaurant_id, name, location, food_type, prep_time)
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

    @staticmethod
    def get_by_id(restaurant_id: int) -> 'Restaurant':
        """
        Retrieve a restaurant by its ID.
        
        Args:
            restaurant_id (int): Restaurant's ID
        
        Returns:
            Restaurant: Restaurant object if found, None otherwise
        """
        try:
            with db_cursor() as cursor:
                cursor.execute(
                    "SELECT restaurant_id, name, location, food_type, prep_time FROM restaurants WHERE restaurant_id = ?",
                    (restaurant_id,)
                )
                result = cursor.fetchone()
                if result:
                    return Restaurant(*result)
                return None
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

    @staticmethod
    def add_menu_item(restaurant_id: int, item_name: str, price: float) -> bool:
        """
        Add a menu item to a restaurant.
        
        Args:
            restaurant_id (int): Restaurant's ID
            item_name (str): Name of the menu item
            price (float): Price of the item
        
        Returns:
            bool: True if successful
        """
        if not item_name or price <= 0:
            raise ValueError("Item name and valid price are required")
        
        try:
            with db_cursor() as cursor:
                cursor.execute(
                    "SELECT restaurant_id FROM restaurants WHERE restaurant_id = ?",
                    (restaurant_id,)
                )
                if not cursor.fetchone():
                    return False
                
                cursor.execute(
                    "INSERT INTO menus (restaurant_id, item_name, price) VALUES (?, ?, ?)",
                    (restaurant_id, item_name, price)
                )
                return True
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

    @staticmethod
    def get_menu(restaurant_id: int) -> list:
        """
        Retrieve the menu for a restaurant.
        
        Args:
            restaurant_id (int): Restaurant's ID
        
        Returns:
            list: List of menu items (dicts with menu_id, item_name, price)
        """
        try:
            with db_cursor() as cursor:
                cursor.execute(
                    "SELECT menu_id, item_name, price FROM menus WHERE restaurant_id = ?",
                    (restaurant_id,)
                )
                results = cursor.fetchall()
                return [{"menu_id": r['menu_id'], "item_name": r['item_name'], "price": r['price']} for r in results]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")