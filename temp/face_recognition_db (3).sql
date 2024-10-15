-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3307
-- Generation Time: Sep 30, 2024 at 05:31 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `face_recognition_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `admins`
--

CREATE TABLE `admins` (
  `login_name` varchar(20) NOT NULL COMMENT 'اسم الدخول',
  `full_name` varchar(40) NOT NULL COMMENT 'الاسم بالكامل',
  `phone_no` varchar(10) NOT NULL COMMENT 'رقم الهاتف',
  `email` varchar(50) NOT NULL COMMENT 'البريد الإلكتروني',
  `password` char(64) NOT NULL COMMENT 'كلمة السر Sha256'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='جدول بيانات المسؤولين';

-- --------------------------------------------------------

--
-- Table structure for table `faces`
--

CREATE TABLE `faces` (
  `id` int(11) NOT NULL COMMENT 'رقم تسلسلي',
  `ref_no` varchar(20) NOT NULL COMMENT 'الرقم التعريفي للشخصية كالرقم الوظيفي مثلا',
  `name` varchar(50) NOT NULL COMMENT 'اسم الشخصية',
  `data` mediumblob NOT NULL COMMENT 'البصمة الرقمية للوجه'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='جدول البصمات الرقمية لوجوه الشخصيات';

--
-- Dumping data for table `faces`
--

INSERT INTO `faces` (`id`, `ref_no`, `name`, `data`) VALUES
(1, '3', 'adele',0xffd8ffe100 );

-- --------------------------------------------------------

--
-- Table structure for table `recognized_faces`
--

CREATE TABLE `recognized_faces` (
  `id` int(11) NOT NULL COMMENT 'رقم تسلسلي',
  `date_time` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'بصمة التاريخ والوقت',
  `face_id` int(11) NOT NULL COMMENT 'رابط سجل الوجه',
  `snapshot` mediumblob NOT NULL COMMENT 'لقطة عند التعرف',
  `category` enum('ENTERING','LEAVING') NOT NULL COMMENT 'تصنيف : دخول والانصراف'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='جدول حركات التعرف على الوجوه';

--
-- Dumping data for table `recognized_faces`
--

INSERT INTO `recognized_faces` (`id`, `date_time`, `face_id`, `snapshot`, `category`) VALUES
(1, '2024-08-19 02:58:11', 1,dddddd, 'ENTERING');
INSERT INTO `recognized_faces` (`id`, `date_time`, `face_id`, `snapshot`, `category`) VALUES
(2, '2024-08-19 02:59:58', 1, dsdsd, 'LEAVING');

-- --------------------------------------------------------

--
-- Table structure for table `unrecognized_faces`
--

CREATE TABLE `unrecognized_faces` (
  `id` int(11) NOT NULL COMMENT 'رقم تسلسلي',
  `date_time` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'بصمة التاريخ والوقت',
  `category` enum('ENTERING','LEAVING') NOT NULL COMMENT 'التصنيف: دخول ام خروج',
  `snapshot` mediumblob NOT NULL COMMENT 'لقطة عند التعرف'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='جدول حركات عدم التعرف على الوجوه';

--
-- Dumping data for table `unrecognized_faces`
--

INSERT INTO `unrecognized_faces` (`id`, `date_time`, `category`, `snapshot`) VALUES
(1, '2024-08-19 02:37:40', 'ENTERING', dssd);
INSERT INTO `unrecognized_faces` (`id`, `date_time`, `category`, `snapshot`) VALUES
(2, '2024-08-19 02:37:45', 'LEAVING', sd);
--
-- Indexes for dumped tables
--

--
-- Indexes for table `admins`
--
ALTER TABLE `admins`
  ADD PRIMARY KEY (`login_name`);

--
-- Indexes for table `faces`
--
ALTER TABLE `faces`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unqRefNo` (`ref_no`),
  ADD KEY `idxName` (`name`(25)) USING BTREE;

--
-- Indexes for table `recognized_faces`
--
ALTER TABLE `recognized_faces`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idxFace` (`face_id`);

--
-- Indexes for table `unrecognized_faces`
--
ALTER TABLE `unrecognized_faces`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `faces`
--
ALTER TABLE `faces`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'رقم تسلسلي', AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT for table `recognized_faces`
--
ALTER TABLE `recognized_faces`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'رقم تسلسلي', AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `unrecognized_faces`
--
ALTER TABLE `unrecognized_faces`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'رقم تسلسلي', AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `recognized_faces`
--
ALTER TABLE `recognized_faces`
  ADD CONSTRAINT `regognized_faces_ibfk_1` FOREIGN KEY (`face_id`) REFERENCES `faces` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
