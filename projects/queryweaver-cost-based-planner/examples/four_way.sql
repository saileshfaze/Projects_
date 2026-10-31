SELECT c.id, p.price FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN regions r ON c.region_id = r.id
JOIN products p ON o.product_id = p.id
WHERE p.price > 50
