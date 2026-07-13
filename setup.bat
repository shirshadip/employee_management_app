@echo off
setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "DB_HOST=localhost"
set "DB_USER=root"
set "DB_PASSWORD="
set "DB_NAME=Employees"

echo [1/4] Checking Python...
where python >nul 2>&1
if errorlevel 1 (
    echo Python was not found on PATH. Please install Python 3 and try again.
    exit /b 1
)

echo [2/4] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install mysql-connector-python pyinstaller

echo [3/4] Preparing the database...
where mysql >nul 2>&1
if errorlevel 1 (
    echo MySQL client not found. Make sure XAMPP or MySQL is installed and mysql.exe is available on PATH.
    echo If the database is not created yet, import Database_Schema.sql manually in phpMyAdmin.
) else (
    set "MYSQL_CMD=mysql -h !DB_HOST! -u !DB_USER!"
    if not "!DB_PASSWORD!"=="" set "MYSQL_CMD=!MYSQL_CMD! --password=!DB_PASSWORD!"
    echo Running database schema import...
    !MYSQL_CMD! < Database_Schema.sql
    if errorlevel 1 (
        echo Database import failed. Please verify your MySQL credentials and try again.
    ) else (
        echo Database setup completed successfully.
    )
)

echo [4/4] Starting the application...
set "DB_HOST=!DB_HOST!"
set "DB_USER=!DB_USER!"
set "DB_PASSWORD=!DB_PASSWORD!"
set "DB_NAME=!DB_NAME!"
if exist "%SCRIPT_DIR%dist\EmployeeManagementSystem.exe" (
    echo Launching packaged executable...
    "%SCRIPT_DIR%dist\EmployeeManagementSystem.exe"
) else (
    echo Launching Python app...
    python main.py
)
