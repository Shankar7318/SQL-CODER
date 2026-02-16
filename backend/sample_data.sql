-- Create Database (run this separately if needed)
-- CREATE DATABASE ecommerce_db;

-- Connect to the database
-- \c ecommerce_db;

-- ============================================
-- 1. USERS TABLE
-- ============================================
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    age INTEGER,
    city VARCHAR(50),
    country VARCHAR(50),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Insert 20 sample users
INSERT INTO users (username, email, first_name, last_name, age, city, country, phone, is_active, created_at, last_login) VALUES
('john_doe', 'john.doe@email.com', 'John', 'Doe', 28, 'New York', 'USA', '+1-212-555-1234', true, '2024-01-15 10:30:00', '2024-02-10 14:25:00'),
('jane_smith', 'jane.smith@email.com', 'Jane', 'Smith', 32, 'Los Angeles', 'USA', '+1-310-555-5678', true, '2024-01-16 09:15:00', '2024-02-09 11:20:00'),
('bob_wilson', 'bob.wilson@email.com', 'Bob', 'Wilson', 45, 'Chicago', 'USA', '+1-312-555-9012', true, '2024-01-17 14:45:00', '2024-02-08 16:30:00'),
('alice_brown', 'alice.b@email.com', 'Alice', 'Brown', 29, 'Houston', 'USA', '+1-713-555-3456', true, '2024-01-18 11:20:00', '2024-02-07 09:45:00'),
('charlie_davis', 'charlie.d@email.com', 'Charlie', 'Davis', 38, 'Phoenix', 'USA', '+1-602-555-7890', false, '2024-01-19 08:30:00', '2024-01-20 10:15:00'),
('diana_prince', 'diana.p@email.com', 'Diana', 'Prince', 27, 'Philadelphia', 'USA', '+1-215-555-2345', true, '2024-01-20 13:40:00', '2024-02-06 12:10:00'),
('edward_norton', 'edward.n@email.com', 'Edward', 'Norton', 41, 'San Antonio', 'USA', '+1-210-555-6789', true, '2024-01-21 10:25:00', '2024-02-05 15:40:00'),
('fiona_green', 'fiona.g@email.com', 'Fiona', 'Green', 33, 'San Diego', 'USA', '+1-619-555-0123', true, '2024-01-22 09:50:00', '2024-02-04 08:55:00'),
('george_harris', 'george.h@email.com', 'George', 'Harris', 52, 'Dallas', 'USA', '+1-214-555-4567', false, '2024-01-23 15:15:00', '2024-01-24 13:20:00'),
('hannah_lee', 'hannah.l@email.com', 'Hannah', 'Lee', 24, 'San Jose', 'USA', '+1-408-555-8901', true, '2024-01-24 12:30:00', '2024-02-03 17:30:00'),
('ian_martin', 'ian.m@email.com', 'Ian', 'Martin', 36, 'Austin', 'USA', '+1-512-555-2345', true, '2024-01-25 08:45:00', '2024-02-02 10:50:00'),
('julia_roberts', 'julia.r@email.com', 'Julia', 'Roberts', 42, 'Jacksonville', 'USA', '+1-904-555-6789', true, '2024-01-26 14:20:00', '2024-02-01 09:15:00'),
('kevin_bacon', 'kevin.b@email.com', 'Kevin', 'Bacon', 48, 'Fort Worth', 'USA', '+1-817-555-0123', true, '2024-01-27 11:10:00', '2024-01-31 14:40:00'),
('lisa_kudrow', 'lisa.k@email.com', 'Lisa', 'Kudrow', 39, 'Columbus', 'USA', '+1-614-555-4567', true, '2024-01-28 10:05:00', '2024-01-30 16:25:00'),
('mike_jordan', 'mike.j@email.com', 'Mike', 'Jordan', 35, 'Charlotte', 'USA', '+1-704-555-8901', true, '2024-01-29 13:35:00', '2024-01-29 19:50:00'),
('nina_dobrev', 'nina.d@email.com', 'Nina', 'Dobrev', 31, 'San Francisco', 'USA', '+1-415-555-2345', true, '2024-01-30 09:55:00', '2024-02-08 11:30:00'),
('oscar_isaac', 'oscar.i@email.com', 'Oscar', 'Isaac', 44, 'Indianapolis', 'USA', '+1-317-555-6789', false, '2024-01-31 16:40:00', '2024-02-01 08:20:00'),
('paula_patton', 'paula.p@email.com', 'Paula', 'Patton', 37, 'Seattle', 'USA', '+1-206-555-0123', true, '2024-02-01 12:15:00', '2024-02-09 13:45:00'),
('quentin_tarantino', 'quentin.t@email.com', 'Quentin', 'Tarantino', 51, 'Denver', 'USA', '+1-303-555-4567', true, '2024-02-02 08:20:00', '2024-02-07 10:35:00'),
('rachel_mcadams', 'rachel.m@email.com', 'Rachel', 'McAdams', 34, 'Boston', 'USA', '+1-617-555-8901', true, '2024-02-03 14:50:00', '2024-02-06 15:20:00');

-- ============================================
-- 2. PRODUCTS TABLE
-- ============================================
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    price DECIMAL(10, 2),
    cost DECIMAL(10, 2),
    stock_quantity INTEGER DEFAULT 0,
    supplier VARCHAR(100),
    rating DECIMAL(3, 2) DEFAULT 0,
    is_available BOOLEAN DEFAULT true,
    added_date DATE DEFAULT CURRENT_DATE
);

-- Insert 20 sample products
INSERT INTO products (product_name, description, category, price, cost, stock_quantity, supplier, rating, is_available, added_date) VALUES
('Laptop Pro 15"', 'High-performance laptop with 16GB RAM, 512GB SSD', 'Electronics', 1499.99, 1100.00, 25, 'TechSupply Inc.', 4.7, true, '2024-01-15'),
('Wireless Mouse', 'Ergonomic wireless mouse with USB receiver', 'Accessories', 29.99, 15.00, 150, 'GadgetWorld', 4.5, true, '2024-01-16'),
('Mechanical Keyboard', 'RGB mechanical keyboard with blue switches', 'Accessories', 89.99, 45.00, 75, 'KeyMaster', 4.8, true, '2024-01-17'),
('4K Monitor 27"', '27-inch 4K UHD monitor for professionals', 'Electronics', 399.99, 280.00, 30, 'DisplayTech', 4.6, true, '2024-01-18'),
('USB-C Hub', '7-in-1 USB-C hub with HDMI and card reader', 'Accessories', 49.99, 25.00, 200, 'ConnectPlus', 4.4, true, '2024-01-19'),
('External SSD 1TB', 'Portable SSD with USB 3.2 Gen 2', 'Storage', 129.99, 80.00, 45, 'StorageMax', 4.9, true, '2024-01-20'),
('Webcam HD', '1080p webcam with microphone', 'Electronics', 79.99, 40.00, 60, 'CamTech', 4.3, true, '2024-01-21'),
('Headphones Noise-Cancelling', 'Wireless noise-cancelling headphones', 'Audio', 249.99, 150.00, 35, 'SoundWave', 4.8, true, '2024-01-22'),
('Smartphone 12', 'Latest smartphone with 128GB storage', 'Electronics', 799.99, 600.00, 20, 'MobileTech', 4.7, true, '2024-01-23'),
('Tablet 10"', '10-inch tablet for entertainment', 'Electronics', 329.99, 220.00, 18, 'TabWorld', 4.5, true, '2024-01-24'),
('Printer Wireless', 'All-in-one wireless printer', 'Office', 149.99, 90.00, 12, 'PrintMaster', 4.2, true, '2024-01-25'),
('Desk Lamp LED', 'Adjustable LED desk lamp with USB port', 'Furniture', 39.99, 20.00, 85, 'LightUp', 4.6, true, '2024-01-26'),
('Office Chair', 'Ergonomic office chair with lumbar support', 'Furniture', 299.99, 180.00, 10, 'ComfortSeating', 4.8, true, '2024-01-27'),
('Monitor Stand', 'Adjustable monitor stand/riser', 'Accessories', 34.99, 15.00, 120, 'DeskOrg', 4.5, true, '2024-01-28'),
('Laptop Backpack', 'Water-resistant laptop backpack', 'Bags', 59.99, 30.00, 95, 'BagWorld', 4.7, true, '2024-01-29'),
('Wireless Earbuds', 'True wireless earbuds with charging case', 'Audio', 129.99, 70.00, 55, 'SoundWave', 4.6, true, '2024-01-30'),
('Graphics Tablet', 'Drawing tablet for digital artists', 'Electronics', 199.99, 120.00, 22, 'CreativeTech', 4.8, true, '2024-01-31'),
('Portable Charger', '20000mAh power bank', 'Accessories', 49.99, 25.00, 110, 'PowerUp', 4.5, true, '2024-02-01'),
('Smart Watch', 'Fitness tracker with heart rate monitor', 'Wearables', 199.99, 120.00, 40, 'WearableTech', 4.4, true, '2024-02-02'),
('Gaming Mouse', 'High-DPI gaming mouse with RGB', 'Gaming', 59.99, 30.00, 65, 'GameGear', 4.9, true, '2024-02-03');

-- ============================================
-- 3. ORDERS TABLE
-- ============================================
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(30),
    shipping_address TEXT,
    shipping_city VARCHAR(50),
    shipping_country VARCHAR(50)
);

-- Insert 30 sample orders
INSERT INTO orders (user_id, order_date, total_amount, status, payment_method, shipping_address, shipping_city, shipping_country) VALUES
(1, '2024-01-20 10:30:00', 1529.98, 'delivered', 'credit_card', '123 Main St, Apt 4B', 'New York', 'USA'),
(2, '2024-01-21 14:45:00', 89.99, 'delivered', 'paypal', '456 Oak Ave', 'Los Angeles', 'USA'),
(3, '2024-01-22 09:15:00', 449.98, 'delivered', 'credit_card', '789 Pine Rd', 'Chicago', 'USA'),
(4, '2024-01-23 16:20:00', 79.99, 'shipped', 'debit_card', '321 Elm St', 'Houston', 'USA'),
(5, '2024-01-24 11:10:00', 249.99, 'cancelled', 'credit_card', '654 Maple Dr', 'Phoenix', 'USA'),
(6, '2024-01-25 13:40:00', 129.99, 'delivered', 'paypal', '987 Cedar Ln', 'Philadelphia', 'USA'),
(7, '2024-01-26 08:30:00', 379.98, 'delivered', 'credit_card', '147 Birch Ave', 'San Antonio', 'USA'),
(8, '2024-01-27 15:55:00', 59.99, 'shipped', 'debit_card', '258 Spruce St', 'San Diego', 'USA'),
(9, '2024-01-28 12:25:00', 299.99, 'pending', 'credit_card', '369 Willow Way', 'Dallas', 'USA'),
(10, '2024-01-29 10:15:00', 169.98, 'delivered', 'paypal', '741 Ash Blvd', 'San Jose', 'USA'),
(11, '2024-01-30 09:45:00', 799.99, 'delivered', 'credit_card', '852 Poplar Ave', 'Austin', 'USA'),
(12, '2024-01-31 14:10:00', 129.99, 'shipped', 'debit_card', '963 Hickory Ln', 'Jacksonville', 'USA'),
(13, '2024-02-01 11:35:00', 59.99, 'delivered', 'credit_card', '159 Beech St', 'Fort Worth', 'USA'),
(14, '2024-02-02 13:50:00', 329.99, 'delivered', 'paypal', '753 Sycamore Dr', 'Columbus', 'USA'),
(15, '2024-02-03 08:20:00', 149.99, 'pending', 'credit_card', '951 Magnolia Ave', 'Charlotte', 'USA'),
(16, '2024-02-04 16:40:00', 89.98, 'shipped', 'debit_card', '357 Dogwood St', 'San Francisco', 'USA'),
(17, '2024-02-05 10:05:00', 44.98, 'cancelled', 'credit_card', '654 Redwood Rd', 'Indianapolis', 'USA'),
(18, '2024-02-06 14:30:00', 199.99, 'delivered', 'paypal', '852 Sequoia Ave', 'Seattle', 'USA'),
(19, '2024-02-07 09:55:00', 399.99, 'delivered', 'credit_card', '456 Cottonwood Ln', 'Denver', 'USA'),
(20, '2024-02-08 12:15:00', 89.99, 'shipped', 'debit_card', '789 Juniper St', 'Boston', 'USA'),
(1, '2024-02-09 15:30:00', 279.98, 'pending', 'credit_card', '123 Main St, Apt 4B', 'New York', 'USA'),
(2, '2024-02-10 11:25:00', 129.99, 'processing', 'paypal', '456 Oak Ave', 'Los Angeles', 'USA'),
(3, '2024-02-11 10:40:00', 49.99, 'processing', 'credit_card', '789 Pine Rd', 'Chicago', 'USA'),
(4, '2024-02-12 13:15:00', 249.99, 'confirmed', 'debit_card', '321 Elm St', 'Houston', 'USA'),
(5, '2024-02-13 09:50:00', 79.99, 'confirmed', 'credit_card', '654 Maple Dr', 'Phoenix', 'USA');

-- ============================================
-- 4. ORDER_ITEMS TABLE (for order details)
-- ============================================
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER,
    unit_price DECIMAL(10, 2),
    discount DECIMAL(5, 2) DEFAULT 0
);

-- Insert order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount) VALUES
(1, 1, 1, 1499.99, 0),
(1, 2, 1, 29.99, 0),
(2, 3, 1, 89.99, 0),
(3, 4, 1, 399.99, 50.00),
(3, 5, 1, 49.99, 0),
(4, 6, 1, 79.99, 0),
(5, 7, 1, 249.99, 0),
(6, 8, 1, 129.99, 0),
(7, 9, 1, 329.99, 50.00),
(7, 10, 1, 49.99, 0),
(8, 11, 1, 59.99, 0),
(9, 12, 1, 299.99, 0),
(10, 13, 1, 129.99, 0),
(10, 14, 1, 39.99, 0),
(11, 15, 1, 799.99, 0),
(12, 16, 1, 129.99, 0),
(13, 17, 1, 59.99, 0),
(14, 18, 1, 329.99, 0),
(15, 19, 1, 149.99, 0),
(16, 20, 1, 59.99, 0),
(16, 2, 1, 29.99, 0),
(17, 3, 1, 44.98, 0),
(18, 4, 1, 199.99, 0),
(19, 5, 1, 399.99, 0),
(20, 6, 1, 89.99, 0),
(21, 7, 1, 249.99, 0),
(21, 8, 1, 29.99, 0),
(22, 9, 1, 129.99, 0),
(23, 10, 1, 49.99, 0),
(24, 11, 1, 249.99, 0),
(25, 12, 1, 79.99, 0);

-- ============================================
-- 5. PRODUCT_REVIEWS TABLE
-- ============================================
CREATE TABLE product_reviews (
    review_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    user_id INTEGER REFERENCES users(user_id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified_purchase BOOLEAN DEFAULT false
);

-- Insert sample reviews
INSERT INTO product_reviews (product_id, user_id, rating, review_text, review_date, is_verified_purchase) VALUES
(1, 1, 5, 'Excellent laptop, very fast and great battery life!', '2024-01-25 14:30:00', true),
(1, 3, 4, 'Good performance but a bit expensive', '2024-01-28 09:15:00', true),
(2, 2, 5, 'Perfect mouse, comfortable to use', '2024-01-26 11:20:00', true),
(2, 5, 4, 'Works well, battery lasts long', '2024-01-29 16:40:00', true),
(3, 4, 5, 'Awesome keyboard, love the RGB', '2024-01-27 13:10:00', true),
(3, 6, 5, 'Best mechanical keyboard I''ve used', '2024-01-30 10:25:00', true),
(4, 7, 4, 'Great monitor, colors are vibrant', '2024-01-31 15:45:00', true),
(4, 8, 5, 'Perfect for work and gaming', '2024-02-02 12:30:00', true),
(5, 9, 3, 'Good but gets a bit warm', '2024-02-03 09:50:00', true),
(6, 10, 5, 'Fast SSD, great for gaming', '2024-02-04 14:15:00', true);

-- ============================================
-- 6. CATEGORY STATS VIEW (for analytics)
-- ============================================
CREATE VIEW category_sales AS
SELECT 
    p.category,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(oi.quantity) as total_items_sold,
    SUM(oi.quantity * oi.unit_price - oi.discount) as total_revenue,
    AVG(p.rating) as avg_rating
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'delivered'
GROUP BY p.category;

-- ============================================
-- Useful Queries for Testing
-- ============================================

-- 1. Get all users from a specific city
-- SELECT * FROM users WHERE city = 'New York';

-- 2. Get total revenue by category
-- SELECT * FROM category_sales ORDER BY total_revenue DESC;

-- 3. Get top 5 products by sales
-- SELECT p.product_name, SUM(oi.quantity) as units_sold, SUM(oi.quantity * oi.unit_price) as revenue
-- FROM products p
-- JOIN order_items oi ON p.product_id = oi.product_id
-- GROUP BY p.product_id, p.product_name
-- ORDER BY revenue DESC
-- LIMIT 5;

-- 4. Get users who haven't placed any orders
-- SELECT u.* FROM users u
-- LEFT JOIN orders o ON u.user_id = o.user_id
-- WHERE o.order_id IS NULL;

-- 5. Get monthly sales trend
-- SELECT 
--     DATE_TRUNC('month', order_date) as month,
--     COUNT(*) as orders_count,
--     SUM(total_amount) as total_sales
-- FROM orders
-- WHERE status = 'delivered'
-- GROUP BY DATE_TRUNC('month', order_date)
-- ORDER BY month;

-- 6. Get average order value by city
-- SELECT 
--     u.city,
--     COUNT(DISTINCT o.order_id) as orders,
--     AVG(o.total_amount) as avg_order_value
-- FROM users u
-- JOIN orders o ON u.user_id = o.user_id
-- WHERE o.status = 'delivered'
-- GROUP BY u.city
-- HAVING COUNT(DISTINCT o.order_id) > 1;

-- 7. Get product recommendations based on ratings
-- SELECT 
--     product_name,
--     category,
--     price,
--     rating
-- FROM products
-- WHERE rating >= 4.5 AND is_available = true
-- ORDER BY rating DESC, price ASC;

-- 8. Get inventory status
-- SELECT 
--     category,
--     COUNT(*) as products,
--     SUM(stock_quantity) as total_stock,
--     AVG(stock_quantity) as avg_stock_per_product
-- FROM products
-- WHERE is_available = true
-- GROUP BY category;