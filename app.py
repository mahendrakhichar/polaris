from flask import Flask, jsonify, render_template
from routes.user_routes import user_routes
from routes.rider_routes import rider_routes
from routes.restaurant_routes import restaurant_routes
from routes.order_routes import order_routes
from routes.notification_routes import notification_routes
from db import db_cursor, init_db

app = Flask(__name__)

# Register Blueprints for API routes
app.register_blueprint(user_routes)
app.register_blueprint(rider_routes)
app.register_blueprint(restaurant_routes)
app.register_blueprint(order_routes)
app.register_blueprint(notification_routes)

# Initialize database
init_db()

# Web UI Routes
@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/register_user')
def register_user_page():
    """Render the user registration page."""
    return render_template('register_user.html')

@app.route('/register_rider')
def register_rider_page():
    """Render the rider registration page."""
    return render_template('register_rider.html')

@app.route('/register_restaurant')
def register_restaurant_page():
    """Render the restaurant registration page."""
    return render_template('register_restaurant.html')

@app.route('/suggest_restaurants')
def suggest_restaurants():
    with db_cursor() as cursor:
        # Get all cuisines
        cursor.execute("SELECT DISTINCT food_type FROM restaurants")
        cuisines = [row['food_type'] for row in cursor.fetchall()]

        # Get all restaurants with details
        cursor.execute("""
            SELECT * FROM restaurants
            ORDER BY name
        """)
        restaurants = cursor.fetchall()

        return render_template('suggest_restaurants.html',
                             restaurants=restaurants,
                             cuisines=cuisines)

@app.route('/view_menu')
def view_menu():
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT restaurant_id, name
            FROM restaurants
            ORDER BY name
        """)
        restaurants = cursor.fetchall()
        return render_template('view_menu.html', restaurants=restaurants)



@app.route('/place_order')
def place_order_page():
    """Render the order placement page with restaurants."""
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM restaurants
            ORDER BY name
        """)
        restaurants = cursor.fetchall()
        return render_template('place_order.html', restaurants=restaurants)

@app.route('/assign_rider')
def assign_rider_page():
    """Render the rider assignment page."""
    return render_template('assign_rider.html')

@app.route('/update_rider_location')
def update_rider_location_page():
    """Render the rider location update page."""
    return render_template('update_rider_location.html')

@app.route('/user_orders')
def user_orders_page():
    """Render the user order history page."""
    return render_template('user_orders.html')

@app.route('/rider_orders')
def rider_orders_page():
    """Render the rider order history page."""
    return render_template('rider_orders.html')

@app.route('/completed_orders')
def completed_orders_page():
    """Render the completed orders page."""
    return render_template('completed_orders.html')

@app.route('/users')
def all_users_page():
    return render_template('users.html')

@app.route('/riders')
def all_riders_page():
    return render_template('riders.html')

@app.route('/restaurants')
def all_restaurants_page():
    return render_template('restaurants.html')

@app.route('/api/restaurant/<int:restaurant_id>/menu')
def get_restaurant_menu(restaurant_id):
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT menu_id, item_name, price
                FROM menus
                WHERE restaurant_id = ?
            """, (restaurant_id,))
            menu_items = cursor.fetchall()
            return jsonify([{
                'menu_id': item['menu_id'],
                'item_name': item['item_name'],
                'price': float(item['price'])
            } for item in menu_items])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
