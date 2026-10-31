SELECT c.id, o.id FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.age >= 40
