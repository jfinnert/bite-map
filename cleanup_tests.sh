#!/bin/bash
# Script to clean up the duplicate app/tests directory now that tests are working

# Set variables
PROJECT_DIR="/Users/josh/Python/3.7/Bite Map Project/bite-map"
APP_TESTS_DIR="${PROJECT_DIR}/app/tests"
MAIN_TESTS_DIR="${PROJECT_DIR}/tests"
BACKUP_DIR="${PROJECT_DIR}/app/tests_backup_$(date +%Y%m%d)"

echo "Creating backup of app/tests before removing..."
mkdir -p "$BACKUP_DIR"
cp -r "$APP_TESTS_DIR"/* "$BACKUP_DIR/"

echo "Backup created at: $BACKUP_DIR"
echo "Removing app/tests directory..."

# Verify that the main tests directory exists and has content before removing app/tests
if [ -d "$MAIN_TESTS_DIR" ] && [ "$(ls -A "$MAIN_TESTS_DIR")" ]; then
    rm -rf "$APP_TESTS_DIR"
    echo "Successfully removed app/tests directory"
    echo "All tests are now consolidated in: $MAIN_TESTS_DIR"
else
    echo "ERROR: Main tests directory is missing or empty. Aborting cleanup."
    exit 1
fi

echo "Test cleanup complete."
