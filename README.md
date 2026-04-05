# AgentOS: Secure Sovereign AI with Auth0 Token Vault

## �️ Submission Period Updates

- 2026-03-26: Hardened token flow to strict Auth0 Token Vault no-raw-token storage.
- 2026-03-26: Added official federated connection token exchange grant and step-up/CIBA support.
- 2026-03-26: Added integration metadata (`consent_timestamp`, `granted_scopes`) and explicit revocation history.
- 2026-03-26: Added operational dashboards (`/integrations`, `/approvals`) and interactive resume flows.
- 2026-03-26: Introduced retry+exponential backoff for all Token Vault calls for reliability.

## �📺 Live Demo Video (3 mins)

**[Insert Video Link Here]** _(Starting with a 10-second TL;DR of what problem this solves!)_

## 🐾 Project Theme: OpenClaw Sandbox

AgentOS acts as an **intermediary agent** that keeps **OpenClaw** (or any local sovereign AI) in restricted, local sandbox mode. It securely bridges the gap between private LLMs and the outside world by acting as the sole gateway to external APIs, strictly managed by the **Auth0 Token Vault for AI Agents**.

## 🔐 Security Model

- Strict Token Vault usage: No raw access or refresh tokens are written to local DB fields or logs.
- DB stores only non-sensitive connection references (e.g., `google:12345678`) using `Integration.token_reference`.
- Backend runtime obtains provider tokens through official Auth0 federated token exchange grant (`urn:auth0:params:oauth:grant-type:token-exchange:federated-connection-access-token`) via `/oauth/token`, with `connection` set to provider connection name; fallback secure identity lookup (`/api/v2/users/{id}`) is last resort only.
- Raw token inputs from clients are rejected with clear `400` errors.
- Revocation reliably deletes identity from Auth0 (`/api/v2/users/{id}/identities/{provider}/{user_id}`).

## 🏗️ Architecture (Mermaid)

```mermaid
flowchart LR
    U[User] -->|Login| A(Auth0 Login)
    A -->|ID Token| TV[Token Vault]
    TV -->|Federated exchange| AT[Agent Toolkit]
    AT -->|restricts via policy| OC[OpenClaw (local AI sandbox)]
    OC -->|calls| E[External APIs]

    AT -->|requests step-up| SU[Step-Up / CIBA]
    SU -->|approval response| AT
```

## 💡 Insights from Building

- _“We discovered that current agent frameworks lack explicit permission boundaries for long-running processes—an agent either executes an action immediately with raw tokens, or fails. Here’s the new pattern we built using Token Vault that solves it: an **Async CIBA flow** that parks the execution thread, signals the UI, and awaits human Step-Up Auth before dynamically exchanging tokens.”_
- _“Users often don't understand what scopes an AI has → our dedicated User Dashboard makes it completely transparent by mapping obscure API scopes to plain-english boundaries with a one-click **Revoke Consent** button.”_\* _“Revealed gap: agents need explicit delayed human consent for high-risk tool execution. Solved with Token Vault + step-up/CIBA-style pending approval, with in-stream agent pause and manual resume.”_

## 🛡️ Advanced Token Vault Features Built

1. **Step-Up Authentication for High-Stakes Actions:** Before destructive or highly sensitive actions (e.g., Slack messages or Google Drive uploads), the backend triggers a pending approval record via Auth0 step-up and returns `pending_approval` state with a binding message.
2. **Asynchronous Auth Flows (CIBA):** The execution thread halts. Using Server-Sent Events, the frontend UI is instantly notified to render a glowing purple `[Authorize Step-Up]` MFA prompt; this state can also be polled in a dedicated Approvals dashboard at `/approvals`.
3. **Scoped Tokens with Auto-Refresh & Revocation:** Our `/integrations/disconnect` route executes a strict cross-origin `/api/v2/users/{id}/identities/{provider}/{user_id}` DELETE call to physically purge the token from the Vault.
4. **Production-Aware Polish:** We incorporated API rate-limiting (`@limiter`), structured agent activity logging (saved to `activity.db`), and graceful retry/error handling. _To scale this in production, we would map the SQLite execution memory to Redis and deploy serverless worker instances for stateless CIBA polling._

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
   _(A public demo test account can be provided to judges upon request!)_

---

# AgentOS - Complete Architecture Diagram

## 🏗️ **High-Level System Architecture**

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      AGENTOS PLATFORM                                          │
│                         Secure Sovereign AI with Auth0 Token Vault                            │
└────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    PRESENTATION LAYER                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌──────────────────────┐          ┌──────────────────────┐         ┌────────────────────┐  │
│  │   Web Browser        │          │   Mobile Devices     │         │   API Clients      │  │
│  │   (Chrome/Firefox)   │          │   (Future Support)   │         │   (3rd Party)      │  │
│  └──────────┬───────────┘          └──────────┬───────────┘         └─────────┬──────────┘  │
│             │                                  │                               │             │
│             └──────────────────────────────────┼───────────────────────────────┘             │
│                                                │                                             │
└────────────────────────────────────────────────┼─────────────────────────────────────────────┘
                                                 │
                                                 │ HTTPS
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   AUTHENTICATION LAYER                                       │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│                              ┌─────────────────────────────┐                                 │
│                              │      Auth0 Platform         │                                 │
│                              │  ┌───────────────────────┐  │                                 │
│                              │  │  Universal Login      │  │◄────── OpenID Connect          │
│                              │  │  (OIDC/OAuth 2.0)     │  │                                 │
│                              │  └───────────┬───────────┘  │                                 │
│                              │              │              │                                 │
│                              │  ┌───────────▼───────────┐  │                                 │
│                              │  │   Token Vault         │  │◄────── Federated Token         │
│                              │  │   (NO RAW TOKENS!)    │  │        Exchange Grant          │
│                              │  └───────────┬───────────┘  │                                 │
│                              │              │              │                                 │
│                              │  ┌───────────▼───────────┐  │                                 │
│                              │  │  Step-Up Auth / CIBA  │  │◄────── MFA for High-Stakes     │
│                              │  │  (Async Approval)     │  │        Actions                 │
│                              │  └───────────────────────┘  │                                 │
│                              └──────────────┬──────────────┘                                 │
│                                             │                                                │
│                                             │ JWT ID Token                                   │
└─────────────────────────────────────────────┼────────────────────────────────────────────────┘
                                              │
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FRONTEND LAYER (Port 3000)                                │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐     │
│  │                          Next.js 16 (React 19 + TypeScript 5)                      │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐   │     │
│  │  │   Dashboard  │  │ Integrations │  │   Approvals  │  │   Activity Logs     │   │     │
│  │  │   Page (/)   │  │   Manager    │  │   UI (CIBA)  │  │   & Analytics       │   │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────────────┘   │     │
│  │                                                                                    │     │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐ │     │
│  │  │  UI Components Layer                                                         │ │     │
│  │  │  - Tailwind CSS 4 (Styling)                                                  │ │     │
│  │  │  - ReactFlow 11 (Workflow Visualization)                                     │ │     │
│  │  │  - @auth0/auth0-react (Authentication Provider)                              │ │     │
│  │  │  - Server-Sent Events (SSE) Client (Real-time Approval Notifications)        │ │     │
│  │  └──────────────────────────────────────────────────────────────────────────────┘ │     │
│  └────────────────────────────────────────────────────────────────────────────────────┘     │
│                                             │                                                │
│                                             │ HTTP REST + WebSockets/SSE                     │
└─────────────────────────────────────────────┼────────────────────────────────────────────────┘
                                              │
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   BACKEND LAYER (Port 8000)                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐     │
│  │                          FastAPI (Python 3.11 + Uvicorn ASGI)                      │     │
│  │  ┌────────────────────────────────────────────────────────────────────────────┐   │     │
│  │  │                         API ROUTING LAYER                                  │   │     │
│  │  │                                                                            │   │     │
│  │  │  /api/agent/*         - Agent planning & execution endpoints              │   │     │
│  │  │  /api/integrations/*  - OAuth integration management                      │   │     │
│  │  │  /api/approvals/*     - CIBA approval workflows                           │   │     │
│  │  │  /api/activity/*      - Execution logging & analytics                     │   │     │
│  │  │  /metrics             - Prometheus metrics endpoint                       │   │     │
│  │  └────────────────────────────────────────────────────────────────────────────┘   │     │
│  └────────────────────────────────────────────────────────────────────────────────────┘     │
│                                             │                                                │
│           ┌─────────────────────────────────┼─────────────────────────────────┐             │
│           │                                 │                                 │             │
│           ▼                                 ▼                                 ▼             │
│  ┌────────────────────┐        ┌────────────────────┐          ┌────────────────────┐      │
│  │  MIDDLEWARE LAYER  │        │  SECURITY LAYER    │          │   OBSERVABILITY    │      │
│  ├────────────────────┤        ├────────────────────┤          ├────────────────────┤      │
│  │ • JWT Validator    │        │ • Token Vault      │          │ • Prometheus       │      │
│  │ • Rate Limiter     │        │   Client           │          │   Metrics          │      │
│  │   (SlowAPI)        │        │ • Scope Checker    │          │ • Activity Logger  │      │
│  │ • CORS Handler     │        │ • Retry Logic      │          │ • Error Tracking   │      │
│  │ • Error Handler    │        │   (Tenacity)       │          │ • Request Tracing  │      │
│  └────────────────────┘        └────────────────────┘          └────────────────────┘      │
│                                             │                                                │
└─────────────────────────────────────────────┼────────────────────────────────────────────────┘
                                              │
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 AGENT ORCHESTRATION LAYER                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐     │
│  │                    LangChain + LangGraph Agent Framework                           │     │
│  │  ┌─────────────┐      ┌──────────────┐      ┌──────────────┐    ┌──────────────┐ │     │
│  │  │   Planner   │─────▶│   Executor   │─────▶│   Validator  │───▶│   Reporter   │ │     │
│  │  │   Agent     │      │   Agent      │      │   Agent      │    │   Agent      │ │     │
│  │  │             │      │              │      │              │    │              │ │     │
│  │  │ (ChatGPT)   │      │ (Tool Calls) │      │ (Checks)     │    │ (Summary)    │ │     │
│  │  └─────────────┘      └──────────────┘      └──────────────┘    └──────────────┘ │     │
│  │                                                                                    │     │
│  │  Flow: User Request → Plan Tasks → Execute Tools → Validate → Generate Summary   │     │
│  └────────────────────────────────────────────────────────────────────────────────────┘     │
│                                             │                                                │
│                                             │                                                │
│                                             ▼                                                │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐     │
│  │                              TOOL EXECUTION ENGINE                                 │     │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐ │     │
│  │  │ Google APIs    │  │  Slack/Discord │  │  GitHub/GitLab │  │  Browser Auto   │ │     │
│  │  │ (Gmail, Drive) │  │  Integration   │  │  Integration   │  │  (Playwright)   │ │     │
│  │  └────────────────┘  └────────────────┘  └────────────────┘  └─────────────────┘ │     │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐ │     │
│  │  │ File System    │  │  HTTP Requests │  │  Database Ops  │  │  Custom Tools   │ │     │
│  │  │ Operations     │  │  (API Calls)   │  │  (CRUD)        │  │  (Extensible)   │ │     │
│  │  └────────────────┘  └────────────────┘  └────────────────┘  └─────────────────┘ │     │
│  │                                                                                    │     │
│  │  Each Tool: Check if HIGH-STAKES → Trigger Approval Flow or Execute Directly      │     │
│  └────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DATA PERSISTENCE LAYER                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌────────────────────┐      ┌────────────────────┐      ┌──────────────────────┐          │
│  │  Primary Database  │      │   Cache Layer      │      │  Execution State     │          │
│  ├────────────────────┤      ├────────────────────┤      ├──────────────────────┤          │
│  │ • SQLite (Dev)     │      │ • Redis 7          │      │ • Approval Records   │          │
│  │ • PostgreSQL (Prod)│      │   - Rate limiting  │      │ • Activity Logs      │          │
│  │                    │      │   - Sessions       │      │ • Execution History  │          │
│  │ Tables:            │      │   - Task queues    │      │ • Integration Refs   │          │
│  │ - users            │      │   - SSE channels   │      │   (token_reference)  │          │
│  │ - integrations     │      └────────────────────┘      └──────────────────────┘          │
│  │ - approvals        │                                                                     │
│  │ - activity_logs    │      ⚠️  CRITICAL: NO raw tokens stored locally!                    │
│  │ - executions       │          Only connection references like "google:12345678"          │
│  └────────────────────┘                                                                     │
│                                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  EXTERNAL INTEGRATIONS                                       │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐                  │
│  │  OpenAI API        │   │  Ollama (OpenClaw) │   │  Google Workspace  │                  │
│  │  (ChatGPT GPT-4)   │   │  - Llama 3         │   │  - Gmail           │                  │
│  │                    │   │  - Mistral         │   │  - Google Drive    │                  │
│  │  Primary LLM for   │   │  - CodeLlama       │   │  - Google Calendar │                  │
│  │  agent planning    │   │                    │   │                    │                  │
│  └────────────────────┘   │  Local LLM Sandbox │   └────────────────────┘                  │
│                           │  (GPU/CPU modes)   │                                            │
│  ┌────────────────────┐   └────────────────────┘   ┌────────────────────┐                  │
│  │  Slack API         │                            │  Discord API       │                  │
│  │  - Messages        │   ┌────────────────────┐   │  - Webhooks        │                  │
│  │  - Channels        │   │  GitHub API        │   │  - Bot Commands    │                  │
│  │  - Webhooks        │   │  - Repos           │   └────────────────────┘                  │
│  └────────────────────┘   │  - Issues          │                                            │
│                           │  - Pull Requests   │   ┌────────────────────┐                  │
│  ┌────────────────────┐   └────────────────────┘   │  Custom APIs       │                  │
│  │  LeetCode API      │                            │  (Extensible)      │                  │
│  │  - Problems        │                            └────────────────────┘                  │
│  │  - Submissions     │                                                                     │
│  └────────────────────┘                                                                     │
│                                                                                              │
│  🔒 All external API access goes through Auth0 Token Vault - NO direct token storage!       │
│                                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                              MONITORING & OBSERVABILITY LAYER                                │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐     │
│  │  Prometheus (Port 9090)                      Grafana (Port 3001)                   │     │
│  │  ┌──────────────────────┐                   ┌──────────────────────┐              │     │
│  │  │ Metrics Collection:  │                   │ Visualization:       │              │     │
│  │  │ • HTTP requests      │───────────────────│ • System dashboards  │              │     │
│  │  │ • Response times     │     Queries       │ • Custom panels      │              │     │
│  │  │ • Error rates        │                   │ • Alert management   │              │     │
│  │  │ • Agent executions   │                   │ • Real-time graphs   │              │     │
│  │  │ • Tool invocations   │                   └──────────────────────┘              │     │
│  │  │ • Token vault calls  │                                                          │     │
│  │  │ • Cache hit ratios   │                   Credentials:                           │     │
│  │  └──────────────────────┘                   User: admin                            │     │
│  │                                              Pass: agentos123                       │     │
│  │  Storage: 15-day retention                                                          │     │
│  └────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                              │
│  Alert Rules: High error rate, slow response times, token vault failures, disk space        │
│                                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                            INFRASTRUCTURE & DEPLOYMENT LAYER                                 │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐     │
│  │                              LOCAL DEVELOPMENT                                     │     │
│  │  ┌──────────────────────────────────────────────────────────────────────────┐     │     │
│  │  │ Docker Compose (docker-compose.yml)                                      │     │     │
│  │  │                                                                           │     │     │
│  │  │  Services:                                                                │     │     │
│  │  │  • backend (FastAPI) - Port 8000                                          │     │     │
│  │  │  • frontend (Next.js) - Port 3000                                         │     │     │
│  │  │  • redis (Redis 7) - Port 6379                                            │     │     │
│  │  │  • prometheus (Prom v2.50) - Port 9090                                    │     │     │
│  │  │  • grafana (Grafana 10.3) - Port 3001                                     │     │     │
│  │  │  • openclaw (Ollama GPU) - Port 11434 [Profile: gpu]                     │     │     │
│  │  │  • openclaw-cpu (Ollama CPU) - Port 11434 [Profile: cpu]                 │     │     │
│  │  │                                                                           │     │     │
│  │  │  Network: agentos-network (172.28.0.0/16)                                │     │     │
│  │  │  Volumes: redis_data, prometheus_data, grafana_data, ollama_data         │     │     │
│  │  │                                                                           │     │     │
│  │  │  Start: docker-compose up -d                                             │     │     │
│  │  │  With GPU: docker-compose --profile gpu up -d                            │     │     │
│  │  └──────────────────────────────────────────────────────────────────────────┘     │     │
│  └────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐     │
│  │                           PRODUCTION DEPLOYMENT                                    │     │
│  │  ┌──────────────────────────────────────────────────────────────────────────┐     │     │
│  │  │ Kubernetes Cluster (k8s/)                                                │     │     │
│  │  │                                                                           │     │     │
│  │  │  Namespace: agentos                                                      │     │     │
│  │  │                                                                           │     │     │
│  │  │  Deployments:                                                            │     │     │
│  │  │  • backend-deployment (3-20 replicas with HPA)                           │     │     │
│  │  │    - CPU: 500m-2000m, Memory: 1Gi-4Gi                                    │     │     │
│  │  │    - Auto-scale on CPU (70%), Memory (80%), HTTP RPS (100)               │     │     │
│  │  │  • frontend-deployment (2+ replicas)                                     │     │     │
│  │  │  • redis-deployment (1 replica with persistence)                         │     │     │
│  │  │  • prometheus-deployment (monitoring stack)                              │     │     │
│  │  │  • grafana-deployment (visualization)                                    │     │     │
│  │  │                                                                           │     │     │
│  │  │  Services:                                                                │     │     │
│  │  │  • backend-service (ClusterIP + NodePort 30800)                          │     │     │
│  │  │  • frontend-service (ClusterIP + NodePort 30300)                         │     │     │
│  │  │  • redis-service (ClusterIP)                                             │     │     │
│  │  │  • prometheus-service (ClusterIP + NodePort 30900)                       │     │     │
│  │  │  • grafana-service (ClusterIP + NodePort 30301)                          │     │     │
│  │  │                                                                           │     │     │
│  │  │  Ingress:                                                                 │     │     │
│  │  │  • NGINX Ingress Controller                                              │     │     │
│  │  │  • Path routing: /api → backend, / → frontend                            │     │     │
│  │  │  • TLS/SSL termination                                                   │     │     │
│  │  │                                                                           │     │     │
│  │  │  ConfigMaps & Secrets:                                                   │     │     │
│  │  │  • Environment variables (Auth0, OpenAI keys)                            │     │     │
│  │  │  • Prometheus config, Grafana dashboards                                 │     │     │
│  │  │                                                                           │     │     │
│  │  │  Deploy: kubectl apply -f k8s/                                           │     │     │
│  │  └──────────────────────────────────────────────────────────────────────────┘     │     │
│  │                                                                                    │     │
│  │  ┌──────────────────────────────────────────────────────────────────────────┐     │     │
│  │  │ Helm Chart (helm/agentos/)                                               │     │     │
│  │  │                                                                           │     │     │
│  │  │  Templates: Service, Deployment, HPA, Ingress                            │     │     │
│  │  │  Values: Configurable replicas, resources, scaling policies              │     │     │
│  │  │                                                                           │     │     │
│  │  │  Install: helm install agentos ./helm/agentos                            │     │     │
│  │  │  Upgrade: helm upgrade agentos ./helm/agentos                            │     │     │
│  │  └──────────────────────────────────────────────────────────────────────────┘     │     │
│  └────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 **Data Flow Diagram - Complete Request Lifecycle**

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE REQUEST LIFECYCLE                                        │
└───────────────────────────────────────────────────────────────────────────────────────────┘

STEP 1: USER AUTHENTICATION
┌─────────────┐
│   User      │
│  (Browser)  │
└──────┬──────┘
       │
       │ 1. Click "Login"
       ▼
┌──────────────────────┐
│  Next.js Frontend    │
│  (/login redirect)   │
└──────┬───────────────┘
       │
       │ 2. Redirect to Auth0 Universal Login
       ▼
┌───────────────────────────────┐
│  Auth0 Universal Login        │
│  - Email/Password             │
│  - Social Login (Google, etc) │
│  - Enterprise SSO             │
└──────┬────────────────────────┘
       │
       │ 3. Authenticate user
       │    (MFA if enabled)
       ▼
┌───────────────────────────────┐
│  Auth0 Authorization Server   │
│  - Validate credentials       │
│  - Generate tokens            │
│  - Create session             │
└──────┬────────────────────────┘
       │
       │ 4. Return ID Token (JWT) + Access Token
       ▼
┌──────────────────────┐
│  Next.js Frontend    │
│  - Store JWT in      │
│    sessionStorage    │
│  - Set user context  │
└──────────────────────┘


STEP 2: AGENT REQUEST - LOW-STAKES ACTION (Read-Only)
┌─────────────┐
│   User      │
│  Dashboard  │
└──────┬──────┘
       │
       │ 5. Request: "Read my latest Gmail messages"
       ▼
┌──────────────────────┐
│  POST /api/agent/plan│
│  Headers:            │
│  Authorization:      │
│   Bearer <JWT>       │
└──────┬───────────────┘
       │
       │ 6. JWT Validation
       ▼
┌──────────────────────────┐
│  FastAPI Backend         │
│  JWT Middleware:         │
│  - Decode JWT            │
│  - Verify signature      │
│  - Check expiration      │
│  - Extract user context  │
└──────┬───────────────────┘
       │
       │ 7. user_context = {"sub": "auth0|123", "email": "user@example.com"}
       ▼
┌─────────────────────────────────┐
│  Planner Agent (LangChain)      │
│  LLM: OpenAI GPT-4              │
│                                 │
│  Input: "Read latest Gmail"     │
│  Output: [                      │
│    {tool: "read_gmail",         │
│     args: {count: 10}},         │
│    {tool: "summarize_text"}     │
│  ]                              │
└──────┬──────────────────────────┘
       │
       │ 8. Execution plan created
       ▼
┌─────────────────────────────────┐
│  Executor Agent                 │
│  For tool in plan:              │
│    Check if HIGH-STAKES         │
└──────┬──────────────────────────┘
       │
       │ 9. read_gmail is LOW-STAKES (read-only)
       ▼
┌─────────────────────────────────────────┐
│  Integration Service                    │
│  1. Lookup integration record in DB     │
│     WHERE user_id AND provider='google' │
│  2. Found: token_reference =            │
│     "google:987654321"                  │
└──────┬──────────────────────────────────┘
       │
       │ 10. Request provider token from Auth0 Token Vault
       ▼
┌──────────────────────────────────────────────────┐
│  Auth0 Token Vault API                           │
│  POST /oauth/token                               │
│  {                                               │
│    grant_type: "urn:auth0:params:oauth:         │
│      grant-type:token-exchange:                  │
│      federated-connection-access-token",         │
│    connection: "google-oauth2",                  │
│    subject_token: <user_id_token>,               │
│    scope: "https://www.googleapis.com/auth/gmail.readonly" │
│  }                                               │
└──────┬───────────────────────────────────────────┘
       │
       │ 11. Return scoped provider access token (ephemeral)
       │     NEVER stored in AgentOS database!
       ▼
┌─────────────────────────────────────────┐
│  Tool Executor                          │
│  Execute: read_gmail(token, count=10)   │
│  HTTP GET to Gmail API with token       │
└──────┬──────────────────────────────────┘
       │
       │ 12. Gmail API returns messages
       ▼
┌─────────────────────────────────────────┐
│  Summarize Tool                         │
│  LLM summarizes email content           │
└──────┬──────────────────────────────────┘
       │
       │ 13. Generate final summary
       ▼
┌─────────────────────────────────────────┐
│  Activity Logger                        │
│  INSERT INTO activity_logs:             │
│  {                                      │
│    user_id, action: "read_gmail",       │
│    status: "success",                   │
│    timestamp, result_preview            │
│  }                                      │
└──────┬──────────────────────────────────┘
       │
       │ 14. Return result to frontend
       ▼
┌──────────────────────┐
│  Frontend Dashboard  │
│  Display: "You have  │
│  5 unread emails..." │
└──────────────────────┘


STEP 3: HIGH-STAKES ACTION (Requires Step-Up Auth)
┌─────────────┐
│   User      │
│  Dashboard  │
└──────┬──────┘
       │
       │ 15. Request: "Send a message to #general Slack: 'Meeting in 10 mins'"
       ▼
┌──────────────────────┐
│  POST /api/agent/plan│
│  Authorization:      │
│   Bearer <JWT>       │
└──────┬───────────────┘
       │
       │ 16. JWT validated, plan created
       ▼
┌─────────────────────────────────┐
│  Planner Agent                  │
│  Output: [                      │
│    {tool: "send_slack_message", │
│     args: {                     │
│       channel: "#general",      │
│       text: "Meeting..."        │
│     }}                          │
│  ]                              │
└──────┬──────────────────────────┘
       │
       │ 17. Executor checks tool type
       ▼
┌─────────────────────────────────┐
│  Executor Agent                 │
│  send_slack_message is          │
│  HIGH-STAKES (destructive write)│
└──────┬──────────────────────────┘
       │
       │ 18. Create approval record
       ▼
┌──────────────────────────────────────────┐
│  Approvals Service                       │
│  INSERT INTO approvals:                  │
│  {                                       │
│    id: "appr_abc123",                    │
│    user_id: "auth0|123",                 │
│    tool: "send_slack_message",           │
│    args: {...},                          │
│    status: "pending",                    │
│    created_at: NOW(),                    │
│    binding_message: "AgentOS wants to   │
│      send a Slack message to #general.  │
│      Authorize to proceed."              │
│  }                                       │
└──────┬───────────────────────────────────┘
       │
       │ 19. Return 202 Accepted with approval_id
       ▼
┌──────────────────────────────────────────┐
│  FastAPI Response                        │
│  {                                       │
│    status: "pending_approval",           │
│    approval_id: "appr_abc123",           │
│    message: "Human consent required"     │
│  }                                       │
└──────┬───────────────────────────────────┘
       │
       │ 20. SSE notification sent to frontend
       │     (Server-Sent Events channel)
       ▼
┌──────────────────────────────────────────┐
│  Frontend Approvals UI                   │
│  🟣 [SECURITY HALT]                      │
│  "AgentOS wants to send a Slack message  │
│   to #general. Authorize to proceed."    │
│                                          │
│   [Authorize Step-Up] [Deny]             │
└──────┬───────────────────────────────────┘
       │
       │ 21. User clicks [Authorize]
       │     POST /api/approvals/appr_abc123/approve
       ▼
┌──────────────────────────────────────────┐
│  Backend Approval Handler                │
│  1. Verify approval_id exists            │
│  2. Check user_id matches                │
│  3. Trigger Auth0 Step-Up flow           │
└──────┬───────────────────────────────────┘
       │
       │ 22. Redirect to Auth0 Step-Up Auth (MFA)
       ▼
┌──────────────────────────────────────────┐
│  Auth0 Step-Up / CIBA Flow               │
│  - Request MFA (SMS, TOTP, Biometric)    │
│  - User confirms identity                │
│  - Generate elevated-scope token         │
└──────┬───────────────────────────────────┘
       │
       │ 23. Step-Up completed, return elevated token
       ▼
┌──────────────────────────────────────────┐
│  Backend Resume Execution                │
│  1. UPDATE approvals SET status='approved'│
│  2. Request Slack token from Token Vault │
│  3. Execute: send_slack_message()        │
└──────┬───────────────────────────────────┘
       │
       │ 24. POST to Slack API with token
       ▼
┌──────────────────────────────────────────┐
│  Slack API                               │
│  Message sent successfully               │
└──────┬───────────────────────────────────┘
       │
       │ 25. Log activity & notify user
       ▼
┌──────────────────────────────────────────┐
│  Activity Logger                         │
│  INSERT: {                               │
│    action: "send_slack_message",         │
│    status: "success",                    │
│    approval_id: "appr_abc123",           │
│    consent_timestamp: NOW()              │
│  }                                       │
└──────┬───────────────────────────────────┘
       │
       │ 26. Success response
       ▼
┌──────────────────────────────────────────┐
│  Frontend Dashboard                      │
│  ✅ "Message sent to #general"           │
└──────────────────────────────────────────┘
```

---

## 🔐 **Security Architecture - Token Vault Flow**

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    ZERO-TRUST TOKEN VAULT ARCHITECTURE                     │
└────────────────────────────────────────────────────────────────────────────┘

PRINCIPLE: Raw tokens NEVER touch AgentOS infrastructure
           Only non-sensitive connection references are stored

┌─────────────────────────────────────────────────────────────────────────────┐
│  INITIAL INTEGRATION SETUP (One-Time OAuth Flow)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  User Action: Click "Connect Google" in /integrations                       │
│                                                                             │
│  1. Frontend → POST /api/integrations/connect/google                        │
│     ↓                                                                       │
│  2. Backend generates Auth0 authorization URL                               │
│     ↓                                                                       │
│  3. Redirect user to Auth0 Universal Login with connection=google-oauth2   │
│     ↓                                                                       │
│  4. User authenticates with Google (OAuth 2.0 consent screen)              │
│     ↓                                                                       │
│  5. Google returns authorization code to Auth0                              │
│     ↓                                                                       │
│  6. Auth0 exchanges code for tokens AND stores in Token Vault              │
│     (access_token, refresh_token stored securely in Auth0)                  │
│     ↓                                                                       │
│  7. Auth0 creates federated identity link:                                  │
│     user_id: auth0|123 → google-oauth2|987654321                           │
│     ↓                                                                       │
│  8. Auth0 redirects to AgentOS callback:                                    │
│     /api/integrations/callback?code=<auth_code>                             │
│     ↓                                                                       │
│  9. Backend validates callback, stores ONLY connection reference:           │
│                                                                             │
│     ┌──────────────────────────────────────────────────────────┐           │
│     │  AgentOS Database (Local)                                │           │
│     │  ┌────────────────────────────────────────────────────┐  │           │
│     │  │ Table: integrations                                │  │           │
│     │  │ ┌──────────────────────────────────────────────┐   │  │           │
│     │  │ │ user_id: auth0|123                           │   │  │           │
│     │  │ │ provider: google                             │   │  │           │
│     │  │ │ token_reference: "google:987654321"          │   │  │           │
│     │  │ │ granted_scopes: ["gmail.readonly", ...]      │   │  │           │
│     │  │ │ consent_timestamp: 2026-04-05T10:00:00Z      │   │  │           │
│     │  │ │ status: active                               │   │  │           │
│     │  │ └──────────────────────────────────────────────┘   │  │           │
│     │  └────────────────────────────────────────────────────┘  │           │
│     └──────────────────────────────────────────────────────────┘           │
│                                                                             │
│     ⚠️  NO access_token field                                              │
│     ⚠️  NO refresh_token field                                             │
│     ⚠️  ONLY non-sensitive metadata                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  RUNTIME TOKEN RETRIEVAL (Every Tool Execution)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Agent needs to call Gmail API                                              │
│                                                                             │
│  1. Executor checks DB for integration record                               │
│     SELECT * FROM integrations WHERE user_id='auth0|123' AND provider='google' │
│     Result: token_reference = "google:987654321"                            │
│     ↓                                                                       │
│  2. Backend makes federated token exchange request to Auth0:                │
│                                                                             │
│     POST https://{AUTH0_DOMAIN}/oauth/token                                 │
│     {                                                                       │
│       grant_type: "urn:auth0:params:oauth:grant-type:                      │
│                    token-exchange:federated-connection-access-token",       │
│       connection: "google-oauth2",                                          │
│       subject_token: <user_id_token>,                                       │
│       scope: "https://www.googleapis.com/auth/gmail.readonly",              │
│       client_id: <AUTH0_CLIENT_ID>,                                         │
│       client_secret: <AUTH0_CLIENT_SECRET>                                  │
│     }                                                                       │
│     ↓                                                                       │
│  3. Auth0 Token Vault:                                                      │
│     a) Validates request (client credentials, user session)                 │
│     b) Checks requested scope against granted_scopes                        │
│     c) Retrieves stored refresh_token (if needed)                           │
│     d) Obtains fresh access_token from Google (auto-refresh if expired)     │
│     e) Returns ephemeral provider access token                              │
│     ↓                                                                       │
│  4. Response (ephemeral, short-lived):                                      │
│     {                                                                       │
│       access_token: "ya29.a0AfH6SMB...",  ← NEVER stored in AgentOS        │
│       token_type: "Bearer",                                                 │
│       expires_in: 3600                                                      │
│     }                                                                       │
│     ↓                                                                       │
│  5. Backend uses token ONLY in memory for immediate API call:               │
│     GET https://gmail.googleapis.com/gmail/v1/users/me/messages             │
│     Authorization: Bearer ya29.a0AfH6SMB...                                 │
│     ↓                                                                       │
│  6. Token discarded after API call completes                                │
│     (Garbage collected, never persisted to disk/DB/logs)                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  REVOCATION FLOW (User Disconnects Integration)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  User Action: Click "Disconnect" in /integrations                            │
│                                                                             │
│  1. Frontend → DELETE /api/integrations/disconnect/google                   │
│     ↓                                                                       │
│  2. Backend retrieves integration record:                                   │
│     token_reference = "google:987654321"                                    │
│     ↓                                                                       │
│  3. Backend calls Auth0 Management API to delete federated identity:        │
│                                                                             │
│     DELETE https://{AUTH0_DOMAIN}/api/v2/users/{user_id}/identities/       │
│            google-oauth2/987654321                                          │
│     ↓                                                                       │
│  4. Auth0 Token Vault:                                                      │
│     a) Revokes stored refresh_token with Google                             │
│     b) Invalidates all cached access_tokens                                 │
│     c) Deletes federated identity link                                      │
│     ↓                                                                       │
│  5. Backend deletes local integration record:                               │
│     DELETE FROM integrations WHERE id=<id>                                  │
│     ↓                                                                       │
│  6. INSERT INTO activity_logs:                                              │
│     { action: "revoke_integration", provider: "google", ... }               │
│     ↓                                                                       │
│  7. Response: { status: "disconnected" }                                    │
│                                                                             │
│  Result: All traces removed from both Auth0 Vault and AgentOS               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  RETRY & ERROR HANDLING (Production Reliability)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  All Token Vault calls wrapped with exponential backoff (Tenacity):         │
│                                                                             │
│  @retry(                                                                    │
│      stop=stop_after_attempt(3),                                            │
│      wait=wait_exponential(multiplier=1, min=2, max=10),                    │
│      retry=retry_if_exception_type(HTTPError)                               │
│  )                                                                          │
│  def get_provider_token(user_id, provider, scope):                          │
│      # Token exchange request                                               │
│                                                                             │
│  Failure scenarios:                                                         │
│  • Network timeout → Retry (2s, 4s, 8s delays)                             │
│  • 429 Rate Limit → Exponential backoff                                     │
│  • 401 Unauthorized → Trigger re-authentication flow                        │
│  • 403 Forbidden → Check scope permissions, log error                       │
│  • Refresh token expired → Notify user to re-connect integration            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 **Technology Stack Summary**

| Layer | Components | Technologies |
|-------|-----------|--------------|
| **Frontend** | UI, Routing, State Management | Next.js 16, React 19, TypeScript 5, Tailwind CSS 4, ReactFlow, Auth0-React |
| **Backend** | API, Agent Engine, Orchestration | FastAPI, Python 3.11, LangChain, LangGraph, OpenAI, Playwright |
| **Authentication** | Identity, Authorization, Token Management | Auth0 (OIDC, OAuth 2.0, Token Vault, CIBA) |
| **Data Layer** | Persistence, Caching, Sessions | SQLite (Dev), PostgreSQL (Prod), Redis 7 |
| **AI/ML** | Language Models | OpenAI GPT-4 (Cloud), Ollama (Llama 3, Mistral - Local) |
| **Observability** | Metrics, Dashboards, Alerts | Prometheus 2.50, Grafana 10.3, Custom Activity Logs |
| **Infrastructure** | Containerization, Orchestration | Docker, Kubernetes 1.24+, Helm v3 |
| **External APIs** | Integrations | Google Workspace, Slack, Discord, GitHub, LeetCode |

---

## 🚦 **Deployment Architecture**

### **Development Environment**
```
Local Machine
├── Docker Compose (orchestration)
│   ├── Backend container (port 8000)
│   ├── Frontend container (port 3000)
│   ├── Redis container (port 6379)
│   ├── Prometheus container (port 9090)
│   ├── Grafana container (port 3001)
│   └── Ollama container (port 11434) [Optional GPU/CPU]
└── Network: agentos-network (172.28.0.0/16)

Start: docker-compose up -d
Stop: docker-compose down
Logs: docker-compose logs -f
```

### **Production Environment**
```
Kubernetes Cluster
├── Namespace: agentos
├── Backend Deployment
│   ├── Replicas: 3-20 (HPA based on CPU/Memory/RPS)
│   ├── Resources: CPU 500m-2000m, Memory 1Gi-4Gi
│   └── Service: ClusterIP + NodePort 30800
├── Frontend Deployment
│   ├── Replicas: 2+ (Auto-scaling)
│   └── Service: ClusterIP + NodePort 30300
├── Redis Deployment
│   ├── Replicas: 1 (StatefulSet for persistence)
│   └── Service: ClusterIP
├── Prometheus & Grafana
│   └── Services: ClusterIP + NodePorts
├── Ingress (NGINX)
│   ├── Path /api/* → Backend Service
│   ├── Path /* → Frontend Service
│   └── TLS/SSL Termination
└── Secrets & ConfigMaps
    ├── Auth0 credentials
    ├── OpenAI API keys
    └── Prometheus/Grafana configs

Deploy: kubectl apply -f k8s/ OR helm install agentos ./helm/agentos
```

---

## 🔍 **Key Architectural Patterns**

1. **Zero-Trust Token Management**
   - No raw tokens stored locally
   - Federated token exchange via Auth0
   - Ephemeral tokens with automatic refresh

2. **Human-in-the-Loop Authorization**
   - Async CIBA flows for high-stakes actions
   - Real-time SSE notifications
   - Step-Up authentication with MFA

3. **Microservices Architecture**
   - Containerized services with Docker
   - Kubernetes orchestration for scalability
   - Service mesh for inter-service communication

4. **Agent Orchestration**
   - LangChain + LangGraph framework
   - Multi-agent workflows (Planner → Executor → Validator → Reporter)
   - Extensible tool ecosystem

5. **Observability First**
   - Prometheus metrics collection
   - Grafana visualization
   - Structured activity logging
   - Alert rules for SLA monitoring

6. **Production Ready**
   - Horizontal auto-scaling (HPA)
   - Health checks and readiness probes
   - Rolling updates with zero downtime
   - 15-day metrics retention

---

## 📈 **Scalability & Performance**

- **Backend Scaling:** 3-20 replicas based on CPU (70%), Memory (80%), HTTP RPS (100/pod)
- **Database:** PostgreSQL with connection pooling for production
- **Caching:** Redis for session management and rate limiting
- **CDN:** Static assets served via Next.js optimized build
- **API Rate Limiting:** SlowAPI middleware (per-user quotas)
- **Retry Logic:** Exponential backoff for external API calls

---

## 🛡️ **Security Layers**

1. **Authentication:** Auth0 OIDC with JWT validation
2. **Authorization:** Scope-based access control via Token Vault
3. **Data Protection:** No raw tokens in database/logs
4. **Network Security:** HTTPS/TLS everywhere, CORS policies
5. **Audit Trail:** Complete activity logging with consent timestamps
6. **MFA:** Step-Up authentication for destructive actions
7. **Secrets Management:** Kubernetes Secrets for sensitive configs

---

**End of Architecture Diagram**


## Bonus Blog Post: Securing the Autonomous Frontier

Developing an autonomous agent capable of traversing our digital lives is thrilling, but handing an LLM the raw access keys to an inbox or a corporate Slack channel fundamentally breaks standard OAuth patterns. We knew early on that AgentOS couldn't function securely unless the human remained in total control. The technical hurdle was implementing an asynchronous, "human-in-the-loop" step-up authorization flow without constantly breaking the agent's context window.

Auth0’s Token Vault fundamentally altered our approach. Instead of managing complex token lifecycles and encrypted state machines in our database, we offloaded the entire authorization layer to Auth0. The revelation came when we built our `ConsentRequiredException` handling. We realized that the Auth0 Token Vault doesn’t just store tokens safely—it allows the agent runtime to safely "pause" whenever an elevated scope is required.

We integrated an event-driven hook into our streaming Execution Engine. The moment an agent requests a high-stakes tool execution (e.g., Google Drive uploads), our backend verifies the Vault context. If explicit consent is absent, the execution suspends, and the UI immediately prompts the user with a stylized alert: "SECURITY HALT: Human Consent Required". Only upon Auth0’s secure confirmation does the stream resume. It feels magical—the agent proposes the work, Auth0 secures the boundary, and the user holds the final key. Token Vault proved that sovereign, hyper-capable agents and zero-trust security are not mutually exclusive; they are seamlessly complementary.
