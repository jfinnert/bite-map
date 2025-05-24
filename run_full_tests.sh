#!/bin/bash
# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/run_full_tests.sh
#
# This script runs the full test suite in both local (SQLite) and Docker (PostgreSQL) modes
# and generates a comprehensive test report.

set -e  # Exit on first error

# Initialize variables
SKIP_LOCAL=0
SKIP_DOCKER=0
HTML_REPORT=0
PUBLISH_REPORT=0
COVERAGE=0

# Process command-line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --skip-local)
      SKIP_LOCAL=1
      shift
      ;;
    --skip-docker)
      SKIP_DOCKER=1
      shift
      ;;
    --html)
      HTML_REPORT=1
      shift
      ;;
    --publish-report)
      PUBLISH_REPORT=1
      HTML_REPORT=1
      shift
      ;;
    --coverage)
      COVERAGE=1
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--skip-local] [--skip-docker] [--html] [--coverage] [--publish-report]"
      exit 1
      ;;
  esac
done

# Create reports directory
mkdir -p test-reports

# Print header
echo "====================================================="
echo "BiteMap Full Test Suite Runner"
echo "====================================================="
echo "Running tests on $(date)"
echo

# Run update_tests.sh to ensure dependencies
echo "Ensuring test dependencies..."
bash ./update_tests.sh

# Initialize report
REPORT_FILE="test-reports/full-test-report-$(date +%Y%m%d-%H%M%S).md"
echo "# Bite Map Full Test Report" > $REPORT_FILE
echo >> $REPORT_FILE
echo "**Date:** $(date)" >> $REPORT_FILE
echo >> $REPORT_FILE
echo "## Test Summary" >> $REPORT_FILE
echo >> $REPORT_FILE

# Run local tests with SQLite if not skipped
if [ $SKIP_LOCAL -eq 0 ]; then
  echo "====================================================="
  echo "Running Local Tests (SQLite)"
  echo "====================================================="
  
  START_TIME=$(date +%s)
  
  # Build the command
  CMD="python run_tests.py"
  
  # Add options
  if [ $HTML_REPORT -eq 1 ]; then
    CMD="$CMD --html"
  fi
  
  if [ $COVERAGE -eq 1 ]; then
    CMD="$CMD --coverage"
  fi
  
  # Add report flag
  CMD="$CMD --report tests/"
  
  # Run the command
  if $CMD; then
    LOCAL_RESULT="PASS"
  else
    LOCAL_RESULT="FAIL"
  fi
  
  END_TIME=$(date +%s)
  LOCAL_DURATION=$((END_TIME - START_TIME))
  
  echo >> $REPORT_FILE
  echo "### Local Tests (SQLite)" >> $REPORT_FILE
  echo >> $REPORT_FILE
  echo "* **Result:** $LOCAL_RESULT" >> $REPORT_FILE
  echo "* **Duration:** ${LOCAL_DURATION}s" >> $REPORT_FILE
  echo >> $REPORT_FILE
fi

# Run Docker tests with PostgreSQL if not skipped
if [ $SKIP_DOCKER -eq 0 ]; then
  echo "====================================================="
  echo "Running Docker Tests (PostgreSQL)"
  echo "====================================================="
  
  START_TIME=$(date +%s)
  
  # Ensure the Docker containers are up
  docker-compose -f docker-compose.test.yml up -d
  
  # Run tests in container
  if docker-compose -f docker-compose.test.yml exec test bash -c "cd /project && PYTHONPATH=/project pytest -v tests/ > /project/test-reports/docker-test-output.txt 2>&1"; then
    DOCKER_RESULT="PASS"
  else
    DOCKER_RESULT="FAIL"
  fi
  
  # Copy the output to the report
  echo >> $REPORT_FILE
  echo "### Docker Tests (PostgreSQL)" >> $REPORT_FILE
  echo >> $REPORT_FILE
  echo "* **Result:** $DOCKER_RESULT" >> $REPORT_FILE
  if [ -f "test-reports/docker-test-output.txt" ]; then
    echo "* **Output:**" >> $REPORT_FILE
    echo '```' >> $REPORT_FILE
    cat test-reports/docker-test-output.txt >> $REPORT_FILE
    echo '```' >> $REPORT_FILE
  fi
  
  END_TIME=$(date +%s)
  DOCKER_DURATION=$((END_TIME - START_TIME))
  echo "* **Duration:** ${DOCKER_DURATION}s" >> $REPORT_FILE
  echo >> $REPORT_FILE
  
  # Shut down Docker containers
  docker-compose -f docker-compose.test.yml down
fi

# Generate final summary
echo >> $REPORT_FILE
echo "## Final Summary" >> $REPORT_FILE
echo >> $REPORT_FILE

if [ $SKIP_LOCAL -eq 0 ] && [ $SKIP_DOCKER -eq 0 ]; then
  if [ "$LOCAL_RESULT" = "PASS" ] && [ "$DOCKER_RESULT" = "PASS" ]; then
    FINAL_RESULT="✅ PASS"
  else
    FINAL_RESULT="❌ FAIL"
  fi
  echo "* **Overall Result:** $FINAL_RESULT" >> $REPORT_FILE
  
  TOTAL_DURATION=$((LOCAL_DURATION + DOCKER_DURATION))
  echo "* **Total Duration:** ${TOTAL_DURATION}s" >> $REPORT_FILE
elif [ $SKIP_LOCAL -eq 0 ]; then
  echo "* **Overall Result:** $LOCAL_RESULT" >> $REPORT_FILE
  echo "* **Total Duration:** ${LOCAL_DURATION}s" >> $REPORT_FILE
elif [ $SKIP_DOCKER -eq 0 ]; then
  echo "* **Overall Result:** $DOCKER_RESULT" >> $REPORT_FILE
  echo "* **Total Duration:** ${DOCKER_DURATION}s" >> $REPORT_FILE
fi

# Print report path
echo "====================================================="
echo "Test report generated at: $REPORT_FILE"
echo "====================================================="

# Open the report in a browser if requested
if [ $PUBLISH_REPORT -eq 1 ]; then
  if command -v python3 &> /dev/null; then
    python3 -m http.server --directory test-reports/ 8000 &
    SERVER_PID=$!
    echo "Report server running at http://localhost:8000"
    echo "Press Ctrl+C to stop the server"
    
    # Convert the markdown to HTML if pandoc is available
    if command -v pandoc &> /dev/null; then
      HTML_FILE=${REPORT_FILE%.md}.html
      pandoc $REPORT_FILE -o $HTML_FILE
      echo "HTML report available at: $HTML_FILE"
    fi
    
    # Try to open in browser
    if command -v xdg-open &> /dev/null; then
      xdg-open http://localhost:8000
    elif command -v open &> /dev/null; then
      open http://localhost:8000
    fi
    
    # Wait for user to press Ctrl+C
    trap 'kill $SERVER_PID; exit 0' INT
    wait $SERVER_PID
  else
    echo "Python 3 not found, cannot start HTTP server"
  fi
fi

# Determine final exit code
if [ $SKIP_LOCAL -eq 0 ] && [ "$LOCAL_RESULT" = "FAIL" ]; then
  exit 1
elif [ $SKIP_DOCKER -eq 0 ] && [ "$DOCKER_RESULT" = "FAIL" ]; then
  exit 1
else
  exit 0
fi
