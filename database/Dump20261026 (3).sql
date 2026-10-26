CREATE DATABASE  IF NOT EXISTS `brovault_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `brovault_db`;
-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: brovault_db
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `cart_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `recipient` varchar(100) DEFAULT '',
  `message` varchar(400) DEFAULT '',
  `wrap` tinyint DEFAULT '0',
  `card` tinyint DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `cart_id` (`cart_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `cart_items_ibfk_1` FOREIGN KEY (`cart_id`) REFERENCES `carts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cart_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `cart_items_chk_1` CHECK ((`quantity` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `carts`
--

DROP TABLE IF EXISTS `carts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `carts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `carts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carts`
--

LOCK TABLES `carts` WRITE;
/*!40000 ALTER TABLE `carts` DISABLE KEYS */;
INSERT INTO `carts` VALUES (1,2);
/*!40000 ALTER TABLE `carts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` varchar(500) DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Watches','Premium watches for men'),(2,'Wallets & Card Holders','Everyday leather essentials'),(3,'Perfumes & Fragrances','Signature fragrances for him'),(4,'Sunglasses','Modern eyewear'),(5,'Bracelets & Rings','Stylish accessories'),(6,'Keychains & Accessories','Small everyday gifts'),(7,'Grooming Accessories','Grooming essentials'),(8,'Personalized Gifts','Custom gifts for him'),(9,'Gift Combos & Boxes','Curated gift sets'),(10,'Birthday & Occasion Gifts','Gifts for special occasions');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coupons`
--

DROP TABLE IF EXISTS `coupons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coupons` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(40) NOT NULL,
  `discount` int NOT NULL DEFAULT '10',
  `active` tinyint DEFAULT '1',
  `expiry` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  CONSTRAINT `coupons_chk_1` CHECK ((`discount` between 1 and 80))
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coupons`
--

LOCK TABLES `coupons` WRITE;
/*!40000 ALTER TABLE `coupons` DISABLE KEYS */;
INSERT INTO `coupons` VALUES (1,'VAULT10',10,1,NULL);
/*!40000 ALTER TABLE `coupons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_log`
--

DROP TABLE IF EXISTS `inventory_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `product_id` bigint DEFAULT NULL,
  `delta` int NOT NULL,
  `note` varchar(255) DEFAULT NULL,
  `created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `inventory_log_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_log`
--

LOCK TABLES `inventory_log` WRITE;
/*!40000 ALTER TABLE `inventory_log` DISABLE KEYS */;
INSERT INTO `inventory_log` VALUES (1,20,-1,'Order #1','2026-10-25 12:10:32'),(2,17,-1,'Order #2','2026-10-25 12:56:38'),(3,17,-1,'Order #3','2026-10-25 12:57:03'),(4,20,-1,'Order #4','2026-10-25 13:37:37'),(5,19,-1,'Order #5','2026-10-25 13:37:55'),(6,5,-1,'Order #6','2026-10-25 13:42:56'),(7,20,-1,'Order #7','2026-10-25 13:43:15'),(8,19,-1,'Order #8','2026-10-25 13:46:47'),(9,5,-1,'Order #9','2026-10-25 13:50:26'),(10,19,-1,'Order #10','2026-10-25 14:01:42'),(11,20,-1,'Order #11','2026-10-25 14:02:29'),(12,19,-1,'Order #12','2026-10-25 14:05:48'),(13,17,-1,'Order #13','2026-10-26 07:29:30'),(14,19,-1,'Order #14','2026-10-26 07:59:34'),(15,10,-1,'Order #14','2026-10-26 07:59:34');
/*!40000 ALTER TABLE `inventory_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_id` bigint NOT NULL,
  `product_id` bigint DEFAULT NULL,
  `product_name` varchar(180) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `quantity` int NOT NULL,
  `custom` varchar(700) DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_items_chk_1` CHECK ((`quantity` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,1,20,'Minimal Silver Watch',3199.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(2,2,17,'Brown Leather Wallet',799.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(3,3,17,'Brown Leather Wallet',799.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(4,4,20,'Minimal Silver Watch',3199.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(5,5,19,'Classic Black Watch',2499.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(6,6,5,'Gentleman Gift Box',2499.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(7,7,20,'Minimal Silver Watch',3199.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(8,8,19,'Classic Black Watch',2499.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(9,9,5,'Gentleman Gift Box',2499.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(10,10,19,'Classic Black Watch',2499.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(11,11,20,'Minimal Silver Watch',3199.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(12,12,19,'Classic Black Watch',2499.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(13,13,17,'Brown Leather Wallet',799.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(14,14,19,'Classic Black Watch',2499.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No'),(15,14,10,'Oud Signature Perfume',1899.00,1,'Recipient: ; Message: ; Wrapping: No; Card: No');
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `total` decimal(10,2) NOT NULL,
  `status` enum('Pending','Confirmed','Processing','Shipped','Delivered','Cancelled') DEFAULT 'Pending',
  `payment` varchar(50) DEFAULT NULL,
  `checkout_token` varchar(64) DEFAULT NULL,
  `address` varchar(800) NOT NULL,
  `coupon` varchar(40) DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `checkout_token` (`checkout_token`),
  KEY `idx_orders_date` (`created`),
  KEY `idx_orders_status` (`status`),
  KEY `idx_orders_user` (`user_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,2,'2026-10-25 12:10:32',3199.00,'Pending','Scan QR & Pay','pCDzOwExv0dCsvCBC_0CpS-SuCvBG2rP','Aniket Sharma | 08219830441 | North Campus | Kharar | Chandigarh | 140413.',''),(2,2,'2026-10-25 12:56:38',878.00,'Pending','Cash on Delivery','blOnDMrI2EhenUh237cB993s5y9F3dvL','Aniket Sharma | 08219830441 | North Campus | Kharar | Chandigarh | 140413.',''),(3,2,'2026-10-25 12:57:03',878.00,'Pending','Scan QR & Pay','hA7yPOYjkXEJGmMiKe9NmSpxicnKnBYO','Aniket Sharma | 08219830441 | North Campus | Kharar | Chandigarh | 140413.',''),(4,2,'2026-10-25 13:37:37',3199.00,'Pending','Cash on Delivery','7rrKOarzwrc_V0tlnWBISA2f0OdsUV4b','Aniket Sharma | 08219830441 | 177113 | Bassi | Himachal Pradesh | 140413.',''),(5,2,'2026-10-25 13:37:55',2499.00,'Pending','Scan QR & Pay','I3_E6CW8iymgk_yjXAWCd7cwK9kwGSSO','Aniket Sharma | 08219830441 | 177113 | Bassi | Himachal Pradesh | 140413.',''),(6,2,'2026-10-25 13:42:56',2499.00,'Pending','UPI Payment Submitted (unverified)','TG1m6wu5HMquvYjxNRi90HzLJo4U3tXY','Aniket Sharma | 08219830441 | 177113 | Bassi | Himachal Pradesh | 140413.',''),(7,2,'2026-10-25 13:43:15',3199.00,'Pending','Scan QR & Pay','hxwUYNdQhqt3oCG6W6UFWa3IZ4w_5FN3','Aniket Sharma | 08219830441 | North Campus | Kharar | Chandigarh | 140413.',''),(8,2,'2026-10-25 13:46:47',2499.00,'Pending','Scan QR & Pay','kU9DUiwSg26PBwr5wKpeqWCrFMti4UdK','Aniket Sharma | 08219830441 | 177113 | Bassi | Himachal Pradesh | 140413.',''),(9,2,'2026-10-25 13:50:26',2499.00,'Pending','Scan QR & Pay','Dl3I_7YZwKEY1er1N4J3pXHvS7rpWmaB','Aniket Sharma | 08219830441 | North Campus | Kharar | Chandigarh | 140413.',''),(10,2,'2026-10-25 14:01:42',2499.00,'Pending','Scan QR & Pay','GIq1qhaDpT5twcdEUCXLJ7JCRaOby5NE','Aniket Sharma | 08219830441 | 177113 | Bassi | Himachal Pradesh | 140413.',''),(11,2,'2026-10-25 14:02:29',3199.00,'Pending','Scan QR & Pay','Z7zY_lBEz3lodmYgmlE_GuUiqHDzwHb-','Aniket Sharma | 08219830441 | 177113 | Bassi | Himachal Pradesh | 140413.',''),(12,2,'2026-10-25 14:05:48',2499.00,'Pending','Scan QR & Pay','gsZ2N37mCJxGZ7IGGUFliNKqPSe4ghyd','Aniket Sharma | 08219830441 | North Campus | Kharar | Chandigarh | 140413.',''),(13,2,'2026-10-26 07:29:30',878.00,'Pending','Scan QR & Pay','_scxxGFCSB8E-Axum07Asgmz4pYZ98fU','Aniket Sharma | 08219830441 | North Campus | Kharar | Chandigarh | 140413.',''),(14,2,'2026-10-26 07:59:34',4398.00,'Pending','Scan QR & Pay','W-oYuRLP8J4zXhVdC1wFFPXbQFg5BKlv','Aniket Sharma | +918219830441 | 177113 | Bassi | Himachal Pradesh | 140413.','');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(180) NOT NULL,
  `description` text,
  `category_id` bigint DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `original_price` decimal(10,2) DEFAULT NULL,
  `stock` int NOT NULL DEFAULT '0',
  `image` varchar(255) DEFAULT NULL,
  `featured` tinyint DEFAULT '0',
  `active` tinyint DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_products_category` (`category_id`),
  KEY `idx_products_active` (`active`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `products_chk_1` CHECK ((`price` >= 0)),
  CONSTRAINT `products_chk_2` CHECK ((`stock` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'Birthday Surprise Box','A premium birthday gift-box concept.',10,1799.00,2399.00,10,'uploads/birthday_box.png',1,1,'2026-10-25 11:42:25'),(2,'Steel Link Bracelet','Polished steel bracelet for men.',5,599.00,899.00,22,'uploads/steel_bracelet.png',0,1,'2026-10-25 11:42:25'),(3,'Matte Black Ring','Minimal black ring with a modern finish.',5,399.00,599.00,20,'uploads/black_ring.png',0,1,'2026-10-25 11:42:25'),(4,'Premium Cuff Bracelet','Understated bracelet for formal looks.',5,749.00,999.00,16,'uploads/cuff_bracelet.png',0,1,'2026-10-25 11:42:25'),(5,'Gentleman Gift Box','Curated accessories gift-box concept.',9,2499.00,3299.00,6,'uploads/gentleman_box.png',1,1,'2026-10-25 11:42:25'),(6,'Watch and Wallet Combo','Coordinated watch and wallet gift set.',9,2999.00,3999.00,6,'uploads/watch_wallet_combo.png',1,1,'2026-10-25 11:42:25'),(7,'Everyday Essentials Box','A curated small-accessories gift set.',9,1399.00,1899.00,12,'uploads/essentials_box.png',0,1,'2026-10-25 11:42:25'),(8,'Executive Grooming Kit','A compact grooming essentials kit.',7,1299.00,1799.00,12,'uploads/grooming_kit.png',1,1,'2026-10-25 11:42:25'),(9,'Metal Initial Keychain','Sleek keychain for everyday carry.',6,249.00,399.00,35,'uploads/metal_keychain.png',0,1,'2026-10-25 11:42:25'),(10,'Oud Signature Perfume','Warm woody fragrance for special occasions.',3,1899.00,2499.00,9,'uploads/oud_perfume.png',1,1,'2026-10-25 11:42:25'),(11,'Fresh Citrus Fragrance','Fresh citrus-inspired everyday fragrance.',3,999.00,1499.00,18,'uploads/citrus_perfume.png',0,1,'2026-10-25 11:42:25'),(12,'Travel Fragrance Set','Travel-friendly fragrance gift concept.',3,1499.00,1999.00,9,'uploads/travel_fragrance.png',0,1,'2026-10-25 11:42:25'),(13,'Personalized Name Wallet','Name-personalized wallet gift concept.',8,1099.00,1499.00,10,'uploads/name_wallet.png',1,1,'2026-10-25 11:42:25'),(14,'Engraved Keychain Gift','Personalized keychain gift concept.',8,349.00,499.00,25,'uploads/engraved_keychain.png',0,1,'2026-10-25 11:42:25'),(15,'Matte Black Sunglasses','Modern sunglasses with a bold frame.',4,899.00,1299.00,20,'uploads/black_sunglasses.png',1,1,'2026-10-25 11:42:25'),(16,'Classic Brown Sunglasses','Timeless brown-frame sunglasses.',4,1099.00,1599.00,14,'uploads/brown_sunglasses.png',0,1,'2026-10-25 11:42:25'),(17,'Brown Leather Wallet','Classic brown wallet with card slots.',2,799.00,1199.00,22,'uploads/brown_wallet.png',1,1,'2026-10-25 11:42:25'),(18,'Slim Black Card Holder','Compact card holder for daily use.',2,499.00,799.00,30,'uploads/black_cardholder.png',0,1,'2026-10-25 11:42:25'),(19,'Classic Black Watch','Elegant black dial watch for everyday wear.',1,2499.00,3499.00,10,'uploads/black_watch.png',1,1,'2026-10-25 11:42:25'),(20,'Minimal Silver Watch','Minimal silver-tone wristwatch.',1,3199.00,3999.00,8,'uploads/silver_watch.png',1,1,'2026-10-25 11:42:25');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `status_history`
--

DROP TABLE IF EXISTS `status_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `status_history` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_id` bigint NOT NULL,
  `status` varchar(100) NOT NULL,
  `created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `status_history_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `status_history`
--

LOCK TABLES `status_history` WRITE;
/*!40000 ALTER TABLE `status_history` DISABLE KEYS */;
INSERT INTO `status_history` VALUES (1,1,'Pending','2026-10-25 12:10:32'),(2,2,'Pending','2026-10-25 12:56:38'),(3,3,'Pending','2026-10-25 12:57:03'),(4,4,'Pending','2026-10-25 13:37:37'),(5,5,'Pending','2026-10-25 13:37:55'),(6,6,'Pending','2026-10-25 13:42:56'),(7,6,'UPI payment submitted - verification pending','2026-10-25 13:42:58'),(8,7,'Pending','2026-10-25 13:43:15'),(9,8,'Pending','2026-10-25 13:46:47'),(10,9,'Pending','2026-10-25 13:50:26'),(11,10,'Pending','2026-10-25 14:01:42'),(12,11,'Pending','2026-10-25 14:02:29'),(13,12,'Pending','2026-10-25 14:05:48'),(14,13,'Pending','2026-10-26 07:29:30'),(15,14,'Pending','2026-10-26 07:59:34');
/*!40000 ALTER TABLE `status_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `email` varchar(190) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('customer','admin') NOT NULL DEFAULT 'customer',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'BroVault Admin','admin@brovault.local','scrypt:32768:8:1$hlhjKF5GssALKMO9$666f1f8446d9cac5f52188fbffe514843a5bf84152b41621731f06bb97e0c2b4dd59d2118fcb0cf1af6da4fd0ef0d3b5573c77d41d7ff026fcc92f99bde05542','admin','2026-10-25 11:55:48'),(2,'Sh. Sanjeev Jaswal','testuser1234@example.com','scrypt:32768:8:1$2oXxfqpurShDYGpP$10362f85b35fa0a86b7cd95cb429c8a194d5c35c9f5be4d6a69c73ad6d8a8d0996f2ca2ebe940c3488e7e0fec3c9260235dd48b9294acab40b127a37322a2642','customer','2026-10-25 12:10:16');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishlists`
--

DROP TABLE IF EXISTS `wishlists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wishlists` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_wishlist` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `wishlists_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `wishlists_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishlists`
--

LOCK TABLES `wishlists` WRITE;
/*!40000 ALTER TABLE `wishlists` DISABLE KEYS */;
INSERT INTO `wishlists` VALUES (1,2,20);
/*!40000 ALTER TABLE `wishlists` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-26 13:50:19
