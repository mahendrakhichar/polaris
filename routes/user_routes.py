from flask import Blueprint, request, jsonify, render_template
from models.user import User
from models.order import Order
from utils import format_order_details
import logging
from models.restaurant import Restaurant
from models.user import User
from db import db_cursor
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/register_user', methods=['POST'])
def register_user():
    """
    Register a new user.

    Request Body:
        - name (str): User's name
        - location (str): User's location (e.g., 'Downtown')

    Returns:
        JSON: User ID and success message, or error message
    """
    try:
        logger.debug("Received request to register user")
        data = request.get_json()
        logger.debug(f"Request JSON: {data}")

        if not data or 'name' not in data or 'location' not in data:
            logger.warning("Missing name or location in request")
            return jsonify({"error": "Name and location are required"}), 400

        user = User.register(data['name'], data['location'])
        logger.info(f"User registered successfully: ID={user.user_id}")
        return jsonify({
            "user_id": user.user_id,
            "message": "User registered successfully"
        }), 201
    except ValueError as e:
        logger.error(f"ValueError in register_user: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in register_user: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@user_routes.route('/user/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """
    Fetch order history for a user.
    
    Path Parameters:
        - user_id (int): User's ID
    
    Returns:
        JSON: List of user's orders with details
    """
    try:
        logger.debug(f"Fetching orders for user_id={user_id}")
        user = User.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found: user_id={user_id}")
            return jsonify({"error": "User not found"}), 404
        
        orders = Order.get_user_orders(user_id)
        formatted_orders = []
        for order in orders:
            restaurant = Restaurant.get_by_id(order.restaurant_id)
            order_dict = {
                "order_id": order.order_id,
                "restaurant_name": restaurant.name if restaurant else "Unknown",
                "items": order.items,
                "total_price": order.total_price,
                "status": order.status,
                "order_time": order.order_time
            }
            formatted_orders.append(format_order_details(order_dict))
        
        logger.info(f"Retrieved {len(orders)} orders for user_id={user_id}")
        return jsonify({
            "user_id": user_id,
            "orders": formatted_orders
        }), 200
    except Exception as e:
        logger.error(f"Unexpected error in get_user_orders: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    
@user_routes.route('/users')
def get_all_users():
    try:
        # Fetch all users from the database
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()  # Fetch all rows as a list of dictionaries

        # If no users are found, return an error message
        if not users:
            return render_template('users.html', error="No users found.")

        # Render the users page with user data
        return render_template('users.html', users=users)

    except Exception as e:
        print(f"Error: {e}")
        return render_template('users.html', error="Error loading users.")