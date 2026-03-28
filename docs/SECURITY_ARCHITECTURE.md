# Security Architecture

## Overview

This document outlines the comprehensive security measures implemented in the Co-Op platform to protect against supply chain attacks, malicious code injection, and other security threats.

## Threat Model

### Supply Chain Attack Vectors

Based on recent attacks (2026), we protect against:

1. **Compromised Package Maintainers** (LiteLLM Attack - March 2026)
   - Stolen PyPI/npm credentials
   - Malicious package versions published directly to registries
   - Multi-stage payloads with credential harvesting

2. **Registry-Native Worms** (Shai-Hulud Campaign)
   - Self-replicating malware across package ecosystems
   - Automated dependency poisoning

3. **Crypto Wallet Hijacking** (npm Attack - 2026)
   - Monkey-patching fetch/XMLHttpRequest
   - Silent address replacement in transactions

4. **Typosquatting**
   - Packages with names similar to popular libraries
   - Automated installation via typos

5. **Dependency Confusion**
   - Internal package names published to public registries
   - Automatic installation of malicious public packages

## Defense Layers

### Layer 1: Pre-Commit Protection

**Git Hooks**
- Pre-commit hooks scan for secrets
- Prevent accidental credential commits
- Block suspicious code patterns

**Developer Workstation**
- Local security scanning before push
- IDE integration for real-time warnings

### Layer 2: CI/CD Pipeline Security

**Workflow Isolation**
```yaml
permissions:
  contents: read          # Minimal permissions
  security-events: write  # Only for security reporting
```

**SHA-Pinned Actions**
All third-party GitHub Actions are pinned to immutable commit SHAs, not version tags:
```yaml
# ❌ VULNERABLE (tags can be force-pushed)
uses: actions/checkout@v4

# ✅ SECURE (SHA cannot be changed)
uses: actions/checkout@692973e3d937129bcbf40652eb9f2f61becf3332  # v4.1.7
```

### Layer 3: Dependency Verification

**Lockfile Integrity**
- Automated verification of pnpm-lock.yaml and requirements.txt
- Detection of suspicious install scripts
- Hash verification for all dependencies

**Package Provenance**
- Verify package signatures
- Check for unsigned or tampered packages
- Block known compromised versions

**Version Pinning**
```toml
# Critical security: LiteLLM pinned to safe version
"litellm==1.82.6"  # Versions 1.82.7 and 1.82.8 were compromised
```

### Layer 4: Malicious Code Detection

**.pth File Scanning**
Python .pth files can execute arbitrary code during import. We scan for:
- Suspicious system calls (subprocess, exec, eval)
- Network operations (socket, urllib, requests)
- Credential access patterns

**Allowlist**:
- `distutils-precedence.pth` (standard setuptools file)
- `__editable__*.pth` (local development packages)

**Obfuscation Detection**
- Base64-encoded payloads
- Eval/exec usage outside tests
- Suspicious __import__ patterns

**Credential Harvesting Detection**
Patterns from LiteLLM attack:
- AWS credential access
- SSH key reading
- Kubernetes config access
- CI/CD token exfiltration

**Crypto Wallet Hijacking Detection**
Patterns from npm attack:
- fetch/XMLHttpRequest monkey-patching
- Cryptocurrency address patterns
- Silent network request modification

### Layer 5: Runtime Monitoring

**Installation Monitoring**
- Log all network activity during pip/pnpm install
- Detect connections to suspicious domains (.onion, pastebin, discord)
- Monitor file system writes to sensitive directories

**Behavioral Analysis**
- Track package installation behavior
- Alert on unexpected network calls
- Monitor for lateral movement attempts

### Layer 6: Vulnerability Scanning

**pip-audit** (Python)
- Scans against OSV and PyPI Advisory databases
- Runs on every PR and daily schedule
- Blocks PRs with critical vulnerabilities

**pnpm audit** (Node.js)
- Scans npm dependencies
- Enforces moderate+ severity threshold
- Automated overrides for false positives

**Trivy** (Containers)
- Scans Docker images for CVEs
- Checks OS packages and application dependencies
- SARIF output uploaded to GitHub Security

**Gitleaks** (Secrets)
- Scans entire git history for leaked secrets
- Detects API keys, tokens, passwords
- Runs on every commit

### Layer 7: SBOM & Compliance

**Software Bill of Materials (SBOM)**
- Generated in CycloneDX format
- Stored for 90 days
- Used for vulnerability tracking

**License Compliance**
- Automated GPL/AGPL detection
- Prevents incompatible license usage
- Generates license reports

## Security Workflows

### 1. Main CI Workflow (`.github/workflows/ci.yml`)
- Python lint & test
- Node.js lint & build
- Docker build & Trivy scan

### 2. Security Scan Workflow (`.github/workflows/security_scan.yml`)
- pip-audit (Python CVE scan)
- pnpm audit (Node CVE scan)
- Trivy container scan
- Malicious .pth file check
- LiteLLM version gate

### 3. Advanced Security Workflow (`.github/workflows/advanced-security.yml`)
- Lockfile integrity verification
- Typosquatting detection
- Source code integrity scan
- Backdoor detection
- Credential harvesting detection
- Crypto wallet hijacking detection
- Package provenance verification
- Runtime behavior monitoring
- SBOM generation
- Secret scanning (gitleaks)
- Dependency confusion check
- License compliance

### 4. Build Dev Images Workflow (`.github/workflows/build-dev-images.yml`)
- Builds development Docker images
- Pushes to GitHub Container Registry
- Includes submodule checkout

### 5. Release Workflow (`.github/workflows/release.yml`)
- Automated releases on tags
- Builds production artifacts
- Generates release notes

## Known Compromised Packages

### Python (PyPI)

**LiteLLM** (March 24, 2026)
- **Compromised versions**: 1.82.7, 1.82.8
- **Attack vector**: Stolen maintainer credentials
- **Payload**: Multi-stage credential harvesting, Kubernetes lateral movement, persistent backdoor
- **Mitigation**: Pinned to 1.82.6, version gate in CI
- **References**: [CVE-2026-33634](https://github.com/advisories/GHSA-xxxx-xxxx-xxxx)

### Node.js (npm)

**Shai-Hulud Campaign** (2026)
- **Affected**: ~1,000 npm packages
- **Attack vector**: Registry-native worm
- **Payload**: Self-replicating malware, credential theft
- **Mitigation**: Lockfile verification, typosquatting detection

**Crypto Wallet Hijacking** (2026)
- **Affected**: chalk, debug, and 16 other popular packages
- **Attack vector**: Compromised maintainer accounts (phishing)
- **Payload**: Monkey-patched fetch/XMLHttpRequest to hijack crypto transactions
- **Mitigation**: Code integrity scanning, behavioral monitoring

## Incident Response

### Detection
1. CI workflow fails with security alert
2. Automated notification to security team
3. PR blocked from merging

### Analysis
1. Review security workflow logs
2. Identify compromised package/code
3. Assess blast radius

### Containment
1. Block affected package versions
2. Rollback to last known good version
3. Update lockfiles

### Remediation
1. Update to patched version
2. Scan for indicators of compromise
3. Rotate credentials if exposed

### Recovery
1. Verify clean state
2. Update security rules
3. Document lessons learned

## Best Practices for Contributors

### Before Committing
- Run `ruff check .` (Python)
- Run `pnpm lint` (Node.js)
- Scan for secrets locally
- Review dependency changes

### Adding Dependencies
- Research package reputation
- Check for recent security issues
- Verify package maintainer
- Use exact version pinning
- Document why dependency is needed

### Reviewing PRs
- Check for new dependencies
- Review lockfile changes
- Look for suspicious code patterns
- Verify CI checks pass
- Request security review for sensitive changes

### Reporting Security Issues
- **DO NOT** open public issues for security vulnerabilities
- Email: security@co-op.example.com
- Use GitHub Security Advisories
- Provide detailed reproduction steps

## Security Contacts

- **Security Team**: security@co-op.example.com
- **Incident Response**: incident@co-op.example.com
- **Bug Bounty**: bounty@co-op.example.com

## References

### Supply Chain Attacks (2026)
- [LiteLLM PyPI Compromise](https://www.trendmicro.com/en_us/research/26/c/inside-litellm-supply-chain-compromise.html)
- [Shai-Hulud npm Worm](https://www.reversinglabs.com/blog/sscs-report-2026-takeaways)
- [npm Crypto Wallet Hijacking](https://www.bleepingcomputer.com/news/security/hackers-hijack-npm-packages-with-2-billion-weekly-downloads-in-supply-chain-attack/)

### Security Standards
- [SLSA Framework](https://slsa.dev/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)

### Tools
- [pip-audit](https://github.com/pypa/pip-audit)
- [Trivy](https://github.com/aquasecurity/trivy)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [CycloneDX](https://cyclonedx.org/)
