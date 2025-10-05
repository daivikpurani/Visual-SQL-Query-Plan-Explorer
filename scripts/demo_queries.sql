-- Demo queries for Visual SQL Plan Explorer
-- These queries are designed to produce different types of query plans
-- to demonstrate various optimization scenarios

-- Query 1: Sequential scan with filter (should suggest index)
-- This query will perform a sequential scan on customers table
-- Expected suggestion: CREATE INDEX ON customers(city)
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM customers 
WHERE city = 'New York' 
AND status = 'active';

-- Query 2: Join without proper indexes (should suggest FK index)
-- This query joins customers and orders
-- Expected suggestion: CREATE INDEX ON orders(customer_id) if not exists
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT c.name, c.email, o.order_date, o.total_amount
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE c.city = 'Los Angeles'
AND o.order_date >= '2024-01-01';

-- Query 3: Complex query with multiple filters
-- This query has multiple equality conditions
-- Expected suggestion: Composite index on (category, price)
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT p.name, p.price, p.stock_quantity
FROM products p
WHERE p.category = 'Electronics'
AND p.price > 500
AND p.stock_quantity > 50;

-- Query 4: Range query with sort
-- This query uses range conditions and ordering
-- Expected suggestion: Index on order_date for range queries
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT o.id, o.customer_id, o.total_amount, o.order_date
FROM orders o
WHERE o.order_date BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY o.order_date DESC
LIMIT 100;

-- Query 5: Aggregation with grouping
-- This query groups and aggregates data
-- Expected suggestion: Index on grouping columns
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT c.city, c.state, COUNT(*) as customer_count, AVG(o.total_amount) as avg_order
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE c.status = 'active'
GROUP BY c.city, c.state
HAVING COUNT(*) > 1000
ORDER BY customer_count DESC;

-- Query 6: Subquery with EXISTS
-- This query uses EXISTS subquery
-- Expected suggestion: Index on foreign key relationships
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT c.name, c.email
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.customer_id = c.id 
    AND o.total_amount > 1000
    AND o.status = 'completed'
);

-- Query 7: Text search with LIKE
-- This query uses pattern matching
-- Expected suggestion: Text pattern index for LIKE queries
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT p.name, p.category, p.price
FROM products p
WHERE p.name LIKE 'iPhone%'
OR p.name LIKE 'Samsung%'
ORDER BY p.price DESC;

-- Query 8: Complex join with multiple tables
-- This query joins multiple tables
-- Expected suggestion: Multiple indexes for join optimization
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT 
    c.name as customer_name,
    c.city,
    o.order_date,
    o.total_amount,
    li.product_name,
    li.quantity,
    li.unit_price
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN line_items li ON o.id = li.order_id
WHERE c.city IN ('New York', 'Los Angeles', 'Chicago')
AND o.order_date >= '2024-06-01'
AND o.status = 'completed'
ORDER BY o.total_amount DESC
LIMIT 50;

-- Query 9: Window function with ordering
-- This query uses window functions
-- Expected suggestion: Index to support ORDER BY in window function
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT 
    c.name,
    c.city,
    o.order_date,
    o.total_amount,
    ROW_NUMBER() OVER (PARTITION BY c.city ORDER BY o.total_amount DESC) as city_rank
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE c.status = 'active'
ORDER BY c.city, o.total_amount DESC;

-- Query 10: Union query
-- This query combines results from multiple queries
-- Expected suggestion: Indexes on filter conditions
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT name, email, city, 'customer' as type FROM customers WHERE city = 'New York'
UNION ALL
SELECT name, email, city, 'customer' as type FROM customers WHERE city = 'Los Angeles'
ORDER BY name;
