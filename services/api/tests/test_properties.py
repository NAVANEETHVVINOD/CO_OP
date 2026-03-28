"""Property-based tests for configuration validation.

Feature: seo-documentation-test-coverage
These tests use Hypothesis to validate configuration properties across the codebase.
"""
import os
import re
from pathlib import Path
from typing import List

import pytest
from hypothesis import given, settings, strategies as st

# Feature: seo-documentation-test-coverage, Property 1: Backend Code Has No Hardcoded URLs
# This property validates that Python files do not contain hardcoded localhost URLs


def find_python_files(root: Path) -> List[Path]:
    """Find all Python files in the app directory."""
    app_dir = root / "app"
    if not app_dir.exists():
        return []
    return [f for f in app_dir.rglob("*.py") if not f.name.startswith("test_")]


def contains_hardcoded_url(content: str, file_path: str) -> bool:
    """Check if content contains hardcoded localhost URLs.
    
    Allows URLs in:
    - Comments
    - Configuration files (config.py, settings.py)
    - Test files
    """
    # Skip if this is a config or test file
    if "config" in file_path.lower() or "test" in file_path.lower():
        return False
    
    # Patterns to detect hardcoded URLs
    patterns = [
        r'["\']https?://localhost:\d+',
        r'["\']https?://127\.0\.0\.1:\d+',
        r'["\']http://localhost["\']',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            # Check if it's in a comment
            line_start = content.rfind('\n', 0, match.start()) + 1
            line = content[line_start:content.find('\n', match.start())]
            if not line.strip().startswith('#'):
                return True
    
    return False


@settings(max_examples=100)
@given(st.sampled_from(["check_hardcoded_urls"]))
def test_no_hardcoded_urls_in_backend(trigger: str):
    """Property: Backend Python files should not contain hardcoded localhost URLs.
    
    This test scans all Python files in the app directory and ensures they don't
    contain hardcoded URLs like 'http://localhost:8000' or 'http://127.0.0.1:8000'.
    URLs should be read from settings or environment variables instead.
    """
    root = Path(__file__).parent.parent
    python_files = find_python_files(root)
    
    violations = []
    for py_file in python_files:
        content = py_file.read_text(encoding='utf-8')
        if contains_hardcoded_url(content, str(py_file)):
            violations.append(str(py_file.relative_to(root)))
    
    assert not violations, f"Found hardcoded URLs in: {', '.join(violations)}"


# Feature: seo-documentation-test-coverage, Property 2: Environment Variable Completeness
# This property validates that all required environment variables are defined


REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "REDIS_URL",
    "QDRANT_URL",
    "MINIO_URL",
    "MINIO_ROOT_USER",
    "MINIO_ROOT_PASSWORD",
    "SECRET_KEY",
]


@settings(max_examples=100)
@given(st.sampled_from(REQUIRED_ENV_VARS))
def test_required_env_vars_documented(env_var: str):
    """Property: All required environment variables must be documented in .env.example.
    
    This test ensures that every required environment variable is documented
    in the .env.example file with a description.
    """
    root = Path(__file__).parent.parent
    env_example_files = [
        root.parent / "infrastructure" / "docker" / ".env.example",
        root / ".env.example",
    ]
    
    found = False
    for env_file in env_example_files:
        if env_file.exists():
            content = env_file.read_text(encoding='utf-8')
            if env_var in content:
                found = True
                break
    
    assert found, f"Required environment variable {env_var} not documented in .env.example"


@settings(max_examples=100)
@given(st.sampled_from(["check_settings_usage"]))
def test_settings_class_uses_env_vars(trigger: str):
    """Property: Settings class should use environment variables, not hardcoded values.
    
    This test checks that the Settings class in config.py uses environment variables
    for all configuration values.
    """
    root = Path(__file__).parent.parent
    config_file = root / "app" / "config.py"
    
    if not config_file.exists():
        pytest.skip("config.py not found")
    
    content = config_file.read_text(encoding='utf-8')
    
    # Check for hardcoded connection strings
    hardcoded_patterns = [
        r'=\s*["\']postgresql://[^"\']+["\']',
        r'=\s*["\']redis://localhost',
        r'=\s*["\']http://localhost:\d+["\']',
    ]
    
    violations = []
    for pattern in hardcoded_patterns:
        if re.search(pattern, content):
            violations.append(pattern)
    
    assert not violations, f"Found hardcoded values in config.py: {violations}"
