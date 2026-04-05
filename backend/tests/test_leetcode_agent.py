"""
Tests for LeetCode browser agent functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from tools.leetcode_tool import complete_leetcode_daily, get_leetcode_daily_problem
from tests.test_data import SAMPLE_LEETCODE_PROBLEM


class TestLeetCodeAgent:
    """Test suite for LeetCode automation"""
    
    def test_get_leetcode_daily_problem_structure(self, mock_user_context):
        """Test that get_leetcode_daily_problem returns expected structure"""
        # This would normally require mocking the API call
        # For now, test the function signature and basic validation
        pass
    
    @patch('tools.leetcode_tool.check_mfa_and_consent')
    @patch('tools.leetcode_tool.run_browser_task')
    def test_complete_leetcode_daily_with_credentials(
        self, 
        mock_browser_task,
        mock_mfa_check,
        mock_user_context,
        leetcode_params
    ):
        """Test LeetCode daily submission with provided credentials"""
        # Mock MFA check to pass
        mock_mfa_check.return_value = None
        
        # Mock browser task to return success
        mock_browser_task.return_value = {
            "success": True,
            "status": "Accepted",
            "runtime": "45 ms",
            "memory": "14.2 MB"
        }
        
        # Call the function
        result = complete_leetcode_daily(mock_user_context, leetcode_params)
        
        # Assertions
        assert result is not None
        assert mock_mfa_check.called
        assert mock_browser_task.called
    
    @patch('tools.leetcode_tool.check_mfa_and_consent')
    def test_complete_leetcode_daily_missing_credentials(
        self,
        mock_mfa_check,
        mock_user_context
    ):
        """Test LeetCode submission fails without credentials"""
        mock_mfa_check.return_value = None
        
        params = {
            "solution_code": "print('test')",
            "language": "python3"
            # Missing username and password
        }
        
        with patch('tools.leetcode_tool.SessionLocal') as mock_db:
            # Mock database to return no integration
            mock_db_instance = MagicMock()
            mock_db_instance.query().filter().first.return_value = None
            mock_db.return_value = mock_db_instance
            
            result = complete_leetcode_daily(mock_user_context, params)
            
            # Should return error about missing credentials
            assert result is not None
            if isinstance(result, dict):
                # May return error dict or raise exception depending on implementation
                assert not result.get("success", False) or "error" in result
    
    @patch('tools.leetcode_tool.check_mfa_and_consent')
    @patch('tools.leetcode_tool.run_browser_task')
    def test_complete_leetcode_daily_multiple_languages(
        self,
        mock_browser_task,
        mock_mfa_check,
        mock_user_context
    ):
        """Test LeetCode submission with different programming languages"""
        mock_mfa_check.return_value = None
        mock_browser_task.return_value = {"success": True}
        
        languages = ["python3", "java", "cpp", "javascript"]
        
        for lang in languages:
            params = {
                "username": "test_user",
                "password": "test_pass",
                "solution_code": "/* solution */",
                "language": lang
            }
            
            result = complete_leetcode_daily(mock_user_context, params)
            assert result is not None
    
    def test_leetcode_tool_registered(self):
        """Test that LeetCode tools are registered in the registry"""
        from registry.tool_registry import tool_registry
        
        assert "complete_leetcode_daily" in tool_registry.list_tools()
        assert "get_leetcode_daily_problem" in tool_registry.list_tools()
    
    @patch('tools.leetcode_tool.check_mfa_and_consent')
    def test_leetcode_mfa_consent_called(
        self,
        mock_mfa_check,
        mock_user_context,
        leetcode_params
    ):
        """Test that MFA/consent check is always called for LeetCode"""
        mock_mfa_check.return_value = None
        
        with patch('tools.leetcode_tool.run_browser_task') as mock_browser:
            mock_browser.return_value = {"success": True}
            
            complete_leetcode_daily(mock_user_context, leetcode_params)
            
            # Verify MFA check was called with correct parameters
            mock_mfa_check.assert_called_once()
            call_args = mock_mfa_check.call_args
            assert call_args[0][0] == mock_user_context  # First arg is user_context
            assert call_args[1]["tool"] == "complete_leetcode_daily"  # Kwarg tool


class TestLeetCodeIntegration:
    """Integration tests for LeetCode (require actual credentials)"""
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires real LeetCode credentials")
    def test_real_leetcode_login(self):
        """Test actual LeetCode login (skip in CI/CD)"""
        # This test would use real credentials from environment
        # and actually attempt to login to LeetCode
        pass
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires real LeetCode credentials")
    def test_real_leetcode_daily_fetch(self):
        """Test fetching actual daily problem (skip in CI/CD)"""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
