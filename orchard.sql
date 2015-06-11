--
-- Database: `orchard`
--
CREATE DATABASE IF NOT EXISTS `orchard` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `orchard`;


-- ----------------------------------------------------------------------------
-- ----------------------------------------------------------------------------
-- ----------------------------------------------------------------------------


--
-- Table structure for table `store`
--
DROP TABLE IF EXISTS `store`;
CREATE TABLE IF NOT EXISTS `store` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL,
  `boro` varchar(20) DEFAULT NULL,
  `building` varchar(10) DEFAULT NULL,
  `street` varchar(100) DEFAULT NULL,
  `zipcode` varchar(10) DEFAULT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `cuisine` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for table `store`
--
ALTER TABLE `store` ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for table `store`
--
ALTER TABLE `store` MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;


-- ----------------------------------------------------------------------------
-- ----------------------------------------------------------------------------
-- ----------------------------------------------------------------------------


--
-- Table structure for table `violations`
--
DROP TABLE IF EXISTS `violations`;
CREATE TABLE IF NOT EXISTS `violations` (
  `id` int(11) NOT NULL,
  `store_id` int(11) DEFAULT NULL,
  `inspection_date` date DEFAULT NULL,
  `record_date` date DEFAULT NULL,
  `grade_date` date DEFAULT NULL,
  `grade` varchar(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for table `violations`
--
ALTER TABLE `violations` ADD PRIMARY KEY (`id`), ADD KEY `store_id` (`store_id`);

--
-- AUTO_INCREMENT for table `violations`
--
ALTER TABLE `violations` MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;


-- ----------------------------------------------------------------------------
-- ----------------------------------------------------------------------------
-- ----------------------------------------------------------------------------


--
-- Constraints for table `violations`
--
ALTER TABLE `violations`
  ADD CONSTRAINT `violations_ibfk_1` FOREIGN KEY (`store_id`) REFERENCES `store` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;