USE brovault_db;
DELIMITER //
CREATE FUNCTION CalculateDiscountedTotal(subtotal DECIMAL(10,2),discount_percent INT) RETURNS DECIMAL(10,2) DETERMINISTIC BEGIN RETURN GREATEST(0,subtotal-(subtotal*discount_percent/100)); END//
DELIMITER ;
