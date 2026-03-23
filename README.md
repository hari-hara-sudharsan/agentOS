# AgentOS: Secure Sovereign AI with Auth0 Token Vault

## 📺 Live Demo Video (3 mins)
**[Insert Video Link Here]** *(Starting with a 10-second TL;DR of what problem this solves!)*

## 🐾 Project Theme: OpenClaw Sandbox
AgentOS acts as an **intermediary agent** that keeps **OpenClaw** (or any local sovereign AI) in restricted, local sandbox mode. It securely bridges the gap between private LLMs and the outside world by acting as the sole gateway to external APIs, strictly managed by the **Auth0 Token Vault for AI Agents**.

## 💡 Insights from Building
* *“We discovered that current agent frameworks lack explicit permission boundaries for long-running processes—an agent either executes an action immediately with raw tokens, or fails. Here’s the new pattern we built using Token Vault that solves it: an **Async CIBA flow** that parks the execution thread, signals the UI, and awaits human Step-Up Auth before dynamically exchanging tokens.”*
* *“Users often don't understand what scopes an AI has → our dedicated User Dashboard makes it completely transparent by mapping obscure API scopes to plain-english boundaries with a one-click **Revoke Consent** button.”*

## 🛡️ Advanced Token Vault Features Built
1. **Step-Up Authentication for High-Stakes Actions:** Before destructive or highly sensitive actions (e.g., Slack messages or Google Drive uploads), the backend throws a `ConsentRequiredException` and drops into an Awaiting Consent state. 
2. **Asynchronous Auth Flows (CIBA):** The execution thread halts. Using Server-Sent Events, the frontend UI is instantly notified to render a glowing purple `[Authorize Step-Up]` MFA prompt.
3. **Scoped Tokens with Auto-Refresh & Revocation:** Our `/integrations/disconnect` route executes a strict cross-origin `/api/v2/users/{id}/identities/{provider}/{user_id}` DELETE call to physically purge the token from the Vault.
4. **Production-Aware Polish:** We incorporated API rate-limiting (`@limiter`), structured agent activity logging (saved to `activity.db`), and graceful retry/error handling. *To scale this in production, we would map the SQLite execution memory to Redis and deploy serverless worker instances for stateless CIBA polling.*

---

## 🚀 Quick Setup (One-Click)
We've made running the project incredibly easy.

1. **Install dependencies**:
   ```bash
   cd backend && pip install -r requirements.txt
   cd frontend && npm install
   ```
2. **Launch the platform** (in separate terminals):
   ```bash
   cd backend && uvicorn main:app --reload
   cd frontend && npm run dev
   ```
*(A public demo test account can be provided to judges upon request!)*

---

## Bonus Blog Post: Securing the Autonomous Frontier

Developing an autonomous agent capable of traversing our digital lives is thrilling, but handing an LLM the raw access keys to an inbox or a corporate Slack channel fundamentally breaks standard OAuth patterns. We knew early on that AgentOS couldn't function securely unless the human remained in total control. The technical hurdle was implementing an asynchronous, "human-in-the-loop" step-up authorization flow without constantly breaking the agent's context window.

Auth0’s Token Vault fundamentally altered our approach. Instead of managing complex token lifecycles and encrypted state machines in our database, we offloaded the entire authorization layer to Auth0. The revelation came when we built our `ConsentRequiredException` handling. We realized that the Auth0 Token Vault doesn’t just store tokens safely—it allows the agent runtime to safely "pause" whenever an elevated scope is required. 

We integrated an event-driven hook into our streaming Execution Engine. The moment an agent requests a high-stakes tool execution (e.g., Google Drive uploads), our backend verifies the Vault context. If explicit consent is absent, the execution suspends, and the UI immediately prompts the user with a stylized alert: "SECURITY HALT: Human Consent Required". Only upon Auth0’s secure confirmation does the stream resume. It feels magical—the agent proposes the work, Auth0 secures the boundary, and the user holds the final key. Token Vault proved that sovereign, hyper-capable agents and zero-trust security are not mutually exclusive; they are seamlessly complementary.
