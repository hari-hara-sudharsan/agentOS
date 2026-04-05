"""
Test data and constants for browser agent tests
"""

# Sample LeetCode daily problem response
SAMPLE_LEETCODE_PROBLEM = {
    "questionId": "1",
    "questionFrontendId": "1",
    "title": "Two Sum",
    "titleSlug": "two-sum",
    "difficulty": "Easy",
    "content": "Given an array of integers nums and an integer target...",
    "codeSnippets": [
        {
            "lang": "Python3",
            "langSlug": "python3",
            "code": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        "
        }
    ]
}

# Sample billing providers
TEST_PROVIDERS = [
    "demo_electric",
    "test_power_co",
    "sample_utilities",
    "mock_energy",
    "demo_grid"
]

# Sample bill amounts
SAMPLE_BILL_AMOUNTS = {
    "demo_electric": 125.50,
    "test_power_co": 87.25,
    "sample_utilities": 156.80,
    "mock_energy": 93.40,
    "demo_grid": 112.15
}

# Sample GitHub repositories
SAMPLE_GITHUB_REPOS = [
    {
        "id": 1,
        "name": "test-repo",
        "full_name": "test-owner/test-repo",
        "private": False,
        "description": "Test repository"
    },
    {
        "id": 2,
        "name": "demo-project",
        "full_name": "test-owner/demo-project",
        "private": True,
        "description": "Demo project for testing"
    }
]

# Sample GitHub issue
SAMPLE_GITHUB_ISSUE = {
    "id": 1,
    "number": 42,
    "title": "Test Issue",
    "body": "This is a test issue",
    "state": "open",
    "created_at": "2026-04-04T00:00:00Z"
}
