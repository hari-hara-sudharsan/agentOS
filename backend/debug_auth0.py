#!/usr/bin/env python3
"""
Auth0 Token Vault Diagnostic Script
Run this to identify the exact issue with Token Vault exchange.
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 60)
    print("AUTH0 TOKEN VAULT DIAGNOSTIC")
    print("=" * 60)
    
    domain = os.getenv("AUTH0_DOMAIN")
    client_id = os.getenv("AUTH0_CLIENT_ID")
    client_secret = os.getenv("AUTH0_CLIENT_SECRET")
    
    print(f"\n1. CONFIGURATION CHECK")
    print(f"   Domain: {domain}")
    print(f"   Client ID: {client_id}")
    print(f"   Has Secret: {'✓' if client_secret else '✗'}")
    
    if not all([domain, client_id, client_secret]):
        print("\n❌ Missing configuration! Check .env file.")
        return
    
    print(f"\n2. AUTH0 CONNECTIVITY")
    try:
        url = f"https://{domain}/.well-known/openid-configuration"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            print(f"   ✓ Auth0 tenant reachable")
            config = res.json()
            token_endpoint = config.get("token_endpoint")
            print(f"   Token Endpoint: {token_endpoint}")
        else:
            print(f"   ✗ Auth0 returned {res.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Connection error: {e}")
        return
    
    print(f"\n3. CLIENT CREDENTIALS TEST")
    try:
        # Test client credentials grant (basic test)
        res = requests.post(
            f"https://{domain}/oauth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "audience": f"https://{domain}/api/v2/"
            },
            timeout=10
        )
        if res.status_code == 200:
            print(f"   ✓ Client credentials valid")
        else:
            error = res.json()
            print(f"   ✗ Client auth failed: {error.get('error')}: {error.get('error_description')}")
            if "unauthorized_client" in str(error):
                print("\n   FIX: Enable 'Client Credentials' grant in Auth0 App settings")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print(f"\n4. TOKEN EXCHANGE GRANT CHECK")
    print("   Testing federated token exchange...")
    try:
        # Test token exchange with a dummy token (will fail, but shows if grant is enabled)
        res = requests.post(
            f"https://{domain}/oauth/token",
            json={
                "grant_type": "urn:auth0:params:oauth:grant-type:token-exchange:federated-connection-access-token",
                "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "requested_token_type": "http://auth0.com/oauth/token-type/federated-connection-access-token",
                "subject_token": "dummy_test_token",
                "connection": "google-oauth2",
                "scope": "openid profile email"
            },
            auth=(client_id, client_secret),
            timeout=10
        )
        error = res.json()
        error_code = error.get("error")
        error_desc = error.get("error_description", "")
        
        if error_code == "unauthorized_client" and "grant type" in error_desc.lower():
            print(f"   ✗ Token Exchange grant NOT enabled!")
            print("\n   === FIX REQUIRED ===")
            print("   1. Go to Auth0 Dashboard → Applications → Your App")
            print("   2. Settings → Advanced Settings → Grant Types")
            print("   3. Enable 'Token Exchange'")
            print("   4. Save changes")
        elif "subject_token" in error_desc.lower() or "access token" in error_desc.lower() or "Invalid Token" in error_desc:
            print(f"   ✓ Token Vault grant is ENABLED (test token rejected as expected)")
        elif "connection" in error_desc.lower():
            print(f"   ✗ Connection issue: {error_desc}")
            print("\n   FIX: Check that 'google-oauth2' social connection is enabled")
        else:
            print(f"   ? Unknown response: {error_code}: {error_desc}")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print(f"\n5. GOOGLE SOCIAL CONNECTION CHECK")
    print("   (Requires Management API access)")
    try:
        # Get management token
        res = requests.post(
            f"https://{domain}/oauth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "audience": f"https://{domain}/api/v2/"
            },
            timeout=10
        )
        if res.status_code == 200:
            mgmt_token = res.json().get("access_token")
            
            # Get connections
            conn_res = requests.get(
                f"https://{domain}/api/v2/connections",
                headers={"Authorization": f"Bearer {mgmt_token}"},
                params={"strategy": "google-oauth2"},
                timeout=10
            )
            if conn_res.status_code == 200:
                connections = conn_res.json()
                if connections:
                    conn = connections[0]
                    print(f"   ✓ Google connection found: {conn.get('name')}")
                    print(f"   Enabled clients: {conn.get('enabled_clients', [])}")
                    if client_id in conn.get('enabled_clients', []):
                        print(f"   ✓ Your app ({client_id}) is enabled")
                    else:
                        print(f"   ✗ Your app ({client_id}) NOT enabled for this connection!")
                        print("\n   FIX: Go to Auth0 → Authentication → Social → google-oauth2")
                        print("   Then go to 'Applications' tab and enable your app")
                else:
                    print(f"   ✗ No Google connection found!")
                    print("\n   FIX: Set up Google Social Connection in Auth0")
            else:
                print(f"   Could not fetch connections: {conn_res.status_code}")
        else:
            print(f"   Skipped (no Management API access)")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
