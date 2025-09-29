/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.4.7-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: ueipab_2025_data
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
-- Table structure for table `attendance_alerts`
--

DROP TABLE IF EXISTS `attendance_alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance_alerts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `alert_type` enum('chronic_absence','pattern_change','improvement_needed') NOT NULL,
  `severity` enum('low','medium','high','critical') NOT NULL,
  `threshold_percentage` decimal(5,2) DEFAULT NULL,
  `current_percentage` decimal(5,2) DEFAULT NULL,
  `absence_days` int(11) DEFAULT NULL,
  `message` text NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `acknowledged_at` datetime DEFAULT NULL,
  `acknowledged_by` int(11) DEFAULT NULL,
  `resolved_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  KEY `acknowledged_by` (`acknowledged_by`),
  CONSTRAINT `attendance_alerts_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `attendance_alerts_ibfk_2` FOREIGN KEY (`acknowledged_by`) REFERENCES `teachers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance_alerts`
--

LOCK TABLES `attendance_alerts` WRITE;
/*!40000 ALTER TABLE `attendance_alerts` DISABLE KEYS */;
/*!40000 ALTER TABLE `attendance_alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classrooms`
--

DROP TABLE IF EXISTS `classrooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `classrooms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_id` int(11) DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `capacity` int(11) DEFAULT NULL,
  `room_type` enum('REGULAR','LABORATORY','SPORTS','LIBRARY','AUDITORIUM','COMPUTER_LAB') DEFAULT NULL,
  `location` varchar(200) DEFAULT NULL,
  `equipment` text DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classrooms`
--

LOCK TABLES `classrooms` WRITE;
/*!40000 ALTER TABLE `classrooms` DISABLE KEYS */;
INSERT INTO `classrooms` VALUES
(1,1,'Aula 1',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(2,2,'Aula 2',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(3,3,'Aula 3',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(4,4,'Aula 4',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(5,5,'Aula 5',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(6,6,'Aula 6',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(7,7,'Aula 7',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(8,8,'Aula 8',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(9,9,'Aula 9',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(10,10,'Aula 10',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(11,11,'Aula 11',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(12,12,'Aula 12',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(13,13,'Aula 13',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(14,14,'Aula 14',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(15,15,'Cancha 1',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:18',NULL),
(16,1,'Aula 1',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(17,2,'Aula 2',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(18,3,'Aula 3',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(19,4,'Aula 4',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(20,5,'Aula 5',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(21,6,'Aula 6',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(22,7,'Aula 7',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(23,8,'Aula 8',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(24,9,'Aula 9',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(25,10,'Aula 10',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(26,11,'Aula 11',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(27,12,'Aula 12',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(28,13,'Aula 13',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(29,14,'Aula 14',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(30,15,'Cancha 1',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:36',NULL),
(31,1,'Aula 1',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(32,2,'Aula 2',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(33,3,'Aula 3',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(34,4,'Aula 4',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(35,5,'Aula 5',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(36,6,'Aula 6',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(37,7,'Aula 7',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(38,8,'Aula 8',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(39,9,'Aula 9',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(40,10,'Aula 10',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(41,11,'Aula 11',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(42,12,'Aula 12',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(43,13,'Aula 13',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(44,14,'Aula 14',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL),
(45,15,'Cancha 1',35,'REGULAR','Edificio Principal','Aula estándar',1,'2025-09-27 15:46:59',NULL);
/*!40000 ALTER TABLE `classrooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `daily_attendance`
--

DROP TABLE IF EXISTS `daily_attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `daily_attendance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `section_id` int(11) NOT NULL,
  `attendance_date` date NOT NULL,
  `present` tinyint(1) NOT NULL DEFAULT 0,
  `excused` tinyint(1) DEFAULT 0,
  `late_arrival` tinyint(1) DEFAULT 0,
  `absence_reason` enum('medical','family','transport','weather','other') DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `teacher_id` int(11) DEFAULT NULL,
  `recorded_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_student_date` (`student_id`,`attendance_date`),
  KEY `section_id` (`section_id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `daily_attendance_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `daily_attendance_ibfk_2` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`),
  CONSTRAINT `daily_attendance_ibfk_3` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8053 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daily_attendance`
--

LOCK TABLES `daily_attendance` WRITE;
/*!40000 ALTER TABLE `daily_attendance` DISABLE KEYS */;
/*!40000 ALTER TABLE `daily_attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_calendar_events`
--

DROP TABLE IF EXISTS `exam_calendar_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_calendar_events` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `exam_id` int(11) NOT NULL,
  `event_title` varchar(200) NOT NULL,
  `event_description` text DEFAULT NULL,
  `event_type` varchar(30) DEFAULT NULL,
  `start_datetime` datetime NOT NULL,
  `end_datetime` datetime NOT NULL,
  `all_day` tinyint(1) DEFAULT NULL,
  `color_code` varchar(10) DEFAULT NULL,
  `is_visible` tinyint(1) DEFAULT NULL,
  `display_priority` int(11) DEFAULT NULL,
  `is_recurring` tinyint(1) DEFAULT NULL,
  `recurrence_pattern` varchar(50) DEFAULT NULL,
  `recurrence_end_date` datetime DEFAULT NULL,
  `reminder_enabled` tinyint(1) DEFAULT NULL,
  `reminder_minutes_before` int(11) DEFAULT NULL,
  `reminder_sent` tinyint(1) DEFAULT NULL,
  `target_audience` varchar(100) DEFAULT NULL,
  `mandatory_attendance` tinyint(1) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exam_id` (`exam_id`),
  CONSTRAINT `exam_calendar_events_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_calendar_events`
--

LOCK TABLES `exam_calendar_events` WRITE;
/*!40000 ALTER TABLE `exam_calendar_events` DISABLE KEYS */;
/*!40000 ALTER TABLE `exam_calendar_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_conflicts`
--

DROP TABLE IF EXISTS `exam_conflicts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_conflicts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `conflict_type` varchar(50) NOT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `exam_1_id` int(11) NOT NULL,
  `exam_2_id` int(11) DEFAULT NULL,
  `description` text NOT NULL,
  `affected_students` text DEFAULT NULL,
  `affected_resources` text DEFAULT NULL,
  `suggested_resolution` text DEFAULT NULL,
  `auto_resolvable` tinyint(1) DEFAULT NULL,
  `resolution_priority` int(11) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `resolved_by` varchar(100) DEFAULT NULL,
  `resolved_at` datetime DEFAULT NULL,
  `resolution_notes` text DEFAULT NULL,
  `students_affected_count` int(11) DEFAULT NULL,
  `teachers_affected_count` int(11) DEFAULT NULL,
  `classrooms_affected_count` int(11) DEFAULT NULL,
  `detected_at` datetime DEFAULT NULL,
  `academic_year` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `exam_1_id` (`exam_1_id`),
  KEY `exam_2_id` (`exam_2_id`),
  CONSTRAINT `exam_conflicts_ibfk_1` FOREIGN KEY (`exam_1_id`) REFERENCES `exams` (`id`),
  CONSTRAINT `exam_conflicts_ibfk_2` FOREIGN KEY (`exam_2_id`) REFERENCES `exams` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_conflicts`
--

LOCK TABLES `exam_conflicts` WRITE;
/*!40000 ALTER TABLE `exam_conflicts` DISABLE KEYS */;
/*!40000 ALTER TABLE `exam_conflicts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_supervisors`
--

DROP TABLE IF EXISTS `exam_supervisors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_supervisors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `exam_id` int(11) NOT NULL,
  `teacher_id` int(11) NOT NULL,
  `supervisor_role` enum('PRIMARY','SECONDARY','OBSERVER','SUBSTITUTE') DEFAULT NULL,
  `is_confirmed` tinyint(1) DEFAULT NULL,
  `confirmation_date` datetime DEFAULT NULL,
  `arrival_time` time DEFAULT NULL,
  `departure_time` time DEFAULT NULL,
  `responsibilities` text DEFAULT NULL,
  `has_subject_expertise` tinyint(1) DEFAULT NULL,
  `supervision_hours` decimal(4,2) DEFAULT NULL,
  `hourly_rate` decimal(8,2) DEFAULT NULL,
  `total_payment` decimal(10,2) DEFAULT NULL,
  `attendance_status` varchar(20) DEFAULT NULL,
  `substitute_assigned` tinyint(1) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `assigned_by` varchar(100) DEFAULT NULL,
  `assigned_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exam_id` (`exam_id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `exam_supervisors_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`),
  CONSTRAINT `exam_supervisors_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_supervisors`
--

LOCK TABLES `exam_supervisors` WRITE;
/*!40000 ALTER TABLE `exam_supervisors` DISABLE KEYS */;
/*!40000 ALTER TABLE `exam_supervisors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exams`
--

DROP TABLE IF EXISTS `exams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `exams` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `exam_name` varchar(200) NOT NULL,
  `exam_type` enum('PARCIAL','FINAL','RECUPERACION','EXTRAORDINARIO','DIAGNOSTICO','EVALUACION_CONTINUA') NOT NULL,
  `subject_id` int(11) NOT NULL,
  `section_id` int(11) NOT NULL,
  `exam_date` datetime NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `duration_minutes` int(11) NOT NULL,
  `classroom_id` int(11) NOT NULL,
  `backup_classroom_id` int(11) DEFAULT NULL,
  `max_students` int(11) NOT NULL,
  `enrolled_students` int(11) DEFAULT NULL,
  `students_list` text DEFAULT NULL,
  `exam_instructions` text DEFAULT NULL,
  `materials_allowed` text DEFAULT NULL,
  `materials_forbidden` text DEFAULT NULL,
  `status` enum('DRAFT','SCHEDULED','CONFIRMED','IN_PROGRESS','COMPLETED','CANCELLED','POSTPONED') DEFAULT NULL,
  `is_published` tinyint(1) DEFAULT NULL,
  `requires_supervisor` tinyint(1) DEFAULT NULL,
  `academic_year` varchar(10) NOT NULL,
  `academic_period` varchar(50) DEFAULT NULL,
  `weight_percentage` decimal(5,2) DEFAULT NULL,
  `min_preparation_days` int(11) DEFAULT NULL,
  `max_daily_exams_per_student` int(11) DEFAULT NULL,
  `min_break_between_exams` int(11) DEFAULT NULL,
  `published_date` datetime DEFAULT NULL,
  `notification_sent` tinyint(1) DEFAULT NULL,
  `reminder_sent` tinyint(1) DEFAULT NULL,
  `graded` tinyint(1) DEFAULT NULL,
  `results_published` tinyint(1) DEFAULT NULL,
  `average_score` decimal(5,2) DEFAULT NULL,
  `pass_rate` decimal(5,2) DEFAULT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subject_id` (`subject_id`),
  KEY `section_id` (`section_id`),
  KEY `classroom_id` (`classroom_id`),
  KEY `backup_classroom_id` (`backup_classroom_id`),
  CONSTRAINT `exams_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`),
  CONSTRAINT `exams_ibfk_2` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`),
  CONSTRAINT `exams_ibfk_3` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`),
  CONSTRAINT `exams_ibfk_4` FOREIGN KEY (`backup_classroom_id`) REFERENCES `classrooms` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exams`
--

LOCK TABLES `exams` WRITE;
/*!40000 ALTER TABLE `exams` DISABLE KEYS */;
/*!40000 ALTER TABLE `exams` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `monthly_attendance_summary`
--

DROP TABLE IF EXISTS `monthly_attendance_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `monthly_attendance_summary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `month` int(11) NOT NULL,
  `year` int(11) NOT NULL,
  `academic_year` varchar(20) NOT NULL,
  `total_days` int(11) NOT NULL,
  `present_days` int(11) NOT NULL,
  `absent_days` int(11) NOT NULL,
  `excused_days` int(11) DEFAULT 0,
  `late_days` int(11) DEFAULT 0,
  `attendance_percentage` decimal(5,2) NOT NULL,
  `grade_level` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_student_month` (`student_id`,`month`,`year`),
  CONSTRAINT `monthly_attendance_summary_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `monthly_attendance_summary`
--

LOCK TABLES `monthly_attendance_summary` WRITE;
/*!40000 ALTER TABLE `monthly_attendance_summary` DISABLE KEYS */;
/*!40000 ALTER TABLE `monthly_attendance_summary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedule_assignments`
--

DROP TABLE IF EXISTS `schedule_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedule_assignments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `schedule_id` int(11) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `time_period_id` int(11) NOT NULL,
  `teacher_id` int(11) NOT NULL,
  `subject_id` int(11) NOT NULL,
  `section_id` int(11) NOT NULL,
  `classroom_id` int(11) NOT NULL,
  `day_of_week` enum('LUNES','MARTES','MIERCOLES','JUEVES','VIERNES') NOT NULL,
  `academic_year` varchar(10) NOT NULL,
  `effective_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `assignment_type` varchar(20) DEFAULT NULL,
  `priority` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_locked` tinyint(1) DEFAULT NULL,
  `conflict_status` varchar(20) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `schedule_id` (`schedule_id`),
  KEY `time_period_id` (`time_period_id`),
  KEY `teacher_id` (`teacher_id`),
  KEY `subject_id` (`subject_id`),
  KEY `section_id` (`section_id`),
  KEY `classroom_id` (`classroom_id`),
  CONSTRAINT `schedule_assignments_ibfk_1` FOREIGN KEY (`schedule_id`) REFERENCES `schedules` (`id`),
  CONSTRAINT `schedule_assignments_ibfk_2` FOREIGN KEY (`time_period_id`) REFERENCES `time_periods` (`id`),
  CONSTRAINT `schedule_assignments_ibfk_3` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`),
  CONSTRAINT `schedule_assignments_ibfk_4` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`),
  CONSTRAINT `schedule_assignments_ibfk_5` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`),
  CONSTRAINT `schedule_assignments_ibfk_6` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=348 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedule_assignments`
--

LOCK TABLES `schedule_assignments` WRITE;
/*!40000 ALTER TABLE `schedule_assignments` DISABLE KEYS */;
INSERT INTO `schedule_assignments` VALUES
(20,NULL,1,1,1,2,30,20,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(21,NULL,1,2,1,2,30,21,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(22,NULL,1,3,1,2,30,22,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(23,NULL,1,4,1,2,30,23,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(24,NULL,1,1,5,3,30,24,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(25,NULL,1,2,5,3,30,25,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(26,NULL,1,3,5,3,30,26,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(27,NULL,1,1,4,11,30,27,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(28,NULL,1,2,4,11,30,28,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(29,NULL,1,3,4,11,30,29,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(30,NULL,1,4,4,11,30,30,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(31,NULL,1,6,4,11,30,31,'VIERNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(32,NULL,1,1,1,16,30,32,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(33,NULL,1,2,1,16,30,33,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(34,NULL,1,3,1,16,30,34,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(35,NULL,1,4,1,16,30,35,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(36,NULL,1,1,5,17,30,36,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(37,NULL,1,2,5,17,30,37,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(38,NULL,1,3,5,17,30,38,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(39,NULL,1,1,1,2,31,39,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(40,NULL,1,2,1,2,31,40,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(41,NULL,1,3,1,2,31,41,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(42,NULL,1,4,1,2,31,42,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(43,NULL,1,1,1,3,31,43,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(44,NULL,1,2,1,3,31,44,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(45,NULL,1,3,1,3,31,45,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(46,NULL,1,1,1,11,31,1,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(47,NULL,1,2,1,11,31,2,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(48,NULL,1,3,1,11,31,3,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(49,NULL,1,4,1,11,31,4,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(50,NULL,1,6,1,11,31,5,'VIERNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(51,NULL,1,1,1,16,31,6,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(52,NULL,1,2,1,16,31,7,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(53,NULL,1,3,1,16,31,8,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(54,NULL,1,4,1,16,31,9,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(55,NULL,1,1,1,17,31,10,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(56,NULL,1,2,1,17,31,11,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(57,NULL,1,3,1,17,31,12,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(58,NULL,1,1,1,2,33,13,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(59,NULL,1,2,1,2,33,14,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(60,NULL,1,3,1,2,33,15,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(61,NULL,1,4,1,2,33,16,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(62,NULL,1,1,1,3,33,17,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(63,NULL,1,2,1,3,33,18,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(64,NULL,1,3,1,3,33,19,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(65,NULL,1,1,1,11,33,20,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(66,NULL,1,2,1,11,33,21,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(67,NULL,1,3,1,11,33,22,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(68,NULL,1,4,1,11,33,23,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(69,NULL,1,6,1,11,33,24,'VIERNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(70,NULL,1,1,1,16,33,25,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(71,NULL,1,2,1,16,33,26,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(72,NULL,1,3,1,16,33,27,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(73,NULL,1,4,1,16,33,28,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(74,NULL,1,1,1,17,33,29,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(75,NULL,1,2,1,17,33,30,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(76,NULL,1,3,1,17,33,31,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(77,NULL,1,1,1,2,34,32,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(78,NULL,1,2,1,2,34,33,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(79,NULL,1,3,1,2,34,34,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(80,NULL,1,4,1,2,34,35,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(81,NULL,1,1,1,3,34,36,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(82,NULL,1,2,1,3,34,37,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(83,NULL,1,3,1,3,34,38,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(84,NULL,1,1,1,11,34,39,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(85,NULL,1,2,1,11,34,40,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(86,NULL,1,3,1,11,34,41,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(87,NULL,1,4,1,11,34,42,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(88,NULL,1,6,1,11,34,43,'VIERNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(89,NULL,1,1,1,16,34,44,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(90,NULL,1,2,1,16,34,45,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(91,NULL,1,3,1,16,34,1,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(92,NULL,1,4,1,16,34,2,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(93,NULL,1,1,1,17,34,3,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(94,NULL,1,2,1,17,34,4,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(95,NULL,1,3,1,17,34,5,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(96,NULL,1,1,1,2,23,6,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(97,NULL,1,2,1,2,23,7,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(98,NULL,1,3,1,2,23,8,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(99,NULL,1,4,1,2,23,9,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(100,NULL,1,1,1,3,23,10,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(101,NULL,1,2,1,3,23,11,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(102,NULL,1,3,1,3,23,12,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(103,NULL,1,1,1,11,23,13,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(104,NULL,1,2,1,11,23,14,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(105,NULL,1,3,1,11,23,15,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(106,NULL,1,4,1,11,23,16,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(107,NULL,1,6,1,11,23,17,'VIERNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(108,NULL,1,1,1,16,23,18,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(109,NULL,1,2,1,16,23,19,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(110,NULL,1,3,1,16,23,20,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(111,NULL,1,4,1,16,23,21,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(112,NULL,1,1,1,17,23,22,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(113,NULL,1,2,1,17,23,23,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(114,NULL,1,3,1,17,23,24,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(115,NULL,1,1,1,2,24,25,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(116,NULL,1,2,1,2,24,26,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(117,NULL,1,3,1,2,24,27,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(118,NULL,1,4,1,2,24,28,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(119,NULL,1,1,1,3,24,29,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(120,NULL,1,2,1,3,24,30,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(121,NULL,1,3,1,3,24,31,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(122,NULL,1,1,1,11,24,32,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(123,NULL,1,2,1,11,24,33,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(124,NULL,1,3,1,11,24,34,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(125,NULL,1,4,1,11,24,35,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(126,NULL,1,6,1,11,24,36,'VIERNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(127,NULL,1,1,1,16,24,37,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(128,NULL,1,2,1,16,24,38,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(129,NULL,1,3,1,16,24,39,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(130,NULL,1,4,1,16,24,40,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(131,NULL,1,1,1,17,24,41,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(132,NULL,1,2,1,17,24,42,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(133,NULL,1,3,1,17,24,43,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(134,NULL,1,1,1,2,25,44,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(135,NULL,1,2,1,2,25,45,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(136,NULL,1,3,1,2,25,1,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(137,NULL,1,4,1,2,25,2,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(138,NULL,1,1,1,3,25,3,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(139,NULL,1,2,1,3,25,4,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(140,NULL,1,3,1,3,25,5,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(141,NULL,1,1,1,11,25,6,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(142,NULL,1,2,1,11,25,7,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(143,NULL,1,3,1,11,25,8,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(144,NULL,1,4,1,11,25,9,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(145,NULL,1,6,1,11,25,10,'VIERNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(146,NULL,1,1,1,16,25,11,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(147,NULL,1,2,1,16,25,12,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(148,NULL,1,3,1,16,25,13,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(149,NULL,1,4,1,16,25,14,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(150,NULL,1,1,1,17,25,15,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(151,NULL,1,2,1,17,25,16,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(152,NULL,1,3,1,17,25,17,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(153,NULL,1,1,1,2,26,18,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(154,NULL,1,2,1,2,26,19,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(155,NULL,1,3,1,2,26,20,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(156,NULL,1,4,1,2,26,21,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(157,NULL,1,1,1,3,26,22,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(158,NULL,1,2,1,3,26,23,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(159,NULL,1,3,1,3,26,24,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(160,NULL,1,1,1,11,26,25,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(161,NULL,1,2,1,11,26,26,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(162,NULL,1,3,1,11,26,27,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(163,NULL,1,4,1,11,26,28,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(164,NULL,1,6,1,11,26,29,'VIERNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(165,NULL,1,1,1,16,26,30,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(166,NULL,1,2,1,16,26,31,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(167,NULL,1,3,1,16,26,32,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(168,NULL,1,4,1,16,26,33,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(169,NULL,1,1,1,17,26,34,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(170,NULL,1,2,1,17,26,35,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(171,NULL,1,3,1,17,26,36,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(172,NULL,1,1,1,2,27,37,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(173,NULL,1,2,1,2,27,38,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(174,NULL,1,3,1,2,27,39,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(175,NULL,1,4,1,2,27,40,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(176,NULL,1,1,1,3,27,41,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(177,NULL,1,2,1,3,27,42,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(178,NULL,1,3,1,3,27,43,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(179,NULL,1,1,1,11,27,44,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(180,NULL,1,2,1,11,27,45,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(181,NULL,1,3,1,11,27,1,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(182,NULL,1,4,1,11,27,2,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(183,NULL,1,6,1,11,27,3,'VIERNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(184,NULL,1,1,1,16,27,4,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(185,NULL,1,2,1,16,27,5,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(186,NULL,1,3,1,16,27,6,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(187,NULL,1,4,1,16,27,7,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(188,NULL,1,1,1,17,27,8,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(189,NULL,1,2,1,17,27,9,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(190,NULL,1,3,1,17,27,10,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(191,NULL,1,1,1,2,28,11,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(192,NULL,1,2,1,2,28,12,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(193,NULL,1,3,1,2,28,13,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(194,NULL,1,4,1,2,28,14,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(195,NULL,1,1,1,3,28,15,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(196,NULL,1,2,1,3,28,16,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(197,NULL,1,3,1,3,28,17,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(198,NULL,1,1,1,11,28,18,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(199,NULL,1,2,1,11,28,19,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(200,NULL,1,3,1,11,28,20,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(201,NULL,1,4,1,11,28,21,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(202,NULL,1,6,1,11,28,22,'VIERNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(203,NULL,1,1,1,16,28,23,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(204,NULL,1,2,1,16,28,24,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(205,NULL,1,3,1,16,28,25,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(206,NULL,1,4,1,16,28,26,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(207,NULL,1,1,1,17,28,27,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(208,NULL,1,2,1,17,28,28,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(209,NULL,1,3,1,17,28,29,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(210,NULL,1,1,1,2,22,30,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(211,NULL,1,2,1,2,22,31,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(212,NULL,1,3,1,2,22,32,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(213,NULL,1,4,1,2,22,33,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(214,NULL,1,1,1,3,22,34,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(215,NULL,1,2,1,3,22,35,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(216,NULL,1,3,1,3,22,36,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(217,NULL,1,1,1,11,22,37,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(218,NULL,1,2,1,11,22,38,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(219,NULL,1,3,1,11,22,39,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(220,NULL,1,4,1,11,22,40,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(221,NULL,1,6,1,11,22,41,'VIERNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(222,NULL,1,1,1,16,22,42,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(223,NULL,1,2,1,16,22,43,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(224,NULL,1,3,1,16,22,44,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(225,NULL,1,4,1,16,22,45,'JUEVES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(226,NULL,1,1,1,17,22,1,'LUNES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(227,NULL,1,2,1,17,22,2,'MARTES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(228,NULL,1,3,1,17,22,3,'MIERCOLES','2025-2026','2025-09-27 15:46:59',NULL,'regular',1,NULL,1,0,'none','data_import_script','2025-09-27 15:46:59',NULL),
(307,NULL,1,1,10,11,29,1,'LUNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(308,NULL,1,1,14,71,29,1,'MARTES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(309,NULL,1,1,1,1,29,1,'MIERCOLES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(310,NULL,1,1,14,71,29,1,'JUEVES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(311,NULL,1,1,6,2,29,1,'VIERNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(312,NULL,1,2,10,11,29,1,'LUNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(313,NULL,1,2,14,71,29,1,'MARTES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(314,NULL,1,2,1,1,29,1,'MIERCOLES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(315,NULL,1,2,14,71,29,1,'JUEVES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(316,NULL,1,2,6,2,29,1,'VIERNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(317,NULL,1,3,91,10,29,1,'LUNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(318,NULL,1,3,2,4,29,1,'MARTES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(319,NULL,1,3,6,2,29,1,'MIERCOLES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(320,NULL,1,3,10,11,29,1,'JUEVES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(321,NULL,1,3,7,9,29,1,'VIERNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(322,NULL,1,4,2,4,29,1,'MARTES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(323,NULL,1,4,6,2,29,1,'MIERCOLES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(324,NULL,1,4,10,11,29,1,'JUEVES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(325,NULL,1,4,7,9,29,1,'VIERNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(326,NULL,1,6,2,4,29,1,'LUNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(327,NULL,1,6,1,1,29,1,'MARTES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(328,NULL,1,6,7,9,29,1,'MIERCOLES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(329,NULL,1,6,7,9,29,1,'JUEVES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(330,NULL,1,6,9,6,29,1,'VIERNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(331,NULL,1,7,2,4,29,1,'LUNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(332,NULL,1,7,1,1,29,1,'MARTES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(333,NULL,1,7,7,9,29,1,'MIERCOLES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(334,NULL,1,7,7,9,29,1,'JUEVES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(335,NULL,1,7,9,6,29,1,'VIERNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(336,NULL,1,8,9,6,29,1,'LUNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(337,NULL,1,8,8,5,29,1,'MARTES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(338,NULL,1,8,3,13,29,1,'MIERCOLES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(339,NULL,1,8,9,6,29,1,'JUEVES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(340,NULL,1,8,14,71,29,1,'VIERNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(341,NULL,1,9,9,6,29,1,'LUNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(342,NULL,1,9,8,5,29,1,'MARTES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(343,NULL,1,9,3,13,29,1,'MIERCOLES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(344,NULL,1,9,9,6,29,1,'JUEVES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(345,NULL,1,9,14,71,29,1,'VIERNES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(346,NULL,1,11,96,12,29,1,'MARTES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL),
(347,NULL,1,11,96,12,29,1,'JUEVES','2025-2026',NULL,NULL,'regular',NULL,NULL,1,NULL,NULL,NULL,'2025-09-28 21:24:25',NULL);
/*!40000 ALTER TABLE `schedule_assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedule_change_requests`
--

DROP TABLE IF EXISTS `schedule_change_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedule_change_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `teacher_id` int(11) NOT NULL,
  `assignment_id` int(11) NOT NULL,
  `request_type` varchar(30) NOT NULL,
  `requested_change` text NOT NULL,
  `justification` text NOT NULL,
  `proposed_time_period_id` int(11) DEFAULT NULL,
  `proposed_day_of_week` enum('LUNES','MARTES','MIERCOLES','JUEVES','VIERNES') DEFAULT NULL,
  `proposed_classroom_id` int(11) DEFAULT NULL,
  `swap_with_teacher_id` int(11) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `priority` varchar(20) DEFAULT NULL,
  `reviewed_by` varchar(100) DEFAULT NULL,
  `reviewed_at` datetime DEFAULT NULL,
  `response_message` text DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `implemented_at` datetime DEFAULT NULL,
  `requested_date` datetime NOT NULL,
  `expiration_date` datetime DEFAULT NULL,
  `academic_year` varchar(10) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  KEY `assignment_id` (`assignment_id`),
  KEY `proposed_time_period_id` (`proposed_time_period_id`),
  KEY `proposed_classroom_id` (`proposed_classroom_id`),
  KEY `swap_with_teacher_id` (`swap_with_teacher_id`),
  CONSTRAINT `schedule_change_requests_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`),
  CONSTRAINT `schedule_change_requests_ibfk_2` FOREIGN KEY (`assignment_id`) REFERENCES `schedule_assignments` (`id`),
  CONSTRAINT `schedule_change_requests_ibfk_3` FOREIGN KEY (`proposed_time_period_id`) REFERENCES `time_periods` (`id`),
  CONSTRAINT `schedule_change_requests_ibfk_4` FOREIGN KEY (`proposed_classroom_id`) REFERENCES `classrooms` (`id`),
  CONSTRAINT `schedule_change_requests_ibfk_5` FOREIGN KEY (`swap_with_teacher_id`) REFERENCES `teachers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedule_change_requests`
--

LOCK TABLES `schedule_change_requests` WRITE;
/*!40000 ALTER TABLE `schedule_change_requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `schedule_change_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedule_conflicts`
--

DROP TABLE IF EXISTS `schedule_conflicts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedule_conflicts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `conflict_type` varchar(50) NOT NULL,
  `severity` varchar(20) DEFAULT NULL,
  `assignment_1_id` int(11) DEFAULT NULL,
  `assignment_2_id` int(11) DEFAULT NULL,
  `description` text NOT NULL,
  `suggested_resolution` text DEFAULT NULL,
  `auto_resolvable` tinyint(1) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `resolved_by` varchar(100) DEFAULT NULL,
  `resolved_at` datetime DEFAULT NULL,
  `resolution_notes` text DEFAULT NULL,
  `detected_at` datetime DEFAULT NULL,
  `academic_year` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `assignment_1_id` (`assignment_1_id`),
  KEY `assignment_2_id` (`assignment_2_id`),
  CONSTRAINT `schedule_conflicts_ibfk_1` FOREIGN KEY (`assignment_1_id`) REFERENCES `schedule_assignments` (`id`),
  CONSTRAINT `schedule_conflicts_ibfk_2` FOREIGN KEY (`assignment_2_id`) REFERENCES `schedule_assignments` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedule_conflicts`
--

LOCK TABLES `schedule_conflicts` WRITE;
/*!40000 ALTER TABLE `schedule_conflicts` DISABLE KEYS */;
/*!40000 ALTER TABLE `schedule_conflicts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedules`
--

DROP TABLE IF EXISTS `schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tenant_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `academic_year` int(11) NOT NULL,
  `semester` int(11) NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `meta_data` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedules`
--

LOCK TABLES `schedules` WRITE;
/*!40000 ALTER TABLE `schedules` DISABLE KEYS */;
/*!40000 ALTER TABLE `schedules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sections`
--

DROP TABLE IF EXISTS `sections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `sections` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_id` int(11) DEFAULT NULL,
  `name` varchar(50) NOT NULL,
  `grade_level` int(11) NOT NULL,
  `section_letter` varchar(5) DEFAULT NULL,
  `educational_level` enum('PREESCOLAR','PRIMARIA','BACHILLERATO') DEFAULT NULL,
  `max_students` int(11) DEFAULT NULL,
  `current_students` int(11) DEFAULT NULL,
  `academic_year` varchar(10) NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sections`
--

LOCK TABLES `sections` WRITE;
/*!40000 ALTER TABLE `sections` DISABLE KEYS */;
INSERT INTO `sections` VALUES
(22,NULL,'1er Grupo',0,'U','PREESCOLAR',35,NULL,'2025-2026',1,'2025-09-28 11:00:59',NULL),
(23,NULL,'1er. Grado',1,'U','PRIMARIA',35,NULL,'2025-2026',1,'2025-09-28 11:00:59',NULL),
(24,NULL,'2do. Grado',2,'U','PRIMARIA',35,NULL,'2025-2026',1,'2025-09-28 11:00:59',NULL),
(25,NULL,'3er. Grado',3,'U','PRIMARIA',35,NULL,'2025-2026',1,'2025-09-28 11:00:59',NULL),
(26,NULL,'4to. Grado',4,'U','PRIMARIA',35,NULL,'2025-2026',1,'2025-09-28 11:00:59',NULL),
(27,NULL,'5to. Grado',5,'U','PRIMARIA',35,NULL,'2025-2026',1,'2025-09-28 11:01:00',NULL),
(28,NULL,'6to. Grado',6,'U','PRIMARIA',35,NULL,'2025-2026',1,'2025-09-28 11:01:00',NULL),
(29,NULL,'1er. Año',7,'U','BACHILLERATO',35,NULL,'2025-2026',1,'2025-09-28 11:01:00',NULL),
(30,NULL,'2do. Año',8,'U','BACHILLERATO',35,NULL,'2025-2026',1,'2025-09-28 11:01:00',NULL),
(31,NULL,'3er. Año',9,'A','BACHILLERATO',35,NULL,'2025-2026',1,'2025-09-28 11:01:00',NULL),
(32,NULL,'3er. Año',9,'B','BACHILLERATO',35,NULL,'2025-2026',1,'2025-09-28 11:01:00',NULL),
(33,NULL,'4to. Año',10,'U','BACHILLERATO',35,NULL,'2025-2026',1,'2025-09-28 11:01:00',NULL),
(34,NULL,'5to. Año',11,'U','BACHILLERATO',35,NULL,'2025-2026',1,'2025-09-28 11:01:00',NULL),
(35,NULL,'2do Grupo',0,'U','PREESCOLAR',35,0,'2025-2026',1,'2025-09-28 17:49:47','2025-09-28 17:49:47'),
(36,NULL,'3er Grupo',0,'U','PREESCOLAR',35,0,'2025-2026',1,'2025-09-28 17:49:47','2025-09-28 17:49:47');
/*!40000 ALTER TABLE `sections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_exam_schedules`
--

DROP TABLE IF EXISTS `student_exam_schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_exam_schedules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `student_cedula` varchar(20) NOT NULL,
  `student_name` varchar(200) NOT NULL,
  `section_id` int(11) NOT NULL,
  `exam_id` int(11) NOT NULL,
  `is_enrolled` tinyint(1) DEFAULT NULL,
  `enrollment_date` datetime DEFAULT NULL,
  `needs_accommodation` tinyint(1) DEFAULT NULL,
  `accommodation_type` varchar(100) DEFAULT NULL,
  `accommodation_details` text DEFAULT NULL,
  `notification_received` tinyint(1) DEFAULT NULL,
  `notification_date` datetime DEFAULT NULL,
  `preparation_materials_accessed` tinyint(1) DEFAULT NULL,
  `attendance_status` varchar(20) DEFAULT NULL,
  `start_time_actual` datetime DEFAULT NULL,
  `submission_time` datetime DEFAULT NULL,
  `exam_completed` tinyint(1) DEFAULT NULL,
  `score` decimal(5,2) DEFAULT NULL,
  `grade_letter` varchar(5) DEFAULT NULL,
  `passed` tinyint(1) DEFAULT NULL,
  `academic_year` varchar(10) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `section_id` (`section_id`),
  KEY `exam_id` (`exam_id`),
  CONSTRAINT `student_exam_schedules_ibfk_1` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`),
  CONSTRAINT `student_exam_schedules_ibfk_2` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_exam_schedules`
--

LOCK TABLES `student_exam_schedules` WRITE;
/*!40000 ALTER TABLE `student_exam_schedules` DISABLE KEYS */;
/*!40000 ALTER TABLE `student_exam_schedules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_id` varchar(50) DEFAULT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `full_name` varchar(200) NOT NULL,
  `cedula_escolar` varchar(20) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `gender` char(1) NOT NULL,
  `grade_level` int(11) NOT NULL,
  `section_id` int(11) NOT NULL,
  `parent_name` varchar(200) DEFAULT NULL,
  `parent_phone` varchar(50) DEFAULT NULL,
  `parent_email` varchar(100) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `academic_year` varchar(20) NOT NULL,
  `enrollment_date` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cedula_escolar` (`cedula_escolar`),
  KEY `section_id` (`section_id`),
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=797 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES
(582,NULL,'ANA BARBARA','GONZALEZ SAFFON','ANA BARBARA GONZALEZ SAFFON','V12222702888','2022-03-22','F',0,22,NULL,'(0424) 925-0034',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(583,NULL,'IZHAR ANER','HERNANDEZ MAESTRE','IZHAR ANER HERNANDEZ MAESTRE','V12217264876','2022-04-04','M',0,22,NULL,'(0412) 040-1735',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(584,NULL,'ALONSO DE JESÚS','ROSAS GRATEROL','ALONSO DE JESÚS ROSAS GRATEROL','V12217586963','2022-06-16','M',0,22,NULL,'(0414) 638-3998',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(585,NULL,'MAURICIO JOSE','CUELLAR HERNANDEZ','MAURICIO JOSE CUELLAR HERNANDEZ','V12119939485','2021-04-08','M',0,35,NULL,'04126955104',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(586,NULL,'LUSSIANO ALEXANDER','RAMIREZ KEY','LUSSIANO ALEXANDER RAMIREZ KEY','V12125059787','2021-04-24','M',0,35,NULL,'(0424) 884-8029',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(587,NULL,'IAN ALEJANDRO','RODRIGUEZ PEÑALOZA','IAN ALEJANDRO RODRIGUEZ PEÑALOZA','V12125321330','2021-04-09','M',0,35,NULL,'(0424) 843-6864',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(588,NULL,'SAVINA MISEL','SPADAVECCHIA HERNÁNDEZ','SAVINA MISEL SPADAVECCHIA HERNÁNDEZ','V12116573118','2021-06-03','F',0,35,NULL,'0424 8430873',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(589,NULL,'MARCELO JULIAN','BORGES GUERRA','MARCELO JULIAN BORGES GUERRA','V22012679751','2020-11-06','M',0,36,NULL,'(0414) 844-0527',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(590,NULL,'ATHENA DE LOS ANGELES','CRUZ PERDOMO','ATHENA DE LOS ANGELES CRUZ PERDOMO','V12016250914','2020-07-06','F',0,36,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(591,NULL,'JOB ELIAS DE DIOS','JIMENEZ RODRÍGUEZ','JOB ELIAS DE DIOS JIMENEZ RODRÍGUEZ','V112016571252','2020-12-16','M',0,36,NULL,'(0416) 880-1818',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(592,NULL,'RAEL AUGUSTO','TENORIO LUZARDO','RAEL AUGUSTO TENORIO LUZARDO','V22025581897','2020-06-15','M',0,36,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(593,NULL,'MIRANDA ISABEL','CUELLAR HERNANDEZ','MIRANDA ISABEL CUELLAR HERNANDEZ','V11819939485','2018-12-20','F',1,23,NULL,'04126955104',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(594,NULL,'MATHIAS DANIEL','DOMINGUEZ SANCHEZ','MATHIAS DANIEL DOMINGUEZ SANCHEZ','V11919143976','2019-08-01','M',1,23,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(595,NULL,'MARTIN ELIAS','GONZALEZ GONZALEZ','MARTIN ELIAS GONZALEZ GONZALEZ','V11916572986','2019-07-17','M',1,23,NULL,'04147996070',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(596,NULL,'PAULA VALENTINA','GONZALEZ RIVERA','PAULA VALENTINA GONZALEZ RIVERA','V11919939608','2019-05-13','F',1,23,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(597,NULL,'NAHOMI SALOME','MORETY VELASQUEZ','NAHOMI SALOME MORETY VELASQUEZ','V11915846744','2019-07-15','F',1,23,NULL,'(0414) 383-9199',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(598,NULL,'SAILEH DEL VALLE','MUÑOZ AGUILERA','SAILEH DEL VALLE MUÑOZ AGUILERA','V11917870661','2019-03-22','F',1,23,NULL,'(0424) 804-9564',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(599,NULL,'ISABEL ANTONELLA DE JESUS','ORTEGA IENI','ISABEL ANTONELLA DE JESUS ORTEGA IENI','V11919728953','2019-10-07','F',1,23,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(600,NULL,'LUCIA PAULETTE','PEREIRA PIÑANGO','LUCIA PAULETTE PEREIRA PIÑANGO','V12519662257','2019-02-26','F',1,23,NULL,'(0414) 790-6117',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(601,NULL,'ILEANA SOFIA','PEREZ MARCANO','ILEANA SOFIA PEREZ MARCANO','V11914188332','2019-03-21','F',1,23,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(602,NULL,'HANNA PAULA','SALAZAR RIVAS','HANNA PAULA SALAZAR RIVAS','V11919984502','2019-02-27','F',1,23,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(603,NULL,'LUCIANO ALBERTO','ALFONZO MACHADO','LUCIANO ALBERTO ALFONZO MACHADO','V11817590801','2018-02-27','M',2,24,NULL,'04248918250',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(604,NULL,'JESUS ALBERTO','BRITO RAMIREZ','JESUS ALBERTO BRITO RAMIREZ','V11714641852','2017-11-11','M',2,24,NULL,'04248225368',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(605,NULL,'HÉCTOR MARTIN','CALLES URTIZ','HÉCTOR MARTIN CALLES URTIZ','V11819956513','2018-04-09','M',2,24,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(606,NULL,'VALERIA ALESSANDRA','DUGARTE MONTAGUTH','VALERIA ALESSANDRA DUGARTE MONTAGUTH','V11816250166','2018-10-11','F',2,24,NULL,'(0424) 856-8016',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(607,NULL,'ANTONELLA VALENTINA','FIORITA ALVAREZ','ANTONELLA VALENTINA FIORITA ALVAREZ','V21826563051','2018-12-06','F',2,24,NULL,'(0424) 843-6999',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(608,NULL,'ANGEL DE JESUS','FUENTES APONTE','ANGEL DE JESUS FUENTES APONTE','V11818478630','2018-08-20','M',2,24,NULL,'(0416) 285-9660',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(609,NULL,'LUCIA VICTORIA','GONZALEZ CASTELLANOS','LUCIA VICTORIA GONZALEZ CASTELLANOS','V11817535680','2018-02-19','F',2,24,NULL,'(0424) 804-2440',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(610,NULL,'ALAN GABRIEL','HERNANDEZ FIGUERA','ALAN GABRIEL HERNANDEZ FIGUERA','V11820341085','2018-08-03','M',2,24,NULL,'(0424) 882-3716',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(611,NULL,'THIAGO','HERNANDEZ LORETO','THIAGO HERNANDEZ LORETO','V118016573600','2018-09-15','M',2,24,NULL,'(414) 849-9959',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(612,NULL,'MATHIAS ALEJANDRO','LORETO AZOCAR','MATHIAS ALEJANDRO LORETO AZOCAR','V11820737316','2018-09-10','M',2,24,NULL,'(0412) 110-0174',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(613,NULL,'SAMARA ITZAYANA IRÉ','MARCANO ALCALÁ','SAMARA ITZAYANA IRÉ MARCANO ALCALÁ','V11813258695','2018-12-22','F',2,24,NULL,'(0414) 894-1730',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(614,NULL,'JUAN DAVID','MONTILLA GUELI','JUAN DAVID MONTILLA GUELI','V11820546920','2018-08-17','M',2,24,NULL,'(0412) 109-9590',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(615,NULL,'LEIA ALEJANDRA','NUÑEZ GONZALEZ','LEIA ALEJANDRA NUÑEZ GONZALEZ','V11814688499','2018-08-03','F',2,24,NULL,'(0424) 839-0730',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(616,NULL,'ALEXANDRA SAMARA','SANCHEZ MENESES','ALEXANDRA SAMARA SANCHEZ MENESES','V11812880452','2018-07-01','F',2,24,NULL,'(0424) 982-0191',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(617,NULL,'Kendry David','Urrecheaga Barrios','Kendry David Urrecheaga Barrios','V11818981353','2018-06-08','M',2,24,NULL,'(0424) 883-1254',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(618,NULL,'CARLOS DAVID','VELIZ GONZALEZ','CARLOS DAVID VELIZ GONZALEZ','V11818228698','2018-12-17','M',2,24,NULL,'04141908372',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(619,NULL,'MATEO ALEJANDRO','VERA FERNANDEZ','MATEO ALEJANDRO VERA FERNANDEZ','V11816923716','2018-05-05','M',2,24,NULL,'(0514) 083-2852',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(620,NULL,'WILANGELA VICTORIA','VILLARROEL PEÑA','WILANGELA VICTORIA VILLARROEL PEÑA','V11814916794','2018-11-30','F',2,24,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(621,NULL,'BENYAMIN ALEJANDRO','BRITO BRAVO','BENYAMIN ALEJANDRO BRITO BRAVO','V11715533989','2017-12-21','M',3,25,NULL,'04145861990',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(622,NULL,'FIORELLA CAMILA','CASTILLO HEREDIA','FIORELLA CAMILA CASTILLO HEREDIA','V11811726859','2018-01-25','F',3,25,NULL,'04248079250',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(623,NULL,'PEDRO GERMÁN','CHANCHAMIRE VELÁSQUEZ','PEDRO GERMÁN CHANCHAMIRE VELÁSQUEZ','V11716667942','2017-07-16','M',3,25,NULL,'(0414) 839-9691',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(624,NULL,'VICTORIA','CONTRERAS HERNÁNDEZ','VICTORIA CONTRERAS HERNÁNDEZ','V11718453357','2017-11-29','F',3,25,NULL,'(0414) 621-2207',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(625,NULL,'MAXIMO CHARBEL','DE MARCO TARABOULSI','MAXIMO CHARBEL DE MARCO TARABOULSI','V11717870433','2017-10-06','M',3,25,NULL,'04248414454',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(626,NULL,'DARIANA DEL VALLE','FIGUEROA MARTINEZ','DARIANA DEL VALLE FIGUEROA MARTINEZ','V11717547949','2017-11-09','F',3,25,NULL,'(0424) 866-4125',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(627,NULL,'GAIL ALEJANDRA','GONZALEZ DAUHARE','GAIL ALEJANDRA GONZALEZ DAUHARE','V11716747976','2017-10-31','F',3,25,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(628,NULL,'LUCIANO MATHIAS','GONZALEZ RIVERA','LUCIANO MATHIAS GONZALEZ RIVERA','V11719939608','2017-01-10','M',3,25,NULL,'4248023200',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(629,NULL,'ALVARO DAMIAN','LAYA BOLIVAR','ALVARO DAMIAN LAYA BOLIVAR','V11716249287','2017-01-31','M',3,25,NULL,'(0414) 826-8441',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(630,NULL,'MARIAPAULA JOSE','MARCHAN FAJARDO','MARIAPAULA JOSE MARCHAN FAJARDO','V11715637834','2017-06-30','F',3,25,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(631,NULL,'MIGUEL SANTIAGO','MARIN QUIJADA','MIGUEL SANTIAGO MARIN QUIJADA','V11817009360','2018-01-30','M',3,25,NULL,'(0414) 814-1556',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(632,NULL,'SANTIAGO ALESSANDRO','MARTINEZ MEDINA','SANTIAGO ALESSANDRO MARTINEZ MEDINA','V11718525938','2017-05-31','M',3,25,NULL,'(0424) 548-7397',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(633,NULL,'STEVEN JOSE GREGORIO','MENDEZ BARRIOS','STEVEN JOSE GREGORIO MENDEZ BARRIOS','V11714817110','2017-05-17','M',3,25,NULL,'(0424) 883-1280',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(634,NULL,'DIEGO IGNACIO','NAVAS ALMERIDA','DIEGO IGNACIO NAVAS ALMERIDA','V11718848372','2017-04-17','M',3,25,NULL,'(0424) 534-6460',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(635,NULL,'DIONY MARCELO','PEREZ MARCANO','DIONY MARCELO PEREZ MARCANO','V11714188332','2017-06-22','M',3,25,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(636,NULL,'ITSABELLA VICTORIA','RODRIGUEZ HERRERA','ITSABELLA VICTORIA RODRIGUEZ HERRERA','V11718454823','2017-03-18','F',3,25,NULL,'(0414) 783-1089',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(637,NULL,'SUSAN VICTORIA DE JESUS','RODRIGUEZ TILLERO','SUSAN VICTORIA DE JESUS RODRIGUEZ TILLERO','V21715417452','2017-09-20','F',3,25,NULL,'(0424) 856-5305',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(638,NULL,'SANTIAGO ALBERTO','SALAZAR REYES','SANTIAGO ALBERTO SALAZAR REYES','V11717558736','2017-11-20','M',3,25,NULL,'(0412) 697-3279',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(639,NULL,'BIANCA SOPHIA','SANCHEZ CONTRERAS','BIANCA SOPHIA SANCHEZ CONTRERAS','V11725427177','2017-08-17','F',3,25,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(640,NULL,'JEREMIAS RAFAEL','URRECHEAGA BARRIOS','JEREMIAS RAFAEL URRECHEAGA BARRIOS','V11718981353','2017-06-07','M',3,25,NULL,'(0412) 474-0164',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(641,NULL,'FABRIZIO ANTONIO','VELASCO MUÑOZ','FABRIZIO ANTONIO VELASCO MUÑOZ','V11720172139','2017-05-26','M',3,25,NULL,'04148117249',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(642,NULL,'ANDREA VALENTINA','VICENT NAVARRO','ANDREA VALENTINA VICENT NAVARRO','V11717746586','2017-09-25','F',3,25,NULL,'(0414) 842-9169',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(643,NULL,'SANTIAGO DAVID','ALDANA PARRA','SANTIAGO DAVID ALDANA PARRA','V11620172974','2016-05-19','M',4,26,NULL,'(0424) 822-1712',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(644,NULL,'DHANA BARBARA','BUTTO GONZALEZ','DHANA BARBARA BUTTO GONZALEZ','V11619077620','2016-02-10','F',4,26,NULL,'(0424) 935-7581',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(645,NULL,'MARCO AUGUSTO','CAÑIZALEZ MELEAN','MARCO AUGUSTO CAÑIZALEZ MELEAN','V11615887593','2016-01-07','M',4,26,NULL,'(0414) 037-9492',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(646,NULL,'NESTOR DAVID','CASTRO PLAZ','NESTOR DAVID CASTRO PLAZ','V11719536826','2017-02-10','M',4,26,NULL,'(0412) 394-6261',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(647,NULL,'ABRAHAM JOSE','CONDALES SILVERA','ABRAHAM JOSE CONDALES SILVERA','V11612677116','2016-09-21','M',4,26,NULL,'(0412) 191-5154',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(648,NULL,'CARMELA ALEJANDRA','FARIAS MADERA','CARMELA ALEJANDRA FARIAS MADERA','V11618622714','2016-07-08','F',4,26,NULL,'04248228772',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(649,NULL,'GIANLUIGI','FIORITA ALVAREZ','GIANLUIGI FIORITA ALVAREZ','V11626563051','2016-12-14','M',4,26,NULL,'(0424) 843-6999',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(650,NULL,'JUAN PABLO','GONZALEZ MARQUEZ','JUAN PABLO GONZALEZ MARQUEZ','V11616251039','2016-11-15','M',4,26,NULL,'(0414) 842-6401',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(651,NULL,'GALA FEDERICA','GONZALEZ VILLAGRAN','GALA FEDERICA GONZALEZ VILLAGRAN','V11715124782','2017-02-01','F',4,26,NULL,'(0414) 778-3093',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(652,NULL,'VICTOR MANUEL DE JESUS','LORETO RIVERO','VICTOR MANUEL DE JESUS LORETO RIVERO','V11613017937','2016-10-01','M',4,26,NULL,'(0412) 921-8980',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(653,NULL,'LUIS JESUS','MARCANO LUNA','LUIS JESUS MARCANO LUNA','V37084275','2016-04-15','M',4,26,NULL,'04148680587',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(654,NULL,'LEONARDO SEBASTIAN','MARTINEZ HAYER','LEONARDO SEBASTIAN MARTINEZ HAYER','V11615846930','2016-03-02','M',4,26,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(655,NULL,'MARIANA CECILIA','MARTINEZ MORENO','MARIANA CECILIA MARTINEZ MORENO','V11616172157','2016-10-06','F',4,26,NULL,'(0416) 683-5233',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(656,NULL,'MIA','MATA MARQUEZ','MIA MATA MARQUEZ','V37187602','2016-05-06','F',4,26,NULL,'(0424) 846-5431',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(657,NULL,'ANDRES YSRRAEL','MORETY VELASQUEZ','ANDRES YSRRAEL MORETY VELASQUEZ','V11615846744','2016-06-02','M',4,26,NULL,'(0414) 383-9199',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:00:59',NULL),
(658,NULL,'VALERIA ISABEL','MUÑOZ PALMA','VALERIA ISABEL MUÑOZ PALMA','V11618229170','2016-12-09','F',4,26,NULL,'(0414) 788-9911',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(659,NULL,'AMELIA CRISTINA','POGGIO CARPIO','AMELIA CRISTINA POGGIO CARPIO','V11620547670','2016-05-29','F',4,26,NULL,'04121105020',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(660,NULL,'DIANA LY','RIVERO VALERA','DIANA LY RIVERO VALERA','V11616819202','2016-01-31','F',4,26,NULL,'(0424) 802-2288',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(661,NULL,'MARIA SOFIA DE JESUS','ROSAS MARIN','MARIA SOFIA DE JESUS ROSAS MARIN','V11618476850','2016-12-21','F',4,26,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(662,NULL,'DANNA PAOLA','SALAZAR RIVAS','DANNA PAOLA SALAZAR RIVAS','V11619984502','2016-02-25','F',4,26,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(663,NULL,'NATALIA SUSEJ','VELASQUEZ BELLORIN','NATALIA SUSEJ VELASQUEZ BELLORIN','V11618228101','2016-10-19','F',4,26,NULL,'(0414) 382-3477',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(664,NULL,'FRANKLIN ANTONIO JOSE','ZORILLA RENDON','FRANKLIN ANTONIO JOSE ZORILLA RENDON','V11612914780','2016-06-17','M',4,26,NULL,'(0414) 813-6529',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(665,NULL,'HIDELMARYS DE LOS ANGELES','ARRIOJA ROMERO','HIDELMARYS DE LOS ANGELES ARRIOJA ROMERO','V111517446047','2015-11-17','F',5,27,NULL,'(0412) 190-3336',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(666,NULL,'JEANIEL ALEJANDRO','CANO CAMPOS','JEANIEL ALEJANDRO CANO CAMPOS','V36845548','2015-10-15','M',5,27,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(667,NULL,'LUCIANA CECILIA','DIAZ AMAYA','LUCIANA CECILIA DIAZ AMAYA','V11514271850','2015-04-23','F',5,27,NULL,'(0416) 586-6432',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(668,NULL,'EMMA ISABELLA','FIGUEROA GUAYAPERO','EMMA ISABELLA FIGUEROA GUAYAPERO','V11520170251','2015-08-13','F',5,27,NULL,'0414-7792620',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(669,NULL,'ARIELA DEL VALLE','FIGUEROA MARTINEZ','ARIELA DEL VALLE FIGUEROA MARTINEZ','V36590593','2015-01-20','F',5,27,NULL,'(0424) 866-4125',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(670,NULL,'VICTOR AUGUSTO','FUENTES APONTE','VICTOR AUGUSTO FUENTES APONTE','V36770893','2015-07-20','M',5,27,NULL,'(0412) 877-4256',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(671,NULL,'LEONARDO ALEJANDRO','MARIN MILLAN','LEONARDO ALEJANDRO MARIN MILLAN','V11517263838','2015-09-03','M',5,27,NULL,'(0414) 383-4267',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(672,NULL,'DOALBERT ALEJANDRO','NUÑEZ FLORES','DOALBERT ALEJANDRO NUÑEZ FLORES','V11519668234','2015-05-11','M',5,27,NULL,'(0412) 061-6586',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(673,NULL,'JOSÉ LEONARDO','OLIVIER QUILARQUEZ','JOSÉ LEONARDO OLIVIER QUILARQUEZ','V36770943','2015-11-19','M',5,27,NULL,'(0412) 841-5557',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(674,NULL,'AMELIA MARIA','RIOS SANTAELLA','AMELIA MARIA RIOS SANTAELLA','V11513498097','2015-09-03','F',5,27,NULL,'(0424) 877-4690',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(675,NULL,'GABRIEL MATHIAS','RODRIGUEZ PEÑALOZA','GABRIEL MATHIAS RODRIGUEZ PEÑALOZA','V11525321330','2015-08-11','M',5,27,NULL,'(0412) 484-3163',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(676,NULL,'CELIMAR ESTEFANIA','TABASCA SALAZAR','CELIMAR ESTEFANIA TABASCA SALAZAR','V37151563','2015-12-11','F',5,27,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(677,NULL,'CARLOS ENRIQUE','ACOSTA SUAREZ','CARLOS ENRIQUE ACOSTA SUAREZ','V11413610528','2014-09-27','M',6,28,NULL,'(0424) 813-9699',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(678,NULL,'SAVERIO GIUSEPPE','ANTONAZZO BAUDANZA','SAVERIO GIUSEPPE ANTONAZZO BAUDANZA','V37074334','2014-03-11','M',6,28,NULL,'(0424) 893-1126',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(679,NULL,'Adrianella Sophia','Barreto Candiago','Adrianella Sophia Barreto Candiago','V36643420','2014-12-26','F',6,28,NULL,'(0414) 457-8531',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(680,NULL,'VALENTINA KISBEL','COLINA HERNANDEZ','VALENTINA KISBEL COLINA HERNANDEZ','V36078926','2014-05-29','F',6,28,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(681,NULL,'SEBASTIAN JOSUE','DELGADO GIL','SEBASTIAN JOSUE DELGADO GIL','V11416393232','2014-04-11','M',6,28,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(682,NULL,'CHRISTOFER JARED','FLORES ROMERO','CHRISTOFER JARED FLORES ROMERO','V36355975','2014-04-29','M',6,28,NULL,'(0414) 087-6700',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(683,NULL,'ARANTZA FABIOLA','GARCIA FIGUERA','ARANTZA FABIOLA GARCIA FIGUERA','V36375610','2015-01-04','F',6,28,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(684,NULL,'ARAN ISAAC','GARCIA HERNANDEZ','ARAN ISAAC GARCIA HERNANDEZ','V11416786298','2014-12-22','M',6,28,NULL,'(0412) 215-6582',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(685,NULL,'CORNELIO ANTONIO','GUZMAN SANCHEZ','CORNELIO ANTONIO GUZMAN SANCHEZ','V11420741570','2014-08-27','M',6,28,NULL,'(0424) 830-1510',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(686,NULL,'SANTIAGO IGNACIO','LOPEZ LORETO','SANTIAGO IGNACIO LOPEZ LORETO','V36547748','2014-03-05','M',6,28,NULL,'(0414) 837-0866',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(687,NULL,'JORGE MANUEL','MARTÍNEZ MORENO','JORGE MANUEL MARTÍNEZ MORENO','V11418144268','2014-09-16','M',6,28,NULL,'(0416) 683-5233',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(688,NULL,'ABEL DAVID','MARTINEZ SANTAMARIA','ABEL DAVID MARTINEZ SANTAMARIA','V35098799','2013-10-31','M',6,28,NULL,'(0414) 845-3631',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(689,NULL,'FIORELLA DE LOS ANGELES','MENDEZ BARRIOS','FIORELLA DE LOS ANGELES MENDEZ BARRIOS','V36504464','2014-08-22','F',6,28,NULL,'(0424) 851-3872',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(690,NULL,'CAMILA ISABEL','NAVAS ALMERIDA','CAMILA ISABEL NAVAS ALMERIDA','V36427828','2014-03-09','F',6,28,NULL,'(0423) 534-6460',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(691,NULL,'FRANCISCO ANTONIO','ORTEGA IENI','FRANCISCO ANTONIO ORTEGA IENI','V11519728953','2015-02-23','M',6,28,NULL,'04249233423',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(692,NULL,'MATHIAS ALEJANDRO','PERDOMO VELASCO','MATHIAS ALEJANDRO PERDOMO VELASCO','V36279089','2014-05-29','M',6,28,NULL,'0424-8068948',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(693,NULL,'PAULA ROBEIMY','PEREZ QUINTERO','PAULA ROBEIMY PEREZ QUINTERO','V36815532','2014-12-09','F',6,28,NULL,'(0424) 711-1593',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(694,NULL,'SUSEJ VALERIA DEL VALLE','RODRIGUEZ TILLERO','SUSEJ VALERIA DEL VALLE RODRIGUEZ TILLERO','V36450709','2014-10-23','F',6,28,NULL,'(0424) 810-9296',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(695,NULL,'OCTAVIO DAVID','RUIZ VARELA','OCTAVIO DAVID RUIZ VARELA','V11414127930','2014-12-26','M',6,28,NULL,'(0424) 897-7552',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(696,NULL,'ARANTZA VALENTINA','SUBERO VILLAMIZAR','ARANTZA VALENTINA SUBERO VILLAMIZAR','V36619544','2014-12-12','F',6,28,NULL,'(0412) 875-0115',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(697,NULL,'SABRINA','TORRES FIGUEROA','SABRINA TORRES FIGUEROA','V11418228058','2014-06-09','F',6,28,NULL,'(0414) 816-3760',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(698,NULL,'HASLYMM VALENTINA','VALLADARES VASQUEZ','HASLYMM VALENTINA VALLADARES VASQUEZ','V36611082','2014-02-06','F',6,28,NULL,'(0412) 191-0868',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(699,NULL,'LUIS FERNANDO','VALECILLOS ZABALA','LUIS FERNANDO VALECILLOS ZABALA','V11317871809','2013-04-16','M',7,29,NULL,'(0414) 843-5378',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(700,NULL,'FABRICCIO ALEJANDRO','FIGUEROA GUAYAPERO','FABRICCIO ALEJANDRO FIGUEROA GUAYAPERO','V11320170251','2013-12-12','M',7,29,NULL,'0414-7792620',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(701,NULL,'ANNA VALENTINA','GARCIA QUINTERO','ANNA VALENTINA GARCIA QUINTERO','V31214805636','2012-04-16','F',7,29,NULL,'(0424) 819-9626',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(702,NULL,'JOAQUIN ANDRES','HERNANDEZ GAMBOA','JOAQUIN ANDRES HERNANDEZ GAMBOA','V34818564','2013-05-08','M',7,29,NULL,'04140832536',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(703,NULL,'JESUS ADRIANO','BARRETO CANDIAGO','JESUS ADRIANO BARRETO CANDIAGO','V34820644','2013-05-28','M',7,29,NULL,'(0414) 457-8531',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(704,NULL,'ENDIS PAUL','PELEYON BELTRAN','ENDIS PAUL PELEYON BELTRAN','V34891610','2013-09-03','M',7,29,NULL,'(0424) 662-3495',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(705,NULL,'VICTORIA CARMELA','GONZÁLEZ PUERTA','VICTORIA CARMELA GONZÁLEZ PUERTA','V34891658','2013-05-30','F',7,29,NULL,'(0412) 109-1139',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(706,NULL,'REYNALDO SEBASTIAN','MAIZ MOGOLLON','REYNALDO SEBASTIAN MAIZ MOGOLLON','V35082186','2013-10-25','M',7,29,NULL,'(0414) 848-4860',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(707,NULL,'MARIA SOFIA','SOLORZANO FEBRES','MARIA SOFIA SOLORZANO FEBRES','V35098590','2013-03-07','F',7,29,NULL,'(0424) 893-9765',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(708,NULL,'VICTORIA NAZARETH','MARCANO MARIN','VICTORIA NAZARETH MARCANO MARIN','V35102996','2013-04-18','F',7,29,NULL,'(0424) 892-7735',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(709,NULL,'LORENZO IGNACIO','GONZALEZ VILLAGRAN','LORENZO IGNACIO GONZALEZ VILLAGRAN','V35120049','2013-07-10','M',7,29,NULL,'(0414) 778-3093',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(710,NULL,'KEYVER ALEXANDER','GOMEZ ROMERO','KEYVER ALEXANDER GOMEZ ROMERO','V36033367','2013-11-29','M',7,29,NULL,'(0412) 133-7147',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(711,NULL,'GRECIA CAMILA','RANGEL VILLANUEVA','GRECIA CAMILA RANGEL VILLANUEVA','V36044728','2013-12-05','F',7,29,NULL,'(0412) 322-6891',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(712,NULL,'VICTORIA VALENTINA','SANCHEZ CONTRERAS','VICTORIA VALENTINA SANCHEZ CONTRERAS','V36093652','2013-07-17','F',7,29,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(713,NULL,'DANIEL ENRIQUE','VASQUEZ ULLOA','DANIEL ENRIQUE VASQUEZ ULLOA','V36095981','2013-11-12','M',7,29,NULL,'(0426) 596-0462',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(714,NULL,'ANA CECILIA','BLONDELL CORRALES','ANA CECILIA BLONDELL CORRALES','V36111336','2013-03-21','F',7,29,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(715,NULL,'LUIS ALFONZO','GOITE VELA','LUIS ALFONZO GOITE VELA','V36124617','2013-10-03','M',7,29,NULL,'(0414) 892-3121',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(716,NULL,'ROMAN EDUARDO','BENAVIDES GONZALEZ','ROMAN EDUARDO BENAVIDES GONZALEZ','V36233215','2013-12-25','M',7,29,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(717,NULL,'AIVEUSON','CHING LIANG','AIVEUSON CHING LIANG','V36364220','2013-02-07','M',7,29,NULL,'(0414) 193-6611',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(718,NULL,'MARIANA VALERIA','FARIAS MADERA','MARIANA VALERIA FARIAS MADERA','V36461906','2013-09-10','F',7,29,NULL,'+584248228772',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(719,NULL,'ISABELLA ANDREA','FUENTES APONTE','ISABELLA ANDREA FUENTES APONTE','V36503058','2013-05-26','F',7,29,NULL,'(0414) 189-0506',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(720,NULL,'SUSEJ GABRIELA','LA CRUZ SANTOYO','SUSEJ GABRIELA LA CRUZ SANTOYO','V36523192','2013-05-06','F',7,29,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(721,NULL,'JOSMER IVAN','ALVAREZ MATA','JOSMER IVAN ALVAREZ MATA','V36534298','2013-10-10','M',7,29,NULL,'(0414) 088-6783',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(722,NULL,'MIA GRACIA DE DIOS','JIMENEZ RODRIGUEZ','MIA GRACIA DE DIOS JIMENEZ RODRIGUEZ','V36652816','2013-03-26','F',7,29,NULL,'(0416) 880-1818',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(723,NULL,'MERKIAN JOSUE','NUÑEZ MARTINEZ','MERKIAN JOSUE NUÑEZ MARTINEZ','V36757188','2013-05-10','M',7,29,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(724,NULL,'HECTOR ALONSO','RUIZ VARELA','HECTOR ALONSO RUIZ VARELA','V33855348','2012-01-05','M',8,30,NULL,'(0424) 897-7552',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(725,NULL,'RICARDO RAFAEL','OLIVIER QUILARQUEZ','RICARDO RAFAEL OLIVIER QUILARQUEZ','V34275263','2012-06-09','M',8,30,NULL,'(0414) 395-5330',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(726,NULL,'DAVID ENRIQUE','VELASQUEZ BELLORIN','DAVID ENRIQUE VELASQUEZ BELLORIN','V34364887','2012-05-31','M',8,30,NULL,'(0414) 382-3477',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(727,NULL,'MOISES ANTONIO','GUERRA GONZALEZ','MOISES ANTONIO GUERRA GONZALEZ','V34401882','2012-09-27','M',8,30,NULL,'(0426) 580-4769',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(728,NULL,'LUNA SOFIA','LOPEZ GONZALEZ','LUNA SOFIA LOPEZ GONZALEZ','V34489014','2012-05-22','F',8,30,NULL,'(0414) 899-8415',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(729,NULL,'ABDIAS RICARDO','VICENT NAVARRO','ABDIAS RICARDO VICENT NAVARRO','V34507875','2012-01-27','M',8,30,NULL,'(0414) 795-9857',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(730,NULL,'FABIANNA ISABELLA','VILORIA BRITO','FABIANNA ISABELLA VILORIA BRITO','V34543807','2012-03-05','F',8,30,NULL,'(0412) 103-8174',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(731,NULL,'HECTOR FABIAN','VELASQUEZ AGOSTINI','HECTOR FABIAN VELASQUEZ AGOSTINI','V34559720','2012-11-17','M',8,30,NULL,'(0412) 193-6741',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(732,NULL,'JOSNEL JOSE','GUERRA ARAY','JOSNEL JOSE GUERRA ARAY','V34559816','2012-04-08','M',8,30,NULL,'(0424) 843-5609',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(733,NULL,'ADELYBERT ISABEL','GONZALEZ MARCHAN','ADELYBERT ISABEL GONZALEZ MARCHAN','V34574624','2012-10-09','F',8,30,NULL,'(58) 424-8615',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(734,NULL,'ALONDRA ISABEL','CASTILLO MARIN','ALONDRA ISABEL CASTILLO MARIN','V34578139','2012-11-26','F',8,30,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(735,NULL,'DANIEL JONAS','ESCALONA URDANETA','DANIEL JONAS ESCALONA URDANETA','V34586798','2012-06-25','M',8,30,NULL,'(0424) 862-2220',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(736,NULL,'CAMILA VICTORIA','PEREIRA MARTINEZ','CAMILA VICTORIA PEREIRA MARTINEZ','V34595251','2012-08-15','F',8,30,NULL,'(0424) 872-0402',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(737,NULL,'JADASA REBECA','MAYZ LÓPEZ','JADASA REBECA MAYZ LÓPEZ','V34638240','2012-03-23','F',8,30,NULL,'(0416) 963-3672',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(738,NULL,'LUIS RENE','PRADO MARIN','LUIS RENE PRADO MARIN','V34687153','2012-09-19','M',8,30,NULL,'(0426) 284-4756',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(739,NULL,'LUCIA MARGARITA','RÍOS SANTAELLA','LUCIA MARGARITA RÍOS SANTAELLA','V34914574','2012-11-19','F',8,30,NULL,'(0416) 368-6044',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(740,NULL,'KAOLINETH MISLEIVIR','CASTRO PLAZ','KAOLINETH MISLEIVIR CASTRO PLAZ','V35023816','2013-07-25','F',8,30,NULL,'(0412) 394-6261',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(741,NULL,'GENIO ALEXANDER','GARCIA HERNANDEZ','GENIO ALEXANDER GARCIA HERNANDEZ','V35114052','2012-05-10','M',8,30,NULL,'(0412) 215-6582',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(742,NULL,'ALEJANDRA DEL VALLE','OSUNA CAMPOS','ALEJANDRA DEL VALLE OSUNA CAMPOS','V36128396','2012-07-13','F',8,30,NULL,'(0416) 283-5191',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(743,NULL,'PAULA ANTHONELLA','QUIJADA HERRERA','PAULA ANTHONELLA QUIJADA HERRERA','V36171258','2012-09-08','F',8,30,NULL,'(0424) 819-8382',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(744,NULL,'CONSTANZA SOPHIA','CABEZA GUERRA','CONSTANZA SOPHIA CABEZA GUERRA','V36209658','2012-09-06','F',8,30,NULL,'04148150726',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(745,NULL,'AARON RAFAEL','PINTO GUEVARA','AARON RAFAEL PINTO GUEVARA','V36310951','2012-02-16','M',8,30,NULL,'(0424) 877-9640',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(746,NULL,'DANIELA COROMOTO','DOMINGUEZ SANCHEZ','DANIELA COROMOTO DOMINGUEZ SANCHEZ','V36453660','2012-11-27','F',8,30,NULL,'(0424) 885-0148',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(747,NULL,'FERNANDO ROBERTO','TINEO RODRÍGUEZ','FERNANDO ROBERTO TINEO RODRÍGUEZ','V33905572','2011-09-01','M',9,31,NULL,'(0414) 874-2721',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(748,NULL,'ADRIAN HERNAN','VARGAS GUEVARA','ADRIAN HERNAN VARGAS GUEVARA','V33999509','2011-10-05','M',9,31,NULL,'(0424) 811-3657',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(749,NULL,'SOFÍA VICTORIA','ESCOBAR MACHADO','SOFÍA VICTORIA ESCOBAR MACHADO','V34048558','2011-03-17','F',9,31,NULL,'(0412) 048-9475',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(750,NULL,'SANTIAGO RAFAEL','CUMANA NARVAEZ','SANTIAGO RAFAEL CUMANA NARVAEZ','V34081364','2011-03-22','M',9,31,NULL,'(0424) 819-2886',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(751,NULL,'LUIS ALESSANDRO','JIMENEZ DIAZ','LUIS ALESSANDRO JIMENEZ DIAZ','V34122870','2011-04-09','M',9,31,NULL,'(0424) 836-6020',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(752,NULL,'JULIETT FABIANA','CEDEÑO SANCHEZ','JULIETT FABIANA CEDEÑO SANCHEZ','V34122897','2011-02-26','F',9,31,NULL,'(0416) 583-9083',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(753,NULL,'ANDRES DANIEL','CORDOBA GONZALEZ','ANDRES DANIEL CORDOBA GONZALEZ','V34177278','2011-10-14','M',9,31,NULL,'(0412) 807-4724',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(754,NULL,'CECILIA ELENA','CAÑIZALEZ MELEAN','CECILIA ELENA CAÑIZALEZ MELEAN','V34400121','2011-03-08','F',9,31,NULL,'(0424) 822-9991',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(755,NULL,'ISAAC ALFONSO','CARRILLO RONDÓN','ISAAC ALFONSO CARRILLO RONDÓN','V34530298','2011-09-02','M',9,31,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(756,NULL,'DAGMAR ARIADNA','BOLIVAR MARTINEZ','DAGMAR ARIADNA BOLIVAR MARTINEZ','V34889118','2010-10-18','F',9,31,NULL,'04248133011',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(757,NULL,'ROSYBELL ALEXANDRA','DUERTO PINTO','ROSYBELL ALEXANDRA DUERTO PINTO','V34895478','2011-11-11','F',9,31,NULL,'04148023735',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(758,NULL,'JOSE SANTIAGO','FREITES SALAZAR','JOSE SANTIAGO FREITES SALAZAR','V34914637','2011-05-10','M',9,31,NULL,'04148084631',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(759,NULL,'CAMILA SOFÍA','VELASQUEZ RODRIGUEZ','CAMILA SOFÍA VELASQUEZ RODRIGUEZ','V36034758','2011-11-25','F',9,31,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(760,NULL,'SAMUEL ALFONSO','ACEVEDO BRITO','SAMUEL ALFONSO ACEVEDO BRITO','V36156923','2011-02-07','M',9,31,NULL,'(0424) 847-3525',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(761,NULL,'YULIANNA','CHING LIANG','YULIANNA CHING LIANG','V36174613','2011-10-26','F',9,31,NULL,'(0412) 180-4329',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(762,NULL,'ISABELLA MÍA','GARCÍA FIGUERA','ISABELLA MÍA GARCÍA FIGUERA','V33744003','2011-01-14','F',9,32,NULL,'(0412) 113-1297',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(763,NULL,'LEONARDO VALENTIN','PORTERO TENIAS','LEONARDO VALENTIN PORTERO TENIAS','V33791324','2011-02-23','M',9,32,NULL,'(0412) 987-3409',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(764,NULL,'MATIAS GIOVANI','BECERRA VELASQUEZ','MATIAS GIOVANI BECERRA VELASQUEZ','V33791852','2011-03-29','M',9,32,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(765,NULL,'ANNELIS ANGELICA','ALZOLAR GALVIS','ANNELIS ANGELICA ALZOLAR GALVIS','V33857480','2011-08-27','F',9,32,NULL,'(0412) 086-2757',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(766,NULL,'FRANNIEL SANTIAGO','RODRIGUEZ MARTINEZ','FRANNIEL SANTIAGO RODRIGUEZ MARTINEZ','V33916031','2011-08-03','M',9,32,NULL,'04124379288',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(767,NULL,'LAURA ISABELLA','FERMIN LANZ','LAURA ISABELLA FERMIN LANZ','V33975028','2011-05-31','F',9,32,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(768,NULL,'DEIVERSON','EVANS','DEIVERSON EVANS','V33975034','2011-05-03','M',9,32,NULL,'(0424) 808-6312',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(769,NULL,'SAMUEL ABRAHAM DE DIOS','JIMENEZ RODRIGUEZ','SAMUEL ABRAHAM DE DIOS JIMENEZ RODRIGUEZ','V33995463','2011-09-11','M',9,32,NULL,'(0416) 880-1818',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(770,NULL,'GABRIELA VICTORIA','REQUENA MARIN','GABRIELA VICTORIA REQUENA MARIN','V34034818','2011-08-15','F',9,32,NULL,'(0414) 030-6445',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(771,NULL,'DIEGO ALEJANDRO','MARIN MILLAN','DIEGO ALEJANDRO MARIN MILLAN','V34036450','2011-07-02','M',9,32,NULL,'(0414) 383-4267',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(772,NULL,'YENNY ANGELES','PERDOMO ROJAS','YENNY ANGELES PERDOMO ROJAS','V34117353','2011-05-06','F',9,32,NULL,'(0424) 836-1469',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(773,NULL,'RANIA CAMILA','CABEZA HERNANDEZ','RANIA CAMILA CABEZA HERNANDEZ','V34214990','2011-09-23','F',9,32,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(774,NULL,'PABLO DANIEL','NAVARRO BOMPART','PABLO DANIEL NAVARRO BOMPART','V34250633','2011-05-27','M',9,32,NULL,'(0414) 342-7990',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(775,NULL,'OLIVIER RAPHAEL','JOSUE BRAVO','OLIVIER RAPHAEL JOSUE BRAVO','V34364861','2011-12-15','M',9,32,NULL,'04145861990',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(776,NULL,'FIORELLA SOFIA','COLINA DUGARTE','FIORELLA SOFIA COLINA DUGARTE','V34446674','2011-08-15','F',9,32,NULL,'04124389971',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(777,NULL,'MOISES ALEJANDRO','MARTINEZ MAITA','MOISES ALEJANDRO MARTINEZ MAITA','V33070832','2010-02-01','F',10,33,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(778,NULL,'EMANUEL ISAAC','MORILLO VASQUEZ','EMANUEL ISAAC MORILLO VASQUEZ','V33354504','2010-03-08','M',10,33,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(779,NULL,'TATIANA VALENTINA','CUMANA NARVAEZ','TATIANA VALENTINA CUMANA NARVAEZ','V33431375','2010-01-11','F',10,33,NULL,'(0424) 819-2886',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(780,NULL,'ANTHONY JOSUE','GUERRA GONZALEZ','ANTHONY JOSUE GUERRA GONZALEZ','V33476569','2010-07-29','M',10,33,NULL,'(0426) 580-4769',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(781,NULL,'EDGAR DUBAN','PERDOMO ROMERO','EDGAR DUBAN PERDOMO ROMERO','V33651412','2010-09-15','M',10,33,NULL,'(0424) 851-0490',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(782,NULL,'KAMILA ALESSANDRA','TORREALBA GUELI','KAMILA ALESSANDRA TORREALBA GUELI','V33662756','2010-09-10','F',10,33,NULL,'(0412) 947-6383',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(783,NULL,'SERENA ANDREA','VELASQUEZ URICARE','SERENA ANDREA VELASQUEZ URICARE','V33717276','2010-07-29','F',10,33,NULL,'(0412) 184-5223',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(784,NULL,'STEFANY VALENTINA','CORTEZ BELLORIN','STEFANY VALENTINA CORTEZ BELLORIN','V33933746','2010-06-17','F',10,33,NULL,'04248096154',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(785,NULL,'SAMUEL ALEJANDRO','MIRABAL PARRA','SAMUEL ALEJANDRO MIRABAL PARRA','V34178085','2010-03-05','M',10,33,NULL,'(0424) 819-8638',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(786,NULL,'MARIA LUISA','FRONTADO BOMPART','MARIA LUISA FRONTADO BOMPART','V34250621','2010-05-03','F',10,33,NULL,'04147755914',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(787,NULL,'ANGEL EDUARDO','RANGEL VILLANUEVA','ANGEL EDUARDO RANGEL VILLANUEVA','V34657922','2010-04-03','M',10,33,NULL,'(0424) 800-7787',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(788,NULL,'FERNANDO ESTEBAN','SEQUEA RODRIGUEZ','FERNANDO ESTEBAN SEQUEA RODRIGUEZ','V32847861','2008-02-27','M',11,34,NULL,'(0412) 928-5890',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(789,NULL,'SOFÍA VICTORIA','MUÑOZ GOMES','SOFÍA VICTORIA MUÑOZ GOMES','V33108663','2009-12-25','F',11,34,NULL,'(0414) 823-3381',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(790,NULL,'PATRICIA DEL VALLE','TORRES FIGUEROA','PATRICIA DEL VALLE TORRES FIGUEROA','V33234760','2010-01-06','F',11,34,NULL,'(0412) 862-8054',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(791,NULL,'MARIANA ALEJANDRA','TORRES NIETO','MARIANA ALEJANDRA TORRES NIETO','V33234761','2009-09-13','F',11,34,NULL,'(0414) 801-2347',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(792,NULL,'ANGEL GABRIEL','QUILARQUE LA CRUZ','ANGEL GABRIEL QUILARQUE LA CRUZ','V33271356','2009-08-04','M',11,34,NULL,'(0412) 207-7896',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(793,NULL,'FARES','EL RYFAIE AL RIFAI','FARES EL RYFAIE AL RIFAI','V33415474','2008-07-01','M',11,34,NULL,'(0414) 846-1591',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(794,NULL,'NUR YASMIN','RACHID KHATIB','NUR YASMIN RACHID KHATIB','V33431023','2010-01-04','F',11,34,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(795,NULL,'ADRIAN ALBERTO','ALZOLAR GALVIS','ADRIAN ALBERTO ALZOLAR GALVIS','V33763374','2009-12-23','M',11,34,NULL,'(0412) 110-9912',NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL),
(796,NULL,'SOFIA PAOLA','CUAURO NUÑEZ','SOFIA PAOLA CUAURO NUÑEZ','V34489035','2009-12-01','F',11,34,NULL,NULL,NULL,NULL,'2025-2026','2025-09-01 00:00:00',1,'2025-09-28 11:01:00',NULL);
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subjects`
--

DROP TABLE IF EXISTS `subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `subjects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_id` int(11) DEFAULT NULL,
  `subject_name` varchar(200) NOT NULL,
  `short_name` varchar(50) DEFAULT NULL,
  `curriculum_level` enum('PREESCOLAR','PRIMARIA','BACHILLERATO') DEFAULT NULL,
  `subject_category` enum('MATHEMATICS','LANGUAGE','SCIENCE','SOCIAL_STUDIES','SPORTS','ARTS','TECHNOLOGY','GENERAL') DEFAULT NULL,
  `is_core_subject` tinyint(1) DEFAULT NULL,
  `weekly_hours_default` int(11) DEFAULT NULL,
  `mppe_code` varchar(20) DEFAULT NULL,
  `curriculum_area` varchar(100) DEFAULT NULL,
  `is_elective` tinyint(1) DEFAULT NULL,
  `prerequisite_subjects` text DEFAULT NULL,
  `academic_year` varchar(10) NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=75 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subjects`
--

LOCK TABLES `subjects` WRITE;
/*!40000 ALTER TABLE `subjects` DISABLE KEYS */;
INSERT INTO `subjects` VALUES
(1,6,'BIOLOGÍA AMBIENTE Y TECNOLOGÍA','BIOLOGÍA AMBIENTE Y ','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(2,1,'CASTELLANO Y LITERATURA','CASTELLANO Y LITERAT','BACHILLERATO','LANGUAGE',1,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(3,5,'CIENCIAS DE LA TIERRA','CIENCIAS DE LA TIERR','BACHILLERATO','SCIENCE',1,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(4,11,'EDUCACIÓN FÍSICA','EDUCACIÓN FÍSICA','BACHILLERATO','SPORTS',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(5,8,'FISICA','FISICA','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(6,4,'GHC PARA LA SOBERANIA NACIONAL','GHC PARA LA SOBERANI','BACHILLERATO','SOCIAL_STUDIES',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(7,13,'Grupo de CRP','Grupo de CRP','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(8,10,'IDIOMAS','IDIOMAS','BACHILLERATO','LANGUAGE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(9,12,'Innovación TP','Innovación TP','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(10,3,'LOGICA MATEMÁNTICA','LOGICA MATEMÁNTICA','BACHILLERATO','MATHEMATICS',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(11,2,'MATEMÁTICAS','MATEMÁTICAS','BACHILLERATO','MATHEMATICS',1,6,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(12,14,'Orientacion Vocacional','Orientacion Vocacion','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(13,9,'QUIMICA','QUIMICA','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(14,7,'SOBERANÍA NACIONAL','SOBERANÍA NACIONAL','BACHILLERATO','SOCIAL_STUDIES',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:09',NULL),
(15,6,'BIOLOGÍA AMBIENTE Y TECNOLOGÍA','BIOLOGÍA AMBIENTE Y ','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(16,1,'CASTELLANO Y LITERATURA','CASTELLANO Y LITERAT','BACHILLERATO','LANGUAGE',1,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(17,5,'CIENCIAS DE LA TIERRA','CIENCIAS DE LA TIERR','BACHILLERATO','SCIENCE',1,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(18,11,'EDUCACIÓN FÍSICA','EDUCACIÓN FÍSICA','BACHILLERATO','SPORTS',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(19,8,'FISICA','FISICA','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(20,4,'GHC PARA LA SOBERANIA NACIONAL','GHC PARA LA SOBERANI','BACHILLERATO','SOCIAL_STUDIES',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(21,13,'Grupo de CRP','Grupo de CRP','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(22,10,'IDIOMAS','IDIOMAS','BACHILLERATO','LANGUAGE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(23,12,'Innovación TP','Innovación TP','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(24,3,'LOGICA MATEMÁNTICA','LOGICA MATEMÁNTICA','BACHILLERATO','MATHEMATICS',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(25,2,'MATEMÁTICAS','MATEMÁTICAS','BACHILLERATO','MATHEMATICS',1,6,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(26,14,'Orientacion Vocacional','Orientacion Vocacion','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(27,9,'QUIMICA','QUIMICA','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(28,7,'SOBERANÍA NACIONAL','SOBERANÍA NACIONAL','BACHILLERATO','SOCIAL_STUDIES',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:45:47',NULL),
(29,6,'BIOLOGÍA AMBIENTE Y TECNOLOGÍA','BIOLOGÍA AMBIENTE Y ','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(30,1,'CASTELLANO Y LITERATURA','CASTELLANO Y LITERAT','BACHILLERATO','LANGUAGE',1,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(31,5,'CIENCIAS DE LA TIERRA','CIENCIAS DE LA TIERR','BACHILLERATO','SCIENCE',1,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(32,11,'EDUCACIÓN FÍSICA','EDUCACIÓN FÍSICA','BACHILLERATO','SPORTS',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(33,8,'FISICA','FISICA','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(34,4,'GHC PARA LA SOBERANIA NACIONAL','GHC PARA LA SOBERANI','BACHILLERATO','SOCIAL_STUDIES',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(35,13,'Grupo de CRP','Grupo de CRP','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(36,10,'IDIOMAS','IDIOMAS','BACHILLERATO','LANGUAGE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(37,12,'Innovación TP','Innovación TP','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(38,3,'LOGICA MATEMÁNTICA','LOGICA MATEMÁNTICA','BACHILLERATO','MATHEMATICS',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(39,2,'MATEMÁTICAS','MATEMÁTICAS','BACHILLERATO','MATHEMATICS',1,6,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(40,14,'Orientacion Vocacional','Orientacion Vocacion','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(41,9,'QUIMICA','QUIMICA','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(42,7,'SOBERANÍA NACIONAL','SOBERANÍA NACIONAL','BACHILLERATO','SOCIAL_STUDIES',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:18',NULL),
(43,6,'BIOLOGÍA AMBIENTE Y TECNOLOGÍA','BIOLOGÍA AMBIENTE Y ','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(44,1,'CASTELLANO Y LITERATURA','CASTELLANO Y LITERAT','BACHILLERATO','LANGUAGE',1,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(45,5,'CIENCIAS DE LA TIERRA','CIENCIAS DE LA TIERR','BACHILLERATO','SCIENCE',1,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(46,11,'EDUCACIÓN FÍSICA','EDUCACIÓN FÍSICA','BACHILLERATO','SPORTS',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(47,8,'FISICA','FISICA','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(48,4,'GHC PARA LA SOBERANIA NACIONAL','GHC PARA LA SOBERANI','BACHILLERATO','SOCIAL_STUDIES',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(49,13,'Grupo de CRP','Grupo de CRP','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(50,10,'IDIOMAS','IDIOMAS','BACHILLERATO','LANGUAGE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(51,12,'Innovación TP','Innovación TP','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(52,3,'LOGICA MATEMÁNTICA','LOGICA MATEMÁNTICA','BACHILLERATO','MATHEMATICS',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(53,2,'MATEMÁTICAS','MATEMÁTICAS','BACHILLERATO','MATHEMATICS',1,6,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(54,14,'Orientacion Vocacional','Orientacion Vocacion','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(55,9,'QUIMICA','QUIMICA','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(56,7,'SOBERANÍA NACIONAL','SOBERANÍA NACIONAL','BACHILLERATO','SOCIAL_STUDIES',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:36',NULL),
(57,6,'BIOLOGÍA AMBIENTE Y TECNOLOGÍA','BIOLOGÍA AMBIENTE Y ','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(58,1,'CASTELLANO Y LITERATURA','CASTELLANO Y LITERAT','BACHILLERATO','LANGUAGE',1,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(59,5,'CIENCIAS DE LA TIERRA','CIENCIAS DE LA TIERR','BACHILLERATO','SCIENCE',1,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(60,11,'EDUCACIÓN FÍSICA','EDUCACIÓN FÍSICA','BACHILLERATO','SPORTS',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(61,8,'FISICA','FISICA','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(62,4,'GHC PARA LA SOBERANIA NACIONAL','GHC PARA LA SOBERANI','BACHILLERATO','SOCIAL_STUDIES',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(63,13,'Grupo de CRP','Grupo de CRP','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(64,10,'IDIOMAS','IDIOMAS','BACHILLERATO','LANGUAGE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(65,12,'Innovación TP','Innovación TP','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(66,3,'LOGICA MATEMÁNTICA','LOGICA MATEMÁNTICA','BACHILLERATO','MATHEMATICS',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(67,2,'MATEMÁTICAS','MATEMÁTICAS','BACHILLERATO','MATHEMATICS',1,6,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(68,14,'Orientacion Vocacional','Orientacion Vocacion','BACHILLERATO','GENERAL',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(69,9,'QUIMICA','QUIMICA','BACHILLERATO','SCIENCE',0,4,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(70,7,'SOBERANÍA NACIONAL','SOBERANÍA NACIONAL','BACHILLERATO','SOCIAL_STUDIES',0,3,NULL,NULL,0,NULL,'2025-2026',1,'2025-09-27 15:46:59',NULL),
(71,NULL,'INGLÉS','INGLÉS','BACHILLERATO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-2026',1,'2025-09-28 21:18:24',NULL),
(72,NULL,'LÓGICA MATEMÁTICA','LÓGICA MAT','BACHILLERATO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-2026',1,'2025-09-28 21:18:24',NULL),
(73,NULL,'INGLÉS','INGLÉS','BACHILLERATO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-2026',1,'2025-09-28 21:18:31',NULL),
(74,NULL,'LÓGICA MATEMÁTICA','LÓGICA MAT','BACHILLERATO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-2026',1,'2025-09-28 21:18:31',NULL);
/*!40000 ALTER TABLE `subjects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher_availability`
--

DROP TABLE IF EXISTS `teacher_availability`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher_availability` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `teacher_id` int(11) NOT NULL,
  `day_of_week` enum('LUNES','MARTES','MIERCOLES','JUEVES','VIERNES') NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `availability_type` varchar(20) DEFAULT NULL,
  `reason` varchar(200) DEFAULT NULL,
  `effective_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `academic_year` varchar(10) NOT NULL,
  `is_recurring` tinyint(1) DEFAULT NULL,
  `specific_dates` text DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_approved` tinyint(1) DEFAULT NULL,
  `approved_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `teacher_availability_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher_availability`
--

LOCK TABLES `teacher_availability` WRITE;
/*!40000 ALTER TABLE `teacher_availability` DISABLE KEYS */;
/*!40000 ALTER TABLE `teacher_availability` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher_dashboard_stats`
--

DROP TABLE IF EXISTS `teacher_dashboard_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher_dashboard_stats` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `teacher_id` int(11) NOT NULL,
  `academic_year` varchar(10) NOT NULL,
  `total_weekly_hours` int(11) DEFAULT NULL,
  `total_classes` int(11) DEFAULT NULL,
  `total_subjects` int(11) DEFAULT NULL,
  `total_sections` int(11) DEFAULT NULL,
  `preference_satisfaction_score` decimal(5,2) DEFAULT NULL,
  `time_preference_score` decimal(5,2) DEFAULT NULL,
  `day_preference_score` decimal(5,2) DEFAULT NULL,
  `subject_preference_score` decimal(5,2) DEFAULT NULL,
  `classroom_preference_score` decimal(5,2) DEFAULT NULL,
  `total_change_requests` int(11) DEFAULT NULL,
  `approved_change_requests` int(11) DEFAULT NULL,
  `pending_change_requests` int(11) DEFAULT NULL,
  `workload_balance_score` decimal(5,2) DEFAULT NULL,
  `consecutive_classes_max` int(11) DEFAULT NULL,
  `free_periods_per_week` int(11) DEFAULT NULL,
  `last_calculated` datetime DEFAULT NULL,
  `calculation_version` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `teacher_dashboard_stats_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher_dashboard_stats`
--

LOCK TABLES `teacher_dashboard_stats` WRITE;
/*!40000 ALTER TABLE `teacher_dashboard_stats` DISABLE KEYS */;
/*!40000 ALTER TABLE `teacher_dashboard_stats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher_preferences`
--

DROP TABLE IF EXISTS `teacher_preferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher_preferences` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `teacher_id` int(11) NOT NULL,
  `preference_type` enum('TIME_SLOT','DAY_OF_WEEK','SUBJECT','CLASSROOM','SECTION') NOT NULL,
  `preference_level` enum('AVOID','DISLIKE','NEUTRAL','LIKE','PREFER') NOT NULL,
  `time_period_id` int(11) DEFAULT NULL,
  `day_of_week` enum('LUNES','MARTES','MIERCOLES','JUEVES','VIERNES') DEFAULT NULL,
  `subject_id` int(11) DEFAULT NULL,
  `classroom_id` int(11) DEFAULT NULL,
  `section_id` int(11) DEFAULT NULL,
  `reason` text DEFAULT NULL,
  `priority_score` int(11) DEFAULT NULL,
  `effective_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `academic_year` varchar(10) NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_approved` tinyint(1) DEFAULT NULL,
  `approved_by` varchar(100) DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  KEY `time_period_id` (`time_period_id`),
  KEY `subject_id` (`subject_id`),
  KEY `classroom_id` (`classroom_id`),
  KEY `section_id` (`section_id`),
  CONSTRAINT `teacher_preferences_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`),
  CONSTRAINT `teacher_preferences_ibfk_2` FOREIGN KEY (`time_period_id`) REFERENCES `time_periods` (`id`),
  CONSTRAINT `teacher_preferences_ibfk_3` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`),
  CONSTRAINT `teacher_preferences_ibfk_4` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`),
  CONSTRAINT `teacher_preferences_ibfk_5` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher_preferences`
--

LOCK TABLES `teacher_preferences` WRITE;
/*!40000 ALTER TABLE `teacher_preferences` DISABLE KEYS */;
/*!40000 ALTER TABLE `teacher_preferences` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher_subjects`
--

DROP TABLE IF EXISTS `teacher_subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher_subjects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `teacher_id` int(11) NOT NULL,
  `subject_id` int(11) NOT NULL,
  `weekly_hours` int(11) NOT NULL,
  `is_primary_subject` tinyint(1) DEFAULT NULL,
  `competency_level` varchar(20) DEFAULT NULL,
  `academic_year` varchar(10) NOT NULL,
  `assigned_date` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  KEY `subject_id` (`subject_id`),
  CONSTRAINT `teacher_subjects_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`),
  CONSTRAINT `teacher_subjects_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher_subjects`
--

LOCK TABLES `teacher_subjects` WRITE;
/*!40000 ALTER TABLE `teacher_subjects` DISABLE KEYS */;
/*!40000 ALTER TABLE `teacher_subjects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher_workload`
--

DROP TABLE IF EXISTS `teacher_workload`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher_workload` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `teacher_id` int(11) NOT NULL,
  `academic_year` varchar(10) NOT NULL,
  `total_weekly_hours` int(11) DEFAULT NULL,
  `max_allowed_hours` int(11) DEFAULT NULL,
  `calculated_hours` int(11) DEFAULT NULL,
  `mppe_hours_requirement` int(11) DEFAULT NULL,
  `overtime_hours` int(11) DEFAULT NULL,
  `is_valid` tinyint(1) DEFAULT NULL,
  `validation_notes` text DEFAULT NULL,
  `last_calculated` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `teacher_workload_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher_workload`
--

LOCK TABLES `teacher_workload` WRITE;
/*!40000 ALTER TABLE `teacher_workload` DISABLE KEYS */;
/*!40000 ALTER TABLE `teacher_workload` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teachers`
--

DROP TABLE IF EXISTS `teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_id` int(11) DEFAULT NULL,
  `teacher_name` varchar(255) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(155) DEFAULT NULL,
  `cedula` varchar(20) DEFAULT NULL,
  `professional_id` varchar(50) DEFAULT NULL,
  `area_specialization` varchar(100) DEFAULT NULL,
  `education_level` varchar(100) DEFAULT NULL,
  `years_experience` int(11) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `hire_date` datetime DEFAULT NULL,
  `employment_type` varchar(50) DEFAULT NULL,
  `max_weekly_hours` int(11) DEFAULT NULL,
  `current_weekly_hours` int(11) DEFAULT NULL,
  `user_id` varchar(100) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `academic_year` varchar(10) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cedula` (`cedula`)
) ENGINE=InnoDB AUTO_INCREMENT=98 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers`
--

LOCK TABLES `teachers` WRITE;
/*!40000 ALTER TABLE `teachers` DISABLE KEYS */;
INSERT INTO `teachers` VALUES
(1,0,'AUDREY GARCIA',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'audrey.lucia.garcia.areyan@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(2,1,'EMILIO ISEA',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'emilio.isea@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(3,2,'FLORMAR HERNANDEZ',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'flormar.hernandez@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(4,3,'GABRIEL ESPAÑA',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'gabriel.españa@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(5,4,'GIOVANNI VEZZA',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'giovanni.vezza@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(6,5,'ISMARY ARCILA',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'ismary.arcila@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(7,6,'JOSE HERNANDEZ',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'jose.hernandez@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(8,7,'LUISA ELENA ABREU',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'luisa.elena.abreu@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(9,8,'MARIA FIGUERA',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'maria.figuera@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(10,9,'MARIA NIETO',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'maria.nieto@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(11,10,'MONICA MOSQUEDA',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'monica.mosqueda@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(13,12,'RAMON BELLO',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'ramon.bello@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(14,13,'STEFANY ROMERO',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'stefany.romero@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(15,14,'VIRGINIA VERDE',NULL,NULL,NULL,NULL,'Secundaria','bachillerato',NULL,'virginia.waleska.verde.de.quero@ueipab.edu.ve',NULL,NULL,NULL,'full_time',40,0,NULL,NULL,1,'2025-2026','2025-09-27 15:44:32','2025-09-28 20:11:19'),
(91,NULL,'ROBERT QUIJADA',NULL,NULL,NULL,NULL,'Secundaria',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-2026','2025-09-28 21:18:24',NULL),
(92,NULL,'LUISA ABREU',NULL,NULL,NULL,NULL,'Secundaria',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-2026','2025-09-28 21:18:24',NULL),
(93,NULL,'LUISA ELENA ABREU',NULL,NULL,NULL,NULL,'Secundaria',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-2026','2025-09-28 21:18:24',NULL),
(94,NULL,'ROBERT QUIJADA',NULL,NULL,NULL,NULL,'Secundaria',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-2026','2025-09-28 21:18:31',NULL),
(95,NULL,'LUISA ABREU',NULL,NULL,NULL,NULL,'Secundaria',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-2026','2025-09-28 21:18:31',NULL),
(96,NULL,'LUIS RODRIGUEZ',NULL,NULL,NULL,NULL,'Secundaria',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-2026','2025-09-28 21:23:51',NULL),
(97,NULL,'LUIS RODRÍGUEZ',NULL,NULL,NULL,NULL,'Secundaria',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-2026','2025-09-28 21:23:51',NULL);
/*!40000 ALTER TABLE `teachers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `time_periods`
--

DROP TABLE IF EXISTS `time_periods`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `time_periods` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `period_name` varchar(50) NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `is_break` tinyint(1) DEFAULT NULL,
  `schedule_type` varchar(20) DEFAULT NULL,
  `display_order` int(11) NOT NULL,
  `academic_year` varchar(10) NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=87 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `time_periods`
--

LOCK TABLES `time_periods` WRITE;
/*!40000 ALTER TABLE `time_periods` DISABLE KEYS */;
INSERT INTO `time_periods` VALUES
(1,'P1','07:00:00','07:40:00',0,'bimodal',1,'2025-2026',1),
(2,'P2','07:40:00','08:20:00',0,'bimodal',2,'2025-2026',1),
(3,'P3','08:20:00','09:00:00',0,'bimodal',3,'2025-2026',1),
(4,'P4','09:00:00','09:40:00',0,'bimodal',4,'2025-2026',1),
(5,'RECREO','09:40:00','10:00:00',1,'bimodal',5,'2025-2026',1),
(6,'P5','10:00:00','10:40:00',0,'bimodal',6,'2025-2026',1),
(7,'P6','10:40:00','11:20:00',0,'bimodal',7,'2025-2026',1),
(8,'P7','11:20:00','12:00:00',0,'bimodal',8,'2025-2026',1),
(9,'P8','12:00:00','12:40:00',0,'bimodal',9,'2025-2026',1),
(11,'P9','13:00:00','13:40:00',0,'bimodal',11,'2025-2026',1),
(12,'P10','14:00:00','14:20:00',0,'bimodal',12,'2025-2026',1),
(85,'ALMUERZO','12:40:00','13:00:00',1,NULL,9,'2025-2026',1);
/*!40000 ALTER TABLE `time_periods` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'ueipab_2025_data'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-09-29  8:20:40
