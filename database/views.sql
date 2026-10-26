USE brovault_db;
CREATE OR REPLACE VIEW vw_product_inventory AS SELECT p.id,p.name,c.name category,p.price,p.stock,CASE WHEN p.stock=0 THEN 'Out of stock' WHEN p.stock<6 THEN 'Low stock' ELSE 'In stock' END stock_status FROM products p LEFT JOIN categories c ON c.id=p.category_id WHERE p.active=1;
CREATE OR REPLACE VIEW vw_order_summary AS SELECT o.id order_id,o.created,u.name customer,u.email,o.status,o.payment,o.total FROM orders o JOIN users u ON u.id=o.user_id;
CREATE OR REPLACE VIEW vw_monthly_sales AS SELECT DATE_FORMAT(created,'%Y-%m') sales_month,COUNT(*) order_count,SUM(total) revenue FROM orders WHERE status<>'Cancelled' GROUP BY DATE_FORMAT(created,'%Y-%m');
CREATE OR REPLACE VIEW vw_best_selling_products AS SELECT product_name,SUM(quantity) units_sold,SUM(quantity*price) revenue FROM order_items GROUP BY product_name;
