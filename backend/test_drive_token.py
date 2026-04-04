"""
Quick test to check Drive token scopes.
Run: python test_drive_token.py
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# You need to paste a token here to test
# Get it from the backend DEBUG logs
TOKEN = input("Paste the Drive/Google token (from DEBUG logs): ").strip()

if not TOKEN:
    print("No token provided")
    exit(1)

# Test token info
print("\n1. Checking token info...")
info_url = f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={TOKEN}"
res = requests.get(info_url)
print(f"   Status: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    print(f"   Scopes: {data.get('scope', 'N/A')}")
    print(f"   Email: {data.get('email', 'N/A')}")
    print(f"   Expires in: {data.get('expires_in', 'N/A')} seconds")
else:
    print(f"   Error: {res.text}")

# Test Drive API
print("\n2. Testing Drive API...")
headers = {"Authorization": f"Bearer {TOKEN}"}
drive_url = "https://www.googleapis.com/drive/v3/files?pageSize=5"
res = requests.get(drive_url, headers=headers)
print(f"   Status: {res.status_code}")
if res.status_code == 200:
    files = res.json().get("files", [])
    print(f"   Files found: {len(files)}")
    for f in files[:3]:
        print(f"   - {f.get('name')}")
else:
    print(f"   Error: {res.text[:500]}")
