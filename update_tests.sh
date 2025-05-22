#!/bin/bash

# Script to update test files with improved versions
echo "Updating test files with improved versions..."

# Backup the original files
cp -f /Users/josh/Python/3.7/Bite\ Map\ Project/bite-map/tests/conftest.py /Users/josh/Python/3.7/Bite\ Map\ Project/bite-map/tests/conftest.py.bak2
cp -f /Users/josh/Python/3.7/Bite\ Map\ Project/bite-map/tests/api/test_auth.py /Users/josh/Python/3.7/Bite\ Map\ Project/bite-map/tests/api/test_auth.py.bak

# Replace with new versions
cp -f /Users/josh/Python/3.7/Bite\ Map\ Project/bite-map/tests/conftest.py.new /Users/josh/Python/3.7/Bite\ Map\ Project/bite-map/tests/conftest.py
cp -f /Users/josh/Python/3.7/Bite\ Map\ Project/bite-map/tests/api/test_auth.py.new /Users/josh/Python/3.7/Bite\ Map\ Project/bite-map/tests/api/test_auth.py

echo "Files updated successfully!"
