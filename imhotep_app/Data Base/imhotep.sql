-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 25, 2025 at 06:10 PM
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
-- Database: `imhotep`
--

-- --------------------------------------------------------

--
-- Table structure for table `doctor_portal`
--

CREATE TABLE `doctor_portal` (
  `User_ID` int(11) DEFAULT NULL,
  `doctor_ID` int(11) NOT NULL,
  `Patient_ID` int(11) DEFAULT NULL,
  `Doctor_Name` varchar(100) DEFAULT NULL,
  `Pr_ID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `doctor_portal`
--

INSERT INTO `doctor_portal` (`User_ID`, `doctor_ID`, `Patient_ID`, `Doctor_Name`, `Pr_ID`) VALUES
(1, 501, 101, 'Dr. John Smith', 201),
(1, 501, 103, 'Dr. John Smith', 203),
(4, 502, 102, 'Dr. Emily Davis', 202),
(4, 502, 104, 'Dr. Emily Davis', 204),
(4, 502, 105, 'Dr. Emily Davis', 205);

-- --------------------------------------------------------

--
-- Table structure for table `patient_portal`
--

CREATE TABLE `patient_portal` (
  `Patient_ID` int(11) NOT NULL,
  `User_ID` int(11) DEFAULT NULL,
  `User_Name` varchar(100) DEFAULT NULL,
  `Doctor_sugg` text DEFAULT NULL,
  `Pr_ID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `patient_portal`
--

INSERT INTO `patient_portal` (`Patient_ID`, `User_ID`, `User_Name`, `Doctor_sugg`, `Pr_ID`) VALUES
(101, 2, 'Alice Green', 'Headache and mild fever', 201),
(102, 3, 'Bob Brown', 'Sore throat and cough', 202),
(103, 2, 'Alice Green', 'High blood pressure', 203),
(104, 3, 'Bob Brown', 'Seasonal allergy and sneezing', 204),
(105, 2, 'Alice Green', 'Mild flu and fatigue', 205);

-- --------------------------------------------------------

--
-- Table structure for table `pharmacist_portal`
--

CREATE TABLE `pharmacist_portal` (
  `User_ID` int(11) DEFAULT NULL,
  `Pharma_ID` int(11) NOT NULL,
  `Patient_UID` int(11) DEFAULT NULL,
  `Pr_ID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pharmacist_portal`
--

INSERT INTO `pharmacist_portal` (`User_ID`, `Pharma_ID`, `Patient_UID`, `Pr_ID`) VALUES
(5, 601, 101, 201),
(5, 601, 102, 202),
(5, 601, 103, 203),
(5, 601, 104, 204),
(5, 601, 105, 205);

-- --------------------------------------------------------

--
-- Table structure for table `prescription`
--

CREATE TABLE `prescription` (
  `Pr_ID` int(11) NOT NULL,
  `Patient_ID` int(11) DEFAULT NULL,
  `Doctor_Sugg` text DEFAULT NULL,
  `Prescription` text DEFAULT NULL,
  `Visit_Date` date DEFAULT NULL,
  `Dispense` tinyint(4) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `prescription`
--

INSERT INTO `prescription` (`Pr_ID`, `Patient_ID`, `Doctor_Sugg`, `Prescription`, `Visit_Date`, `Dispense`) VALUES
(5, 112233, 'Frommmm doctors note sami is sick', 'From Presciption take napa twice a day', NULL, 1);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `User_ID` int(11) NOT NULL,
  `User_Name` varchar(100) NOT NULL,
  `Password` varchar(100) NOT NULL,
  `match` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`User_ID`, `User_Name`, `Password`, `match`) VALUES
(112233, 'Syed Sami Sayem', '$2b$12$FqRHD1x/GzbPhRpkUDHJLO.lEAQM4mFp7MeGpA.7zNxxVaDPfSvBm', '$2b$12$5ioHOhk6nWGgQ.iaiN0t7usjrqJhtDL1GtBv2EHzi/JtAahhHCdJS');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `patient_portal`
--
ALTER TABLE `patient_portal`
  ADD PRIMARY KEY (`Patient_ID`);

--
-- Indexes for table `prescription`
--
ALTER TABLE `prescription`
  ADD PRIMARY KEY (`Pr_ID`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`User_ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `prescription`
--
ALTER TABLE `prescription`
  MODIFY `Pr_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
