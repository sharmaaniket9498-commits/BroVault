USE brovault_db;
INSERT IGNORE INTO categories(id,name,description) VALUES
(1,'Watches','Everyday and statement watches'),
(2,'Wallets & Card Holders','Slim wallets and card holders'),
(3,'Perfumes & Fragrances','Signature scents'),
(4,'Sunglasses','Modern eyewear'),
(5,'Bracelets & Rings','Finishing-touch accessories'),
(6,'Keychains & Small Accessories','Useful little extras'),
(7,'Grooming Accessories','Everyday grooming essentials'),
(8,'Personalized Gifts','Made personal for him'),
(9,'Gift Combos & Gift Boxes','Ready-to-gift sets'),
(10,'Birthday & Occasion Gifts','Gifts for memorable days');
INSERT IGNORE INTO coupons(code,discount,active) VALUES('VAULT10',10,1);
-- Products are seeded safely by app.py only when the products table is empty.
