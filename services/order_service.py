from db import db_cursor
from models.user import User
from models.restaurant import Restaurant
from models.order import Order
from services.matching_service import MatchingService

class OrderService:
    """Service to handle order placement and related operations."""
    
    @staticmethod
    @staticmethod
    def place_order(user_id: int, restaurant_id: int, item_ids: list) -> dict:
        """
    Place an order for a user from a restaurant with selected menu items.
    
    Args:
        user_id (int): User's ID
        restaurant_id (int): Restaurant's ID
        item_ids (list): List of menu item IDs to order
        
    Returns:
        dict: Order details including order_id, items, total_price, and status
        
    Raises:
        ValueError: If user, restaurant, or items are invalid
    """
        if not item_ids:
            raise ValueError("At least one item must be selected")
        
    # Validate user
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
    # Validate restaurant
        restaurant = Restaurant.get_by_id(restaurant_id)
        if not restaurant:
           raise ValueError("Restaurant not found")
        
    # Fetch and validate menu items
        with db_cursor() as cursor:
           placeholders = ','.join('?' for _ in item_ids)
           cursor.execute(
               f"SELECT menu_id, item_name, price FROM menus WHERE menu_id IN ({placeholders}) AND restaurant_id = ?",
               item_ids + [restaurant_id]
           )
           menu_items = cursor.fetchall()

           if len(menu_items) != len(item_ids):
               raise ValueError("Some items are invalid or not available at this restaurant")

           # Calculate total price and format items
           total_price = sum(item['price'] for item in menu_items)
           items_str = ','.join(item['item_name'] for item in menu_items)

    #    Place order
        order = Order.place_order(user_id, restaurant_id, items_str, total_price)
    
        # Assign rider
        rider = MatchingService.find_nearest_rider(restaurant.location)
        rider_status = "Pending"
        if rider:
           if Order.assign_rider(order.order_id, rider['rider_id']):
               rider_status = "Assigned"

        return {
            "order_id": order.order_id,
            "user_id": user_id,
            "restaurant_name": restaurant.name,
            "items": items_str,
            "total_price": total_price,
            "status": order.status,
            "rider_status": rider_status
        }