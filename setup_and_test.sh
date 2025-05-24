#!/bin/bash
# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/setup_and_test.sh
# This script installs all dependencies and runs tests with detailed logging

set -e  # Exit on first error

PROJECT_DIR="$(pwd)"
echo "Working in: $PROJECT_DIR"

# Create a log file
LOG_FILE="${PROJECT_DIR}/test_setup.log"
echo "Setup started at $(date)" > "${LOG_FILE}"

# Determine Python and pip commands
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
else
    PIP_CMD="pip"
fi

echo "Using Python: $($PYTHON_CMD --version)" | tee -a "${LOG_FILE}"
echo "Using pip: $($PIP_CMD --version)" | tee -a "${LOG_FILE}"

# Function to install a package and log the result
install_package() {
    local package=$1
    local version=$2
    
    echo "Installing $package${version:+ version $version}..." | tee -a "${LOG_FILE}"
    
    if [ -n "$version" ]; then
        $PIP_CMD install "$package==$version" 2>&1 | tee -a "${LOG_FILE}"
    else
        $PIP_CMD install "$package" 2>&1 | tee -a "${LOG_FILE}"
    fi
    
    if $PIP_CMD list | grep -i -q "$package"; then
        echo "✅ $package installed successfully" | tee -a "${LOG_FILE}"
    else
        echo "❌ Failed to install $package" | tee -a "${LOG_FILE}"
    fi
}

echo "======================================================"
echo "Step 1: Installing core testing dependencies"
echo "======================================================"

install_package "pytest" "8.3.5"
install_package "pytest-mock" "3.10.0"
install_package "pytest-cov" "4.1.0"
install_package "httpx" "0.26.0"
install_package "fastapi" "0.108.0"
install_package "sqlalchemy" "2.0.0"

echo "======================================================"
echo "Step 2: Installing authentication dependencies"
echo "======================================================"

install_package "python-jose" "3.3.0"
install_package "passlib" "1.7.4"
install_package "python-multipart" "0.0.9"

echo "======================================================"
echo "Step 3: Installing utility packages"
echo "======================================================"

install_package "python-slugify" "8.0.4"
install_package "pydantic" "2.6.0"
install_package "uvicorn" "0.25.0"
install_package "requests" "2.31.0"

echo "======================================================"
echo "Step 4: Installing database drivers"
echo "======================================================"

install_package "psycopg2-binary" "2.9.9" || echo "Skipping PostgreSQL driver, will use SQLite for tests"

echo "======================================================"
echo "Step 5: Running test setup script"
echo "======================================================"

bash ./update_tests.sh | tee -a "${LOG_FILE}"

echo "======================================================"
echo "Step 6: Running tests with SQLite"
echo "======================================================"

# Use environment variables to ensure proper test setup
PYTHONPATH=. DATABASE_URL="sqlite:///:memory:" $PYTHON_CMD run_tests.py tests/test_worker.py | tee -a "${LOG_FILE}"

echo "======================================================"
echo "Tests complete! Check test_setup.log for details."
echo "======================================================"

echo "To view all test logs, run: cat ${LOG_FILE}"
