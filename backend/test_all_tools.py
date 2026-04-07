"""
Comprehensive Test Suite for All AgentOS Tools
Tests each tool with mock/real data depending on integration status
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import SessionLocal
from database.models import Integration
from registry.tool_registry import tool_registry
import json

# Import all tools to ensure registration
from tools import gmail_tool, github_tool, calendar_tool, drive_tool
from tools import slack_tool, discord_tool, summarize_text, pic_tools
from tools import linear_tool, salesforce_tool, azure_tool

# Test user context (use your actual user ID from Auth0)
TEST_USER_CONTEXT = {
    "sub": "google-oauth2|115860559711395850790",  # Your actual user ID
    "email": "test@example.com"
}


def get_integration_status():
    """Check which integrations are connected"""
    db = SessionLocal()
    try:
        integrations = db.query(Integration).filter(
            Integration.user_id == TEST_USER_CONTEXT["sub"]
        ).all()
        
        status = {}
        for integ in integrations:
            has_token = bool(integ.token_reference and integ.token_reference != "auth0-vault-linked")
            status[integ.service] = {
                "connected": True,
                "has_token": has_token
            }
        return status
    finally:
        db.close()


def test_github():
    """Test GitHub tool - list repos"""
    print("\n" + "="*60)
    print("[TEST] GitHub Integration")
    print("="*60)
    
    try:
        result = tool_registry.get("list_github_repos")(TEST_USER_CONTEXT, {})
        
        if "error" in result:
            print(f"[FAIL] GitHub Error: {result.get('message', result.get('error'))}")
            return False, result
        
        repos = result.get("repos", [])
        print(f"[PASS] GitHub SUCCESS: Found {len(repos)} repositories")
        for repo in repos[:3]:
            print(f"   > {repo['name']}")
        return True, result
        
    except Exception as e:
        print(f"[FAIL] GitHub Exception: {str(e)}")
        return False, {"error": str(e)}


def test_gmail():
    """Test Gmail tool - read inbox"""
    print("\n" + "="*60)
    print("[TEST] Gmail Integration")
    print("="*60)
    
    try:
        result = tool_registry.get("read_gmail")(TEST_USER_CONTEXT, {"query": ""})
        
        if "error" in result:
            print(f"[FAIL] Gmail Error: {result.get('message', result.get('error'))}")
            return False, result
        
        text = result.get("text", "")
        email_count = text.count("From:")
        print(f"[PASS] Gmail SUCCESS: Retrieved {email_count} emails")
        # Show preview of first email
        if text:
            lines = text.split("\n")[:4]
            for line in lines:
                print(f"   {line[:60]}...")
        return True, result
        
    except Exception as e:
        print(f"[FAIL] Gmail Exception: {str(e)}")
        return False, {"error": str(e)}


def test_drive():
    """Test Google Drive tool - list files"""
    print("\n" + "="*60)
    print("[TEST] Google Drive Integration")
    print("="*60)
    
    try:
        list_files = tool_registry.get("list_drive_files")
        if not list_files:
            print("[FAIL] list_drive_files not registered")
            return False, {"error": "tool_not_registered"}
            
        result = list_files(TEST_USER_CONTEXT, {})
        
        if "error" in result:
            print(f"[FAIL] Drive Error: {result.get('message', result.get('error'))}")
            return False, result
        
        files = result.get("files", [])
        print(f"[PASS] Drive SUCCESS: Found {len(files)} files")
        for f in files[:3]:
            print(f"   > {f.get('name', f)}")
        return True, result
        
    except Exception as e:
        print(f"[FAIL] Drive Exception: {str(e)}")
        return False, {"error": str(e)}


def test_calendar():
    """Test Calendar tool - list or check (no event creation in test)"""
    print("\n" + "="*60)
    print("[TEST] Google Calendar Integration")
    print("="*60)
    
    # Just check if the integration is connected
    from integrations.integration_service import get_integration_token
    token = get_integration_token(TEST_USER_CONTEXT, "calendar")
    
    if not token:
        print("[FAIL] Calendar not connected - no token found")
        return False, {"error": "calendar_not_connected"}
    
    if token == "auth0-vault-linked":
        print("[WARN] Calendar linked but token not resolved")
        return False, {"error": "token_not_resolved"}
    
    print(f"[PASS] Calendar CONNECTED: Token available (length: {len(token)})")
    print("   (Skipping event creation in test mode)")
    return True, {"status": "connected", "token_length": len(token)}


def test_summarize():
    """Test text summarization tool"""
    print("\n" + "="*60)
    print("[TEST] Text Summarization")
    print("="*60)
    
    try:
        test_text = """
        Artificial intelligence is transforming industries across the globe. 
        From healthcare to finance, AI systems are being deployed to automate 
        tasks, make predictions, and assist human decision-making. Machine 
        learning, a subset of AI, enables computers to learn from data without 
        being explicitly programmed. Deep learning, using neural networks with 
        many layers, has achieved breakthrough results in image recognition, 
        natural language processing, and game playing.
        """
        
        result = tool_registry.get("summarize_text")(
            TEST_USER_CONTEXT, 
            {"text": test_text}
        )
        
        if "error" in result:
            print(f"[FAIL] Summarize Error: {result.get('message', result.get('error'))}")
            return False, result
        
        summary = result.get("summary", "")
        print(f"[PASS] Summarize SUCCESS:")
        print(f"   {summary[:200]}...")
        return True, result
        
    except Exception as e:
        print(f"[FAIL] Summarize Exception: {str(e)}")
        return False, {"error": str(e)}


def test_slack():
    """Test Slack tool - check connection"""
    print("\n" + "="*60)
    print("[TEST] Slack Integration")
    print("="*60)
    
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.user_id == TEST_USER_CONTEXT["sub"],
            Integration.service == "slack"
        ).first()
        
        if not integration or not integration.token_reference:
            print("[WARN] Slack not connected - add bot token in Integrations")
            return False, {"error": "slack_not_connected"}
        
        print(f"[PASS] Slack CONNECTED: Bot token configured")
        print("   (Skipping message send in test mode)")
        return True, {"status": "connected"}
        
    finally:
        db.close()


def test_discord():
    """Test Discord tool - check connection"""
    print("\n" + "="*60)
    print("[TEST] Discord Integration")
    print("="*60)
    
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.user_id == TEST_USER_CONTEXT["sub"],
            Integration.service == "discord"
        ).first()
        
        if not integration or not integration.token_reference:
            print("[WARN] Discord not connected - add webhook URL in Integrations")
            return False, {"error": "discord_not_connected"}
        
        print(f"[PASS] Discord CONNECTED: Webhook configured")
        print("   (Skipping message post in test mode)")
        return True, {"status": "connected"}
        
    finally:
        db.close()


def test_browser():
    """Test browser automation - simple scrape"""
    print("\n" + "="*60)
    print("[TEST] Browser Automation")
    print("="*60)
    
    try:
        from browser.playwright_runner import run_browser_task
        
        result = run_browser_task("browser_search", {"query": "test"})
        
        if "error" in result:
            print(f"[FAIL] Browser Error: {result.get('error')}")
            return False, result
        
        text = result.get("text", "")
        print(f"[PASS] Browser SUCCESS: Got {len(text)} chars of content")
        return True, result
        
    except Exception as e:
        print(f"[FAIL] Browser Exception: {str(e)}")
        return False, {"error": str(e)}


def test_image_generation():
    """Test image generation tool"""
    print("\n" + "="*60)
    print("[TEST] Image Generation")
    print("="*60)
    
    try:
        create_image = tool_registry.get("create_image")
        if not create_image:
            print("[WARN] create_image tool not registered")
            return False, {"error": "tool_not_registered"}
        
        result = create_image(TEST_USER_CONTEXT, {"prompt": "A sunset over mountains"})
        
        if "error" in result:
            print(f"[WARN] Image Generation: {result.get('message', result.get('error'))}")
            return False, result
        
        print(f"[PASS] Image Generation SUCCESS: {result.get('message', 'Image created')}")
        return True, result
        
    except Exception as e:
        print(f"[FAIL] Image Exception: {str(e)}")
        return False, {"error": str(e)}


def run_all_tests():
    """Run all tool tests and generate report"""
    print("\n")
    print("+" + "="*58 + "+")
    print("|" + " "*15 + "AGENTOS TOOL TEST SUITE" + " "*20 + "|")
    print("+" + "="*58 + "+")
    
    # Check integration status first
    print("\n[INFO] Checking Integration Status...")
    status = get_integration_status()
    print(f"   Connected services: {list(status.keys())}")
    
    # Run all tests
    results = {}
    
    tests = [
        ("GitHub", test_github),
        ("Gmail", test_gmail),
        ("Google Drive", test_drive),
        ("Calendar", test_calendar),
        ("Text Summarize", test_summarize),
        ("Slack", test_slack),
        ("Discord", test_discord),
        ("Browser", test_browser),
        ("Image Gen", test_image_generation),
    ]
    
    for name, test_func in tests:
        try:
            success, result = test_func()
            results[name] = {"success": success, "result": result}
        except Exception as e:
            results[name] = {"success": False, "result": {"error": str(e)}}
    
    # Generate summary report
    print("\n")
    print("+" + "="*58 + "+")
    print("|" + " "*20 + "TEST RESULTS" + " "*26 + "|")
    print("+" + "="*58 + "+")
    
    passed = sum(1 for r in results.values() if r["success"])
    failed = len(results) - passed
    
    for name, data in results.items():
        icon = "[PASS]" if data["success"] else "[FAIL]"
        print(f"   {icon} {name}")
    
    print("\n" + "-"*60)
    print(f"   TOTAL: {passed} passed, {failed} failed")
    print("-"*60)
    
    return results


if __name__ == "__main__":
    results = run_all_tests()
