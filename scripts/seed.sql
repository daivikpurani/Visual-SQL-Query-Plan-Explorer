-- Sample database schema and data for Visual SQL Plan Explorer demo
-- This creates realistic tables with skewed data distributions to demonstrate
-- various query plan scenarios

-- Create demo tables
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    city VARCHAR(50),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending',
    shipping_address TEXT
);

CREATE TABLE IF NOT EXISTS line_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER,
    product_name VARCHAR(100),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10,2),
    stock_quantity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data with skewed distributions
-- Customers: More customers in major cities
INSERT INTO customers (name, email, city, state, zip_code, status) VALUES
('John Smith', 'john@example.com', 'New York', 'NY', '10001', 'active'),
('Jane Doe', 'jane@example.com', 'Los Angeles', 'CA', '90210', 'active'),
('Bob Johnson', 'bob@example.com', 'Chicago', 'IL', '60601', 'active'),
('Alice Brown', 'alice@example.com', 'New York', 'NY', '10002', 'active'),
('Charlie Wilson', 'charlie@example.com', 'Houston', 'TX', '77001', 'active'),
('Diana Davis', 'diana@example.com', 'Phoenix', 'AZ', '85001', 'active'),
('Eve Miller', 'eve@example.com', 'Philadelphia', 'PA', '19101', 'active'),
('Frank Garcia', 'frank@example.com', 'San Antonio', 'TX', '78201', 'active'),
('Grace Lee', 'grace@example.com', 'San Diego', 'CA', '92101', 'active'),
('Henry Taylor', 'henry@example.com', 'Dallas', 'TX', '75201', 'active');

-- Generate more customers (200k total)
INSERT INTO customers (name, email, city, state, zip_code, status)
SELECT 
    'Customer ' || generate_series,
    'customer' || generate_series || '@example.com',
    CASE 
        WHEN random() < 0.3 THEN 'New York'
        WHEN random() < 0.5 THEN 'Los Angeles'
        WHEN random() < 0.7 THEN 'Chicago'
        ELSE 'Other City'
    END,
    CASE 
        WHEN random() < 0.3 THEN 'NY'
        WHEN random() < 0.5 THEN 'CA'
        WHEN random() < 0.7 THEN 'IL'
        ELSE 'TX'
    END,
    LPAD(floor(random() * 99999)::text, 5, '0'),
    CASE WHEN random() < 0.9 THEN 'active' ELSE 'inactive' END
FROM generate_series(11, 200000);

-- Products with skewed popularity
INSERT INTO products (name, category, price, stock_quantity) VALUES
('iPhone 15', 'Electronics', 999.99, 100),
('Samsung Galaxy S24', 'Electronics', 899.99, 80),
('MacBook Pro', 'Electronics', 1999.99, 50),
('iPad Air', 'Electronics', 599.99, 75),
('AirPods Pro', 'Electronics', 249.99, 200),
('Nike Air Max', 'Shoes', 129.99, 150),
('Adidas Ultraboost', 'Shoes', 180.99, 120),
('Levi Jeans', 'Clothing', 79.99, 300),
('Nike T-Shirt', 'Clothing', 29.99, 500),
('Generic Product', 'Misc', 9.99, 1000);

-- Generate more products
INSERT INTO products (name, category, price, stock_quantity)
SELECT 
    'Product ' || generate_series,
    CASE 
        WHEN random() < 0.4 THEN 'Electronics'
        WHEN random() < 0.7 THEN 'Clothing'
        WHEN random() < 0.9 THEN 'Shoes'
        ELSE 'Misc'
    END,
    (random() * 1000 + 10)::decimal(10,2),
    floor(random() * 500 + 10)::integer
FROM generate_series(11, 1000);

-- Orders with realistic patterns
INSERT INTO orders (customer_id, order_date, total_amount, status, shipping_address)
SELECT 
    floor(random() * 200000 + 1)::integer,
    CURRENT_TIMESTAMP - (random() * 365 * 24 * 60 * 60)::integer * interval '1 second',
    (random() * 500 + 10)::decimal(10,2),
    CASE 
        WHEN random() < 0.7 THEN 'completed'
        WHEN random() < 0.9 THEN 'pending'
        ELSE 'cancelled'
    END,
    'Address ' || floor(random() * 1000 + 1)::text
FROM generate_series(1, 100000);

-- Line items
INSERT INTO line_items (order_id, product_id, product_name, quantity, unit_price, total_price)
SELECT 
    floor(random() * 100000 + 1)::integer,
    floor(random() * 1000 + 1)::integer,
    'Product ' || floor(random() * 1000 + 1)::text,
    floor(random() * 5 + 1)::integer,
    (random() * 100 + 10)::decimal(10,2),
    (random() * 500 + 10)::decimal(10,2)
FROM generate_series(1, 200000);

-- Create some baseline indexes
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_line_items_order_id ON line_items(order_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- Update table statistics
ANALYZE customers;
ANALYZE orders;
ANALYZE line_items;
ANALYZE products;
