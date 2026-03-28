# Security

Co-Op follows industry best practices to protect data and ensure safe operation.

## Table of Contents

- [Authentication & Authorization](#authentication--authorization)
- [Data Encryption](#data-encryption)
- [API Security](#api-security)
- [Supply Chain Security](#supply-chain-security)
- [Vulnerability Reporting](#vulnerability-reporting)
- [Security Best Practices](#security-best-practices)
- [Secure Development](#secure-development)

## Authentication & Authorization

### JWT (JSON Web Tokens)

Co-Op uses JWT for stateless authentication:

- **Access tokens**: Short-lived (15 minutes), used for API requests
- **Refresh tokens**: Long-lived (7 days), used to obtain new access tokens
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Secret**: Configured via `SECRET_KEY` environment variable

**Token Structure**:
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "user",
  "exp": 1234567890
}
```

**Security Considerations**:
- Tokens are signed, not encrypted (don't store sensitive data in tokens)
- Rotate `SECRET_KEY` regularly (invalidates all tokens)
- Store tokens securely on client (httpOnly cookies recommended for web)

### Password Security

**Hashing Algorithm**: bcrypt with cost factor 12

**Pre-hashing**: SHA256 applied before bcrypt to handle passwords longer than 72 bytes

**Implementation**:
```python
import hashlib
import bcrypt

def hash_password(password: str) -> str:
    # Pre-hash with SHA256
    prehash = hashlib.sha256(password.encode()).hexdigest()
    # Hash with bcrypt
    return bcrypt.hashpw(prehash.encode(), bcrypt.gensalt(rounds=12)).decode()
```

**Password Requirements** (recommended):
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Role-Based Access Control (RBAC)

Two roles are currently supported:

| Role | Permissions |
|------|-------------|
| `admin` | Full access to all endpoints, user management, system settings |
| `user` | Standard access, cannot manage other users or system settings |

**Protected Routes**:
- All `/v1/*` endpoints require authentication
- Admin-only endpoints: `/v1/admin/*`, `/v1/users/*`

### Session Management

- **Stateless**: No server-side session storage (JWT-based)
- **Token refresh**: Use refresh token to obtain new access token
- **Logout**: Client discards tokens (server-side revocation in Stage 2)

## Data Encryption

### At Rest

**Database (PostgreSQL)**:
- Disk encryption recommended (LUKS, dm-crypt, or cloud provider encryption)
- Sensitive fields can be encrypted at application level (future)

**Object Storage (MinIO)**:
- Server-side encryption (SSE-S3) supported
- Enable with `MINIO_SERVER_SIDE_ENCRYPTION=on`

**Secrets**:
- Stored in environment variables (development)
- HashiCorp Vault recommended for production (Stage 4)
- Never commit secrets to version control

### In Transit

**HTTPS/TLS**:
- All HTTP endpoints should be served over HTTPS in production
- Use reverse proxy (nginx, Traefik) for TLS termination
- Minimum TLS 1.2, TLS 1.3 recommended

**Internal Communication**:
- Docker network provides isolation
- Mutual TLS (mTLS) optional for service-to-service communication (Stage 4)

**Example nginx configuration**:
```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## API Security

### Rate Limiting

**Current**: Basic rate limiting at application level

**Recommended for production**:
- Use reverse proxy (nginx, Traefik) for rate limiting
- Limit by IP address or user ID
- Example: 100 requests per minute per IP

**nginx example**:
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;

location /v1/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://localhost:8000;
}
```

### Input Validation

**Pydantic V2**: All API inputs validated with Pydantic schemas

**SQL Injection**: Prevented by SQLAlchemy ORM (parameterized queries)

**XSS**: Frontend sanitizes user input, API returns JSON (not HTML)

**CSRF**: Not applicable (stateless API, no cookies for auth by default)

### CORS (Cross-Origin Resource Sharing)

**Configuration** in `services/api/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production**: Restrict `allow_origins` to your frontend domain only

### API Keys (Future)

For machine-to-machine authentication:
- API keys with scoped permissions
- Key rotation and revocation
- Usage tracking and rate limiting per key

## Supply Chain Security

### Dependency Scanning

**Python**:
```bash
# Scan for vulnerabilities
pip-audit

# Or with uv
uv pip audit
```

**Node.js**:
```bash
# Scan for vulnerabilities
pnpm audit

# Fix vulnerabilities
pnpm audit --fix
```

### Container Scanning

**Trivy** (recommended):
```bash
# Scan Docker image
trivy image co-op-api:latest

# Scan filesystem
trivy fs .
```

### Regular Updates

- **Base images**: Update regularly (monthly recommended)
- **Dependencies**: Update and test quarterly
- **Security patches**: Apply immediately

### Dependency Pinning

- **Python**: Use exact versions in `pyproject.toml`
- **Node.js**: Use lockfiles (`pnpm-lock.yaml`)
- **Docker**: Pin base image versions

## Vulnerability Reporting

### Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **Do NOT open a public issue**
2. **Email**: security@co-op.local (replace with actual contact)
3. **Or use GitHub's private vulnerability reporting**:
   - Go to repository → Security → Report a vulnerability

### What to Include

- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact and severity
- **Steps to reproduce**: Detailed steps to trigger the vulnerability
- **Proof of concept**: Code or screenshots (if applicable)
- **Suggested fix**: If you have one

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 7 days
- **Fix timeline**: Depends on severity (critical: 7 days, high: 30 days, medium: 90 days)
- **Disclosure**: Coordinated disclosure after fix is released

### Bug Bounty

Currently no bug bounty program. May be added in the future.

## Security Best Practices

### For Deployments

1. **Never commit secrets** to version control
   - Use `.env` files (add to `.gitignore`)
   - Use environment variables
   - Use secrets management (Vault, AWS Secrets Manager, etc.)

2. **Rotate secrets regularly**
   - JWT secret: Every 90 days
   - Database passwords: Every 90 days
   - MinIO credentials: Every 90 days
   - API keys: Every 30 days

3. **Use environment-specific configurations**
   - Development: Relaxed security, debug enabled
   - Production: Strict security, debug disabled

4. **Limit exposure**
   - Only expose necessary ports (80/443 for web, 8000 for API if not proxied)
   - Use firewall rules to restrict access
   - Disable unused services

5. **Enable audit logging**
   - Log all authentication attempts
   - Log all admin actions
   - Log all data access (GDPR compliance)
   - Retain logs for 90 days minimum

6. **Regular backups**
   - Database: Daily backups, 30-day retention
   - Object storage: Versioning enabled
   - Test restore procedures quarterly

7. **Monitoring and alerting**
   - Monitor for failed login attempts
   - Alert on unusual activity
   - Monitor resource usage

8. **Principle of least privilege**
   - Database users: Grant only necessary permissions
   - Container users: Run as non-root
   - File permissions: Restrict to minimum required

### For Development

1. **Code review**: All changes reviewed before merge
2. **Pre-commit hooks**: Run linting and secret scanning
3. **CI/CD security**: Enforce test coverage and security scans
4. **Dependency updates**: Review changelogs before updating
5. **Secure coding practices**: Follow OWASP guidelines

## Secure Development

### Pre-commit Hooks

Install pre-commit hooks to catch issues early:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**Hooks include**:
- Secret scanning (detect-secrets)
- Linting (ruff, eslint)
- Formatting (ruff format, prettier)
- Type checking (pyright, tsc)

### CI/CD Security

**GitHub Actions** (`.github/workflows/ci.yml`):
- Dependency scanning
- Container scanning
- Secret scanning
- Test coverage enforcement
- Linting and formatting checks

### Security Checklist

Before deploying to production:

- [ ] All secrets in environment variables (not hardcoded)
- [ ] HTTPS enabled with valid certificate
- [ ] Rate limiting configured
- [ ] CORS restricted to frontend domain
- [ ] Database backups configured
- [ ] Monitoring and alerting enabled
- [ ] Firewall rules configured
- [ ] Audit logging enabled
- [ ] Dependencies scanned for vulnerabilities
- [ ] Containers scanned for vulnerabilities
- [ ] Security headers configured (CSP, HSTS, etc.)
- [ ] Error messages don't leak sensitive information
- [ ] Debug mode disabled

## Related Documentation

- [Deployment Guide](./DEPLOYMENT.md)
- [Database Schema](./DATABASE.md)
- [Troubleshooting](./TROUBLESHOOTING.md)
- [Contributing](../CONTRIBUTING.md)
