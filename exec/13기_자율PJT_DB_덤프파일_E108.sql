-- MySQL dump 10.13  Distrib 8.0.33, for Win64 (x86_64)
--
-- Host: buriburi.monster    Database: dev
-- ------------------------------------------------------
-- Server version	8.4.6

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `media`
--

DROP TABLE IF EXISTS `media`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `media` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `mime_type` varchar(30) DEFAULT NULL,
  `owner_id` bigint NOT NULL,
  `s3key_or_url` varchar(255) NOT NULL,
  `seq_no` int NOT NULL,
  `type` enum('DEFAULT','ROBOT_VIDEO','ROBOT_VIDEO_THUMBNAIL') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_media_owner_seq` (`type`,`owner_id`,`seq_no`),
  KEY `idx_media_type_owner` (`type`,`owner_id`),
  KEY `idx_media_owner` (`owner_id`)
) ENGINE=InnoDB AUTO_INCREMENT=444 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `member`
--

DROP TABLE IF EXISTS `member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `nickname` varchar(10) NOT NULL,
  `role` enum('ADMIN','USER') NOT NULL,
  `uuid` varchar(60) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `member_social`
--

DROP TABLE IF EXISTS `member_social`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member_social` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `provider_id` varchar(255) NOT NULL,
  `provider_name` enum('GOOGLE','KAKAO','NAVER') NOT NULL,
  `member_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_msocial_email` (`email`),
  UNIQUE KEY `uk_msocial_provider` (`provider_name`,`provider_id`),
  KEY `idx_msocial_member` (`member_id`),
  KEY `idx_msocial_pname` (`provider_name`),
  CONSTRAINT `FK_member_social_member` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `robot`
--

DROP TABLE IF EXISTS `robot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `robot` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `status` enum('ATE_ALL','GOOD_MORNING','GOOD_NIGHT','HEART','HI','HUG','HUNGRY','IDLE','PAPER','ROCK','SCISSORS','SET_JOINT','UNKNOWN','WARMUP') NOT NULL,
  `code` varchar(10) NOT NULL,
  `title` varchar(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'dev'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-20  0:01:43
