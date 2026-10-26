USE brovault_db;
DELIMITER //
CREATE TRIGGER trg_order_status_history AFTER UPDATE ON orders FOR EACH ROW BEGIN IF OLD.status<>NEW.status THEN INSERT INTO status_history(order_id,status) VALUES(NEW.id,NEW.status); END IF; END//
DELIMITER ;
-- Application records inventory movements during checkout to avoid double deductions.
