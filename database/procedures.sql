USE brovault_db;
DELIMITER //
CREATE PROCEDURE GetMonthlySales() BEGIN SELECT DATE_FORMAT(created,'%Y-%m') sales_month,COUNT(*) orders_count,SUM(total) revenue FROM orders WHERE status<>'Cancelled' GROUP BY DATE_FORMAT(created,'%Y-%m') ORDER BY sales_month; END//
CREATE PROCEDURE GetLowStockProducts(IN threshold INT) BEGIN SELECT id,name,stock FROM products WHERE active=1 AND stock<threshold ORDER BY stock; END//
CREATE PROCEDURE UpdateOrderStatus(IN p_order_id BIGINT,IN p_status VARCHAR(30)) BEGIN UPDATE orders SET status=p_status WHERE id=p_order_id; INSERT INTO status_history(order_id,status) VALUES(p_order_id,p_status); END//
DELIMITER ;
