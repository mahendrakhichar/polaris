from db import db_cursor
from datetime import datetime, time
from utils import calculate_distance, estimate_delivery_time
from models.restaurant import Restaurant
from models.rider import Rider

class MatchingService:
    BREAKFAST_START = time(6, 0)
    BREAKFAST_END = time(11, 0)
    LUNCH_START = time(11, 0)
    LUNCH_END = time(16, 0)
    DINNER_START = time(16, 0)
    DINNER_END = time(23, 0)

    def get_current_meal_period():
        current_time = datetime.now().time()

        if MatchingService.BREAKFAST_START <= current_time < MatchingService.BREAKFAST_END:
            return 'breakfast'
        elif MatchingService.LUNCH_START <= current_time < MatchingService.LUNCH_END:
            return 'lunch'
        elif MatchingService.DINNER_START <= current_time < MatchingService.DINNER_END:
            return 'dinner'
        return None

    @staticmethod
    def calculate_distance(point1, point2):
        # Simple distance calculation - in production use proper geocoding
        return abs(hash(point1) - hash(point2)) % 10

    """Service to handle restaurant suggestions and rider assignment."""

    @staticmethod
    def suggest_restaurants(user_location: str, food_type: str, max_delivery_time: int) -> list:
        """
        Suggest restaurants based on food type and delivery time.

        Args:
            user_location (str): User's location (e.g., 'Downtown')
            food_type (str): Desired food type (e.g., 'Italian')
            max_delivery_time (int): Maximum delivery time in minutes

        Returns:
            list: List of restaurant dictionaries with estimated delivery time
        """
        if not user_location or not food_type or max_delivery_time <= 0:
            raise ValueError("User location, food type, and valid delivery time are required")

        suggestions = []
        with db_cursor() as cursor:
            cursor.execute(
                "SELECT restaurant_id, name, location, food_type, prep_time FROM restaurants WHERE food_type = ?",
                (food_type,)
            )
            restaurants = cursor.fetchall()

            for restaurant in restaurants:
                delivery_time = estimate_delivery_time(restaurant['location'], user_location, restaurant['prep_time'])
                if delivery_time <= max_delivery_time:
                    suggestions.append({
                        "restaurant_id": restaurant['restaurant_id'],
                        "name": restaurant['name'],
                        "location": restaurant['location'],
                        "food_type": restaurant['food_type'],
                        "estimated_delivery_time": delivery_time
                    })

        # Sort by estimated delivery time
        return sorted(suggestions, key=lambda x: x['estimated_delivery_time'])


    @staticmethod
    def find_nearest_rider(restaurant_location):
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT r.*,
                    (SELECT COUNT(*) FROM orders
                     WHERE rider_id = r.rider_id
                     AND status = 'in_progress') as active_orders
                FROM riders r
                WHERE is_available = 1
                HAVING active_orders < 3
                ORDER BY ABS(CAST(REPLACE(r.location, ' ', '') AS INTEGER) -
                           CAST(REPLACE(?, ' ', '') AS INTEGER))
                LIMIT 1
            """, (restaurant_location,))
            return cursor.fetchone()

    @staticmethod
    def calculate_delivery_time(restaurant_location, rider_location):
        # Simple mock distance calculation
        distance = abs(int(''.join(filter(str.isdigit, restaurant_location))) -
                      int(''.join(filter(str.isdigit, rider_location))))
        return max(5, min(30, distance // 100))
