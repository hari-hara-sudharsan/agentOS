"""
Pytest configuration and fixtures for AgentOS tests
"""
import pytest
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def mock_user_context() -> Dict[str, Any]:
    """Mock user context for testing"""
    return {
        "sub": "test_user_123",
        "email": "test@example.com",
        "name": "Test User"
    }


@pytest.fixture
def leetcode_params() -> Dict[str, Any]:
    """Sample LeetCode parameters for testing"""
    return {
        "username": "test_leetcode_user",
        "password": "test_password",
        "solution_code": """
class Solution:
    def twoSum(self, nums, target):
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
""",
        "language": "python3"
    }


@pytest.fixture
def billing_params() -> Dict[str, Any]:
    """Sample billing parameters for testing"""
    return {
        "account_number": "12345678",
        "provider": "demo_electric",
        "amount": 125.50,
        "dry_run": True,
        "username": "test_billing_user",
        "password": "test_password"
    }


@pytest.fixture
def github_params() -> Dict[str, Any]:
    """Sample GitHub parameters for testing"""
    return {
        "title": "Test Issue: Browser Agent Testing",
        "body": "This is a test issue created by the browser agent test suite.",
        "repo": "test-repo",
        "owner": "test-owner"
    }


@pytest.fixture
def mock_browser_page(monkeypatch):
    """Mock Playwright page object for testing without actual browser"""
    
    class MockElement:
        def __init__(self, text="Mock Element", visible=True):
            self._text = text
            self._visible = visible
        
        def inner_text(self):
            return self._text
        
        def is_visible(self, timeout=5000):
            return self._visible
        
        def wait_for(self, state="visible", timeout=10000):
            pass
        
        def click(self):
            pass
        
        def fill(self, value):
            pass
        
        def first(self):
            return self
    
    class MockLocator:
        def __init__(self, selector):
            self.selector = selector
        
        def first(self):
            return MockElement()
    
    class MockPage:
        def goto(self, url, wait_until="networkidle", timeout=30000):
            pass
        
        def fill(self, selector, value):
            pass
        
        def click(self, selector):
            pass
        
        def wait_for_load_state(self, state="networkidle", timeout=15000):
            pass
        
        def screenshot(self, path):
            # Create empty file
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write("mock screenshot")
        
        def locator(self, selector):
            return MockLocator(selector)
    
    return MockPage()


@pytest.fixture
def cleanup_screenshots():
    """Cleanup test screenshots after tests"""
    yield
    # Cleanup logic here if needed
    import glob
    screenshots = glob.glob("screenshots/test_*.png")
    for screenshot in screenshots:
        try:
            os.remove(screenshot)
        except:
            pass
