# Contributing to Co-Op

Thank you for considering contributing to Co-Op! We follow a solo-developer-first philosophy: start simple, add complexity only when needed.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Adding New Features](#adding-new-features)
- [Reporting Issues](#reporting-issues)
- [License](#license)

## Code of Conduct

This project adheres to a simple code of conduct:
- Be respectful and constructive
- Focus on the code, not the person
- Welcome newcomers and help them learn
- Keep discussions on-topic

## Getting Started

### Prerequisites

- **Docker** 24+ and Docker Compose 2.20+
- **Git**
- **Python** 3.12+ (for local development)
- **Node.js** 20+ and pnpm (for frontend development)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/CO_OP.git
cd CO_OP
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/NAVANEETHVVINOD/CO_OP.git
```

### Local Development Setup

#### Backend (Python)

```bash
cd services/api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"
# Or with uv
uv pip install -e ".[dev]"

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

#### Frontend (Next.js)

```bash
cd apps/web

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

#### CLI

```bash
cd cli

# Install in development mode
pip install -e .

# Test CLI
coop --help
```

## Development Workflow

### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# Or for bug fixes
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write code following our style guidelines
- Add tests for new functionality
- Update documentation if needed

### 3. Test Locally

```bash
# Backend tests
cd services/api
pytest

# Frontend tests
cd apps/web
pnpm test

# CLI tests
cd cli
pytest

# Linting
cd services/api && ruff check .
cd apps/web && pnpm lint
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add user profile page"
# Or
git commit -m "fix: Resolve MinIO health check issue"
```

**Commit Message Format**:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Then open a pull request on GitHub.

## Code Style

### Python

- **Style guide**: PEP 8
- **Linter**: Ruff
- **Formatter**: Ruff format
- **Type hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings for public functions

```python
def calculate_score(text: str, threshold: float = 0.5) -> float:
    """Calculate relevance score for text.
    
    Args:
        text: Input text to score
        threshold: Minimum score threshold
        
    Returns:
        Relevance score between 0 and 1
        
    Raises:
        ValueError: If text is empty
    """
    if not text:
        raise ValueError("Text cannot be empty")
    return 0.8  # Example
```

**Run linter**:
```bash
ruff check .
ruff check --fix .  # Auto-fix
ruff format .  # Format code
```

### TypeScript/React

- **Style guide**: Airbnb TypeScript Style Guide (relaxed)
- **Linter**: ESLint
- **Formatter**: Prettier
- **Components**: Use functional components with hooks
- **Props**: Define prop types with TypeScript interfaces

```typescript
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

export function Button({ label, onClick, variant = 'primary' }: ButtonProps) {
  return (
    <button onClick={onClick} className={`btn-${variant}`}>
      {label}
    </button>
  );
}
```

**Run linter**:
```bash
pnpm lint
pnpm lint:fix  # Auto-fix
```

### General Guidelines

- **Keep it simple**: Prefer simple solutions over clever ones
- **DRY principle**: Don't repeat yourself, but don't over-abstract
- **YAGNI**: You aren't gonna need it - don't add features speculatively
- **Comments**: Explain why, not what (code should be self-explanatory)
- **Error handling**: Always handle errors gracefully

## Testing

### Writing Tests

#### Backend (pytest)

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_conversation(async_client: AsyncClient, auth_headers):
    """Test creating a new conversation."""
    response = await async_client.post(
        "/v1/conversations",
        json={"title": "Test Conversation"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Conversation"
    assert "id" in data
```

#### Frontend (Vitest)

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

test('button calls onClick when clicked', () => {
  const handleClick = vi.fn();
  render(<Button label="Click me" onClick={handleClick} />);
  
  const button = screen.getByText('Click me');
  fireEvent.click(button);
  
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

### Test Coverage

- **Backend**: Maintain >80% coverage
- **Frontend**: Maintain >70% coverage
- **CLI**: Maintain >75% coverage

Run coverage reports:
```bash
# Backend
cd services/api && pytest --cov=app --cov-report=term

# Frontend
cd apps/web && pnpm test:coverage

# CLI
cd cli && pytest --cov=coop --cov-report=term
```

### Test Types

1. **Unit tests**: Test individual functions/classes
2. **Integration tests**: Test complete workflows
3. **Property tests**: Test invariants (using Hypothesis/fast-check)
4. **End-to-end tests**: Test user flows (future)

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests added for new functionality
- [ ] All tests pass locally
- [ ] Documentation updated (if needed)
- [ ] No merge conflicts with main branch
- [ ] Commit messages are clear and descriptive

### PR Description

Include:
- **What**: Brief description of changes
- **Why**: Motivation for the changes
- **How**: Technical approach (if complex)
- **Testing**: How you tested the changes
- **Screenshots**: For UI changes

### Review Process

1. **Automated checks**: CI must pass (tests, linting, coverage)
2. **Code review**: At least one maintainer approval required
3. **Discussion**: Address review comments
4. **Merge**: Squash and merge (maintainers will handle this)

### PR Size

- **Small PRs are better**: Aim for <500 lines changed
- **Single purpose**: One feature or fix per PR
- **Split large changes**: Break into multiple PRs if possible

## Adding New Features

### Feature Planning

1. **Discuss first**: Open an issue to discuss the feature
2. **Follow staged approach**: Check which stage the feature belongs to
3. **Consider complexity**: Will this make the system harder to use?
4. **Document design**: For large features, write a design doc

### Stage Discipline

Co-Op follows a staged development approach:

- **Stage 0 (current)**: Core functionality, single-user, local deployment
- **Stage 1**: Multi-user, basic auth, simple workflows
- **Stage 2**: Advanced features, integrations
- **Stage 3**: Enterprise features, high availability
- **Stage 4**: Full production, compliance, advanced security

**Don't add Stage 2+ features to Stage 0!** This keeps the system simple for solo developers.

### Feature Checklist

- [ ] Feature belongs to current stage
- [ ] Tests added (unit + integration)
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

## Reporting Issues

### Bug Reports

Include:
- **Description**: Clear description of the bug
- **Steps to reproduce**: Exact steps to trigger the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Docker version, etc.
- **Logs**: Relevant log output
- **Screenshots**: If applicable

### Feature Requests

Include:
- **Use case**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives**: Other approaches considered
- **Stage**: Which stage does this belong to?

### Security Issues

**Do not open public issues for security vulnerabilities!**

Instead:
- Email: (security contact - to be added)
- Or use GitHub's private vulnerability reporting

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

When you submit a pull request, you are certifying that:
- You have the right to submit the code
- Your contribution is your original work
- You agree to license it under Apache 2.0

## Questions?

- **GitHub Discussions**: https://github.com/NAVANEETHVVINOD/CO_OP/discussions
- **Discord**: (if available)
- **Documentation**: Check docs/ folder

Thank you for contributing to Co-Op!
