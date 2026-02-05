# AI-Powered Databricks CI/CD Pipeline

This pipeline integrates AI capabilities throughout the CI/CD process for Databricks Asset Bundles, providing automated code review, security scanning, test generation, and intelligent analysis.

## 🏗️ Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PIPELINE STAGES                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────────┐   │
│  │  AICodeReview    │───▶│ BuildDEVDataBricks│───▶│ PostBuildAIAnalysis │   │
│  │  (Pre-Build)     │    │  (Build + Deploy) │    │  (Post-Build)       │   │
│  └──────────────────┘    └──────────────────┘    └──────────────────────┘   │
│         │                        │                         │                 │
│         ▼                        ▼                         ▼                 │
│  • Security Scan          • Resource Optimization   • Build Log Analysis    │
│  • Best Practices         • AI Test Generation      • Error Detection       │
│  • AI Deep Analysis       • Smoke Test Execution    • Recommendations       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🤖 AI Agent Tasks

### Stage 1: AICodeReview (Pre-Build)

Runs before the build to catch issues early.

| Task | Template | Description |
|------|----------|-------------|
| **Security Scan** | `ai-code-review.yml` | Scans all notebooks for security vulnerabilities |
| **Best Practices** | `ai-code-review.yml` | Analyzes code quality and patterns |
| **AI Deep Analysis** | `ai-code-review.yml` | Comprehensive AI-powered code review |

#### Security Checks Performed:
- 🔒 Hardcoded credentials and secrets
- 💉 SQL injection vulnerabilities
- 🥒 Unsafe pickle deserialization
- 🐛 Exposed tracebacks and error details
- 📦 Runtime pip install commands
- 🖨️ Unsafe error printing

---

### Stage 2: BuildDEVDataBricks (Build Phase)

Executes during the main build process.

| Task | Template/Script | Description |
|------|-----------------|-------------|
| **AI Resource Optimization** | `ai-resource-optimization.yml` | Analyzes Databricks workspace for cost/performance improvements |
| **AI Test Generation** | `generate-ai-tests.yml` | Generates and executes pytest tests for notebooks |
| **AI Smoke Test** | `ai-smoke-test.ps1` | Creates, runs, and analyzes dynamic smoke tests |

#### Resource Optimization Analyzes:
- 💰 **Cost Optimization**: Idle resources, oversized clusters, spot instance opportunities
- ⚡ **Performance**: Cluster sizing, autoscaling configurations
- 🔧 **Configuration**: Autotermination settings, cluster policies
- 📊 **Recommendations**: Specific cluster configurations for ETL, dev, and ML workloads

#### Smoke Test Process:
1. AI generates smoke test notebook based on your codebase
2. Uploads to Databricks workspace (`/Shared/cicd_smoke_tests/`)
3. Executes on single-node cluster
4. AI analyzes results and assesses deployment risk
5. Cleans up temporary notebook

---

### Stage 3: PostBuildAIAnalysis (Post-Build)

Runs after build completion to analyze results.

| Task | Location | Description |
|------|----------|-------------|
| **AI Log Analysis** | `databricks-asset-bundle.yml` | Analyzes build logs for errors and optimization opportunities |

#### Log Analysis Provides:
- 🔴 Error identification and root cause analysis
- 🟡 Warning review and severity assessment
- ⚡ Performance issue detection
- 💡 Best practice recommendations
- 🛡️ Security concern identification

---

## ⚙️ Pipeline Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `deployment_type` | string | `app-datafabric` | Select deployment: `app-datafabric`, `app-claimsanalyzer`, `app-contractanalyzer` |
| `run_ai_code_review` | boolean | `true` | Enable AI code review and security scan stage |
| `fail_on_critical` | boolean | `false` | Fail pipeline on critical security issues |
| `generate_ai_tests` | boolean | `false` | Generate AI-powered unit tests (⚠️ Can take 20+ minutes) |
| `run_smoke_test` | boolean | `true` | Run AI-validated smoke test |
| `run_resource_optimization` | boolean | `true` | Run workspace optimization analysis |
| `notebooks_path` | string | `notebooks/code/datafabric` | Path to notebooks for AI analysis |
| `clean_bundle-root` | boolean | `false` | Clean bundle root before deploy |

---

## 🔗 AI Agent Configuration

All AI tasks use the Azure AI Agent endpoint:

```
Endpoint: https://rkibbe-chat-demo-resource.services.ai.azure.com/api/projects/rkibbe-chat-demo/applications/azure-devops-ai-agent/protocols/openai/responses
API Version: 2025-11-15-preview
Deployment: cicd-ai-agent
```

### Authentication
- Uses Azure Service Connection: `azure-devops-sp2`
- Tokens obtained via `az account get-access-token`

---

## 📁 File Structure

```
pipeline/
├── databricks-asset-bundle.yml      # Main pipeline definition
├── README.md                        # This file
├── scripts/
│   └── ai-smoke-test.ps1           # Smoke test PowerShell script
└── templates/
    ├── ai-code-review.yml          # Code review & security scan
    ├── ai-resource-optimization.yml # Workspace optimization
    ├── ai-smoke-test.yml           # Smoke test template
    ├── ai-log-analysis.yml         # Log analysis template
    ├── generate-ai-tests.yml       # Test generation template
    ├── security-scan.yml           # Security pattern scanning
    ├── install-dbx-cli.yml         # Databricks CLI setup
    ├── get-dbx-config.yml          # Get Databricks config
    ├── get-dbx-token.yml           # Get Databricks token
    ├── set-dbx-dir.yml             # Set working directory
    ├── validate-dbx-bundle.yml     # Validate bundle
    └── delete-dbx-folder.yml       # Cleanup template
```

---

## 🚀 Quick Start

### Run with Default Settings (AI Code Review + Smoke Test)
```yaml
# Pipeline runs with:
# - AI Code Review: ✅ Enabled
# - Smoke Test: ✅ Enabled
# - Resource Optimization: ✅ Enabled
# - AI Test Generation: ❌ Disabled (slow)
```

### Run with All AI Features
```yaml
parameters:
  - name: generate_ai_tests
    value: true  # Enable test generation
  - name: fail_on_critical
    value: true  # Fail on security issues
```

### Run Minimal (No AI)
```yaml
parameters:
  - name: run_ai_code_review
    value: false
  - name: run_smoke_test
    value: false
  - name: run_resource_optimization
    value: false
```

---

## 📊 Output Examples

### AI Code Review Output
```
========================================
       AI CODE REVIEW REPORT            
========================================

🔴 CRITICAL: Hardcoded password found in config.py line 45
🟡 WARNING: SQL query constructed with string concatenation
🟢 INFO: Consider using parameterized queries
💡 SUGGESTION: Add input validation for user parameters
```

### Resource Optimization Output
```
## 💰 COST OPTIMIZATION
- ⚠️ 3 clusters without autotermination - potential cost risk
- 💡 Consider using Instance Pools to reduce startup times

## ⚡ PERFORMANCE OPTIMIZATION  
- Recommend autoscale: min=1, max=4 for ETL workloads
- Use Standard_DS4_v2 for memory-intensive jobs

## 📊 RECOMMENDED CLUSTER CONFIGURATIONS
cluster_config_etl:
  node_type_id: Standard_DS4_v2
  autoscale: {min: 1, max: 4}
```

### Smoke Test Output
```
============================================
   AI-VALIDATED SMOKE TEST                  
============================================

📝 PHASE 1: Generating Smoke Test
📤 PHASE 2: Uploading to Databricks
🚀 PHASE 3: Executing (Run ID: 123456)
🤖 PHASE 4: AI Analysis

Overall Health: HEALTHY ✅
Deployment Risk: LOW
All tests passed successfully
```

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Smoke test timeout | Cluster startup takes 3-5 min; wait or use existing cluster |
| AI test generation slow | Disable with `generate_ai_tests: false` or limit with `maxNotebooks: 3` |
| Security scan false positives | Review and whitelist in `security-scan.yml` |
| Workspace upload fails | Check service principal permissions on Databricks workspace |

### Logs Location
- Build logs: Azure DevOps pipeline run details
- Smoke test results: Pipeline output + Databricks job run
- AI analysis: Embedded in pipeline step output

---

## 📝 Contributing

When adding new AI tasks:
1. Create template in `pipeline/templates/`
2. Use the standard endpoint variable: `$(azureOpenAIEndpoint)`
3. Add parameter to main pipeline if needed
4. Update this README

---

## 📄 License

Internal use only - 3Cloud Solutions
