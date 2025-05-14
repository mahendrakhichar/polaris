from flask import Blueprint, request, jsonify
from db import db_cursor

notification_routes = Blueprint('notification_routes', __name__)

@notification_routes.route('/notify_user', methods=['POST'])
def notify_user():
    """
    Log a notification for a user.
    
    Request Body:
        - user_id (int): ID of the user
        - order_id (int, optional): ID of the related order
        - message (str): Notification message
    
    Returns:
        JSON: Notification ID and success message
    """
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'message' not in data:
            return jsonify({'message': 'User ID and message are required'}), 400
        
        user_id = data['user_id']
        order_id = data.get('order_id')
        message = data['message']
        
        # Validate user
        with db_cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                return jsonify({'message': f'User with ID {user_id} not found'}), 404
            
            # Validate order if provided
            if order_id:
                cursor.execute("SELECT order_id FROM orders WHERE order_id = ?", (order_id,))
                if not cursor.fetchone():
                    return jsonify({'message': f'Order with ID {order_id} not found'}), 404
            
            # Insert notification
            cursor.execute(
                "INSERT INTO notifications (user_id, order_id, message) VALUES (?, ?, ?)",
                (user_id, order_id, message)
            )
            notification_id = cursor.lastrowid
        
        return jsonify({
            'notification_id': notification_id,
            'message': 'Notification logged successfully'
        }), 201
    except Exception as e:
        return jsonify({'message': f'Error logging notification: {str(e)}'}), 500

@notification_routes.route('/list_user_notifications', methods=['POST'])
def list_user_notifications():
    """
    Retrieve all notifications for a user.
    
    Request Body:
        - user_id (int): ID of the user
    
    Returns:
        JSON: List of notifications
    """
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'message': 'User ID is required'}), 400
        
        user_id = data['user_id']
        
        # Validate user
        with db_cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                return jsonify({'message': f'User with ID {user_id} not found'}), 404
            
            # Get notifications
            cursor.execute(
                """
                SELECT notification_id, user_id, order_id, message, created_at
                FROM notifications
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,)
            )
            notifications = cursor.fetchall()
        
        notifications_list = [
            {
                'notification_id': n['notification_id'],
                'order_id': n['order_id'],
                'message': n['message'],
                'created_at': str(n['created_at'])
            }
            for n in notifications
        ]
        
        return jsonify({
            'user_id': user_id,
            'notifications': notifications_list,
            'message': 'Notifications retrieved successfully'
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error retrieving notifications: {str(e)}'}), 500
    
    