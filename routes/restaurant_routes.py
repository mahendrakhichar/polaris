from flask import Blueprint, request, jsonify,render_template
from datetime import datetime
from models.restaurant import Restaurant
from models.restaurant import Restaurant  # ensure this is imported
from db import db_cursor
restaurant_routes = Blueprint('restaurant_routes', __name__)

@restaurant_routes.route('/register_restaurant', methods=['POST'])
def register_restaurant():
    """
    Register a new restaurant.

    Request Body:
        - name (str): Restaurant's name
        - location (str): Restaurant's location (e.g., 'Downtown')
        - food_type (str): Type of cuisine (e.g., 'Italian')
        - prep_time (int, optional): Food preparation time in minutes (default: 10)
        - menu_items (list, optional): List of menu items, each as a dict with 'item_name' and 'price'

    Returns:
        JSON: Restaurant ID and success message, or error message
    """
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'location' not in data or 'food_type' not in data:
            return jsonify({"error": "Name, location, and food type are required"}), 400

        prep_time = data.get('prep_time', 10)
        menu_items = data.get('menu_items', [])

        if menu_items and (not isinstance(menu_items, list) or not all('item_name' in item and 'price' in item for item in menu_items)):
            return jsonify({"error": "Menu items must be a list of dicts with 'item_name' and 'price'"}), 400

        # Register the restaurant along with its menu items
        restaurant = Restaurant.register(data['name'], data['location'], data['food_type'], prep_time, menu_items)

        return jsonify({
            "restaurant_id": restaurant.restaurant_id,
            "message": "Restaurant registered successfully"
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
@restaurant_routes.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    """
    Add a menu item to a restaurant.

    Request Body:
        - restaurant_id (int): Restaurant's ID
        - item_name (str): Name of the menu item
        - price (float): Price of the item

    Returns:
        JSON: Success message or error message
    """
    try:
        data = request.get_json()
        if not data or 'restaurant_id' not in data or 'item_name' not in data or 'price' not in data:
            return jsonify({"error": "Restaurant ID, item name, and price are required"}), 400

        success = Restaurant.add_menu_item(data['restaurant_id'], data['item_name'], data['price'])
        if not success:
            return jsonify({"error": "Restaurant not found"}), 404

        return jsonify({"message": "Menu item added successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@restaurant_routes.route('/menu/<int:restaurant_id>', methods=['GET'])
def get_menu(restaurant_id):
    """
    Fetch the menu for a restaurant.

    Path Parameters:
        - restaurant_id (int): Restaurant's ID

    Returns:
        JSON: List of menu items with details
    """
    try:
        restaurant = Restaurant.get_by_id(restaurant_id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404

        menu = Restaurant.get_menu(restaurant_id)
        return jsonify({
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant.name,
            "menu": menu
        }), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


# Route to display all restaurants
@restaurant_routes.route('/restaurants')
def get_all_restaurants():
    try:
        # Fetch all restaurants from the database
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM restaurants")
            restaurants = cursor.fetchall()

        # If no restaurants are found, return an error message
        if not restaurants:
            return render_template('restaurant.html', error="No restaurants found.")

        # Render the restaurants page with restaurant data
        return render_template('restaurant.html', restaurants=restaurants)

    except Exception as e:
        print(f"Error: {e}")
        return render_template('restaurant.html', error="Error loading restaurants.")


@restaurant_routes.route('/api/restaurants/search')
def search_restaurants():
    current_hour = datetime.now().hour
    current_time = datetime.now().strftime('%H:%M')

    # Determine meal period
    if 6 <= current_hour < 11:
        meal_period = 'breakfast'
    elif 11 <= current_hour < 16:
        meal_period = 'lunch'
    else:
        meal_period = 'dinner'

    with db_cursor() as cursor:
        cursor.execute("""
            SELECT r.*,
                   CASE
                       WHEN time(?) BETWEEN r.opening_time AND r.closing_time THEN 1
                       ELSE 0
                   END as is_open,
                   CASE
                       WHEN ? = 'breakfast' THEN r.serves_breakfast
                       WHEN ? = 'lunch' THEN r.serves_lunch
                       WHEN ? = 'dinner' THEN r.serves_dinner
                   END as serves_current_meal
            FROM restaurants r
            WHERE serves_current_meal = 1
        """, (current_time, meal_period, meal_period, meal_period))

        restaurants = [dict(row) for row in cursor.fetchall()]
        return jsonify(restaurants)
