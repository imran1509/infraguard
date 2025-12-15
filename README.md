# 🛡️ InfraGuard

> AI-Powered Autonomous Infrastructure Incident Response System
>
> 
[![CodeRabbit](https://img.shields.io/badge/CodeRabbit-Enabled-purple)](https://coderabbit.ai)

## 🎯 Overview

InfraGuard is an intelligent incident response platform that automatically detects, diagnoses, and fixes infrastructure issues using AI agents. Built for the **AI Agents Assemble** hackathon.

### The Problem

Infrastructure incidents cost companies millions in downtime. Traditional monitoring alerts humans who must:
1. Wake up at 3 AM
2. Manually diagnose the issue
3. Research solutions
4. Apply fixes
5. Verify resolution

**Average MTTR: 30-60 minutes per incident**

### Our Solution

InfraGuard reduces this to **seconds** by:
1. 🔍 **Detecting** anomalies in real-time with Prometheus
2. 🧠 **Analyzing** root causes with Kestra AI Agent
3. 🔧 **Generating** fixes automatically with Cline CLI
4. ✅ **Reviewing** code quality with CodeRabbit
5. 📊 **Visualizing** everything on a Vercel dashboard

## 🏆 Sponsor Technologies

| Technology | Usage | Prize Track |
|------------|-------|-------------|
| **Cline CLI** | Autonomous code generation for fixes | Infinity Build ($5K) |
| **Kestra** | AI Agent for data summarization & decisions | Wakanda Data ($4K) |
| **Oumi** | RL fine-tuned action selection model | Iron Intelligence ($3K) |
| **Vercel** | Production dashboard deployment | Stormbreaker ($2K) |
| **CodeRabbit** | AI code review on all PRs | Captain Code ($1K) |

## 🎬 Demo Video

[![Demo Video](docs/screenshots/demo-thumbnail.png)](https://youtube.com/watch?v=YOUR_VIDEO_ID)

**[Watch 2-minute demo →](https://youtube.com/watch?v=YOUR_VIDEO_ID)**

## 🖥️ Live Dashboard

**[infraguard.vercel.app](https://infraguard.vercel.app)**

![Dashboard Screenshot](docs/screenshots/dashboard.png)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GITHUB + CODERABBIT                     │
│            Reviews ALL PRs (human + AI-generated)           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┴─────────────────────────────┐
│                     LOCAL ENVIRONMENT                      │
│                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Minikube │→ │Prometheus│→ │  Kestra  │→ │  Cline   │    │
│  │ Cluster  │  │ +Grafana │  │ AI Agent │  │   CLI    │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                                                            │
└────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ AWS Bedrock │      │Google Colab │      │   Vercel    │
│ (LLM API)   │      │(Oumi Train) │      │ (Dashboard) │
└─────────────┘      └─────────────┘      └─────────────┘
```

## ✨ Key Features

### 🔍 Real-Time Detection
- Monitors Kubernetes pods, CPU, memory, restarts
- Custom Prometheus alerts for common issues
- Sub-minute incident detection

### 🧠 AI-Powered Analysis
- Kestra AI Agent summarizes system state
- Correlates metrics from multiple sources
- Identifies root causes automatically

### 🔧 Autonomous Fixes
- Cline generates targeted code patches
- Creates K8s manifest updates
- Opens PRs with proper documentation

### 🐰 Quality Assurance
- CodeRabbit reviews all generated code
- Catches bugs before they reach production
- Ensures best practices

### 📊 Beautiful Dashboard
- Real-time incident feed
- System health at a glance
- Action log with PR links

## 🚀 Quick Start

### Prerequisites

- Docker
- Minikube
- Node.js 18+
- Python 3.10+

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/infraguard
cd infraguard

# Start Minikube
minikube start --cpus=4 --memory=8192

# Deploy sample apps
kubectl apply -f k8s/manifests/sample-apps.yaml

# Install monitoring stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f k8s/manifests/prometheus-values.yaml

# Start Kestra
docker run -d --name kestra -p 8080:8080 kestra/kestra:latest server local

# Start Metrics API
python scripts/metrics-api.py

# Open dashboard
npm run dev --prefix dashboard
```

### Inject Test Incident

```bash
# Inject a crash loop
./scripts/inject-incident.sh crash-loop

# Watch the magic happen in the dashboard!

# Cleanup
./scripts/inject-incident.sh cleanup
```

## 🐰 CodeRabbit Integration

CodeRabbit reviews every PR in this repository:

![CodeRabbit Review](docs/screenshots/coderabbit-review.png)

### CodeRabbit Highlights
- ✅ Reviewed 20+ PRs during development
- ✅ Caught 5 potential bugs
- ✅ Improved documentation quality
- ✅ Reviews AI-generated fixes from Cline

## 🤖 Oumi Training

We fine-tuned an action selection model using Oumi's GRPO:

- **Base Model**: SmolLM2-360M-Instruct
- **Training Data**: 500 synthetic incident scenarios
- **Reward Function**: +10 (resolved), -10 (failed)
- **Training Time**: ~30 minutes on T4 GPU

See [oumi/training/](oumi/training/) for details.

## 📁 Project Structure

```
infraguard/
├── k8s/
│   └── manifests/          # Kubernetes configurations
├── kestra/
│   └── workflows/          # Kestra flow definitions
├── dashboard/              # Next.js Vercel app
├── oumi/
│   └── training/           # Oumi training scripts
├── scripts/
│   ├── metrics-api.py      # Prometheus API wrapper
│   ├── inject-incident.sh  # Demo incident injection
│   └── cline-incident-fix.py
├── cline-tasks/            # Auto-generated Cline tasks
├── .coderabbit.yaml        # CodeRabbit configuration
└── README.md
```

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

Built with ❤️ for [AI Agents Assemble](https://www.wemakedevs.org/hackathons/assemblehack25)
```
