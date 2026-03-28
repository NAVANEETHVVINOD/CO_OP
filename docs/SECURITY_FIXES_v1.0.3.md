# Security Fixes - v1.0.3

## Overview

This document tracks security vulnerabilities fixed in v1.0.3 release.

## Fixed Vulnerabilities

### 1. setuptools: Path Traversal Vulnerability (CVE-2025-47273)

- **Severity**: HIGH
- **Package**: setuptools
- **Vulnerable Version**: 70.2.0
- **Fixed Version**: 78.1.1
- **CVE**: CVE-2025-47273
- **Description**: Path traversal vulnerability in setuptools PackageIndex
- **Fix**: Upgraded setuptools to >=78.1.1 in all Docker images

### 2. pip: Missing Checks on Symbolic Link Extraction (CVE-2025-8869)

- **Severity**: MEDIUM
- **Package**: pip
- **Vulnerable Version**: 25.0.1
- **Fixed Version**: 25.3
- **CVE**: CVE-2025-8869
- **Description**: pip missing checks on symbolic link extraction
- **Fix**: Upgraded pip to >=26.0 in all Docker images

### 3. pip: Information Disclosure via Path Traversal (CVE-2026-1703)

- **Severity**: LOW
- **Package**: pip
- **Vulnerable Version**: 25.0.1
- **Fixed Version**: 26.0
- **CVE**: CVE-2026-1703
- **Description**: Information disclosure via path traversal when installing crafted wheel archives
- **Fix**: Upgraded pip to >=26.0 in all Docker images

## Implementation

### Changes Made

1. **services/api/Dockerfile**:
   - Added `RUN pip install --no-cache-dir --upgrade 'pip>=26.0' 'setuptools>=78.1.1'` in builder stage
   - Added same upgrade command in runtime stage

### Verification

To verify the fixes:

```bash
# Rebuild images
docker compose -f infrastructure/docker/docker-compose.yml build

# Scan with Trivy
trivy image --severity HIGH,CRITICAL co-op-api:latest

# Expected: No HIGH or CRITICAL vulnerabilities for pip/setuptools
```

### Impact

- **Build time**: Minimal increase (~5-10 seconds per build)
- **Runtime**: No impact - these packages are only used during build
- **Compatibility**: No breaking changes - upgrades are backward compatible

## Related Documentation

- [Security Practices](./SECURITY.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Troubleshooting](./TROUBLESHOOTING.md)
