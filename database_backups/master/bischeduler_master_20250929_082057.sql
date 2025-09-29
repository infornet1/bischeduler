/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.4.7-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: bischeduler_master
-- ------------------------------------------------------
-- Server version	11.4.7-MariaDB-0ubuntu0.25.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `tenant_invitations`
--

DROP TABLE IF EXISTS `tenant_invitations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tenant_invitations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `invitation_code` char(36) NOT NULL,
  `institution_name` varchar(255) NOT NULL,
  `institution_type` enum('UNIVERSIDAD','COLEGIO_PUBLICO','COLEGIO_PRIVADO','INSTITUTO','ESCUELA_BASICA','PREESCOLAR') NOT NULL,
  `admin_email` varchar(255) NOT NULL,
  `invited_by_tenant_id` char(36) NOT NULL,
  `invitation_message` text DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `sent_at` datetime NOT NULL,
  `expires_at` datetime NOT NULL,
  `accepted_at` datetime DEFAULT NULL,
  `responded_at` datetime DEFAULT NULL,
  `resulting_tenant_id` char(36) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `invitation_code` (`invitation_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenant_invitations`
--

LOCK TABLES `tenant_invitations` WRITE;
/*!40000 ALTER TABLE `tenant_invitations` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenant_invitations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenant_usage_metrics`
--

DROP TABLE IF EXISTS `tenant_usage_metrics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tenant_usage_metrics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tenant_id` char(36) NOT NULL,
  `metric_date` datetime NOT NULL,
  `metric_type` varchar(50) NOT NULL,
  `active_students` int(11) DEFAULT NULL,
  `active_teachers` int(11) DEFAULT NULL,
  `total_schedules` int(11) DEFAULT NULL,
  `api_requests` int(11) DEFAULT NULL,
  `matricula_exports` int(11) DEFAULT NULL,
  `schedule_conflicts_resolved` int(11) DEFAULT NULL,
  `custom_reports_generated` int(11) DEFAULT NULL,
  `avg_response_time_ms` int(11) DEFAULT NULL,
  `error_count` int(11) DEFAULT NULL,
  `uptime_percentage` int(11) DEFAULT NULL,
  `database_size_mb` int(11) DEFAULT NULL,
  `file_storage_mb` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenant_usage_metrics`
--

LOCK TABLES `tenant_usage_metrics` WRITE;
/*!40000 ALTER TABLE `tenant_usage_metrics` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenant_usage_metrics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenants`
--

DROP TABLE IF EXISTS `tenants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tenants` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tenant_id` char(36) NOT NULL,
  `institution_name` varchar(255) NOT NULL,
  `institution_code` varchar(50) NOT NULL,
  `institution_type` enum('UNIVERSIDAD','COLEGIO_PUBLICO','COLEGIO_PRIVADO','INSTITUTO','ESCUELA_BASICA','PREESCOLAR') NOT NULL,
  `schema_name` varchar(100) NOT NULL,
  `database_url` text NOT NULL,
  `admin_email` varchar(255) NOT NULL,
  `contact_phone` varchar(20) DEFAULT NULL,
  `institution_address` text DEFAULT NULL,
  `website_url` varchar(255) DEFAULT NULL,
  `matricula_code` varchar(20) DEFAULT NULL,
  `state_region` varchar(100) DEFAULT NULL,
  `municipality` varchar(100) DEFAULT NULL,
  `rif_number` varchar(20) DEFAULT NULL,
  `status` enum('PENDING','ACTIVE','SUSPENDED','DEACTIVATED') NOT NULL,
  `max_students` int(11) DEFAULT NULL,
  `max_teachers` int(11) DEFAULT NULL,
  `custom_branding` tinyint(1) DEFAULT NULL,
  `logo_filename` varchar(255) DEFAULT NULL,
  `logo_original_name` varchar(255) DEFAULT NULL,
  `logo_file_size` int(11) DEFAULT NULL,
  `logo_mime_type` varchar(100) DEFAULT NULL,
  `logo_uploaded_at` datetime DEFAULT NULL,
  `logo_uploaded_by` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `activated_at` datetime DEFAULT NULL,
  `last_accessed` datetime DEFAULT NULL,
  `subscription_expires` datetime DEFAULT NULL,
  `configuration_json` text DEFAULT NULL,
  `notes` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tenant_id` (`tenant_id`),
  UNIQUE KEY `institution_code` (`institution_code`),
  UNIQUE KEY `schema_name` (`schema_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenants`
--

LOCK TABLES `tenants` WRITE;
/*!40000 ALTER TABLE `tenants` DISABLE KEYS */;
INSERT INTO `tenants` VALUES
(1,'f316a8e8-c884-47c7-a989-44c85b4cd403','UEIPAB','UEIPAB001','UNIVERSIDAD','ueipab_2025','mysql+pymysql://root:g)8nE>?rq-#v3Ta@localhost/ueipab_2025_data','admin@ueipab.edu.ve',NULL,NULL,'dev.ueipab.edu.ve','UEIPAB001','Miranda','Los Teques',NULL,'ACTIVE',500,50,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-09-27 15:39:39',NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `tenants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_audit_logs`
--

DROP TABLE IF EXISTS `user_audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_audit_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `resource_type` varchar(50) DEFAULT NULL,
  `resource_id` varchar(100) DEFAULT NULL,
  `tenant_id` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `session_id` varchar(255) DEFAULT NULL,
  `old_values` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`old_values`)),
  `new_values` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`new_values`)),
  `created_at` datetime DEFAULT NULL,
  `severity` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_audit_logs`
--

LOCK TABLES `user_audit_logs` WRITE;
/*!40000 ALTER TABLE `user_audit_logs` DISABLE KEYS */;
INSERT INTO `user_audit_logs` VALUES
(1,1,'login_success','authentication',NULL,NULL,'Authentication event: login_success for admin@ueipab.edu.ve','127.0.0.1','curl/8.12.1',NULL,NULL,NULL,'2025-09-26 23:30:38','info'),
(2,1,'login_success','authentication',NULL,NULL,'Authentication event: login_success for admin@ueipab.edu.ve','200.82.130.27','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',NULL,NULL,NULL,'2025-09-26 23:31:27','info'),
(3,1,'login_success','authentication',NULL,NULL,'Authentication event: login_success for admin@ueipab.edu.ve','200.82.130.27','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',NULL,NULL,NULL,'2025-09-27 00:21:07','info'),
(4,1,'login_success','authentication',NULL,NULL,'Authentication event: login_success for admin@ueipab.edu.ve','200.82.130.27','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',NULL,NULL,NULL,'2025-09-27 00:24:35','info'),
(5,1,'login_success','authentication',NULL,NULL,'Authentication event: login_success for admin@ueipab.edu.ve','200.82.130.27','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',NULL,NULL,NULL,'2025-09-27 15:54:00','info'),
(6,1,'login_success','authentication',NULL,NULL,'Authentication event: login_success for admin@ueipab.edu.ve','200.82.130.27','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',NULL,NULL,NULL,'2025-09-27 16:07:05','info');
/*!40000 ALTER TABLE `user_audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_sessions`
--

DROP TABLE IF EXISTS `user_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_sessions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `session_token` varchar(255) NOT NULL,
  `jwt_token_hash` varchar(255) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `device_info` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`device_info`)),
  `location_info` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`location_info`)),
  `created_at` datetime DEFAULT NULL,
  `last_activity` datetime DEFAULT NULL,
  `expires_at` datetime NOT NULL,
  `revoked_at` datetime DEFAULT NULL,
  `revoked_reason` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_suspicious` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_token` (`session_token`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_sessions`
--

LOCK TABLES `user_sessions` WRITE;
/*!40000 ALTER TABLE `user_sessions` DISABLE KEYS */;
INSERT INTO `user_sessions` VALUES
(1,1,'Q6YDPlgmnUAveqCmmQDtJA','77be084f102ba8723b35ec966ea999247b77c5839979d340f184e0949d34b96f','127.0.0.1','curl/8.12.1','{\"method\": \"POST\", \"endpoint\": \"auth.login\"}',NULL,'2025-09-26 23:30:38','2025-09-26 23:30:38','2025-09-27 23:30:38',NULL,NULL,1,0),
(2,1,'gHiHKZ1o7XTamaF5kU37vQ','4fd7bef38beb4918033968acf9989a8de8eabed70ac263f42c6194353fde4b67','200.82.130.27','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0','{\"method\": \"POST\", \"endpoint\": \"auth.login\"}',NULL,'2025-09-26 23:31:27','2025-09-26 23:31:27','2025-09-27 23:31:27',NULL,NULL,1,0),
(3,1,'I6g37mYzLhtyvAJTfA8swQ','1015e33cf7ebeda47e03cb3e9a0adccac3e683125fbb07b7dafb66a956a62147','200.82.130.27','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0','{\"method\": \"POST\", \"endpoint\": \"auth.login\"}',NULL,'2025-09-27 00:21:07','2025-09-27 00:21:07','2025-09-28 00:21:07',NULL,NULL,1,0),
(4,1,'-cv_i5iQkjr2xXcwMpBimw','42ad6e92f84e1fe7ab9d2f3a8fa47b6470cee441e27bc816792d9c70205ceb00','200.82.130.27','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0','{\"method\": \"POST\", \"endpoint\": \"auth.login\"}',NULL,'2025-09-27 00:24:35','2025-09-27 00:24:35','2025-09-28 00:24:35',NULL,NULL,1,0),
(5,1,'YIfT1c8-4yob4BvSxqz-bg','b18ae99346e3234ef2300359a5d7e388e9df2bcc0468d3a0fbce651481f2c544','200.82.130.27','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0','{\"method\": \"POST\", \"endpoint\": \"auth.login\"}',NULL,'2025-09-27 15:54:00','2025-09-27 15:54:00','2025-09-28 15:54:00',NULL,NULL,1,0),
(6,1,'u4hh3_hqgHXaftuvmc9uvg','e6286e2dd57c53d8e4ad4f005c49fd2a8743b471d557389e314ddf1132e6fb9f','200.82.130.27','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0','{\"method\": \"POST\", \"endpoint\": \"auth.login\"}',NULL,'2025-09-27 16:07:05','2025-09-27 16:07:05','2025-09-28 16:07:05',NULL,NULL,1,0),
(7,1,'Bc9plfBgXK6WKR4FOVe2pw','ba2db12e66798213ef0e3f9ff5cd28d6782f8f42f67a56e3ac9e2673563c6a8a','127.0.0.1','curl/8.12.1','{\"method\": \"POST\", \"endpoint\": \"auth.login\"}',NULL,'2025-09-29 12:11:12','2025-09-29 12:11:12','2025-09-30 12:11:12',NULL,NULL,1,NULL),
(8,1,'k2utYgA6VwdS0ZfRqln1rw','4ccaefef320d2a0d4593d8e65b5b57dac52fa1f922f03b86a070f218e62849e0','200.82.130.27','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0','{\"method\": \"POST\", \"endpoint\": \"auth.login\"}',NULL,'2025-09-29 12:11:34','2025-09-29 12:11:34','2025-09-30 12:11:34',NULL,NULL,1,NULL),
(9,1,'HErlYeDF8EPUmc7nrT2IPg','640fcd62222a637c29c085e8e60a4b0538b83d67fb97d9f7eabb355ca70a9394','186.14.93.234','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36','{\"method\": \"POST\", \"endpoint\": \"auth.login\"}',NULL,'2025-09-29 12:13:35','2025-09-29 12:13:35','2025-09-30 12:13:35',NULL,NULL,1,NULL);
/*!40000 ALTER TABLE `user_sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(155) NOT NULL,
  `cedula` varchar(20) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `role` varchar(50) NOT NULL,
  `status` varchar(50) DEFAULT NULL,
  `password_reset_token` varchar(255) DEFAULT NULL,
  `password_reset_expires` datetime DEFAULT NULL,
  `email_verification_token` varchar(255) DEFAULT NULL,
  `email_verified_at` datetime DEFAULT NULL,
  `failed_login_attempts` int(11) DEFAULT NULL,
  `locked_until` datetime DEFAULT NULL,
  `tenant_id` varchar(100) DEFAULT NULL,
  `tenant_permissions` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`tenant_permissions`)),
  `last_login` datetime DEFAULT NULL,
  `last_activity` datetime DEFAULT NULL,
  `current_session_token` varchar(255) DEFAULT NULL,
  `language` varchar(10) DEFAULT NULL,
  `timezone` varchar(50) DEFAULT NULL,
  `ui_preferences` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`ui_preferences`)),
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `cedula` (`cedula`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES
(1,'admin@ueipab.edu.ve','admin','pbkdf2:sha256:1000000$T2o0fYhnu9tQaoFc$cae164a581c2a838b40820c7d219a1073be1c3206402843c8e9d1cc3d280db63','Admin','UEIPAB','12345678',NULL,'platform_admin','active',NULL,NULL,NULL,'2025-09-26 23:30:11',0,NULL,NULL,NULL,'2025-09-29 08:13:35','2025-09-29 08:13:35',NULL,'es','America/Caracas',NULL,'2025-09-26 23:30:12','2025-09-27 16:07:05',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'bischeduler_master'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-09-29  8:20:57
