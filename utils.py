from datetime import datetime

def calculate_distance(loc1: str, loc2: str) -> float:
    """Dummy function to calculate distance between two locations"""
    # Simplified: Treat different location strings as 5 units apart
    return 0 if loc1 == loc2 else 5

def estimate_delivery_time(restaurant_location: str, user_location: str, prep_time: int) -> int:
    """Estimate delivery time as sum of travel time and prep time"""
    travel_time = calculate_distance(restaurant_location, user_location) * 2  # 2 mins per unit distance
    return prep_time + travel_time

def format_order_details(order):
    """
    Format order details for JSON response.

    Args:
    
        order (dict): Dictionary containing order data. Expected keys include:
            - order_id (int)
            - restaurant_name (str)
            - items (str or list)
            - total_price (float or str)
            - status (str)
            - order_time (datetime or str)

    Returns:
        dict: Cleaned and formatted dictionary suitable for API response.
    """
    return {
        "order_id": order.get("order_id"),
        "restaurant": order.get("restaurant_name"),
        "items": order.get("items"),
        "total_price": round(float(order.get("total_price", 0)), 2),
        "status": order.get("status"),
        "ordered_at": (
            order["order_time"].strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(order.get("order_time"), datetime)
            else str(order.get("order_time"))
        )
    }
