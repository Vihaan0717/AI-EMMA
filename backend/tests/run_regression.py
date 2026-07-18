import pytest
import sys
import os
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="JARVIS-X Regression Test Runner")
    parser.add_argument('--mock', action='store_true', help="Run tests with mocked LLM/APIs (faster, cost-free)")
    parser.add_argument('--html', action='store_true', help="Generate HTML report")
    args = parser.parse_args()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Regression Suite...")
    
    # Set environment variables for tests
    os.environ['TEST_MODE'] = '1'
    if args.mock:
        os.environ['MOCK_APIS'] = '1'
        print("-> Running in MOCK mode (APIs and LLMs will be bypassed).")
    else:
        print("-> Running in LIVE mode (APIs and LLMs will be hit).")

    # Build pytest arguments
    pytest_args = ["-v", "--tb=short"]
    
    if args.html:
        report_path = os.path.join(os.path.dirname(__file__), "regression_report.html")
        pytest_args.extend([f"--html={report_path}", "--self-contained-html"])

    # Target directory is the current directory
    target_dir = os.path.dirname(__file__)
    pytest_args.append(target_dir)

    print(f"\nExecuting pytest with args: {' '.join(pytest_args)}\n")
    
    # Run pytest
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print("\n✅ Regression Test Suite PASSED. All systems nominal.")
    else:
        print("\n❌ Regression Test Suite FAILED. Please review the errors above.")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
