CREATE DATABASE IF NOT EXISTS Employees
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE Employees;

CREATE TABLE IF NOT EXISTS employees (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(100)   NOT NULL,
    position  VARCHAR(100)   NOT NULL,
    salary    DECIMAL(10, 2) NOT NULL CHECK (salary >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- To insert sample data into the employees table, you can use the following SQL statement:

INSERT INTO employees (name, position, salary) VALUES
('Asha Verma', 'Software Engineer', 65000.00),
('Rohit Sharma', 'Product Manager', 82000.00);

