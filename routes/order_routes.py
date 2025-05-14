from flask import Blueprint, json, request, jsonify
from datetime import datetime
from services.matching_service import MatchingService
from models.order import Order
from db import db_cursor

order_routes = Blueprint('order_routes', __name__)
@order_routes.route('/api/orders', methods=['POST'])
def place_order():
    try:
        data = request.json
        with db_cursor() as cursor:
            # Create order
            cursor.execute("""
                INSERT INTO orders (
                    restaurant_id,
                    items,
                    total_price,
                    status
                ) VALUES (?, ?, ?, 'pending')
                RETURNING order_id
            """, (
                data['restaurant_id'],
                json.dumps(data['items']),
                sum(item['price'] for item in data['items'])
            ))

            order_id = cursor.fetchone()['order_id']

            # Get restaurant prep time
            cursor.execute("""
                SELECT prep_time FROM restaurants
                WHERE restaurant_id = ?
            """, (data['restaurant_id'],))
            prep_time = cursor.fetchone()['prep_time']

            # Find available rider
            cursor.execute("""
                SELECT * FROM riders
                WHERE is_available = 1
                LIMIT 1
            """)
            rider = cursor.fetchone()

            if rider:
                estimated_time = prep_time + 15  # Base delivery time

                # Update order with rider and estimated time
                cursor.execute("""
                    UPDATE orders
                    SET rider_id = ?,
                        estimated_delivery_time = ?,
                        status = 'assigned'
                    WHERE order_id = ?
                """, (rider['rider_id'], estimated_time, order_id))

                return jsonify({
                    'order_id': order_id,
                    'status': 'assigned',
                    'estimated_time': estimated_time,
                    'rider': {
                        'name': rider['name'],
                        'id': rider['rider_id']
                    }
                })

            return jsonify({
                'order_id': order_id,
                'status': 'pending'
            })

    except Exception as e:
        print(f"Error placing order: {str(e)}")
        return jsonify({'error': str(e)}), 500

@order_routes.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details"""
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT o.*, r.name as restaurant_name,
                       rd.name as rider_name, rd.location as rider_location
                FROM orders o
                JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                LEFT JOIN riders rd ON o.rider_id = rd.rider_id
                WHERE o.order_id = ?
            """, (order_id,))
            order = cursor.fetchone()
            if not order:
                return jsonify({'error': 'Order not found'}), 404

            return jsonify(dict(order))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_routes.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    try:
        data = request.json
        with db_cursor() as cursor:
            cursor.execute("""
                UPDATE orders
                SET status = ?
                WHERE order_id = ?
            """, (data['status'], order_id))

            return jsonify({'message': 'Status updated'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_routes.route('/api/user/<int:user_id>/orders')
def get_user_orders(user_id):
    """Get user's order history"""
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT o.*, r.name as restaurant_name
                FROM orders o
                JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                WHERE o.user_id = ?
                ORDER BY o.order_time DESC
            """, (user_id,))
            orders = cursor.fetchall()

            return jsonify([dict(order) for order in orders])

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_routes.route('/api/orders/assign_rider', methods=['POST'])
def assign_rider():
    try:
        data = request.json
        with db_cursor() as cursor:
            # Validate order exists
            cursor.execute("""
                SELECT * FROM orders WHERE order_id = ?
            """, (data['order_id'],))
            order = cursor.fetchone()
            if not order:
                return jsonify({'error': 'Order not found'}), 404

            # Validate rider
            cursor.execute("""
                SELECT * FROM riders WHERE rider_id = ?
            """, (data['rider_id'],))
            rider = cursor.fetchone()
            if not rider:
                return jsonify({'error': 'Rider not found'}), 404

            # Update order with rider assignment
            cursor.execute("""
                UPDATE orders
                SET rider_id = ?,
                    estimated_delivery_time = ?,
                    status = 'assigned'
                WHERE order_id = ?
            """, (
                data['rider_id'],
                data['estimated_time'],
                data['order_id']
            ))

            return jsonify({
                'message': 'Rider assigned successfully',
                'order_id': data['order_id'],
                'rider_id': data['rider_id'],
                'estimated_time': data['estimated_time']
            })

    except Exception as e:
        print(f"Error assigning rider: {str(e)}")
        return jsonify({'error': str(e)}), 500


@order_routes.route('/api/riders/available', methods=['GET'])
def get_available_riders():
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT r.*,
                   COUNT(o.order_id) as active_orders
            FROM riders r
            LEFT JOIN orders o ON r.rider_id = o.rider_id
            AND o.status = 'in_progress'
            WHERE r.is_available = 1
            GROUP BY r.rider_id
            HAVING active_orders < 3
        """)
        return jsonify([dict(row) for row in cursor.fetchall()])
