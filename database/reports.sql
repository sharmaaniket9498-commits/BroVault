USE brovault_db;
SELECT DATE_FORMAT(created,'%Y-%m') month,SUM(total) revenue FROM orders WHERE status<>'Cancelled' GROUP BY month ORDER BY month;
SELECT product_name,SUM(quantity) units_sold FROM order_items GROUP BY product_name ORDER BY units_sold DESC;
SELECT u.name,u.email,COUNT(o.id) order_count,SUM(o.total) total_spend FROM users u JOIN orders o ON o.user_id=u.id WHERE u.role='customer' GROUP BY u.id,u.name,u.email HAVING COUNT(o.id)>=1;
SELECT c.name,COALESCE(SUM(oi.price*oi.quantity),0) revenue FROM categories c LEFT JOIN products p ON p.category_id=c.id LEFT JOIN order_items oi ON oi.product_id=p.id GROUP BY c.id,c.name ORDER BY revenue DESC;
SELECT product_name,units_sold,DENSE_RANK() OVER(ORDER BY units_sold DESC) sales_rank FROM (SELECT product_name,SUM(quantity) units_sold FROM order_items GROUP BY product_name) x;
