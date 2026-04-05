# 🛡️ AgentOS — The Sovereign AI Agent Platform

> **"Your AI agents, your rules, your data sovereignty."**

AgentOS is a **production-grade, enterprise-ready AI agent platform** that solves the #1 problem in agentic AI: **How do you let AI agents act on your behalf without giving away your credentials?**

Built on **Auth0 Token Vault** with a zero-trust security architecture, AgentOS enables AI agents to perform real-world tasks (pay bills, manage code, send emails) while users maintain **complete control and auditability** over every action.

---

## 🏆 Why AgentOS Wins

| Challenge | Traditional Agents | AgentOS Solution |
|-----------|-------------------|------------------|
| **Credential Exposure** | Agents see your passwords | ✅ Token Vault delegation - agents never see credentials |
| **Uncontrolled Actions** | Agents act without approval | ✅ Step-up auth + CIBA for high-stakes actions |
| **No Audit Trail** | Black box operations | ✅ Prometheus metrics + Grafana dashboards for every action |
| **Single Point of Failure** | Cloud-only LLMs | ✅ OpenClaw local LLM sandbox for sensitive data |
| **Scaling Concerns** | Manual infrastructure | ✅ Kubernetes + Helm + HPA auto-scaling |

---

## 🎯 What Makes This Special

### 1. **Auth0 Token Vault Deep Integration**
Not just authentication — we implement the **full Token Vault security model**:
- **Delegated Token Exchange**: Agent receives scoped tokens, never raw credentials
- **Consent Management**: Per-tool, per-action user consent with audit trail
- **Step-Up Authentication**: High-risk actions trigger MFA/CIBA approval
- **Token Lifecycle**: Automatic refresh, revocation, and expiry handling

### 2. **Real Browser Automation**
Powered by **Playwright**, our agents don't just call APIs — they navigate real websites:
- ✅ Solve LeetCode daily challenges (full browser automation)
- ✅ Pay utility bills across 5+ providers (with dry-run safety)
- ✅ Manage GitHub repos, issues, and PRs
- ✅ Interact with any web application

### 3. **Production-Grade Infrastructure**
This isn't a hackathon prototype — it's **deployment-ready**:
- 📦 **Docker Compose**: One-command local deployment
- ☸️ **Kubernetes Manifests**: Namespace, Deployments, Services, Ingress
- 📈 **HorizontalPodAutoscaler**: CPU + custom metrics scaling
- 🎛️ **Helm Chart**: Fully parameterized deployment
- 📊 **Prometheus + Grafana**: Real-time observability

### 4. **OpenClaw: Local LLM Sandbox**
For enterprises that can't send data to cloud LLMs:
- Run **Llama3, Mistral, CodeLlama** locally
- All requests go through Token Vault security layer
- GPU-accelerated or CPU fallback modes

---

## 🚀 Quick Start (For Judges)

### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate
git clone https://github.com/YOUR_USERNAME/agentos.git
cd agentos

# Create environment file
cp .env.example .env
# Edit .env with provided credentials (see below)

# Start everything
docker-compose up -d

# Access points:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Grafana: http://localhost:3001 (admin/agentos123)
# - Prometheus: http://localhost:9090
```

### Option 2: Local Development

```bash
# Backend
cd backend
pip install -r req_utf8.txt
playwright install chromium
uvicorn main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

---

## 🔑 Test Credentials for Judges

### Auth0 Configuration

```
AUTH0_DOMAIN=<provided-separately>
AUTH0_CLIENT_ID=<provided-separately>
AUTH0_CLIENT_SECRET=<provided-separately>
AUTH0_AUDIENCE=https://api.agentos.io
```

### OpenAI API Key

```
OPENAI_API_KEY=<provided-separately>
```

### Test User Accounts

```
Email: judge@agentos-demo.com
Password: <provided-separately>
```

> **Note:** Actual credentials will be provided in the "Additional Info for Judges" field on DevPost to keep them secure.

---

## 🧪 Testing Instructions

### 1. Browser Agent Testing

#### LeetCode Daily Problem Solver

```bash
# Via API
curl -X POST http://localhost:8000/api/agent/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "prompt": "Solve today'\''s LeetCode daily challenge",
    "tools": ["leetcode"]
  }'

# Expected behavior:
# - Agent navigates to leetcode.com
# - Identifies daily problem
# - Analyzes problem requirements
# - Generates solution with explanation
# - Returns solution code and complexity analysis
```

#### Electricity Bill Payment (Dry-Run Mode)

```bash
# Via API - Safe testing with dry_run=true (default)
curl -X POST http://localhost:8000/api/agent/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "prompt": "Pay my electricity bill for account 12345",
    "tools": ["billing"],
    "params": {
      "provider": "demo_electric",
      "account_number": "12345",
      "dry_run": true
    }
  }'

# Expected behavior:
# - Agent shows bill amount and details
# - Simulates payment workflow
# - Returns confirmation WITHOUT actual payment
# - Full audit trail logged
```

#### GitHub Repository Tasks

```bash
# Create issue
curl -X POST http://localhost:8000/api/agent/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "prompt": "Create a bug report issue in my repo about login timeout",
    "tools": ["github"]
  }'

# List PRs
curl -X POST http://localhost:8000/api/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show me open pull requests in agentos repo",
    "tools": ["github"]
  }'
```

### 2. Interactive CLI Testing

```bash
cd backend
python test_browser_agent.py

# Menu options:
# 1. Test LeetCode Agent
# 2. Test Billing Agent
# 3. Test GitHub Agent
# 4. Run All Tests
# 5. Exit
```

### 3. API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI with all endpoints.

### 4. Observability Testing

```bash
# View metrics
curl http://localhost:8000/metrics

# Grafana Dashboard
open http://localhost:3001
# Login: admin / agentos123
# Navigate to: Dashboards > AgentOS Overview

# Key metrics to observe:
# - Token Vault exchange success/failure
# - Agent tool execution latency
# - Step-up authentication events
# - Browser task completion rates
```

---

## 🏗️ Architecture Highlights

### Security (Auth0 Token Vault Integration)

- **Delegated Token Exchange**: Agent never sees raw user credentials
- **Step-Up Authentication**: High-stakes actions require MFA/CIBA approval
- **Consent Management**: Granular per-tool consent tracking
- **Audit Logging**: Complete trail of all agent actions

### Agent Capabilities

| Tool     | Provider         | Description                      |
| -------- | ---------------- | -------------------------------- |
| LeetCode | leetcode.com     | Solve daily coding challenges    |
| Billing  | 5 demo providers | Pay utility bills (dry-run safe) |
| GitHub   | GitHub API       | Issues, PRs, repos               |
| Gmail    | Google           | Read/send emails                 |
| Slack    | Slack API        | Messages, channels               |
| Calendar | Google Calendar  | Events management                |
| Drive    | Google Drive     | File operations                  |

### Infrastructure

- **Docker Compose**: One-command local deployment
- **Kubernetes**: Production-ready manifests with HPA
- **Helm Chart**: Configurable deployment
- **Prometheus**: Custom metrics for all operations
- **Grafana**: Pre-configured dashboards

### OpenClaw Integration

- Local LLM sandbox for sensitive operations
- Token Vault secured communication
- Supports Llama3, Mistral, CodeLlama models

---

## 🏗️ Architecture Deep Dive

### System Architecture
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AgentOS Architecture                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────┐     ┌───────────────────────────────────────────────────────┐ │
│  │   Frontend   │────▶│                   Auth0 Layer                         │ │
│  │  (Next.js)   │     │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │ │
│  └──────────────┘     │  │ Token Vault │  │  Step-Up MFA │  │ CIBA Push    │  │ │
│         │             │  │  Exchange   │  │  Challenge   │  │ Approval     │  │ │
│         │             │  └─────────────┘  └──────────────┘  └──────────────┘  │ │
│         ▼             └───────────────────────────────────────────────────────┘ │
│  ┌──────────────┐                              │                                 │
│  │   Backend    │◀─────────────────────────────┘                                 │
│  │  (FastAPI)   │                                                                │
│  │              │     ┌───────────────────────────────────────────────────────┐ │
│  │  ┌────────┐  │     │              Agent Orchestration Layer                │ │
│  │  │Metrics │  │────▶│  ┌─────────────────────────────────────────────────┐  │ │
│  │  │Endpoint│  │     │  │            Sovereign Agent Core                  │  │ │
│  │  └────────┘  │     │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ │  │ │
│  └──────────────┘     │  │  │ Planner │ │Executor │ │ Memory  │ │Consent │ │  │ │
│                       │  │  └─────────┘ └─────────┘ └─────────┘ └────────┘ │  │ │
│                       │  └─────────────────────────────────────────────────┘  │ │
│                       └───────────────────────────────────────────────────────┘ │
│                                              │                                   │
│         ┌────────────────────────────────────┼────────────────────────────────┐  │
│         │                                    │                                │  │
│         ▼                                    ▼                                ▼  │
│  ┌──────────────┐                   ┌──────────────┐                ┌──────────┐│
│  │   Browser    │                   │   Tool       │                │ OpenClaw ││
│  │   Automation │                   │   Registry   │                │  Bridge  ││
│  │  (Playwright)│                   │              │                │          ││
│  │              │                   │ ┌──────────┐ │                │ ┌──────┐ ││
│  │ ┌──────────┐ │                   │ │ LeetCode │ │                │ │Llama3│ ││
│  │ │ LeetCode │ │                   │ ├──────────┤ │                │ ├──────┤ ││
│  │ ├──────────┤ │                   │ │ Billing  │ │                │ │Mistral│││
│  │ │ Billing  │ │                   │ ├──────────┤ │                │ ├──────┤ ││
│  │ ├──────────┤ │                   │ │ GitHub   │ │                │ │Code  │ ││
│  │ │ Any Site │ │                   │ ├──────────┤ │                │ │Llama │ ││
│  │ └──────────┘ │                   │ │ Gmail    │ │                │ └──────┘ ││
│  └──────────────┘                   │ ├──────────┤ │                └──────────┘│
│                                     │ │ Slack    │ │                            │
│                                     │ ├──────────┤ │                            │
│                                     │ │ Calendar │ │                            │
│                                     │ ├──────────┤ │                            │
│                                     │ │ Drive    │ │                            │
│                                     │ ├──────────┤ │                            │
│                                     │ │ Discord  │ │                            │
│                                     │ ├──────────┤ │                            │
│                                     │ │Salesforce│ │                            │
│                                     │ ├──────────┤ │                            │
│                                     │ │ Linear   │ │                            │
│                                     │ ├──────────┤ │                            │
│                                     │ │ Azure    │ │                            │
│                                     │ └──────────┘ │                            │
│                                     └──────────────┘                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           Observability Layer                                    │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────────────────────┐    │
│  │  Prometheus   │───▶│    Grafana    │    │        Custom Metrics         │    │
│  │   Scraping    │    │  Dashboards   │    │  • Token Vault exchanges      │    │
│  └───────────────┘    └───────────────┘    │  • Step-up auth latency       │    │
│                                            │  • Tool execution counts      │    │
│                                            │  • Browser task success       │    │
│                                            │  • OpenClaw requests          │    │
│                                            └───────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           Infrastructure Layer                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │    Docker    │  │  Kubernetes  │  │     Helm     │  │   HPA Auto-Scaling   │ │
│  │   Compose    │  │  Manifests   │  │    Chart     │  │  (CPU + Custom)      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Security Flow: Token Vault Integration
```
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌─────────┐     ┌──────────┐
│  User   │     │ Frontend│     │   Auth0     │     │ Backend │     │  Agent   │
└────┬────┘     └────┬────┘     └──────┬──────┘     └────┬────┘     └────┬─────┘
     │               │                 │                 │               │
     │  1. Login     │                 │                 │               │
     │──────────────▶│                 │                 │               │
     │               │  2. Authenticate│                 │               │
     │               │────────────────▶│                 │               │
     │               │  3. ID Token    │                 │               │
     │               │◀────────────────│                 │               │
     │               │                 │                 │               │
     │  4. Request agent action        │                 │               │
     │────────────────────────────────────────────────▶│               │
     │               │                 │                 │               │
     │               │                 │  5. Exchange    │               │
     │               │                 │◀────────────────│               │
     │               │                 │     Token       │               │
     │               │                 │                 │               │
     │               │                 │  6. Delegated   │               │
     │               │                 │────────────────▶│               │
     │               │                 │     Token       │               │
     │               │                 │   (scoped)      │               │
     │               │                 │                 │               │
     │               │                 │                 │  7. Execute   │
     │               │                 │                 │──────────────▶│
     │               │                 │                 │  with scoped  │
     │               │                 │                 │     token     │
     │               │                 │                 │               │
     │               │                 │                 │  8. Result    │
     │               │                 │                 │◀──────────────│
     │               │                 │                 │               │
     │  9. Response  │                 │                 │               │
     │◀────────────────────────────────────────────────│               │
     │               │                 │                 │               │
```

### Step-Up Authentication Flow (High-Stakes Actions)
```
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌─────────┐
│  User   │     │ Backend │     │   Auth0     │     │  Agent  │
└────┬────┘     └────┬────┘     └──────┬──────┘     └────┬────┘
     │               │                 │                 │
     │  1. "Pay my   │                 │                 │
     │   electric    │                 │                 │
     │    bill"      │                 │                 │
     │──────────────▶│                 │                 │
     │               │                 │                 │
     │               │  2. Detect HIGH │                 │
     │               │   STAKES action │                 │
     │               │─────────────────│                 │
     │               │                 │                 │
     │               │  3. Request     │                 │
     │               │   Step-Up       │                 │
     │               │────────────────▶│                 │
     │               │                 │                 │
     │  4. CIBA Push Notification      │                 │
     │◀────────────────────────────────│                 │
     │  "Approve payment of $127.50    │                 │
     │   to Demo Electric?"            │                 │
     │               │                 │                 │
     │  5. User      │                 │                 │
     │   Approves    │                 │                 │
     │   (Biometric) │                 │                 │
     │──────────────────────────────▶│                 │
     │               │                 │                 │
     │               │  6. Elevated    │                 │
     │               │     Token       │                 │
     │               │◀────────────────│                 │
     │               │                 │                 │
     │               │  7. Execute     │                 │
     │               │─────────────────────────────────▶│
     │               │                 │                 │
     │               │  8. Confirmation│                 │
     │◀──────────────│◀────────────────────────────────│
     │               │                 │                 │
```

### Agent Capabilities Matrix

| Tool | Browser Automation | Token Vault | Step-Up Auth | Dry-Run Mode |
|------|-------------------|-------------|--------------|--------------|
| **LeetCode** | ✅ Full Playwright | ✅ Session tokens | ❌ Low risk | N/A |
| **Billing** | ✅ Full Playwright | ✅ Payment provider | ✅ Required | ✅ Default ON |
| **GitHub** | ❌ API only | ✅ OAuth tokens | ⚡ For writes | N/A |
| **Gmail** | ❌ API only | ✅ Google OAuth | ⚡ For sends | N/A |
| **Slack** | ❌ API only | ✅ Slack OAuth | ❌ Low risk | N/A |
| **Calendar** | ❌ API only | ✅ Google OAuth | ⚡ For creates | N/A |
| **Drive** | ❌ API only | ✅ Google OAuth | ⚡ For deletes | N/A |
| **Discord** | ❌ API only | ✅ Discord OAuth | ❌ Low risk | N/A |
| **Salesforce** | ❌ API only | ✅ SF OAuth | ⚡ For updates | N/A |
| **Linear** | ❌ API only | ✅ Linear OAuth | ❌ Low risk | N/A |
| **Azure** | ❌ API only | ✅ Azure AD | ⚡ For deploys | N/A |

### Prometheus Metrics Implemented

```python
# Token Vault Metrics
agentos_token_vault_exchange_total{provider, status}      # Counter
agentos_token_vault_exchange_latency_seconds{provider}    # Histogram

# Step-Up Authentication  
agentos_stepup_approval_total{status}                     # Counter
agentos_stepup_approval_latency_seconds                   # Histogram

# Tool Execution
agentos_tool_calls_total{tool, provider, status}          # Counter
agentos_tool_execution_duration_seconds{tool}             # Histogram

# OpenClaw (Local LLM)
agentos_openclaw_requests_total{operation, status}        # Counter
agentos_openclaw_latency_seconds{operation}               # Histogram
agentos_openclaw_active_sessions                          # Gauge

# Browser Automation
agentos_browser_tasks_total{task_type, status}            # Counter
agentos_browser_task_duration_seconds{task_type}          # Histogram

# HTTP Layer
agentos_http_requests_total{method, endpoint, status}     # Counter
agentos_http_request_duration_seconds{method, endpoint}   # Histogram
agentos_active_requests                                   # Gauge
```

### Kubernetes Scaling Configuration

```yaml
# HorizontalPodAutoscaler with Custom Metrics
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef:
    kind: Deployment
    name: agentos-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: agentos_http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  - type: Pods
    pods:
      metric:
        name: agentos_active_executions
      target:
        type: AverageValue
        averageValue: "5"
```

---

## 📊 Demo Scenarios

### Scenario 1: "Solve my LeetCode daily"

1. User authenticates via Auth0
2. Agent receives delegated token (never sees password)
3. Browser automation navigates to LeetCode
4. AI analyzes problem and generates solution
5. Solution returned with explanation
6. All steps logged to Prometheus/Grafana

### Scenario 2: "Pay my electric bill"

1. User requests bill payment
2. System triggers Step-Up authentication (MFA)
3. User approves via CIBA push notification
4. Agent retrieves bill amount (dry-run mode)
5. Simulates payment workflow
6. Returns confirmation (no actual charge in demo)

### Scenario 3: "Create GitHub issue for bug"

1. User describes the bug
2. Token Vault exchanges for GitHub-scoped token
3. Agent creates well-formatted issue
4. Returns issue URL and number
5. Consent logged for audit

---

## 📁 Key Files for Review

```
agentos/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── agents/
│   │   ├── sovereign_agent.py     # Main agent orchestrator
│   │   └── openclaw_bridge.py     # Local LLM integration
│   ├── security/
│   │   ├── auth0_client.py        # Token Vault integration
│   │   └── token_vault.py         # Delegated token exchange
│   ├── tools/
│   │   ├── leetcode_tool.py       # LeetCode automation
│   │   ├── billing_tool.py        # Bill payment (dry-run)
│   │   └── github_tool.py         # GitHub operations
│   └── utils/
│       └── metrics.py             # Prometheus metrics
├── k8s/                           # Kubernetes manifests
├── helm/                          # Helm chart
├── prometheus/                    # Monitoring config
├── grafana/                       # Dashboards
├── docker-compose.yml             # Local deployment
├── INFRASTRUCTURE.md              # Infra documentation
└── TESTING_GUIDE.md               # Detailed testing guide
```

---

## ⚠️ Important Notes for Judges

1. **Billing is Safe**: The billing tool defaults to `dry_run: true` - no actual payments will be made during testing.

2. **LeetCode Rate Limits**: LeetCode may rate-limit automated requests. If you see errors, wait 30 seconds and retry.

3. **GitHub Token**: For GitHub tests, you'll need a personal access token with `repo` scope.

4. **Docker Requirements**:
   - Docker Desktop must be running
   - At least 4GB RAM allocated to Docker
   - Ports 3000, 3001, 8000, 9090 must be available

5. **GPU Optional**: OpenClaw (local LLM) works without GPU but is slower. Use `docker-compose --profile cpu up` for CPU-only mode.

---

## 🎯 Hackathon Tracks

This submission targets:

- **🏆 Auth0 Token Vault Track**: Deep integration with delegated token exchange, step-up auth, and consent management
- **🤖 Best AI Agent**: Sovereign agent architecture with browser automation
- **🔒 Best Use of Security**: Zero-trust agent design with comprehensive audit logging

---

## 📈 Technical Metrics & Scale

| Metric | Value |
|--------|-------|
| **Lines of Code** | 15,000+ |
| **API Endpoints** | 25+ |
| **Integrated Tools** | 12 |
| **Custom Prometheus Metrics** | 18 |
| **Kubernetes Resources** | 8 manifests |
| **Helm Values** | 50+ configurable |
| **Test Cases** | 25+ |
| **Documentation Pages** | 5 comprehensive guides |

---

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Agent Framework**: LangChain + LangGraph
- **Browser Automation**: Playwright
- **Auth**: Auth0 Token Vault, JWT, CIBA
- **Metrics**: prometheus_client

### Frontend
- **Framework**: Next.js 14
- **Auth**: Auth0 React SDK
- **Styling**: Tailwind CSS

### Infrastructure
- **Containers**: Docker, Docker Compose
- **Orchestration**: Kubernetes 1.24+
- **Package Manager**: Helm 3
- **Monitoring**: Prometheus + Grafana
- **Cache**: Redis 7

### AI/ML
- **Cloud LLM**: OpenAI GPT-4
- **Local LLM**: OpenClaw (Ollama) - Llama3, Mistral, CodeLlama

---

## 📞 Support

If you encounter issues during testing:

1. Check `docker-compose logs` for errors
2. Verify `.env` file has all credentials
3. Ensure Docker Desktop is running
4. Contact: [your-email@example.com]

---

## 🙏 Acknowledgments

- **Auth0** for the Token Vault SDK and excellent documentation
- **OpenAI** for GPT-4 API access
- **Playwright** team for amazing browser automation
- **LangChain** for the agent framework foundation

---

**Built with ❤️ for the Auth0 Hackathon 2024**

*AgentOS — Where AI Agents Meet Zero-Trust Security*
