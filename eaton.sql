-- phpMyAdmin SQL Dump
-- version 4.8.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 30, 2018 at 09:19 AM
-- Server version: 10.1.34-MariaDB
-- PHP Version: 5.6.37

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `eaton`
--

-- --------------------------------------------------------

--
-- Table structure for table `reports`
--

CREATE TABLE `reports` (
  `id` int(10) NOT NULL,
  `devicename` varchar(100) NOT NULL,
  `ip` varchar(200) NOT NULL,
  `macaddress` varchar(100) NOT NULL,
  `status` varchar(10) NOT NULL,
  `datetime` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `reports`
--

INSERT INTO `reports` (`id`, `devicename`, `ip`, `macaddress`, `status`, `datetime`) VALUES
(11, 'pl01', '192.168.1.101', '94:b3:9f:fc:0f:c7', '1', '2018-08-30 15:01:36'),
(12, 'pl01', '192.168.1.101', '94:b3:9f:fc:0f:c7', '4', '2018-08-30 15:01:59'),
(13, 'pl01', '192.168.1.101', '94:b3:9f:fc:0f:c7', '3', '2018-08-30 15:02:41'),
(14, 'pl01', '192.168.1.101', '94:b3:9f:fc:0f:c7', '2', '2018-08-30 15:15:47'),
(15, 'pl01', '192.168.1.101', '94:b3:9f:fc:0f:c7', '1', '2018-08-30 15:16:08'),
(16, 'pl01', '192.168.1.101', '94:b3:9f:fc:0f:c7', '4', '2018-08-30 15:16:22'),
(17, 'pl01', '192.168.1.101', '94:b3:9f:fc:0f:c7', '3', '2018-08-30 15:16:28'),
(18, 'pl01', '192.168.1.101', '94:b3:9f:fc:0f:c7', '2', '2018-08-30 15:16:37'),
(19, 'pl01', '192.168.1.101', '94:b3:9f:fc:0f:c7', '4', '2018-08-30 15:16:43'),
(20, 'pl01', '192.168.1.101', '94:b3:9f:fc:0f:c7', '3', '2018-08-30 15:16:51');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_events`
--

CREATE TABLE `tbl_events` (
  `id` int(10) NOT NULL,
  `eventid` varchar(200) NOT NULL,
  `devicename` varchar(200) NOT NULL,
  `macaddress` varchar(200) NOT NULL,
  `datetime` varchar(200) NOT NULL,
  `remarks` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `tbl_events`
--

INSERT INTO `tbl_events` (`id`, `eventid`, `devicename`, `macaddress`, `datetime`, `remarks`) VALUES
(16, '94:b3:9f:fc:0f:c7', 'pl01', '94:b3:9f:fc:0f:c7', '2018-08-30 14:57:44pl01', '3');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_plnames`
--

CREATE TABLE `tbl_plnames` (
  `id` int(100) NOT NULL,
  `devicename` varchar(200) NOT NULL,
  `plname` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `tbl_plnames`
--

INSERT INTO `tbl_plnames` (`id`, `devicename`, `plname`) VALUES
(1, 'pl01', 'UV%20CELL%202');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `reports`
--
ALTER TABLE `reports`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_events`
--
ALTER TABLE `tbl_events`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_plnames`
--
ALTER TABLE `tbl_plnames`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `reports`
--
ALTER TABLE `reports`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `tbl_events`
--
ALTER TABLE `tbl_events`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `tbl_plnames`
--
ALTER TABLE `tbl_plnames`
  MODIFY `id` int(100) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
