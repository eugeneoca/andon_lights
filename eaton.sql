-- phpMyAdmin SQL Dump
-- version 4.8.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 29, 2018 at 05:43 AM
-- Server version: 10.1.32-MariaDB
-- PHP Version: 7.2.5

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
(1, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '2', '2018-08-29 01:42:28'),
(2, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '3', '2018-08-29 01:42:30'),
(3, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '4', '2018-08-29 01:42:32'),
(4, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '1', '2018-08-29 01:42:34'),
(5, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '2', '2018-08-29 06:46:57'),
(6, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '3', '2018-08-29 06:47:01'),
(7, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '3', '2018-08-29 06:47:03'),
(8, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '3', '2018-08-29 06:47:05'),
(9, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '4', '2018-08-29 06:47:07'),
(10, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '4', '2018-08-29 11:33:16'),
(11, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '4', '2018-08-29 11:33:18'),
(12, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '4', '2018-08-29 11:33:20'),
(13, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '4', '2018-08-29 11:33:22'),
(14, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '4', '2018-08-29 11:33:24'),
(15, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '4', '2018-08-29 11:33:26'),
(16, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '4', '2018-08-29 11:33:28'),
(17, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '4', '2018-08-29 11:33:30'),
(18, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '4', '2018-08-29 11:33:32'),
(19, 'pl01', '192.168.1.21', 'a8:1e:84:ab:89:ed', '2', '2018-08-29 11:33:38'),
(20, 'pl01', '169.254.228.219', 'a8:1e:84:ab:89:ed', '2', '2018-08-29 11:41:37');

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
-- Indexes for dumped tables
--

--
-- Indexes for table `reports`
--
ALTER TABLE `reports`
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
-- AUTO_INCREMENT for table `tbl_plnames`
--
ALTER TABLE `tbl_plnames`
  MODIFY `id` int(100) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
