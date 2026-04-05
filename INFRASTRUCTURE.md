# AgentOS Infrastructure Guide

Complete infrastructure setup for production deployment with Docker, Kubernetes, observability, and local LLM integration.

## Table of Contents

1. [Quick Start (Docker Compose)](#quick-start-docker-compose)
2. [Docker Setup](#docker-setup)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Helm Chart](#helm-chart)
5. [Observability (Prometheus + Grafana)](#observability)
6. [OpenClaw Local LLM](#openclaw-local-llm)
7. [Production Checklist](#production-checklist)

---

## Quick Start (Docker Compose)

**One command to run everything locally:**

```bash
# Start all services (backend, frontend, Redis, Prometheus, Grafana)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop everything
docker-compose down
```

**Access Points:**
| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js UI |
| Backend API | http://localhost:8000 | FastAPI |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Prometheus | http://localhost:9090 | Metrics |
| Grafana | http://localhost:3001 | Dashboards |

**Grafana Login:** `admin` / `agentos123`

---

## Docker Setup

### Backend Dockerfile

```dockerfile
# Dockerfile.backend - Production multi-stage build
FROM python:3.11-slim AS builder
# ... (see Dockerfile.backend for full implementation)
```

**Build Commands:**

```bash
# Production build
docker build -f Dockerfile.backend -t agentos-backend:latest .

# Development build (with hot reload)
docker build -f Dockerfile.backend.dev -t agentos-backend:dev .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e AUTH0_DOMAIN=your-domain.auth0.com \
  -e AUTH0_CLIENT_ID=your-client-id \
  -e OPENAI_API_KEY=sk-xxx \
  agentos-backend:latest
```

### Frontend Dockerfile

```bash
# Build frontend
docker build -f Dockerfile.frontend -t agentos-frontend:latest ./frontend

# Run
docker run -d -p 3000:3000 agentos-frontend:latest
```

### Docker Compose Services

| Service    | Image           | Port  | Description                  |
| ---------- | --------------- | ----- | ---------------------------- |
| backend    | Custom          | 8000  | FastAPI + Playwright browser |
| frontend   | Custom          | 3000  | Next.js UI                   |
| redis      | redis:7-alpine  | 6379  | Session cache, rate limiting |
| prometheus | prom/prometheus | 9090  | Metrics collection           |
| grafana    | grafana/grafana | 3001  | Dashboards                   |
| openclaw   | ollama/ollama   | 11434 | Local LLM (optional, GPU)    |

**GPU Support for OpenClaw:**

```bash
# Run with GPU profile
docker-compose --profile gpu up -d openclaw
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Ingress controller (nginx-ingress recommended)
- Prometheus Operator (optional, for monitoring)

### Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (edit with real values first!)
kubectl apply -f k8s/secrets.yaml

# Deploy all resources
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Deploy monitoring
kubectl apply -f k8s/prometheus.yaml
```

### Kubernetes Resources

```
k8s/
├── namespace.yaml      # agentos namespace
├── deployment.yaml     # Backend (3 replicas), Frontend (2), Redis
├── service.yaml        # ClusterIP + NodePort services
├── ingress.yaml        # NGINX ingress with path routing
├── hpa.yaml            # Horizontal Pod Autoscaler
├── prometheus.yaml     # Prometheus + Grafana
└── secrets.yaml        # Secrets template (edit before applying!)
```

### Scaling Configuration

**Horizontal Pod Autoscaler (HPA):**

| Metric   | Target  | Min Pods | Max Pods |
| -------- | ------- | -------- | -------- |
| CPU      | 70%     | 3        | 20       |
| Memory   | 80%     | 3        | 20       |
| HTTP RPS | 100/pod | 3        | 20       |

```yaml
# Custom metrics scaling (requires Prometheus Adapter)
- type: Pods
  pods:
    metric:
      name: agentos_http_requests_per_second
    target:
      type: AverageValue
      averageValue: "100"
```

### Verify Deployment

```bash
# Check pods
kubectl get pods -n agentos

# Check services
kubectl get svc -n agentos

# Check ingress
kubectl get ingress -n agentos

# View logs
kubectl logs -f deployment/agentos-backend -n agentos

# Scale manually
kubectl scale deployment/agentos-backend --replicas=5 -n agentos
```

---

## Helm Chart

For production deployments, use the Helm chart for more control:

```bash
# Install with default values
helm install agentos ./helm/agentos -n agentos --create-namespace

# Install with custom values
helm install agentos ./helm/agentos -n agentos \
  --set backend.auth0.domain=your-domain.auth0.com \
  --set backend.auth0.clientId=your-client-id \
  --set backend.openai.apiKey=sk-xxx

# Upgrade
helm upgrade agentos ./helm/agentos -n agentos

# Uninstall
helm uninstall agentos -n agentos
```

### Helm Values

Key configuration in `helm/agentos/values.yaml`:

```yaml
backend:
  replicaCount: 3
  image:
    repository: ghcr.io/yourusername/agentos-backend
    tag: latest

  auth0:
    domain: ""
    clientId: ""
    clientSecret: ""

  resources:
    limits:
      cpu: "2"
      memory: 4Gi
    requests:
      cpu: 500m
      memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
```

---

## Observability

### Prometheus Metrics

**Custom Metrics Exposed:**

| Metric                                         | Type      | Labels                   | Description                     |
| ---------------------------------------------- | --------- | ------------------------ | ------------------------------- |
| `agentos_token_vault_exchange_total`           | Counter   | provider, status         | Token Vault exchange operations |
| `agentos_token_vault_exchange_latency_seconds` | Histogram | provider                 | Exchange latency                |
| `agentos_stepup_approval_total`                | Counter   | status                   | Step-up auth approvals          |
| `agentos_stepup_approval_latency_seconds`      | Histogram | -                        | CIBA approval latency           |
| `agentos_tool_calls_total`                     | Counter   | tool, provider, status   | Agent tool invocations          |
| `agentos_openclaw_requests_total`              | Counter   | operation, status        | OpenClaw bridge requests        |
| `agentos_openclaw_latency_seconds`             | Histogram | operation                | OpenClaw latency                |
| `agentos_browser_tasks_total`                  | Counter   | task_type, status        | Browser automation tasks        |
| `agentos_http_requests_total`                  | Counter   | method, endpoint, status | HTTP request counts             |
| `agentos_http_request_duration_seconds`        | Histogram | method, endpoint         | Request latency                 |

### Grafana Dashboards

Pre-configured dashboard included at `grafana/dashboards/agentos-main.json`:

**Dashboard Panels:**

1. **Token Vault Overview** - Exchange success rate, latency percentiles
2. **Step-Up Auth** - Approval rates, CIBA latency
3. **Tool Execution** - Calls by provider (Gmail, Slack, GitHub, etc.)
4. **OpenClaw Metrics** - Local LLM usage, latency
5. **Browser Automation** - Task success rates
6. **HTTP Overview** - Request rate, error rate, latency

### Prometheus Alerts

Alert rules in `prometheus/alerts.yml`:

| Alert                     | Severity | Condition               |
| ------------------------- | -------- | ----------------------- |
| HighTokenVaultFailureRate | critical | >5% failure over 5min   |
| StepUpApprovalSlow        | warning  | p95 latency >10s        |
| HighToolFailureRate       | warning  | >10% failure over 10min |
| HighErrorRate             | critical | >5% HTTP 5xx over 5min  |
| SlowAPIResponses          | warning  | p95 latency >2s         |

### Access Metrics

```bash
# Raw Prometheus metrics
curl http://localhost:8000/metrics

# Prometheus UI
open http://localhost:9090

# Grafana dashboards
open http://localhost:3001
```

---

## OpenClaw Local LLM

OpenClaw provides a secure local LLM sandbox for agent operations.

### Setup

```bash
# Start with GPU support
docker-compose --profile gpu up -d openclaw

# Without GPU (CPU only)
docker run -d -p 11434:11434 ollama/ollama

# Pull a model
docker exec -it agentos-openclaw ollama pull llama3
```

### Available Models

| Model      | Size  | Use Case                 |
| ---------- | ----- | ------------------------ |
| llama3     | 4.7GB | General purpose          |
| llama3:70b | 40GB  | High quality (needs GPU) |
| codellama  | 3.8GB | Code generation          |
| mistral    | 4.1GB | Fast, efficient          |
| mixtral    | 26GB  | Large, high quality      |

### Usage in Code

```python
from agents.openclaw_bridge import get_openclaw_bridge

bridge = get_openclaw_bridge()

# Generate text
result = bridge.generate(
    user_context={"sub": "user_123"},
    prompt="Explain quantum computing",
    model="llama3"
)

# Chat with history
result = bridge.chat(
    user_context={"sub": "user_123"},
    messages=[
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "What's 2+2?"}
    ]
)

# Create embeddings for RAG
result = bridge.create_embedding(
    user_context={"sub": "user_123"},
    text="Document to embed",
    model="nomic-embed-text"
)
```

### Environment Variables

| Variable       | Default   | Description   |
| -------------- | --------- | ------------- |
| OPENCLAW_HOST  | localhost | OpenClaw host |
| OPENCLAW_PORT  | 11434     | OpenClaw port |
| OPENCLAW_MODEL | llama3    | Default model |

---

## Production Checklist

### Security

- [ ] Replace all placeholder secrets in `k8s/secrets.yaml`
- [ ] Enable TLS in ingress (add cert-manager)
- [ ] Configure Auth0 production tenant
- [ ] Enable HTTPS on all endpoints
- [ ] Review and restrict network policies
- [ ] Enable audit logging

### High Availability

- [ ] Set `replicaCount >= 3` for backend
- [ ] Configure Redis cluster or sentinel
- [ ] Enable HPA with appropriate thresholds
- [ ] Configure PodDisruptionBudget
- [ ] Set up multi-region deployment (optional)

### Monitoring

- [ ] Verify Prometheus scraping backend `/metrics`
- [ ] Import Grafana dashboards
- [ ] Configure alerting (PagerDuty, Slack, etc.)
- [ ] Set up log aggregation (Loki, ELK)
- [ ] Enable tracing (Jaeger, optional)

### Performance

- [ ] Configure appropriate resource limits
- [ ] Enable Redis caching
- [ ] Configure CDN for frontend
- [ ] Set up connection pooling
- [ ] Review browser pool size

### Backup & Recovery

- [ ] Configure database backups (if using persistent storage)
- [ ] Document recovery procedures
- [ ] Test rollback procedures
- [ ] Enable persistent volume backups

---

## Troubleshooting

### Common Issues

**Backend won't start:**

```bash
# Check logs
docker-compose logs backend
kubectl logs deployment/agentos-backend -n agentos

# Common causes:
# - Missing environment variables
# - Playwright browsers not installed
# - Auth0 configuration issues
```

**Prometheus not scraping:**

```bash
# Check targets
curl http://localhost:9090/api/v1/targets

# Verify backend metrics endpoint
curl http://localhost:8000/metrics
```

**OpenClaw not responding:**

```bash
# Check if model is loaded
curl http://localhost:11434/api/tags

# Pull model if missing
ollama pull llama3
```

**HPA not scaling:**

```bash
# Check HPA status
kubectl describe hpa agentos-backend -n agentos

# Verify metrics-server is running
kubectl get pods -n kube-system | grep metrics-server
```

### Debug Mode

```bash
# Run backend with debug logging
docker-compose run -e LOG_LEVEL=DEBUG backend

# Enable Playwright headed mode
docker-compose run -e HEADLESS=false backend
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          INGRESS                                │
│                    (nginx-ingress-controller)                   │
└────────────────┬───────────────────────┬───────────────────────┘
                 │                       │
                 ▼                       ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│       FRONTEND          │   │        BACKEND          │
│      (Next.js)          │   │       (FastAPI)         │
│   Replicas: 2-10        │   │   Replicas: 3-20        │
└─────────────────────────┘   └───────────┬─────────────┘
                                          │
                 ┌────────────────────────┼────────────────────────┐
                 │                        │                        │
                 ▼                        ▼                        ▼
┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│         REDIS           │   │      PROMETHEUS         │   │       OPENCLAW          │
│   (Session + Cache)     │   │      (Metrics)          │   │    (Local LLM)          │
└─────────────────────────┘   └───────────┬─────────────┘   └─────────────────────────┘
                                          │
                                          ▼
                              ┌─────────────────────────┐
                              │        GRAFANA          │
                              │      (Dashboards)       │
                              └─────────────────────────┘
```

---

## Contributing

When making infrastructure changes:

1. Test locally with `docker-compose up`
2. Validate Kubernetes manifests: `kubectl apply --dry-run=client -f k8s/`
3. Lint Helm chart: `helm lint ./helm/agentos`
4. Update this documentation

---

**Questions?** Open an issue or check the [TESTING_GUIDE.md](./TESTING_GUIDE.md) for agent testing instructions.
