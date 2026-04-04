#!/usr/bin/env python3
"""
Debug script to test Gmail integration directly
"""
import os
from dotenv import load_dotenv
load_dotenv()

from tools.gmail_tool import read_gmail
from integrations.integration_service import get_integration_token

# Mock user context - you'll need to replace with real Auth0 token
user_context = {
    "sub": "test_user",  # Replace with your actual user ID
    "auth0_access_token": "your_auth0_token_here"  # Replace with real token
}

print("Testing Gmail integration...")

# Test token retrieval
token = get_integration_token(user_context, "gmail")
print(f"Token retrieved: {token[:50] if token and len(token) > 50 else token}")

# Test Gmail tool
params = {"query": "today"}
result = read_gmail(user_context, params)
print(f"Gmail tool result: {result}")

print("Debug complete.")