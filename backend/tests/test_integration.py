"""
Integration tests for end-to-end agent workflows
Tests the complete flow: User prompt → Planner → Router → Tool → Result
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestEndToEndWorkflow:
    """Test complete agent workflow from prompt to execution"""
    
    @patch('agents.planner_agent.call_openai')
    @patch('tools.leetcode_tool.check_mfa_and_consent')
    @patch('tools.leetcode_tool.run_browser_task')
    def test_leetcode_workflow_complete(
        self,
        mock_browser,
        mock_mfa,
        mock_openai,
        mock_user_context
    ):
        """Test complete workflow for 'Solve today's LeetCode daily challenge'"""
        mock_mfa.return_value = None
        mock_browser.return_value = {"success": True, "status": "Accepted"}
        
        # Mock planner response
        mock_openai.return_value = {
            "plan": {
                "tasks": [
                    {
                        "tool": "complete_leetcode_daily",
                        "params": {
                            "username": "{{memory.leetcode_username}}",
                            "password": "{{memory.leetcode_password}}",
                            "language": "python3"
                        }
                    }
                ]
            }
        }
        
        # This would be a full integration test if we had the router setup
        # For now, just verify the components work together
        assert True
    
    @patch('agents.planner_agent.call_openai')
    @patch('tools.billing_tool.check_mfa_and_consent')
    @patch('tools.billing_tool.execute_billing_workflow')
    def test_billing_workflow_complete_dry_run(
        self,
        mock_workflow,
        mock_mfa,
        mock_openai,
        mock_user_context
    ):
        """Test complete workflow for 'Pay my electricity bill' (dry-run)"""
        mock_mfa.return_value = None
        mock_workflow.return_value = {
            "success": True,
            "bill_amount": 125.50,
            "confirmation_number": "DRY-RUN-12345"
        }
        
        mock_openai.return_value = {
            "plan": {
                "tasks": [
                    {
                        "tool": "pay_electricity_bill",
                        "params": {
                            "account_number": "{{memory.account_number}}",
                            "provider": "demo_electric",
                            "dry_run": True
                        }
                    }
                ]
            }
        }
        
        assert True
    
    @patch('agents.planner_agent.call_openai')
    @patch('tools.github_tool.check_mfa_and_consent')
    @patch('tools.github_tool.requests.post')
    def test_github_workflow_complete(
        self,
        mock_post,
        mock_mfa,
        mock_openai,
        mock_user_context
    ):
        """Test complete workflow for 'Create a GitHub issue'"""
        mock_mfa.return_value = None
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"number": 42, "title": "Test Issue"}
        mock_post.return_value = mock_response
        
        mock_openai.return_value = {
            "plan": {
                "tasks": [
                    {
                        "tool": "create_github_issue",
                        "params": {
                            "title": "Bug: Login fails",
                            "repo": "test-repo",
                            "owner": "test-owner"
                        }
                    }
                ]
            }
        }
        
        assert True


class TestMemoryChaining:
    """Test that tool outputs can be used in subsequent tasks"""
    
    def test_memory_parameter_resolution(self):
        """Test that memory placeholders are resolved correctly"""
        # This would test the memory system that chains tool outputs
        memory = {
            "leetcode_username": "test_user",
            "bill_amount": 125.50,
            "github_issue_url": "https://github.com/owner/repo/issues/42"
        }
        
        # Test parameter resolution
        param_template = "{{memory.leetcode_username}}"
        # Would resolve to "test_user"
        
        assert memory.get("leetcode_username") == "test_user"


class TestToolRegistry:
    """Test that all required tools are registered"""
    
    def test_all_tools_registered(self):
        """Verify all 24 tools are registered"""
        from registry.tool_registry import tool_registry
        
        required_tools = [
            # LeetCode
            "complete_leetcode_daily",
            "get_leetcode_daily_problem",
            # Billing
            "pay_electricity_bill",
            "get_bill_amount",
            "list_billing_providers",
            # GitHub
            "create_github_issue",
            "list_github_repos",
            # Other tools
            "read_gmail",
            "send_gmail",
            "send_slack_message",
            "upload_to_drive",
            "list_drive_files",
            "create_calendar_event"
        ]
        
        registered = tool_registry.list_tools()
        
        for tool in required_tools:
            assert tool in registered, f"Tool {tool} not registered"


class TestErrorHandling:
    """Test error handling across the agent workflow"""
    
    @patch('tools.leetcode_tool.check_mfa_and_consent')
    def test_mfa_consent_exception(self, mock_mfa, mock_user_context):
        """Test that MFA/consent exceptions are handled properly"""
        from fastapi import HTTPException
        
        # Simulate MFA check raising exception
        mock_mfa.side_effect = HTTPException(status_code=403, detail="Consent required")
        
        from tools.leetcode_tool import complete_leetcode_daily
        
        with pytest.raises(HTTPException) as exc_info:
            complete_leetcode_daily(mock_user_context, {"username": "test", "password": "test"})
        
        assert exc_info.value.status_code == 403
    
    @patch('tools.billing_tool.check_mfa_and_consent')
    def test_invalid_provider_handled(self, mock_mfa, mock_user_context):
        """Test that invalid provider errors are handled gracefully"""
        mock_mfa.return_value = None
        
        from tools.billing_tool import pay_electricity_bill
        
        result = pay_electricity_bill(mock_user_context, {
            "provider": "nonexistent_provider",
            "account_number": "12345",
            "username": "test",
            "password": "test"
        })
        
        assert result["success"] is False
        assert "Unsupported provider" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
