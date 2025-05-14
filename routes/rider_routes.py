from flask import Blueprint, request, jsonify, render_template
from models.rider import Rider
from models.order import Order
from utils import format_order_details
import logging
from models.restaurant import Restaurant
from db import db_cursor

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the Blueprint for rider-related routes
rider_routes = Blueprint('rider_routes', __name__)

# Route to register a new rider
@rider_routes.route('/register_rider', methods=['POST'])
def register_rider():
    try:
        # Get data from the request
        data = request.get_json()
        name = data.get('name')
        location = data.get('location')

        if not name or not location:
            return jsonify({"error": "Name and location are required!"}), 400

        # Insert the new rider into the database
        with db_cursor() as cursor:
            cursor.execute('''INSERT INTO riders (name, location) VALUES (?, ?)''', (name, location))
            rider_id = cursor.lastrowid

        return jsonify({"message": "Rider registered!", "rider_id": rider_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to update rider's location
@rider_routes.route('/update_rider_location', methods=['PUT'])
def update_rider_location():
    try:
        logger.debug("Received request to update rider location")
        data = request.get_json()
        logger.debug(f"Request JSON: {data}")

        if not data or 'rider_id' not in data or 'location' not in data:
            logger.warning("Missing rider_id or location in request")
            return jsonify({"error": "Rider ID and location are required"}), 400

        rider_id = data['rider_id']
        location = data['location']

        if Rider.update_location(rider_id, location):
            logger.info(f"Rider location updated: ID={rider_id}, Location={location}")
            return jsonify({"message": "Rider location updated successfully"}), 200
        else:
            logger.warning(f"Rider not found: ID={rider_id}")
            return jsonify({"error": "Rider not found"}), 404
    except Exception as e:
        logger.error(f"Unexpected error in update_rider_location: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

# Route to fetch orders for a rider
@rider_routes.route('/rider/<int:rider_id>/orders', methods=['GET'])
def get_rider_orders(rider_id):
    try:
        logger.debug(f"Fetching orders for rider_id={rider_id}")
        rider = Rider.get_by_id(rider_id)
        if not rider:
            logger.warning(f"Rider not found: rider_id={rider_id}")
            return jsonify({"error": "Rider not found"}), 404

        orders = Order.get_rider_orders(rider_id)
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

        logger.info(f"Retrieved {len(orders)} orders for rider_id={rider_id}")
        return jsonify({
            "rider_id": rider_id,
            "orders": formatted_orders
        }), 200
    except Exception as e:
        logger.error(f"Unexpected error in get_rider_orders: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

# Route to display all riders
@rider_routes.route('/riders')
def get_all_riders():
    try:
        # Fetch all riders from the database
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM riders")
            riders = cursor.fetchall()

        # If no riders are found, return an error message
        if not riders:
            return render_template('riders.html', error="No riders found.")

        # Render the riders page with rider data
        return render_template('riders.html', riders=riders)

    except Exception as e:
        print(f"Error: {e}")
        return render_template('riders.html', error="Error loading riders.")

@rider_routes.route('/api/riders/available')
def get_available_riders():
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM riders
            WHERE is_available = 1
        """)
        return jsonify([dict(row) for row in cursor.fetchall()])
