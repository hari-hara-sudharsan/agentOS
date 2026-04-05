"""
Tests for billing/electricity payment browser agent functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from tools.billing_tool import pay_electricity_bill, get_bill_amount, list_billing_providers
from tests.test_data import TEST_PROVIDERS, SAMPLE_BILL_AMOUNTS


class TestBillingAgent:
    """Test suite for electricity bill payment automation"""
    
    def test_list_billing_providers(self):
        """Test listing all supported billing providers"""
        result = list_billing_providers()
        
        assert result["success"] is True
        assert "providers" in result
        assert len(result["providers"]) >= 5
        assert result["count"] == len(result["providers"])
        
        # Check structure of provider list
        for provider in result["providers"]:
            assert "code" in provider
            assert "name" in provider
            assert "url" in provider
    
    @patch('tools.billing_tool.check_mfa_and_consent')
    @patch('tools.billing_tool.execute_billing_workflow')
    def test_pay_electricity_bill_dry_run(
        self,
        mock_workflow,
        mock_mfa_check,
        mock_user_context,
        billing_params
    ):
        """Test electricity bill payment in dry-run mode (safe testing)"""
        mock_mfa_check.return_value = None
        mock_workflow.return_value = {
            "success": True,
            "bill_amount": 125.50,
            "confirmation_number": "DRY-RUN-12345"
        }
        
        # Ensure dry_run is True
        billing_params["dry_run"] = True
        
        result = pay_electricity_bill(mock_user_context, billing_params)
        
        # Assertions
        assert result["success"] is True
        assert result["dry_run"] is True
        assert "DRY RUN" in result["message"]
        assert result["account_number"] == billing_params["account_number"]
        assert "confirmation_number" in result
        
        # Verify MFA check was called
        mock_mfa_check.assert_called_once()
    
    @patch('tools.billing_tool.check_mfa_and_consent')
    def test_pay_electricity_bill_invalid_provider(
        self,
        mock_mfa_check,
        mock_user_context,
        billing_params
    ):
        """Test billing payment with invalid provider code"""
        mock_mfa_check.return_value = None
        
        billing_params["provider"] = "invalid_provider_xyz"
        
        result = pay_electricity_bill(mock_user_context, billing_params)
        
        assert result["success"] is False
        assert "error" in result
        assert "Unsupported provider" in result["error"]
        assert "supported_providers" in result
    
    @patch('tools.billing_tool.check_mfa_and_consent')
    def test_pay_electricity_bill_missing_credentials(
        self,
        mock_mfa_check,
        mock_user_context
    ):
        """Test billing payment fails without credentials"""
        mock_mfa_check.return_value = None
        
        params = {
            "account_number": "12345",
            "provider": "demo_electric",
            "dry_run": True
            # Missing username and password
        }
        
        with patch('tools.billing_tool.SessionLocal') as mock_db:
            mock_db_instance = MagicMock()
            mock_db_instance.query().filter().first.return_value = None
            mock_db.return_value = mock_db_instance
            
            result = pay_electricity_bill(mock_user_context, params)
            
            assert result["success"] is False
            assert "credentials" in result["error"].lower()
    
    @patch('tools.billing_tool.check_mfa_and_consent')
    def test_pay_electricity_bill_missing_account_number(
        self,
        mock_mfa_check,
        mock_user_context,
        billing_params
    ):
        """Test billing payment fails without account number"""
        mock_mfa_check.return_value = None
        
        # Remove account number
        del billing_params["account_number"]
        
        with patch('tools.billing_tool.SessionLocal') as mock_db:
            mock_db_instance = MagicMock()
            mock_db_instance.query().filter().first.return_value = None
            mock_db.return_value = mock_db_instance
            
            result = pay_electricity_bill(mock_user_context, billing_params)
            
            assert result["success"] is False
            assert "account number" in result["error"].lower()
    
    @patch('tools.billing_tool.check_mfa_and_consent')
    @patch('tools.billing_tool.get_billing_info')
    def test_get_bill_amount_success(
        self,
        mock_get_info,
        mock_mfa_check,
        mock_user_context,
        billing_params
    ):
        """Test retrieving bill amount without payment"""
        mock_mfa_check.return_value = None
        mock_get_info.return_value = {
            "success": True,
            "bill_amount": 125.50,
            "account_number": "12345678"
        }
        
        result = get_bill_amount(mock_user_context, billing_params)
        
        assert result["success"] is True
        assert "bill_amount" in result
        assert result["provider"] == "Demo Electric Company"
        assert result["provider_code"] == "demo_electric"
    
    @patch('tools.billing_tool.check_mfa_and_consent')
    @patch('tools.billing_tool.execute_billing_workflow')
    def test_pay_electricity_bill_all_providers(
        self,
        mock_workflow,
        mock_mfa_check,
        mock_user_context,
        billing_params
    ):
        """Test billing payment works for all supported providers"""
        mock_mfa_check.return_value = None
        mock_workflow.return_value = {
            "success": True,
            "bill_amount": 100.0,
            "confirmation_number": "TEST-12345"
        }
        
        for provider_code in TEST_PROVIDERS:
            billing_params["provider"] = provider_code
            billing_params["dry_run"] = True
            
            result = pay_electricity_bill(mock_user_context, billing_params)
            
            assert result["success"] is True
            assert result["provider_code"] == provider_code
            assert result["dry_run"] is True
    
    def test_billing_tools_registered(self):
        """Test that billing tools are registered in the registry"""
        from registry.tool_registry import tool_registry
        
        assert "pay_electricity_bill" in tool_registry.list_tools()
        assert "get_bill_amount" in tool_registry.list_tools()
        assert "list_billing_providers" in tool_registry.list_tools()
    
    @patch('tools.billing_tool.check_mfa_and_consent')
    def test_billing_mfa_consent_required(
        self,
        mock_mfa_check,
        mock_user_context,
        billing_params
    ):
        """Test that MFA/consent check is required for billing operations"""
        mock_mfa_check.return_value = None
        
        with patch('tools.billing_tool.execute_billing_workflow') as mock_workflow:
            mock_workflow.return_value = {"success": True, "confirmation_number": "TEST"}
            
            pay_electricity_bill(mock_user_context, billing_params)
            
            # Verify MFA check was called
            mock_mfa_check.assert_called_once()
            assert mock_mfa_check.call_args[1]["tool"] == "pay_electricity_bill"


class TestBillingWorkflow:
    """Test the actual browser workflow for billing (integration tests)"""
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires browser and test account")
    def test_real_billing_workflow_dry_run(self):
        """Test actual browser automation for billing in dry-run mode"""
        # This would test the actual Playwright workflow
        # with a real test account on a demo provider
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
