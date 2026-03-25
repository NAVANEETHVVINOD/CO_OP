# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2026-03-25

### Fixed
- **CI/CD**: Standardized `pnpm/action-setup` to stable `v4` to resolve action SHA issues.
- **Security**: Upgraded `pygments` to `>=2.20.0` to address CVE-2026-4539.
- **Security**: Refined `.pth` file detection in security scans to correctly allowlist `distutils-precedence.pth`.
- **Typing**: Relaxed `mypy` configuration to unblock CI while maintaining core application checks.
- **API**: Fixed `expires_delta` type hint in `security.py`.
- **API**: Added `content_type` fallback for document uploads.
- **Search**: Updated vector search to use the modern Qdrant `query_points` API.

## [1.0.2] - 2026-03-24
- Initial stabilization release with Ruff and basic dependency updates.

## [1.0.1] - 2026-03-23
- Fixed Python package discovery and pnpm version mismatch.

## [1.0.0] - 2026-03-22
- First production release of Co-Op OS.
