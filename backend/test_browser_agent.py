#!/usr/bin/env python3
"""
Interactive CLI for testing Browser Agent functionality
Provides easy menu-driven interface for testing LeetCode, Billing, and GitHub automation
"""
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tools.leetcode_tool import complete_leetcode_daily, get_leetcode_daily_problem
from tools.billing_tool import pay_electricity_bill, get_bill_amount, list_billing_providers
from tools.github_tool import create_github_issue, list_github_repos
from registry.tool_registry import tool_registry


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def get_mock_user_context() -> Dict[str, Any]:
    """Get mock user context for testing"""
    return {
        "sub": "test_user_cli_123",
        "email": "test@example.com",
        "name": "CLI Test User"
    }


def mock_mfa_check(*args, **kwargs):
    """Mock MFA check that always passes"""
    print_info("MFA/Consent check bypassed for testing")


# Patch MFA check for testing
import tools.leetcode_tool
import tools.billing_tool
import tools.github_tool
tools.leetcode_tool.check_mfa_and_consent = mock_mfa_check
tools.billing_tool.check_mfa_and_consent = mock_mfa_check
tools.github_tool.check_mfa_and_consent = mock_mfa_check


def test_leetcode_daily():
    """Test LeetCode daily challenge automation"""
    print_header("LeetCode Daily Challenge Test")
    
    print("This test will simulate solving LeetCode's daily challenge.\n")
    
    username = input("Enter LeetCode username (or press Enter for 'test_user'): ").strip() or "test_user"
    password = input("Enter LeetCode password (or press Enter for 'test_pass'): ").strip() or "test_pass"
    
    solution_code = """
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
"""
    
    print(f"\n{Colors.BOLD}Solution Code:{Colors.ENDC}")
    print(solution_code)
    
    language = input("\nSelect language (python3/java/cpp/javascript) [python3]: ").strip() or "python3"
    
    params = {
        "username": username,
        "password": password,
        "solution_code": solution_code,
        "language": language
    }
    
    print_info("\nAttempting to submit LeetCode solution...")
    print_warning("Note: This will fail if credentials are invalid or browser automation fails\n")
    
    try:
        result = complete_leetcode_daily(get_mock_user_context(), params)
        
        if result and result.get("success"):
            print_success("LeetCode submission successful!")
            print(f"  Status: {result.get('status', 'Unknown')}")
            print(f"  Runtime: {result.get('runtime', 'N/A')}")
            print(f"  Memory: {result.get('memory', 'N/A')}")
        else:
            print_error("LeetCode submission failed")
            print(f"  Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n{Colors.BOLD}Full Response:{Colors.ENDC}")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")


def test_get_leetcode_problem():
    """Test fetching LeetCode daily problem"""
    print_header("Get LeetCode Daily Problem")
    
    print_info("Fetching today's LeetCode daily problem...\n")
    
    try:
        result = get_leetcode_daily_problem(get_mock_user_context(), {})
        
        if result and result.get("success"):
            print_success("Problem retrieved successfully!")
            print(f"\n{Colors.BOLD}Problem Details:{Colors.ENDC}")
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  Difficulty: {result.get('difficulty', 'N/A')}")
            print(f"  URL: {result.get('url', 'N/A')}")
        else:
            print_error("Failed to retrieve problem")
        
        print(f"\n{Colors.BOLD}Full Response:{Colors.ENDC}")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")


def test_billing_payment():
    """Test electricity bill payment (dry-run mode)"""
    print_header("Electricity Bill Payment Test")
    
    # First, show available providers
    providers = list_billing_providers()
    print(f"{Colors.BOLD}Available Providers:{Colors.ENDC}")
    for provider in providers["providers"]:
        print(f"  - {provider['code']}: {provider['name']}")
    
    print("\n")
    provider = input("Select provider code [demo_electric]: ").strip() or "demo_electric"
    account_number = input("Enter account number [12345678]: ").strip() or "12345678"
    amount = input("Enter bill amount (optional): ").strip()
    username = input("Enter provider username [test_user]: ").strip() or "test_user"
    password = input("Enter provider password [test_pass]: ").strip() or "test_pass"
    
    print(f"\n{Colors.WARNING}{Colors.BOLD}DRY RUN MODE ENABLED{Colors.ENDC}")
    print_warning("No actual payment will be made. This is a simulation only.\n")
    
    dry_run_choice = input("Run in dry-run mode? (y/n) [y]: ").strip().lower()
    dry_run = dry_run_choice != 'n'
    
    if not dry_run:
        print_error("\nWARNING: You chose to disable dry-run mode!")
        confirm = input("This may attempt a REAL payment. Type 'CONFIRM' to proceed: ")
        if confirm != 'CONFIRM':
            print_info("Aborting test for safety")
            return
    
    params = {
        "provider": provider,
        "account_number": account_number,
        "username": username,
        "password": password,
        "dry_run": dry_run
    }
    
    if amount:
        params["amount"] = float(amount)
    
    print_info("\nProcessing bill payment...\n")
    
    try:
        result = pay_electricity_bill(get_mock_user_context(), params)
        
        if result and result.get("success"):
            print_success("Bill payment completed!")
            print(f"  Provider: {result.get('provider', 'N/A')}")
            print(f"  Account: {result.get('account_number', 'N/A')}")
            print(f"  Amount: ${result.get('bill_amount', 'N/A')}")
            print(f"  Confirmation: {result.get('confirmation_number', 'N/A')}")
            print(f"  Dry Run: {result.get('dry_run', 'N/A')}")
            
            if result.get("dry_run"):
                print_warning("\n  → This was a DRY RUN - no actual payment was made")
        else:
            print_error("Bill payment failed")
            print(f"  Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n{Colors.BOLD}Full Response:{Colors.ENDC}")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")


def test_get_bill_amount():
    """Test retrieving bill amount"""
    print_header("Get Bill Amount Test")
    
    providers = list_billing_providers()
    print(f"{Colors.BOLD}Available Providers:{Colors.ENDC}")
    for provider in providers["providers"]:
        print(f"  - {provider['code']}: {provider['name']}")
    
    print("\n")
    provider = input("Select provider code [demo_electric]: ").strip() or "demo_electric"
    account_number = input("Enter account number [12345678]: ").strip() or "12345678"
    username = input("Enter provider username [test_user]: ").strip() or "test_user"
    password = input("Enter provider password [test_pass]: ").strip() or "test_pass"
    
    params = {
        "provider": provider,
        "account_number": account_number,
        "username": username,
        "password": password
    }
    
    print_info("\nRetrieving bill amount...\n")
    
    try:
        result = get_bill_amount(get_mock_user_context(), params)
        
        if result and result.get("success"):
            print_success("Bill amount retrieved!")
            print(f"  Amount: ${result.get('bill_amount', 'N/A')}")
            print(f"  Account: {result.get('account_number', 'N/A')}")
        else:
            print_error("Failed to retrieve bill amount")
        
        print(f"\n{Colors.BOLD}Full Response:{Colors.ENDC}")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")


def test_github_create_issue():
    """Test creating GitHub issue"""
    print_header("Create GitHub Issue Test")
    
    print("This test will create a GitHub issue via the API.\n")
    
    repo = input("Enter repository name [test-repo]: ").strip() or "test-repo"
    owner = input("Enter repository owner [test-owner]: ").strip() or "test-owner"
    title = input("Enter issue title: ").strip() or "Test Issue from Browser Agent"
    body = input("Enter issue body: ").strip() or "This is a test issue created by the browser agent test CLI."
    
    params = {
        "repo": repo,
        "owner": owner,
        "title": title,
        "body": body
    }
    
    print_info("\nCreating GitHub issue...")
    print_warning("Note: This requires a valid GitHub token in the database\n")
    
    try:
        result = create_github_issue(get_mock_user_context(), params)
        
        if result and result.get("success"):
            print_success("GitHub issue created!")
            print(f"  Number: #{result.get('number', 'N/A')}")
            print(f"  URL: {result.get('url', 'N/A')}")
        else:
            print_error("Failed to create issue")
            print(f"  Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n{Colors.BOLD}Full Response:{Colors.ENDC}")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")


def test_github_list_repos():
    """Test listing GitHub repositories"""
    print_header("List GitHub Repositories Test")
    
    print_info("Fetching GitHub repositories...")
    print_warning("Note: This requires a valid GitHub token in the database\n")
    
    try:
        result = list_github_repos(get_mock_user_context(), {})
        
        if result and result.get("success"):
            print_success(f"Found {result.get('count', 0)} repositories!")
            
            repos = result.get('repositories', [])
            for repo in repos[:10]:  # Show first 10
                print(f"  - {repo.get('full_name', 'N/A')}")
        else:
            print_error("Failed to list repositories")
        
        print(f"\n{Colors.BOLD}Full Response:{Colors.ENDC}")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")


def show_example_prompts():
    """Show example natural language prompts"""
    print_header("Example Natural Language Prompts")
    
    print(f"{Colors.BOLD}For the actual AgentOS chat interface, you can use these prompts:{Colors.ENDC}\n")
    
    print(f"{Colors.OKBLUE}{Colors.BOLD}LeetCode Prompts:{Colors.ENDC}")
    print('  • "Solve today\'s LeetCode daily challenge"')
    print('  • "Get the daily LeetCode problem and show me the details"')
    print('  • "Submit my solution for LeetCode daily challenge in Python"')
    print('  • "What is today\'s LeetCode problem?"')
    
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}Billing Prompts:{Colors.ENDC}")
    print('  • "Pay my electricity bill for account #12345678"')
    print('  • "Show me my current electricity bill balance"')
    print('  • "Check my bill amount for demo_electric"')
    print('  • "List all available electricity providers"')
    
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}GitHub Prompts:{Colors.ENDC}")
    print('  • "Create a GitHub issue titled \'Bug: Login fails on Safari\'"')
    print('  • "List all my GitHub repositories"')
    print('  • "Create an issue for \'Add dark mode support\' in my frontend repo"')
    print('  • "Show me my GitHub repos"')
    
    print(f"\n{Colors.BOLD}Note:{Colors.ENDC} All billing operations default to {Colors.WARNING}DRY-RUN mode{Colors.ENDC} for safety!")
    print(f"       No actual payments will be made unless explicitly configured.\n")


def main_menu():
    """Display main menu and handle user selection"""
    while True:
        print_header("AgentOS Browser Agent Test CLI")
        
        print(f"{Colors.BOLD}Select a test scenario:{Colors.ENDC}\n")
        print("  1. LeetCode - Solve Daily Challenge")
        print("  2. LeetCode - Get Daily Problem")
        print("  3. Billing - Pay Electricity Bill (Dry-Run)")
        print("  4. Billing - Get Bill Amount")
        print("  5. GitHub - Create Issue")
        print("  6. GitHub - List Repositories")
        print("  7. Show Example Prompts")
        print("  8. Show Registered Tools")
        print("  0. Exit")
        
        choice = input(f"\n{Colors.OKCYAN}Enter choice (0-8): {Colors.ENDC}").strip()
        
        if choice == "1":
            test_leetcode_daily()
        elif choice == "2":
            test_get_leetcode_problem()
        elif choice == "3":
            test_billing_payment()
        elif choice == "4":
            test_get_bill_amount()
        elif choice == "5":
            test_github_create_issue()
        elif choice == "6":
            test_github_list_repos()
        elif choice == "7":
            show_example_prompts()
        elif choice == "8":
            print_header("Registered Tools")
            tools = tool_registry.list_tools()
            print(f"Total: {len(tools)} tools registered\n")
            for i, tool in enumerate(sorted(tools), 1):
                print(f"  {i:2d}. {tool}")
            print()
        elif choice == "0":
            print_success("\nGoodbye!\n")
            break
        else:
            print_error("Invalid choice. Please select 0-8.")
        
        input(f"\n{Colors.OKCYAN}Press Enter to continue...{Colors.ENDC}")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print_success("\n\nGoodbye!\n")
        sys.exit(0)
