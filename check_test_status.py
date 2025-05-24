#!/usr/bin/env python3
# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/check_test_status.py

import subprocess
import re
import sys
import os
from collections import defaultdict

# Ensure we're in the correct directory
project_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_path)

def run_tests_and_collect_results():
    """Run the tests and collect the results."""
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/", "-v"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.output

def parse_test_output(output):
    """Parse the test output to collect pass/fail information."""
    test_results = defaultdict(list)
    categories = defaultdict(lambda: {"passed": 0, "failed": 0, "skipped": 0})
    
    lines = output.splitlines()
    for line in lines:
        if not line.strip() or "===" in line or "..." in line:
            continue
            
        # Match patterns like:
        # tests/test_worker.py::test_mock_extract_video_data PASSED
        # tests/api/test_auth.py::test_register_user FAILED
        test_match = re.search(r'(tests/(?:([^/]+)/)?([^:]+)::([^ ]+)) (PASSED|FAILED|SKIPPED)', line)
        if test_match:
            full_path = test_match.group(1)
            category = test_match.group(2) if test_match.group(2) else "base"
            file = test_match.group(3)
            test_name = test_match.group(4)
            result = test_match.group(5)
            
            test_key = f"{category}/{file}" if category != "base" else file
            
            if result == "PASSED":
                test_results[test_key].append((test_name, "PASSED"))
                categories[category]["passed"] += 1
            elif result == "FAILED":
                test_results[test_key].append((test_name, "FAILED"))
                categories[category]["failed"] += 1
            elif result == "SKIPPED":
                test_results[test_key].append((test_name, "SKIPPED"))
                categories[category]["skipped"] += 1
    
    return test_results, categories

def print_test_summary(test_results, categories):
    """Print a summary of the test results."""
    print("=" * 80)
    print("TEST STATUS SUMMARY")
    print("=" * 80)
    
    total_passed = sum(cat["passed"] for cat in categories.values())
    total_failed = sum(cat["failed"] for cat in categories.values())
    total_skipped = sum(cat["skipped"] for cat in categories.values())
    total_tests = total_passed + total_failed + total_skipped
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed:      {total_passed} ({total_passed/total_tests*100:.1f}%)")
    print(f"Failed:      {total_failed} ({total_failed/total_tests*100:.1f}%)")
    print(f"Skipped:     {total_skipped} ({total_skipped/total_tests*100:.1f}%)")
    print("\nTest Categories:")
    print("-" * 80)
    print(f"{'Category':<15} {'Total':<10} {'Passed':<10} {'Failed':<10} {'Skipped':<10}")
    print("-" * 80)
    
    for category, counts in sorted(categories.items()):
        total = counts["passed"] + counts["failed"] + counts["skipped"]
        print(f"{category:<15} {total:<10} {counts['passed']:<10} {counts['failed']:<10} {counts['skipped']:<10}")
        
    print("\nDetailed Results:")
    print("-" * 80)
    for file, tests in sorted(test_results.items()):
        print(f"\n{file}:")
        for test_name, result in tests:
            status = "✅" if result == "PASSED" else "❌" if result == "FAILED" else "⏩"
            print(f"  {status} {test_name}")
    
    print("\n")
    total = total_passed + total_failed
    if total_passed == total:
        print("✅ ALL TESTS PASSING")
    else:
        pass_percent = (total_passed / total) * 100 if total > 0 else 0
        print(f"⚠️  TESTS ARE {pass_percent:.1f}% PASSING ({total_passed}/{total})")
    
    print("=" * 80)

def main():
    output = run_tests_and_collect_results()
    test_results, categories = parse_test_output(output)
    print_test_summary(test_results, categories)
    
    # Return a non-zero exit code if any tests failed
    return 1 if sum(cat["failed"] for cat in categories.values()) > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
