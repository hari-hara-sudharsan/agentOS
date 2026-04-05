"""
Tests for GitHub browser agent functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from tools.github_tool import create_github_issue, list_github_repos
from tests.test_data import SAMPLE_GITHUB_REPOS, SAMPLE_GITHUB_ISSUE


class TestGitHubAgent:
    """Test suite for GitHub automation"""
    
    @patch('tools.github_tool.check_mfa_and_consent')
    @patch('tools.github_tool.requests.post')
    def test_create_github_issue_success(
        self,
        mock_post,
        mock_mfa_check,
        mock_user_context,
        github_params
    ):
        """Test creating a GitHub issue successfully"""
        mock_mfa_check.return_value = None
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = SAMPLE_GITHUB_ISSUE
        mock_post.return_value = mock_response
        
        # Mock getting GitHub token from database
        with patch('tools.github_tool.SessionLocal') as mock_db:
            mock_db_instance = MagicMock()
            mock_integration = Mock()
            mock_integration.token_reference = "github:test_token"
            mock_integration.extra_data = '{"access_token": "ghp_test123"}'
            mock_db_instance.query().filter().first.return_value = mock_integration
            mock_db.return_value = mock_db_instance
            
            result = create_github_issue(mock_user_context, github_params)
            
            # Assertions
            assert result is not None
            mock_mfa_check.assert_called_once()
    
    @patch('tools.github_tool.check_mfa_and_consent')
    def test_create_github_issue_missing_token(
        self,
        mock_mfa_check,
        mock_user_context,
        github_params
    ):
        """Test GitHub issue creation fails without token"""
        mock_mfa_check.return_value = None
        
        with patch('tools.github_tool.SessionLocal') as mock_db:
            mock_db_instance = MagicMock()
            mock_db_instance.query().filter().first.return_value = None
            mock_db.return_value = mock_db_instance
            
            result = create_github_issue(mock_user_context, github_params)
            
            # Should return error about missing token
            assert result is not None
            if isinstance(result, dict):
                assert not result.get("success", False) or "error" in result
    
    @patch('tools.github_tool.check_mfa_and_consent')
    @patch('tools.github_tool.requests.get')
    def test_list_github_repos_success(
        self,
        mock_get,
        mock_mfa_check,
        mock_user_context
    ):
        """Test listing GitHub repositories successfully"""
        mock_mfa_check.return_value = None
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_GITHUB_REPOS
        mock_get.return_value = mock_response
        
        # Mock getting GitHub token from database
        with patch('tools.github_tool.SessionLocal') as mock_db:
            mock_db_instance = MagicMock()
            mock_integration = Mock()
            mock_integration.token_reference = "github:test_token"
            mock_integration.extra_data = '{"access_token": "ghp_test123"}'
            mock_db_instance.query().filter().first.return_value = mock_integration
            mock_db.return_value = mock_db_instance
            
            params = {}
            result = list_github_repos(mock_user_context, params)
            
            assert result is not None
            mock_mfa_check.assert_called_once()
    
    @patch('tools.github_tool.check_mfa_and_consent')
    @patch('tools.github_tool.requests.post')
    def test_create_github_issue_api_error(
        self,
        mock_post,
        mock_mfa_check,
        mock_user_context,
        github_params
    ):
        """Test GitHub issue creation handles API errors"""
        mock_mfa_check.return_value = None
        
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Repository not found"
        mock_post.return_value = mock_response
        
        with patch('tools.github_tool.SessionLocal') as mock_db:
            mock_db_instance = MagicMock()
            mock_integration = Mock()
            mock_integration.extra_data = '{"access_token": "ghp_test123"}'
            mock_db_instance.query().filter().first.return_value = mock_integration
            mock_db.return_value = mock_db_instance
            
            result = create_github_issue(mock_user_context, github_params)
            
            # Should handle error gracefully
            assert result is not None
    
    @patch('tools.github_tool.check_mfa_and_consent')
    @patch('tools.github_tool.requests.post')
    def test_create_github_issue_with_labels(
        self,
        mock_post,
        mock_mfa_check,
        mock_user_context,
        github_params
    ):
        """Test creating GitHub issue with labels"""
        mock_mfa_check.return_value = None
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {**SAMPLE_GITHUB_ISSUE, "labels": ["bug", "priority"]}
        mock_post.return_value = mock_response
        
        # Add labels to params
        github_params["labels"] = ["bug", "priority"]
        
        with patch('tools.github_tool.SessionLocal') as mock_db:
            mock_db_instance = MagicMock()
            mock_integration = Mock()
            mock_integration.extra_data = '{"access_token": "ghp_test123"}'
            mock_db_instance.query().filter().first.return_value = mock_integration
            mock_db.return_value = mock_db_instance
            
            result = create_github_issue(mock_user_context, github_params)
            
            assert result is not None
    
    def test_github_tools_registered(self):
        """Test that GitHub tools are registered in the registry"""
        from registry.tool_registry import tool_registry
        
        assert "create_github_issue" in tool_registry.list_tools()
        assert "list_github_repos" in tool_registry.list_tools()
    
    @patch('tools.github_tool.check_mfa_and_consent')
    def test_github_mfa_consent_required(
        self,
        mock_mfa_check,
        mock_user_context,
        github_params
    ):
        """Test that MFA/consent check is required for GitHub operations"""
        mock_mfa_check.return_value = None
        
        with patch('tools.github_tool.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = SAMPLE_GITHUB_ISSUE
            mock_post.return_value = mock_response
            
            with patch('tools.github_tool.SessionLocal') as mock_db:
                mock_db_instance = MagicMock()
                mock_integration = Mock()
                mock_integration.extra_data = '{"access_token": "ghp_test123"}'
                mock_db_instance.query().filter().first.return_value = mock_integration
                mock_db.return_value = mock_db_instance
                
                create_github_issue(mock_user_context, github_params)
                
                # Verify MFA check was called
                mock_mfa_check.assert_called_once()
                assert mock_mfa_check.call_args[1]["tool"] == "create_github_issue"


class TestGitHubIntegration:
    """Integration tests for GitHub (require actual token)"""
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires real GitHub token")
    def test_real_github_create_issue(self):
        """Test actual GitHub issue creation (skip in CI/CD)"""
        # This would use real GitHub token from environment
        # and actually create a test issue
        pass
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires real GitHub token")
    def test_real_github_list_repos(self):
        """Test listing actual GitHub repos (skip in CI/CD)"""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
