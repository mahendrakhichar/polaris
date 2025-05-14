Food Delivery Backend Design Document

1. Approach
   The food delivery backend is designed as a Flask-based RESTful API with a modular architecture to meet the mandatory functional requirements: user/rider/restaurant registration, restaurant suggestions, menu display, order placement, rider assignment, rider location updates, and order history retrieval. A text-based CLI interface is provided for testing, simulating user interactions like placing orders and selecting restaurants.
   Key Components

Database: SQLite for simplicity, with tables for users, riders, restaurants, menus, and orders.
Models: Python classes (User, Rider, Restaurant, Order) encapsulate database operations.
Services: Business logic is handled by MatchingService (restaurant suggestions, rider assignment) and OrderService (order placement).
Routes: Flask Blueprint organizes API endpoints for users, riders, restaurants, and orders.
CLI: A text-based interface in app.py allows testing all features via HTTP requests.
Utilities: Helper functions in utils.py for distance calculation, ETA estimation, and order formatting.

Development Strategy

Modularity: Separate concerns into models, services, and routes for maintainability.
Simplicity: Use SQLite and mock distance calculations for quick prototyping.
Extensibility: Design schema and logic to support future features (e.g., coupons, ratings).
Testing: CLI interface enables end-to-end testing of all requirements.

2. Assumptions

Location Handling:

Locations are text-based (e.g., 'Downtown', 'Uptown') instead of latitude/longitude, as requested.
Distance calculations use a mock table (in utils.py) mapping location pairs to distances (e.g., Downtown to Uptown = 5 km).
Rider speed is assumed to be 20 km/h, and restaurant preparation time defaults to 10 minutes.

Database:

SQLite is used for simplicity, suitable for a prototype but not for production scale.
All tables have primary keys and foreign keys for data integrity.
Indexes are added for frequent queries (e.g., order history by user or rider).

Order Workflow:

Orders are placed with a list of menu item IDs, and the total price is calculated by summing item prices.
Riders are assigned based on the closest available rider to the restaurant’s location.
Order status transitions from 'placed' to 'assigned' upon rider assignment (additional statuses like 'delivered' can be added).

Scalability:

The prototype assumes moderate data volume. Scalability is addressed with indexes and modular design, with recommendations for production (e.g., PostgreSQL, caching).

CLI Interface:

The CLI simulates a user interface, allowing text input for all operations.
Users must know IDs (e.g., user_id, restaurant_id) for some operations, which would be handled by a frontend in production.

3. Low-Level Design
   3.1. Database Schema
   The database (food_delivery.db) consists of five tables, designed for efficiency and integrity:

users

Columns: user_id (PK, INTEGER), name (TEXT), location (TEXT)
Purpose: Stores user details for order placement and history.
Indexes: None (primary key sufficient).

riders

Columns: rider_id (PK, INTEGER), name (TEXT), location (TEXT), is_available (BOOLEAN)
Purpose: Stores rider details for assignment and location tracking.
Indexes: None (add is_available index in production).

restaurants

Columns: restaurant_id (PK, INTEGER), name (TEXT), location (TEXT), food_type (TEXT), prep_time (INTEGER)
Purpose: Stores restaurant details for suggestions and menu management.
Indexes: None (add food_type index in production).

menus

Columns: menu_id (PK, INTEGER), restaurant_id (FK, INTEGER), item_name (TEXT), price (REAL)
Purpose: Stores menu items for each restaurant.
Indexes: restaurant_id for fast menu retrieval.

orders

Columns: order_id (PK, INTEGER), user_id (FK, INTEGER), restaurant_id (FK, INTEGER), rider_id (FK, INTEGER), items (TEXT), total_price (REAL), status (TEXT), order_time (TIMESTAMP)
Purpose: Stores order details for history and rider assignment.
Indexes: user_id, rider_id for fast history queries.

3.2. API Endpoints
The API is organized into four Blueprint modules:

user_routes:
POST /register_user: Register a user.
GET /user/<user_id>/orders: Fetch user order history.

rider_routes:
POST /register_rider: Register a rider.
PUT /update_rider_location: Update rider location.
GET /rider/<rider_id>/orders: Fetch rider order history.

restaurant_routes:
POST /register_restaurant: Register a restaurant.
POST /add_menu_item: Add a menu item.
GET /menu/<restaurant_id>: Fetch restaurant menu.

order_routes:
POST /suggest_restaurants: Suggest restaurants by food type and delivery time.
POST /place_order: Place an order.
POST /assign_rider/<order_id>: Assign a rider.

3.3. Business Logic

Restaurant Suggestions (MatchingService.suggest_restaurants):
Filters restaurants by food_type.
Calculates delivery time using estimate_delivery_time (prep time + travel time based on distance).
Returns restaurants with delivery time ≤ user-specified maximum, sorted by delivery time.

Rider Assignment (MatchingService.find_nearest_rider, Order.assign_rider):
Finds available riders (is_available = True).
Selects the rider closest to the restaurant’s location using calculate_distance.
Marks the rider as unavailable and updates the order status.

Order Placement (OrderService.place_order):
Validates user, restaurant, and menu items.
Calculates total price and formats items.
Places the order and attempts rider assignment.

3.4. CLI Interface

Implemented in app.py using the requests library to call API endpoints.
Provides a menu with 11 options covering all requirements.
Formats responses (e.g., order details, restaurant suggestions) for readability.
Handles errors gracefully with clear messages.

4. How to Handle Scale
   To support millions of users and restaurants, the following enhancements are recommended:
   4.1. Database

Switch to PostgreSQL: SQLite is not suitable for high concurrency. PostgreSQL supports advanced indexing, partitioning, and geospatial queries.
Geospatial Support: Replace text-based location with latitude/longitude and use PostGIS for accurate distance calculations.
Partitioning:
Partition orders by date or region to manage large datasets.
Archive old orders to a separate table or data warehouse.

Indexes:
Add index on restaurants.food_type for faster filtering.
Add index on riders.is_available for quick rider assignment.
Use composite indexes for frequent queries (e.g., orders(user_id, order_time)).

4.2. Caching

Redis:
Cache restaurant menus and popular restaurant suggestions to reduce database load.
Cache order details for quick history retrieval.

Memcached: For temporary storage of rider locations during assignment.

4.3. API Performance

Load Balancing: Use a load balancer (e.g., NGINX) to distribute API requests across multiple Flask instances.
Asynchronous Processing:
Use a message queue (e.g., RabbitMQ, Kafka) for rider assignment and order status updates to reduce API response time.
Process non-critical tasks (e.g., sending notifications) in the background.

Rate Limiting: Implement rate limiting to prevent abuse and ensure fair usage.

4.4. Location Handling

Geospatial Queries: Use PostGIS or a geospatial database to find nearest riders/restaurants efficiently.
External APIs: Integrate Google Maps or OpenStreetMap for accurate distance and ETA calculations.
Location Updates: Store rider locations in a fast, in-memory store (e.g., Redis) for real-time tracking.

4.5. Architecture

Microservices: Split the backend into microservices (e.g., user service, order service, rider service) for independent scaling.
Event-Driven Design: Use events (e.g., via Kafka) to notify services of order placement, rider assignment, etc.
CDN: Use a CDN for static content (e.g., restaurant images, if added).

4.6. Monitoring and Reliability

Monitoring: Use tools like Prometheus and Grafana to monitor API performance and database load.
Logging: Implement centralized logging (e.g., ELK stack) for debugging and auditing.
Redundancy: Deploy the application across multiple regions with failover mechanisms.

5. Conclusion
   The food delivery backend meets all mandatory requirements with a modular, extensible design. The Flask-based API and SQLite database provide a functional prototype, while the CLI interface ensures easy testing. Assumptions like text-based locations and mock distances simplify development but are addressed with production-ready scalability recommendations. The low-level design emphasizes efficiency with indexes and clear separation of concerns. For production, adopting PostgreSQL, caching, and geospatial queries will ensure the system handles millions of users and restaurants effectively.
"# polaris_assignment" 
"# polaris_assigmnet" 
