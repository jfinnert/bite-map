#!/usr/bin/env python3
# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/run_tests.py
"""
Helper script to run tests with PostgreSQL testcontainers and module mocking.

This script runs tests using PostgreSQL testcontainers for production-like validation
while providing fallback SQLite support for quick local development when PostgreSQL
containers are not available.

Usage:
    python run_tests.py [test_paths]
    
Options:
    --coverage: Run with coverage reporting
    --html: Generate HTML test report
    --sqlite: Fallback to SQLite for quick local development
"""

import os
import sys
import subprocess
import importlib
import argparse
from unittest import mock
import tempfile
import time
import shutil
from pathlib import Path

def setup_test_environment():
    """Set up the test environment with PostgreSQL testcontainers by default."""
    # Only set DATABASE_URL if not already set and --sqlite flag is used
    if not os.environ.get("DATABASE_URL") and getattr(setup_test_environment, "use_sqlite", False):
        if getattr(setup_test_environment, "use_in_memory", False):
            os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        else:
            # Use file-based SQLite for fallback
            os.environ["DATABASE_URL"] = "sqlite:///./test.db"
        print("Using SQLite fallback for testing")
    
    # Set test environment variables
    os.environ["TESTING"] = "1"
    os.environ["DEBUG"] = "1"
    
    # Ensure import paths are set up correctly
    root_dir = Path(__file__).parent.absolute()
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    
    app_dir = root_dir / "app"
    if app_dir.exists() and str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    
    # Mock hard-to-install modules
    mock_geoalchemy()
    
def mock_geoalchemy():
    """Mock GeoAlchemy2 module for tests."""
    # Only mock if not already mocked and not installed
    if 'geoalchemy2' in sys.modules:
        return
    
    try:
        import geoalchemy2
        return  # Module exists, no need to mock
    except ImportError:
        pass
    
    # Create mock modules
    sys.modules['geoalchemy2'] = mock.MagicMock()
    sys.modules['geoalchemy2.functions'] = mock.MagicMock()
    sys.modules['geoalchemy2.elements'] = mock.MagicMock()
    sys.modules['geoalchemy2.types'] = mock.MagicMock()

    # Create a Geography class mock
    class MockGeography:
        def __init__(self, *args, **kwargs):
            pass
            
    # Add mocks to geoalchemy2 module
    sys.modules['geoalchemy2'].Geography = MockGeography
    sys.modules['geoalchemy2'].types.Geography = MockGeography
    sys.modules['geoalchemy2'].functions.ST_DWithin = lambda *args: None
    sys.modules['geoalchemy2'].functions.ST_Distance = lambda *args: None
    sys.modules['geoalchemy2'].functions.ST_MakePoint = lambda *args: None
    sys.modules['geoalchemy2'].elements.WKTElement = lambda *args, **kwargs: None

def create_test_report(test_results):
    """Create a test report from the test results."""
    report_dir = Path("test-reports")
    report_dir.mkdir(exist_ok=True)
    
    report_path = report_dir / f"test-report-{time.strftime('%Y%m%d-%H%M%S')}.md"
    
    with open(report_path, "w") as f:
        f.write("# Bite Map Test Report\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Database:** {os.environ.get('DATABASE_URL', 'Unknown')}\n\n")
        f.write(f"**Result:** {'PASS' if test_results.returncode == 0 else 'FAIL'}\n\n")
        
        if test_results.stdout:
            f.write("## Test Output\n\n```\n")
            f.write(test_results.stdout.decode('utf-8', errors='replace'))
            f.write("\n```\n\n")
        
        if test_results.returncode != 0 and test_results.stderr:
            f.write("## Errors\n\n```\n")
            f.write(test_results.stderr.decode('utf-8', errors='replace'))
            f.write("\n```\n\n")
    
    print(f"Test report created at: {report_path}")
    return report_path

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run tests with PostgreSQL testcontainers by default.")
    parser.add_argument('test_paths', nargs='*', default=["tests/"], 
                      help="Paths to test files or directories")
    parser.add_argument('--coverage', action='store_true', help="Run with coverage")
    parser.add_argument('--html', action='store_true', help="Generate HTML test report")
    parser.add_argument('--sqlite', action='store_true', help="Use SQLite for quick local development")
    parser.add_argument('--in-memory', action='store_true', help="Use in-memory SQLite (requires --sqlite)")
    parser.add_argument('--report', action='store_true', help="Generate test report")
    return parser.parse_args()

def main():
    """Run the tests with PostgreSQL testcontainers by default."""
    args = parse_args()
    
    # Set SQLite fallback flags for setup_test_environment
    if args.sqlite:
        setup_test_environment.use_sqlite = True
        if args.in_memory:
            setup_test_environment.use_in_memory = True
    
    # Set up test environment
    setup_test_environment()
    
    if args.sqlite:
        print(f"Running tests with SQLite fallback: {os.environ.get('DATABASE_URL', 'PostgreSQL testcontainers')}")
    else:
        print("Running tests with PostgreSQL testcontainers (default)")
    
    # Try to import pytest
    try:
        import pytest
        has_pytest = True
    except ImportError:
        has_pytest = False
        print("WARNING: pytest not found, falling back to subprocess")
    
    # Prepare command arguments
    pytest_args = ["-v"]
    
    # Add coverage if requested
    if args.coverage:
        pytest_args.extend(["--cov=.", "--cov-report=term", "--cov-report=html:test-reports/coverage"])
    
    # Add HTML report if requested
    if args.html:
        pytest_args.extend(["--html=test-reports/report.html", "--self-contained-html"])
    
    # Add test paths
    pytest_args.extend(args.test_paths)
    
    if has_pytest:
        # Run with pytest API
        exit_code = pytest.main(pytest_args)
        sys.exit(exit_code)
    else:
        # Run as subprocess
        cmd = [sys.executable, "-m", "pytest"] + pytest_args
        result = subprocess.run(cmd, capture_output=args.report)
        
        # Create report if requested
        if args.report:
            create_test_report(result)
        
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
