# Employee Management System

A simple and clean desktop employee management application built with Python, Tkinter, and MySQL. It allows you to add, update, delete, search, and view employee records from a database.

# Windows Executable Application Download

[Download EmployeeManagementSystem.exe](./dist/EmployeeManagementSystem.exe)

## Features

- Add new employees
- Update selected employee details
- Delete employees safely
- Search employees by name or position
- Sort records by column
- Display salary summary totals
- Database connection configured through environment variables
- Build a standalone Windows executable with PyInstaller

## Tech Stack

- Python 3.9+
- Tkinter for the desktop UI
- MySQL / MariaDB
- mysql-connector-python
- PyInstaller

## Project Structure

- main.py — main application source entry point
- EmployeeManagementSystem.exe — generated Windows executable output
- Database_Schema.sql — MySQL database schema and sample data
- enviroment.bat — Windows CMD environment setup
- enviroment.ps1 — Windows PowerShell environment setup
- enviroment.zsh — macOS/Linux shell environment setup
- setup.bat — one-click Windows setup and launch script
- setup.sh — one-click macOS/Linux setup and launch script
- EmployeeManagementSystem.spec — PyInstaller build configuration

## Prerequisites

Before running this project, make sure you have:

- Python installed
- MySQL server running
- XAMPP (recommended for local development) or another MySQL setup
- pip available for installing Python packages

## 1. Install Python

Download and install Python from the official website:

https://www.python.org/downloads/

During installation, make sure to enable the option to add Python to PATH.

## 2. Install and Start XAMPP (Recommended)

If you are using XAMPP for MySQL:

1. Download and install XAMPP
2. Start the XAMPP Control Panel
3. Start Apache and MySQL
4. Open phpMyAdmin in your browser:
   - http://localhost/phpmyadmin

## 3. Create the Database

You can create the database in two ways:

### Option A — Import the SQL file

1. Open phpMyAdmin
2. Create a new database named Employees
3. Go to Import
4. Choose Database_Schema.sql
5. Click Go

### Option B — Run the SQL manually

Run the following SQL in MySQL:

```sql
CREATE DATABASE IF NOT EXISTS Employees
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE Employees;

CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL CHECK (salary >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

## 4. Set Up Environment Variables

The application reads database connection values from environment variables.

### Windows Command Prompt

```bat
set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=
set DB_NAME=Employees
```

### Windows PowerShell

```powershell
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD=""
$env:DB_NAME="Employees"
```

### macOS / Linux / zsh

```zsh
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=
export DB_NAME=Employees
```

You can also use the provided environment helper scripts:

- enviroment.bat for Windows CMD
- enviroment.ps1 for PowerShell
- enviroment.zsh for zsh/bash-compatible shells

## 5. Install Python Dependencies

Open a terminal in the project folder and run:

```bash
pip install mysql-connector-python pyinstaller
```

If you are using a virtual environment, activate it first.

## 6. Quick Setup with Automation Scripts

### Windows

Run:

```bat
setup.bat
```

### macOS / Linux

Run:

```bash
chmod +x setup.sh
./setup.sh
```

These scripts install the required Python packages, attempt to import the database schema, and launch the application.

## 7. Run the Application

For development:

```bash
python main.py
```

If you already built the packaged app, you can run the executable directly:

```bash
./dist/EmployeeManagementSystem.exe
```

On Windows, the packaged executable is typically named EmployeeManagementSystem.exe and will be launched automatically by the setup scripts when it exists.

If you used the environment helper scripts, run them first depending on your shell.

## 8. Build an Executable with PyInstaller

This project already includes a PyInstaller spec file.

### Build using the spec file

```bash
pyinstaller --clean EmployeeManagementSystem.spec
```

The executable will be generated in the dist folder.

### Manual build command

```bash
pyinstaller --onefile --windowed --icon app.ico --add-data "app.png;." --add-data "app.ico;." --name EmployeeManagementSystem main.py
```

> On macOS/Linux, replace the semicolon with a colon in the add-data paths.

## User Guidance

- Make sure MySQL is running before launching the app.
- If the app shows a connection error, verify your database credentials and server status.
- If the app cannot find the database, confirm that the database name matches DB_NAME.
- If you are using XAMPP, check that the MySQL service is running from the XAMPP Control Panel.
- The app uses the Employees database by default. You can change it using environment variables.

## Troubleshooting

### Module Not Found Error

If you see an error like mysql.connector not found:

```bash
pip install mysql-connector-python
```

### Database Connection Failed

Check the following:

- MySQL service is running
- Username and password are correct
- DB_HOST is correct
- Database name exists

### PyInstaller Not Found

```bash
pip install pyinstaller
```

## Contributing

Contributions are welcome.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution guide.

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

Please keep changes clean, documented, and tested where possible.

## License

This project is licensed under the MIT License.

See the LICENSE file for more details.
