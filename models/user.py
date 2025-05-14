import sqlite3

class User:
    def __init__(self, user_id, name, location):
        """
        Initialize a User object.

        Args:
            user_id (int): Unique identifier for the user
            name (str): User's name
            location (str): User's location (e.g., 'Downtown')
        """
        self.user_id = user_id
        self.name = name
        self.location = location

    @staticmethod
    def register(name, location):
        """
        Register a new user in the database.

        Args:
            name (str): User's name
            location (str): User's location

        Returns:
            User: Newly created User object

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
                    "INSERT INTO users (name, location) VALUES (?, ?)",
                    (name, location)
                )
                conn.commit()
                user_id = cursor.lastrowid
                return User(user_id, name, location)
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")

    @staticmethod
    def get_by_id(user_id):
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): User's ID

        Returns:
            User: User object if found, None otherwise
        """
        try:
            with sqlite3.connect('food_delivery.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                result = cursor.fetchone()
                if result:
                    return User(result[0], result[1], result[2])
                return None
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")
