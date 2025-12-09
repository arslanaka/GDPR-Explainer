# Contributing to GDPR Explainer Backend

Thank you for your interest in contributing to GDPR Explainer! This document provides guidelines and instructions for contributing to the project.

## 🌟 Ways to Contribute

- **Bug Reports**: Report bugs via GitHub Issues
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests for bug fixes or features
- **Documentation**: Improve documentation, add examples, or fix typos
- **Translations**: Help translate GDPR content to other EU languages
- **Testing**: Write tests or improve test coverage

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/GDPR-Explainer.git
cd GDPR-Explainer

# Add upstream remote
git remote add upstream https://github.com/arslanaka/GDPR-Explainer.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Start infrastructure
docker-compose up -d

# Copy environment template
cp .env.example .env
# Add your API keys to .env
```

### 3. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

## 📝 Development Guidelines

### Code Style

We follow **PEP 8** style guidelines with some modifications:

- **Line length**: 100 characters (not 79)
- **Imports**: Organized with `isort`
- **Formatting**: Use `black` for automatic formatting
- **Type hints**: Required for all function signatures

**Format your code before committing:**

```bash
# Auto-format with black
black backend/

# Check with flake8
flake8 backend/ --max-line-length=100

# Type checking with mypy
mypy backend/
```

### Project Structure

```
backend/
├── app/
│   ├── routers/          # API endpoints (one file per resource)
│   │   ├── chat.py       # Chat-related endpoints
│   │   ├── search.py     # Search endpoints
│   │   └── cache.py      # Cache management
│   └── services/         # Business logic (keep routers thin)
│       ├── chat_service.py
│       └── cache_service.py
├── scripts/              # Data processing scripts
├── tests/                # Test files (mirror app structure)
│   ├── test_chat.py
│   └── test_cache.py
└── main.py              # FastAPI app entry point
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

### Writing Tests

All new features must include tests:

```python
# tests/test_cache_service.py
import pytest
from app.services.cache_service import cache_service

def test_cache_set_and_get():
    """Test basic cache set and get operations"""
    cache_service.set("test", "key1", {"data": "value"})
    result = cache_service.get("test", "key1")
    assert result == {"data": "value"}

def test_cache_expiration():
    """Test cache TTL expiration"""
    cache_service.set("test", "key2", {"data": "value"}, ttl=1)
    time.sleep(2)
    result = cache_service.get("test", "key2")
    assert result is None
```

**Run tests:**

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_cache_service.py -v
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
feat(cache): add Redis connection pooling

- Implement connection pool with max 50 connections
- Add automatic retry with exponential backoff
- Add graceful degradation when Redis is unavailable

Closes #123
```

```bash
fix(chat): handle empty search results gracefully

Previously, empty search results caused a 500 error.
Now returns a helpful message to the user.

Fixes #456
```

## 🔄 Pull Request Process

### 1. Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass (`pytest tests/`)
- [ ] New features include tests
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts with `main`

### 2. Submit PR

1. Push your branch to your fork
2. Open a Pull Request against `main`
3. Fill out the PR template completely
4. Link related issues

### 3. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### 4. Review Process

- Maintainers will review within 2-3 business days
- Address feedback by pushing new commits
- Once approved, maintainers will merge

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues for duplicates
2. Test with the latest `main` branch
3. Verify it's not a configuration issue

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Start services with '...'
2. Make request to '...'
3. See error

**Expected behavior**
What should happen

**Environment:**
- OS: [e.g., macOS 13.0]
- Python version: [e.g., 3.11]
- Docker version: [e.g., 24.0.0]

**Logs**
```
Paste relevant logs here
```
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Screenshots, examples, etc.
```

## 🌍 Translation Contributions

We welcome translations of GDPR content to all EU languages!

### Adding a New Language

1. Create language-specific data file: `data/gdpr_de.txt`
2. Update parsing script: `scripts/1_parse_gdpr.py`
3. Add language code to `app/services/language_detector.py`
4. Update prompts in `app/services/chat_service.py`
5. Add tests for the new language

### Translation Guidelines

- Use official EU translations from [EUR-Lex](https://eur-lex.europa.eu/)
- Maintain article numbering and structure
- Test with native speakers if possible

## 📚 Documentation

### Types of Documentation

- **Code Comments**: For complex logic
- **Docstrings**: For all public functions/classes
- **README**: Setup and quick start
- **docs/**: Detailed guides and architecture

### Docstring Format

```python
def search(self, query: str, limit: int = 5, language: str = "en"):
    """
    Perform semantic search on GDPR articles.
    
    Args:
        query: Search query text
        limit: Maximum number of results to return
        language: Language code (en, de, etc.)
    
    Returns:
        List of search results with article details
    
    Raises:
        ValueError: If query is empty
        ConnectionError: If Qdrant is unavailable
    
    Example:
        >>> results = search_service.search("data protection", limit=3)
        >>> print(results[0]['title'])
    """
```

## 🔒 Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead, email: [your-email@example.com]

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices

- Never commit API keys or secrets
- Use `.env` files for configuration
- Validate all user inputs
- Use parameterized queries for databases
- Keep dependencies updated

## 📋 Code Review Checklist

Reviewers should check:

- [ ] **Functionality**: Does it work as intended?
- [ ] **Tests**: Are there adequate tests?
- [ ] **Performance**: Any performance concerns?
- [ ] **Security**: Any security issues?
- [ ] **Code Quality**: Is it readable and maintainable?
- [ ] **Documentation**: Is it well-documented?
- [ ] **Breaking Changes**: Are they necessary and documented?

## 🎯 Priority Labels

Issues and PRs are labeled by priority:

- `priority: critical` - Security issues, major bugs
- `priority: high` - Important features, significant bugs
- `priority: medium` - Nice-to-have features, minor bugs
- `priority: low` - Documentation, cleanup

## 🏆 Recognition

Contributors will be:
- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- Given credit in documentation

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Chat**: Join our [Discord/Slack] (if applicable)
- **Email**: [your-email@example.com]

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to GDPR Explainer! 🎉
