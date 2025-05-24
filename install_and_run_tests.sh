#!/bin/bash
# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/install_and_run_tests.sh
#
# This script installs all required test dependencies and runs tests

set -e  # Exit on first error

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

echo "======================================================"
echo "Installing test dependencies for Bite Map"
echo "======================================================"

# Install all test dependencies
if [ -f "test-requirements.txt" ]; then
    echo "Installing from test-requirements.txt..."
    $PIP_CMD install -r test-requirements.txt
    
    # Check if installation was successful
    if [ $? -ne 0 ]; then
        echo "Error: Some packages couldn't be installed."
        echo "Installing critical packages individually..."
        $PIP_CMD install pytest pytest-mock
    fi
else
    echo "Error: test-requirements.txt not found!"
    exit 1
fi

# Run the update_tests.sh script to ensure test setup is correct
echo "======================================================"
echo "Setting up test environment..."
echo "======================================================"
bash ./update_tests.sh

# Run the tests using our hybrid approach
echo "======================================================"
echo "Running tests with SQLite (faster local testing)..."
echo "======================================================"
$PYTHON_CMD run_tests.py --in-memory tests/test_worker.py

# If that succeeded, let's try to run more tests
if [ $? -eq 0 ]; then
    echo "======================================================"
    echo "Worker tests passed! Running more tests..."
    echo "======================================================"
    $PYTHON_CMD run_tests.py --in-memory tests/
fi

echo "======================================================"
echo "Test execution complete!"
echo "======================================================"
echo "For a complete test report, run: ./run_full_tests.sh"
