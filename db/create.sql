CREATE DATABASE IF NOT EXISTS `athletes_db`;
USE `athletes_db`;

CREATE TABLE IF NOT EXISTS users(
id INT primary key auto_increment,
mail_address varchar(100) not null,
password varchar(100) not null
);