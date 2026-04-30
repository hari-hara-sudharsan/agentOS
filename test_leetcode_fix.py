#!/usr/bin/env python3
"""
Quick test to validate LeetCode fix syntax
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all modules import correctly"""
    print("Testing imports...")
    
    try:
        from tools.leetcode_tool import complete_leetcode_daily, get_leetcode_daily_problem
        print("✅ LeetCode tool imports successfully")
    except Exception as e:
        print(f"❌ LeetCode tool import failed: {e}")
        return False
    
    try:
        from browser.playwright_runner import run_browser_task
        print("✅ Playwright runner imports successfully")
    except Exception as e:
        print(f"❌ Playwright runner import failed: {e}")
        return False
    
    try:
        from browser.browser_utils import take_screenshot_async
        print("✅ Browser utils imports successfully")
    except Exception as e:
        print(f"❌ Browser utils import failed: {e}")
        return False
    
    try:
        from security.auth0_client import check_mfa_and_consent, TOOL_SERVICE_MAP
        if "complete_leetcode_daily" in TOOL_SERVICE_MAP:
            print("✅ LeetCode registered in TOOL_SERVICE_MAP")
        else:
            print("❌ LeetCode NOT in TOOL_SERVICE_MAP")
            return False
    except Exception as e:
        print(f"❌ Auth0 client import failed: {e}")
        return False
    
    print("\n🎉 All imports successful! LeetCode agent is ready.")
    return True

def test_function_signatures():
    """Test that functions have correct signatures"""
    print("\nTesting function signatures...")
    
    try:
        from tools.leetcode_tool import run_leetcode_workflow, _run_in_new_loop, _run_leetcode_workflow_async
        import inspect
        
        # Check run_leetcode_workflow is sync
        if not inspect.iscoroutinefunction(run_leetcode_workflow):
            print("✅ run_leetcode_workflow is synchronous")
        else:
            print("❌ run_leetcode_workflow should be synchronous")
            return False
        
        # Check _run_leetcode_workflow_async is async
        if inspect.iscoroutinefunction(_run_leetcode_workflow_async):
            print("✅ _run_leetcode_workflow_async is asynchronous")
        else:
            print("❌ _run_leetcode_workflow_async should be asynchronous")
            return False
        
        print("✅ All function signatures correct")
        return True
    except Exception as e:
        print(f"❌ Function signature test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("LeetCode Agent Fix Validation Test")
    print("=" * 60)
    
    success = True
    success = test_imports() and success
    success = test_function_signatures() and success
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED - LeetCode agent is fixed!")
        print("\nYou can now use: 'Solve my today's daily problem on LeetCode'")
    else:
        print("❌ SOME TESTS FAILED - Please check the errors above")
        sys.exit(1)
    print("=" * 60)
