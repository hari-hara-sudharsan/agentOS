# Browser Agent Testing Guide

## Overview

This guide provides comprehensive instructions for testing the **AgentOS Browser Agent** with three key capabilities:

1. **LeetCode Daily Challenge Automation** - Solve daily coding problems automatically
2. **Electricity Bill Payment** - Pay bills through provider portals (with dry-run mode)
3. **GitHub Task Automation** - Create issues and manage repositories

---

## Quick Start

### Run the Interactive Test CLI

The easiest way to test all three scenarios:

```bash
cd backend
python test_browser_agent.py
```

This provides a menu-driven interface for testing each capability.

### Run the Test Suite

To run all automated tests:

```bash
cd backend
pytest tests/ -v
```

For specific test files:

```bash
pytest tests/test_leetcode_agent.py -v
pytest tests/test_billing_agent.py -v
pytest tests/test_github_agent.py -v
```

---

## Example Natural Language Prompts

Once your AgentOS is running, you can use these natural language prompts in the chat interface:

### LeetCode Prompts ✅

```
"Solve today's LeetCode daily challenge"
"Get the daily LeetCode problem and show me the details"
"Submit my solution for LeetCode daily challenge in Python"
"What is today's LeetCode problem?"
"Show me the LeetCode daily challenge"
```

### Billing Prompts 💰

```
"Pay my electricity bill for account #12345678"
"Show me my current electricity bill balance"
"Check my bill amount for demo_electric provider"
"List all available electricity providers"
"What is my current bill for test_power_co?"
```

**Note:** All billing operations default to **DRY-RUN mode** for safety. No actual payments will be made unless explicitly configured.

### GitHub Prompts 🐙

```
"Create a GitHub issue titled 'Bug: Login fails on Safari'"
"List all my GitHub repositories"
"Create an issue for 'Add dark mode support' in my frontend repo"
"Show me my GitHub repos"
"Create a GitHub issue in test-repo about authentication bug"
```

---

## Test Account Setup

### LeetCode Setup

To test LeetCode automation, you need:

1. **LeetCode Account**
   - Sign up at https://leetcode.com
   - Use a test account (don't use your main account for testing)

2. **Store Credentials in AgentOS**

   Option A: Via API (recommended):

   ```bash
   POST http://localhost:8000/api/integrations
   {
     "service": "leetcode",
     "extra_data": {
       "username": "your_leetcode_username",
       "password": "your_leetcode_password"
     }
   }
   ```

   Option B: Via database directly:

   ```sql
   INSERT INTO integrations (user_id, service, extra_data)
   VALUES ('your_user_id', 'leetcode', '{"username": "test", "password": "pass"}');
   ```

3. **Test Configuration**
   - Username/email for LeetCode login
   - Password
   - Preferred programming language (python3, java, cpp, javascript)

### Billing Provider Setup

The billing tool supports **5 demo providers** for safe testing:

| Provider Code      | Provider Name         | Test Account                                  |
| ------------------ | --------------------- | --------------------------------------------- |
| `demo_electric`    | Demo Electric Company | username: test_user, password: test_pass      |
| `test_power_co`    | Test Power Co         | username: demo@test.com, password: demo123    |
| `sample_utilities` | Sample Utilities Inc  | username: sample_user, password: sample_pass  |
| `mock_energy`      | Mock Energy Services  | username: mock@example.com, password: mock123 |
| `demo_grid`        | Demo Grid Corporation | username: grid_user, password: grid_pass      |

**Store Billing Credentials:**

```bash
POST http://localhost:8000/api/integrations
{
  "service": "billing_demo_electric",
  "extra_data": {
    "username": "test_user",
    "password": "test_pass",
    "account_number": "12345678"
  }
}
```

**IMPORTANT:** These are mock providers for testing. The browser automation will simulate the payment flow. Always use `dry_run: true` (default) unless testing with a real provider.

### GitHub Setup

To test GitHub automation:

1. **Create GitHub Personal Access Token**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control of private repositories)
   - Copy the generated token

2. **Store Token in AgentOS**

   ```bash
   POST http://localhost:8000/api/integrations
   {
     "service": "github",
     "extra_data": {
       "access_token": "ghp_your_token_here"
     }
   }
   ```

3. **Test Repository**
   - Create a test repository on GitHub
   - Use this for creating test issues

---

## Tool Parameters Reference

### LeetCode Tools

#### `complete_leetcode_daily`

```python
{
  "username": "leetcode_username",      # Required (or from DB)
  "password": "leetcode_password",      # Required (or from DB)
  "solution_code": "class Solution...", # Optional (uses template if not provided)
  "language": "python3"                 # Optional (default: python3)
}
```

**Supported Languages:** `python3`, `java`, `cpp`, `javascript`

#### `get_leetcode_daily_problem`

```python
{
  # No parameters required
}
```

**Returns:** Problem title, difficulty, description, URL

---

### Billing Tools

#### `pay_electricity_bill`

```python
{
  "account_number": "12345678",         # Required
  "provider": "demo_electric",          # Required
  "username": "provider_username",      # Required (or from DB)
  "password": "provider_password",      # Required (or from DB)
  "amount": 125.50,                     # Optional (for verification)
  "dry_run": true,                      # Optional (default: true - SAFE)
  "payment_method": "stored"            # Optional (default: stored)
}
```

**Supported Providers:** `demo_electric`, `test_power_co`, `sample_utilities`, `mock_energy`, `demo_grid`

⚠️ **Safety:** Always use `dry_run: true` for testing. Set to `false` only when making real payments.

#### `get_bill_amount`

```python
{
  "account_number": "12345678",         # Required
  "provider": "demo_electric",          # Required
  "username": "provider_username",      # Required (or from DB)
  "password": "provider_password"       # Required (or from DB)
}
```

#### `list_billing_providers`

```python
{
  # No parameters required
}
```

**Returns:** List of all supported providers with codes and names

---

### GitHub Tools

#### `create_github_issue`

```python
{
  "title": "Bug: Login fails",          # Required
  "body": "Description of the issue",   # Optional
  "repo": "repository-name",            # Required
  "owner": "repository-owner",          # Required
  "labels": ["bug", "priority"]         # Optional
}
```

#### `list_github_repos`

```python
{
  # No parameters required
}
```

**Returns:** List of user's repositories

---

## Testing Modes

### 1. Unit Tests (Fast, No Browser)

Run isolated tests with mocked dependencies:

```bash
pytest tests/test_leetcode_agent.py -v
pytest tests/test_billing_agent.py -v
pytest tests/test_github_agent.py -v
```

These tests:

- ✅ Run quickly (no browser automation)
- ✅ Don't require credentials
- ✅ Test logic and error handling
- ✅ Safe for CI/CD pipelines

### 2. Integration Tests (Require Credentials)

Run tests that interact with actual services:

```bash
pytest tests/ -v -m integration
```

These tests:

- ⚠️ Require valid credentials
- ⚠️ Make real API calls (GitHub)
- ⚠️ Launch browser automation (LeetCode, Billing)
- ⚠️ Should not run in CI/CD

### 3. Interactive CLI Testing

Use the menu-driven interface:

```bash
python test_browser_agent.py
```

Features:

- 🎯 Test individual scenarios
- 🎯 Provide credentials interactively
- 🎯 See real-time results
- 🎯 View detailed JSON responses

### 4. End-to-End Testing

Test complete agent workflow (prompt → execution):

```bash
pytest tests/test_integration.py -v
```

---

## Dry-Run Mode (Billing Safety)

### What is Dry-Run Mode?

Dry-run mode simulates the entire billing payment workflow **without actually submitting payment**:

1. ✅ Logs into provider portal
2. ✅ Navigates to billing section
3. ✅ Retrieves bill amount
4. ✅ Validates account number
5. ✅ Simulates payment initiation
6. ❌ **Does NOT click final confirm button**

### How to Use Dry-Run

**Default Behavior:** All billing operations default to `dry_run: true`

```python
# Safe - defaults to dry-run
pay_electricity_bill(user_context, {
    "account_number": "12345",
    "provider": "demo_electric"
})
```

**Explicit Dry-Run:**

```python
pay_electricity_bill(user_context, {
    "account_number": "12345",
    "provider": "demo_electric",
    "dry_run": True  # Explicit
})
```

**Real Payment (Use with Caution):**

```python
pay_electricity_bill(user_context, {
    "account_number": "12345",
    "provider": "real_provider",
    "dry_run": False  # WILL ATTEMPT REAL PAYMENT
})
```

### Dry-Run Response

```json
{
  "success": true,
  "message": "DRY RUN: Payment simulation completed successfully. No actual payment was made.",
  "bill_amount": 125.5,
  "account_number": "12345678",
  "confirmation_number": "DRY-RUN-1712203200",
  "provider": "Demo Electric Company",
  "dry_run": true,
  "timestamp": "2026-04-04T06:00:00"
}
```

---

## Troubleshooting

### LeetCode Issues

#### "Login failed" or "Credentials invalid"

**Cause:** Invalid LeetCode credentials or account issues

**Solutions:**

1. Verify credentials work on https://leetcode.com
2. Check if account requires 2FA (not supported yet)
3. Update credentials in database:
   ```sql
   UPDATE integrations
   SET extra_data = '{"username": "correct_user", "password": "correct_pass"}'
   WHERE service = 'leetcode';
   ```

#### "Could not find submit button" or "Selector not found"

**Cause:** LeetCode UI changed (selectors outdated)

**Solutions:**

1. Check `backend/tools/leetcode_tool.py` for selector updates
2. LeetCode frequently updates UI - may need selector refresh
3. Run in headed mode to inspect elements:
   ```python
   # In playwright_runner.py, temporarily set:
   browser = p.chromium.launch(headless=False)
   ```

#### "Timeout waiting for page load"

**Cause:** Slow network or LeetCode downtime

**Solutions:**

1. Increase timeout in `backend/tools/leetcode_tool.py`:
   ```python
   page.goto(url, wait_until="networkidle", timeout=60000)  # 60 seconds
   ```
2. Check LeetCode status: https://status.leetcode.com
3. Try again later

---

### Billing Issues

#### "Unsupported provider" error

**Cause:** Invalid provider code

**Solutions:**

1. List valid providers:
   ```python
   from tools.billing_tool import list_billing_providers
   print(list_billing_providers())
   ```
2. Use one of: `demo_electric`, `test_power_co`, `sample_utilities`, `mock_energy`, `demo_grid`

#### "Missing credentials" error

**Cause:** No credentials provided and none in database

**Solutions:**

1. Provide credentials in params:
   ```python
   {
     "username": "test_user",
     "password": "test_pass",
     ...
   }
   ```
2. Or store in database:
   ```sql
   INSERT INTO integrations (user_id, service, extra_data)
   VALUES ('user_id', 'billing_demo_electric', '{"username": "test", "password": "pass"}');
   ```

#### "Browser timeout" or "Page not loaded"

**Cause:** Slow connection or provider site down

**Solutions:**

1. Check if mock provider URL is accessible
2. Increase timeout in `backend/browser/workflows.py`
3. For real providers, verify site is up

#### Dry-run mode not working

**Cause:** `dry_run` parameter not set correctly

**Solutions:**

1. Verify parameter: `"dry_run": True` (capital T in Python)
2. Check response includes `"dry_run": true`
3. Response should have message: "DRY RUN: Payment simulation..."

---

### GitHub Issues

#### "Missing GitHub token" or "401 Unauthorized"

**Cause:** No GitHub token or token expired/invalid

**Solutions:**

1. Generate new Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Generate new token with `repo` scope
2. Store in database:
   ```sql
   UPDATE integrations
   SET extra_data = '{"access_token": "ghp_new_token"}'
   WHERE service = 'github';
   ```

#### "404 Repository not found"

**Cause:** Repository doesn't exist or token lacks access

**Solutions:**

1. Verify repository exists on GitHub
2. Check token has access to the repository
3. For private repos, token must have `repo` scope
4. Use correct owner/repo format: `owner/repository-name`

#### "422 Validation Failed"

**Cause:** Invalid issue parameters

**Solutions:**

1. Ensure `title` is provided (required)
2. Check `labels` exist in the repository
3. Verify `repo` and `owner` are correct

---

### General Browser Automation Issues

#### "Playwright not found" or "Browser not installed"

**Cause:** Playwright or Chromium not installed

**Solutions:**

```bash
pip install playwright
playwright install chromium
```

#### Screenshots show blank page

**Cause:** Page didn't fully load before screenshot

**Solutions:**

1. Add wait before screenshot:
   ```python
   page.wait_for_load_state("networkidle")
   time.sleep(2)  # Additional wait
   page.screenshot(path="screenshot.png")
   ```

#### "Permission denied" creating screenshots

**Cause:** Screenshots directory doesn't exist or no write permissions

**Solutions:**

```bash
mkdir -p backend/screenshots
chmod 755 backend/screenshots
```

---

### Database Issues

#### "No such table: integrations"

**Cause:** Database not initialized

**Solutions:**

```bash
cd backend
python init_db.py
```

#### Integration not found in database

**Cause:** Integration record doesn't exist

**Solutions:**

```bash
# Via API
POST http://localhost:8000/api/integrations
{
  "service": "leetcode",
  "extra_data": {"username": "test", "password": "pass"}
}

# Or via Python
from database.db import SessionLocal
from database.models import Integration
db = SessionLocal()
integration = Integration(
    user_id="test_user",
    service="leetcode",
    extra_data='{"username": "test", "password": "pass"}'
)
db.add(integration)
db.commit()
```

---

### MFA/Consent Issues

#### "Consent required" or "403 Forbidden"

**Cause:** Auth0 MFA/consent check failing

**Solutions:**

1. For testing, temporarily bypass MFA:
   ```python
   # In test_browser_agent.py, we already mock it
   tools.leetcode_tool.check_mfa_and_consent = mock_mfa_check
   ```
2. For production, ensure Auth0 is configured
3. Check `backend/security/auth0_client.py`

---

## Advanced Configuration

### Custom Billing Provider

To add a real electricity provider:

1. **Add provider to `backend/tools/billing_tool.py`:**

```python
SUPPORTED_PROVIDERS = {
    # ... existing providers ...
    "my_provider": {
        "name": "My Electric Company",
        "url": "https://billing.myelectric.com",
        "login_url": "https://billing.myelectric.com/login",
        "selectors": {
            "username": "#username-field",
            "password": "#password-field",
            "login_button": "button[type='submit']",
            "account_number": ".account-number",
            "amount_display": ".bill-amount",
            "pay_button": "#pay-now",
            "confirm_button": "#confirm-payment",
            "success_message": ".payment-confirmation"
        }
    }
}
```

2. **Find correct selectors:**

Run browser in headed mode and inspect elements:

```python
# In playwright_runner.py
browser = p.chromium.launch(headless=False, slow_mo=1000)
```

3. **Test with dry-run first:**

```python
pay_electricity_bill(context, {
    "provider": "my_provider",
    "dry_run": True  # ALWAYS test with dry-run first
})
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Browser Agent Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          playwright install chromium

      - name: Run unit tests
        run: |
          cd backend
          pytest tests/ -v --ignore=tests/test_integration.py -m "not integration"

    # Skip integration tests in CI (require credentials)
```

---

## Performance Benchmarks

| Test                  | Duration | Browser Launch | Notes                        |
| --------------------- | -------- | -------------- | ---------------------------- |
| Unit Tests (all)      | ~5s      | No             | Fast, no dependencies        |
| LeetCode Submission   | ~15-30s  | Yes            | Depends on LeetCode response |
| Billing Dry-Run       | ~10-20s  | Yes            | Provider site speed varies   |
| GitHub Issue Creation | ~2-5s    | No             | API call only                |
| Integration Suite     | ~1-2 min | Yes            | All scenarios                |

---

## Support and Resources

- **Main Documentation:** `README.md` in project root
- **API Documentation:** http://localhost:8000/docs (when backend running)
- **Tool Registry:** Check registered tools at `/api/tools`
- **Activity Logs:** `backend/activity.db`
- **Screenshots:** `backend/screenshots/` (debugging)

---

## FAQ

**Q: Do I need real credentials to run tests?**
A: No. Unit tests use mocks. Only integration tests require real credentials.

**Q: Will billing tests charge my account?**
A: No. Default `dry_run: true` prevents actual payments. Explicitly set `dry_run: false` to make real payments.

**Q: Can I add more programming languages for LeetCode?**
A: Yes. The tool supports `python3`, `java`, `cpp`, `javascript`. Add more in `backend/tools/leetcode_tool.py`.

**Q: How do I debug failed browser automation?**
A: 1) Check screenshots in `backend/screenshots/`, 2) Run in headed mode (`headless=False`), 3) Check logs

**Q: Can I use this in production?**
A: Yes, but ensure: 1) Real Auth0 MFA configured, 2) Rate limiting enabled, 3) Proper error handling, 4) Secure credential storage

---

## Next Steps

1. ✅ Run the test CLI: `python backend/test_browser_agent.py`
2. ✅ Try example prompts in AgentOS chat interface
3. ✅ Set up test accounts for LeetCode and GitHub
4. ✅ Review test results and logs
5. ✅ Customize providers and add your own

Happy testing! 🚀
