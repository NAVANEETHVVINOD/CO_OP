# CI/CD Setup Guide

This document describes the CI/CD configuration for Co-Op OS v1.0.3, including required secrets, variables, and the Docker image tagging strategy.

## Overview

The Co-Op OS CI/CD pipeline uses GitHub Actions with three main workflows:

1. **CI Workflow** (`.github/workflows/ci.yml`) - Runs on every push and PR to test code
2. **Release Workflow** (`.github/workflows/release.yml`) - Builds and publishes releases when tags are pushed
3. **Dev Images Workflow** (`.github/workflows/build-dev-images.yml`) - Builds development images for feature branches

All workflows use **GitHub repository secrets and variables** for configuration. No hardcoded values are present in workflow files.

## Required GitHub Secrets

GitHub Secrets are encrypted values used for sensitive information. Set these in your repository settings under **Settings → Secrets and variables → Actions → Secrets**.

| Secret Name | Description | Example Value | Required For |
|-------------|-------------|---------------|--------------|
| `DB_PASS` | PostgreSQL password for 'coop' user | `cooppassword123` | CI tests |
| `SECRET_KEY` | JWT signing key (min 32 chars) | `super-secret-key-change-in-production-min-32-chars` | CI tests, Production |
| `MINIO_ROOT_PASSWORD` | MinIO root password | `minioadmin123` | CI tests, Production |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (optional) | `123456:ABC-DEF...` | Stage 2 features |
| `GROQ_API_KEY` | Groq API key (optional) | `gsk_...` | Stage 2 features |
| `GEMINI_API_KEY` | Google Gemini API key (optional) | `AIza...` | Stage 2 features |
| `GITHUB_TOKEN` | Automatically provided by GitHub | N/A | All workflows |

### Setting Secrets

```bash
# Using GitHub CLI
gh secret set DB_PASS --body "cooppassword123"
gh secret set SECRET_KEY --body "super-secret-key-change-in-production-min-32-chars"
gh secret set MINIO_ROOT_PASSWORD --body "minioadmin123"

# Or via GitHub UI:
# 1. Go to repository Settings
# 2. Click "Secrets and variables" → "Actions"
# 3. Click "New repository secret"
# 4. Enter name and value
# 5. Click "Add secret"
```

## Required GitHub Variables

GitHub Variables are plain-text configuration values. Set these in your repository settings under **Settings → Secrets and variables → Actions → Variables**.

| Variable Name | Description | Default Value | Required |
|---------------|-------------|---------------|----------|
| `OLLAMA_URL` | Ollama LLM service URL | `http://ollama:11434` | No |
| `API_BASE_URL` | Backend API URL | `http://co-op-api:8000` | No |
| `FRONTEND_URL` | Frontend URL | `http://co-op-web:3000` | No |
| `DOCKER_REGISTRY` | Docker registry URL | `ghcr.io` | No |
| `DOCKER_IMAGE_PREFIX` | Docker image name prefix | `navaneethvvinod/co-op` | No |

### Setting Variables

```bash
# Using GitHub CLI
gh variable set DOCKER_REGISTRY --body "ghcr.io"
gh variable set DOCKER_IMAGE_PREFIX --body "your-org/co-op"
gh variable set API_BASE_URL --body "http://co-op-api:8000"

# Or via GitHub UI:
# 1. Go to repository Settings
# 2. Click "Secrets and variables" → "Actions" → "Variables" tab
# 3. Click "New repository variable"
# 4. Enter name and value
# 5. Click "Add variable"
```

## Docker Image Tagging Strategy

Co-Op OS uses a **semantic versioning-based tagging strategy** for Docker images:

### Production Releases (Git Tags)

When you push a Git tag like `v1.0.3`, the release workflow builds and pushes:

```
ghcr.io/navaneethvvinod/co-op-api:v1.0.3
ghcr.io/navaneethvvinod/co-op-api:latest
ghcr.io/navaneethvvinod/co-op-web:v1.0.3
ghcr.io/navaneethvvinod/co-op-web:latest
```

**Production Deployment Rule:** Always use specific version tags (e.g., `v1.0.3`) in production `docker-compose.yml`. Never use `latest` tag in production.

### Development Builds (Feature Branches)

When you push to `develop` or `feature/*` branches, the dev images workflow builds and pushes:

```
ghcr.io/navaneethvvinod/co-op-api:dev-a1b2c3d
ghcr.io/navaneethvvinod/co-op-web:dev-a1b2c3d
```

The tag format is `dev-{short-sha}` where `short-sha` is the first 7 characters of the Git commit SHA.

### Release Candidates (Optional)

For release candidates, manually create tags with `rc-` prefix:

```bash
git tag -a rc-1.0.3 -m "Release candidate for v1.0.3"
git push origin rc-1.0.3
```

This produces:
```
ghcr.io/navaneethvvinod/co-op-api:rc-1.0.3
ghcr.io/navaneethvvinod/co-op-web:rc-1.0.3
```

### Tag Summary

| Tag Format | Use Case | Example | Workflow |
|------------|----------|---------|----------|
| `v{version}` | Production releases | `v1.0.3` | `release.yml` |
| `latest` | Latest production release | `latest` | `release.yml` |
| `dev-{sha}` | Development builds | `dev-a1b2c3d` | `build-dev-images.yml` |
| `rc-{version}` | Release candidates | `rc-1.0.3` | `release.yml` |

## Workflow Details

### CI Workflow (ci.yml)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
1. **python-ci** - Lint, type-check, and test Python backend
2. **node-ci** - Lint and build Next.js frontend
3. **docker-build** - Build Docker images and scan with Trivy

**Environment Variables Used:**
- `DATABASE_URL` - Constructed from `DB_PASS` secret
- `SECRET_KEY` - From secret
- `OLLAMA_URL`, `API_BASE_URL`, `FRONTEND_URL` - From variables
- `NEXT_PUBLIC_API_URL` - Set to `API_BASE_URL` for frontend build

### Release Workflow (release.yml)

**Triggers:**
- Push of Git tags matching `v*` pattern

**Jobs:**
1. **publish-cli** - Build and upload CLI package to PyPI
2. **build-desktop** - Build Tauri desktop app for macOS, Linux, Windows
3. **create-release** - Create GitHub release with artifacts
4. **build-and-push-images** - Build and push Docker images with version tags

**Image Tags Created:**
- `{registry}/{prefix}-api:v{version}`
- `{registry}/{prefix}-api:latest`
- `{registry}/{prefix}-web:v{version}`
- `{registry}/{prefix}-web:latest`

### Dev Images Workflow (build-dev-images.yml)

**Triggers:**
- Push to `develop` branch
- Push to `feature/*` branches
- Manual workflow dispatch

**Jobs:**
1. **build-and-push-dev** - Build and push Docker images with dev tags

**Image Tags Created:**
- `{registry}/{prefix}-api:dev-{sha}`
- `{registry}/{prefix}-web:dev-{sha}`

## Setup Checklist for New Repositories

Use this checklist when setting up CI/CD in a new repository or fork:

### 1. Configure Secrets

- [ ] Set `DB_PASS` secret
- [ ] Set `SECRET_KEY` secret (min 32 characters)
- [ ] Set `MINIO_ROOT_PASSWORD` secret
- [ ] Set `TELEGRAM_BOT_TOKEN` secret (if using Stage 2 features)
- [ ] Set `GROQ_API_KEY` secret (if using Groq)
- [ ] Set `GEMINI_API_KEY` secret (if using Gemini)

### 2. Configure Variables

- [ ] Set `DOCKER_REGISTRY` variable (default: `ghcr.io`)
- [ ] Set `DOCKER_IMAGE_PREFIX` variable (e.g., `your-org/co-op`)
- [ ] Set `API_BASE_URL` variable (default: `http://co-op-api:8000`)
- [ ] Set `FRONTEND_URL` variable (default: `http://co-op-web:3000`)
- [ ] Set `OLLAMA_URL` variable (default: `http://ollama:11434`)

### 3. Enable GitHub Container Registry

- [ ] Go to repository Settings → Actions → General
- [ ] Under "Workflow permissions", select "Read and write permissions"
- [ ] Check "Allow GitHub Actions to create and approve pull requests"
- [ ] Save changes

### 4. Test Workflows

- [ ] Push a commit to `develop` branch
- [ ] Verify CI workflow runs successfully
- [ ] Verify dev images workflow builds and pushes images
- [ ] Check GitHub Container Registry for dev images

### 5. Create First Release

- [ ] Ensure all tests pass on `main` branch
- [ ] Create and push a version tag: `git tag -a v1.0.3 -m "Release v1.0.3" && git push origin v1.0.3`
- [ ] Verify release workflow runs successfully
- [ ] Check GitHub Releases page for new release
- [ ] Check GitHub Container Registry for version-tagged images

## Troubleshooting

### Workflow Fails with "Missing required environment variable"

**Problem:** Workflow fails with error about missing environment variable.

**Solution:** Check that all required secrets and variables are set in repository settings. Use the checklist above.

### Docker Image Push Fails with "Permission denied"

**Problem:** Workflow fails when pushing Docker images to registry.

**Solution:** 
1. Verify "Read and write permissions" are enabled in Settings → Actions → General
2. Verify `GITHUB_TOKEN` has `packages: write` permission (automatically granted)
3. For custom registries, verify authentication credentials are correct

### Frontend Build Fails with "NEXT_PUBLIC_API_URL is required"

**Problem:** Frontend build fails because `NEXT_PUBLIC_API_URL` is not set.

**Solution:** The workflow sets `NEXT_PUBLIC_API_URL` from `API_BASE_URL` variable. Verify `API_BASE_URL` variable is set in repository settings.

### Images Not Appearing in GitHub Container Registry

**Problem:** Workflow succeeds but images don't appear in GitHub Container Registry.

**Solution:**
1. Go to repository Settings → Actions → General
2. Verify "Read and write permissions" is selected
3. Check workflow logs for authentication errors
4. Verify package visibility settings (Settings → Packages)

### Release Workflow Doesn't Trigger

**Problem:** Pushing a tag doesn't trigger the release workflow.

**Solution:**
1. Verify tag matches pattern `v*` (e.g., `v1.0.3`, not `1.0.3`)
2. Verify tag was pushed to remote: `git push origin v1.0.3`
3. Check Actions tab for workflow run
4. Verify workflow file is on `main` branch (workflows only run from default branch for tag events)

## Security Best Practices

1. **Never commit secrets** - Always use GitHub Secrets for sensitive values
2. **Rotate secrets regularly** - Update `SECRET_KEY`, `DB_PASS`, and API keys periodically
3. **Use specific version tags in production** - Never use `latest` tag in production deployments
4. **Review workflow changes** - Always review changes to workflow files in PRs
5. **Limit secret access** - Use environment-specific secrets when possible
6. **Monitor workflow runs** - Regularly check Actions tab for failed or suspicious runs
7. **Pin action versions** - Use commit SHAs for third-party actions (already done in workflows)

## Production Deployment

When deploying to production, update your `docker-compose.yml` to use specific version tags:

```yaml
services:
  co-op-api:
    image: ghcr.io/navaneethvvinod/co-op-api:v1.0.3  # Use specific version
    # ... rest of config

  co-op-web:
    image: ghcr.io/navaneethvvinod/co-op-web:v1.0.3  # Use specific version
    # ... rest of config
```

**Never use:**
```yaml
image: ghcr.io/navaneethvvinod/co-op-api:latest  # ❌ Don't use in production
image: ghcr.io/navaneethvvinod/co-op-api:dev-a1b2c3d  # ❌ Don't use in production
```

## Rollback Procedure

If a release has issues, rollback to the previous version:

1. Update `docker-compose.yml` to use previous version tag:
   ```yaml
   image: ghcr.io/navaneethvvinod/co-op-api:v1.0.2  # Previous version
   ```

2. Restart services:
   ```bash
   docker compose down
   docker compose pull
   docker compose up -d
   ```

3. Verify services are healthy:
   ```bash
   docker compose ps
   curl http://localhost:8000/health | jq
   ```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Co-Op OS Deployment Guide](./DEPLOYMENT.md)
- [Co-Op OS Project Structure](./PROJECT_STRUCTURE.md)
