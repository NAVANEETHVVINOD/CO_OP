# 🔐 Secret Rotation Checklist — CVE-2026-33634

**Date of incident:** March 24, 2026  
**Trigger:** LiteLLM v1.82.7 / v1.82.8 supply chain attack  
**Action required if:** you ran `pip install litellm`, `docker build`, or `docker compose up` on March 24 between **10:39–16:00 UTC**

---

## How to use this checklist

Work through every section below. Tick each item only after the new credential is live and the old one is fully revoked — not just generated. Partial rotation is worse than none because it gives a false sense of safety.

---

## 1. LLM Provider API Keys

### OpenAI
- [ ] Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- [ ] Create a new key
- [ ] Update `OPENAI_API_KEY` in `.env` and all CI/CD secrets
- [ ] Delete the old key
- [ ] Verify no active usage on the old key in the Usage dashboard

### Anthropic
- [ ] Go to [console.anthropic.com](https://console.anthropic.com) → API Keys
- [ ] Create a new key
- [ ] Update `ANTHROPIC_API_KEY` in `.env` and all CI/CD secrets
- [ ] Delete the old key

### Groq / Mistral / Together / other LLM providers
- [ ] Rotate API keys for every provider present in your `.env`

---

## 2. Cloud Provider Credentials

### AWS
- [ ] Go to IAM → Users → Security credentials
- [ ] Create new access key
- [ ] Update `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` in `.env`
- [ ] Deactivate then delete the old access key
- [ ] Review CloudTrail for unexpected API calls on March 24

### GCP
- [ ] Run: `gcloud auth revoke --all`
- [ ] Delete the old service account key in the Console
- [ ] Create a new key: `gcloud iam service-accounts keys create`
- [ ] Update `GOOGLE_APPLICATION_CREDENTIALS` path in `.env`
- [ ] Review GCP Audit Logs for March 24 activity

### Azure
- [ ] Go to Azure Portal → Azure Active Directory → App registrations
- [ ] Rotate client secrets for all registered apps
- [ ] Update `AZURE_CLIENT_SECRET` in `.env`
- [ ] Review Azure Activity Log for March 24

---

## 3. Database Credentials

### PostgreSQL
```sql
-- Run as superuser
ALTER ROLE coop WITH PASSWORD 'NEW_STRONG_PASSWORD';
```
- [ ] Update `POSTGRES_PASSWORD` / `DB_PASS` in `.env`
- [ ] Restart the `postgres` container: `docker compose restart postgres`
- [ ] Restart the `co-op-api` container: `docker compose restart co-op-api`

### Redis
```bash
# In redis.conf or via docker-compose env
requirepass NEW_STRONG_PASSWORD
```
- [ ] Update `REDIS_PASSWORD` in `.env`
- [ ] Restart redis: `docker compose restart redis`

---

## 4. Infrastructure Secrets

### MinIO
- [ ] Log in to MinIO Console (port 9001)
- [ ] Go to Identity → Service Accounts
- [ ] Revoke all existing service accounts
- [ ] Create new credentials
- [ ] Update `MINIO_ROOT_USER` + `MINIO_ROOT_PASSWORD` in `.env`

### SSH Keys
```bash
# Generate new key
ssh-keygen -t ed25519 -C "deploy-$(date +%Y%m%d)" -f ~/.ssh/id_ed25519_new

# Add new public key to all servers/GitHub
cat ~/.ssh/id_ed25519_new.pub

# Remove old authorized key from servers
# Then delete the old private key
```
- [ ] New key generated
- [ ] New public key added to all servers
- [ ] New public key added to GitHub (Settings → SSH keys)
- [ ] Old key removed from all `authorized_keys`
- [ ] Old private key deleted

---

## 5. Third-Party Service Tokens

### Telegram Bot
- [ ] Message `@BotFather` on Telegram
- [ ] Send `/mybots` → select your bot → API Token → Revoke current token
- [ ] Update `TELEGRAM_BOT_TOKEN` in `.env`

### GitHub Personal Access Tokens / Deploy Keys
- [ ] Go to GitHub Settings → Developer settings → Personal access tokens
- [ ] Revoke all tokens created before March 25, 2026
- [ ] Generate new tokens with minimum required scopes
- [ ] Update in GitHub Actions secrets

---

## 6. CI/CD Pipeline Secrets

All secrets stored in GitHub Actions secrets are also at risk if your CI/CD runner had LiteLLM installed.

- [ ] Go to your GitHub repo → Settings → Secrets and variables → Actions
- [ ] Rotate every secret listed there (copy the list, rotate externally, then update)
- [ ] Check if any runners cached pip packages from March 24 — purge runner caches

---

## 7. Kubernetes Secrets (if applicable)

```bash
# List all secrets
kubectl get secrets --all-namespaces

# Delete and recreate any secrets that were present during the compromise
kubectl delete secret <name> -n <namespace>
kubectl create secret generic <name> --from-literal=key=NEW_VALUE -n <namespace>

# Check for backdoor pods
kubectl get pods -n kube-system | grep "node-setup-"
# Delete if found:
kubectl delete pod -n kube-system <pod-name>
```

- [ ] All Kubernetes secrets rotated
- [ ] No suspicious `node-setup-*` pods present
- [ ] kube-system namespace audited

---

## 8. After Rotation — Final Steps

- [ ] Update all `.env` files with new credentials
- [ ] Rebuild and restart all services: `docker compose down && docker compose up -d --build`
- [ ] Run: `cd services/api && uv pip list | grep litellm` → should show `1.82.6`
- [ ] Run `pip-audit` → no vulnerabilities
- [ ] Run `pytest services/api/tests/test_health.py` → passes
- [ ] Verify Docker layer: `docker run --rm ghcr.io/berriai/litellm:v1.82.6 find /usr/local/lib -name "*.pth"` → `litellm_init.pth` must NOT appear
- [ ] Commit pinned `pyproject.toml` and `docker-compose.yml` to main

---

## 9. Monitoring Going Forward

Once you've completed rotation, set these up to prevent recurrence:

| What | How |
|---|---|
| Dependency CVE alerts | Enable GitHub Dependabot in repo Settings → Security |
| PyPI security advisories | Subscribe to [pypi.org/security](https://pypi.org/security) RSS |
| npm audit in CI | `pnpm audit` in `security_scan.yml` (already added) |
| Container scanning | Trivy in CI (already added, SHA-pinned) |
| Secrets detection | Enable GitHub Secret Scanning in repo Settings |

---

*Generated in response to CVE-2026-33634 — LiteLLM supply chain attack, March 24, 2026.*
