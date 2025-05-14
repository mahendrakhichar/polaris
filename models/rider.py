import sqlite3

class Rider:
    def __init__(self, rider_id, name, location, is_available=True):
        """
        Initialize a Rider object.
        
        Args:
            rider_id (int): Unique identifier for the rider
            name (str): Rider's name
            location (str): Rider's current location (e.g., 'Downtown')
            is_available (bool): Whether the rider is available for orders
        """
        self.rider_id = rider_id
        self.name = name
        self.location = location
        self.is_available = is_available

    @staticmethod
    def register(name, location):
        """
        Register a new rider in the database.
        
        Args:
            name (str): Rider's name
            location (str): Rider's location
            
        Returns:
            Rider: Newly created Rider object
            
        Raises:
            ValueError: If name or location is empty
            sqlite3.Error: If database operation fails
        """
        if not name or not location:
            raise ValueError("Name and location are required")
        try:
            with sqlite3.connect('food_delivery.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO riders (name, location, is_available) VALUES (?, ?, ?)",
                    (name, location, True)
                )
                conn.commit()
                rider_id = cursor.lastrowid
                return Rider(rider_id, name, location, True)
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

    @staticmethod
    def get_by_id(rider_id):
        """
        Retrieve a rider by their ID.
        
        Args:
            rider_id (int): Rider's ID
            
        Returns:
            Rider: Rider object if found, None otherwise
        """
        try:
            with sqlite3.connect('food_delivery.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT rider_id, name, location, is_available FROM riders WHERE rider_id = ?",
                    (rider_id,)
                )
                result = cursor.fetchone()
                if result:
                    return Rider(result[0], result[1], result[2], result[3])
                return None
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

    @staticmethod
    def update_location(rider_id, new_location):
        """
        Update a rider's location.
        
        Args:
            rider_id (int): Rider's ID
            new_location (str): New location
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not new_location:
            raise ValueError("New location is required")
        try:
            with sqlite3.connect('food_delivery.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE riders SET location = ? WHERE rider_id = ?",
                    (new_location, rider_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

    @staticmethod
    def get_available_riders():
        """
        Retrieve all available riders.
        
        Returns:
            list: List of Rider objects
        """
        try:
            with sqlite3.connect('food_delivery.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT rider_id, name, location, is_available FROM riders WHERE is_available = ?", (True,))
                results = cursor.fetchall()
                return [Rider(result[0], result[1], result[2], result[3]) for result in results]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

    @staticmethod
    def set_availability(rider_id, is_available):
        """
        Update a rider's availability status.
        
        Args:
            rider_id (int): Rider's ID
            is_available (bool): New availability status
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            with sqlite3.connect('food_delivery.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE riders SET is_available = ? WHERE rider_id = ?",
                    (is_available, rider_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")