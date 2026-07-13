#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DB_HOST="${DB_HOST:-localhost}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME="${DB_NAME:-Employees}"

echo "[1/4] Checking Python..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found. Please install Python 3 and try again."
  exit 1
fi

echo "[2/4] Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install mysql-connector-python pyinstaller

echo "[3/4] Preparing the database..."
if command -v mysql >/dev/null 2>&1; then
  MYSQL_CMD=(mysql -h "$DB_HOST" -u "$DB_USER")
  if [ -n "$DB_PASSWORD" ]; then
    MYSQL_CMD+=(--password="$DB_PASSWORD")
  fi
  echo "Running database schema import..."
  if "${MYSQL_CMD[@]}" < Database_Schema.sql; then
    echo "Database setup completed successfully."
  else
    echo "Database import failed. Please verify your MySQL credentials and try again."
  fi
else
  echo "MySQL client not found. Make sure XAMPP or MySQL is installed and mysql is available on PATH."
  echo "If the database is not created yet, import Database_Schema.sql manually in phpMyAdmin."
fi

echo "[4/4] Starting the application..."
export DB_HOST DB_USER DB_PASSWORD DB_NAME
if [ -x "$SCRIPT_DIR/dist/EmployeeManagementSystem.exe" ] || [ -x "$SCRIPT_DIR/dist/EmployeeManagementSystem" ]; then
  echo "Launching packaged executable..."
  if [ -x "$SCRIPT_DIR/dist/EmployeeManagementSystem.exe" ]; then
    "$SCRIPT_DIR/dist/EmployeeManagementSystem.exe"
  else
    "$SCRIPT_DIR/dist/EmployeeManagementSystem"
  fi
else
  echo "Launching Python app..."
  python3 main.py
fi
