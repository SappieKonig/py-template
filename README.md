# Python Project Template

This is a Python project template that includes:

- **Linting rules**: Custom Python linting rules including keyword-only parameter enforcement
- **Pre-commit hooks**: Automated code quality checks
- **Comprehensive .gitignore**: Python-specific gitignore configuration
- **pyproject.toml**: Modern Python project configuration

## Usage

1. Clone this template
2. Update `pyproject.toml` with your project details
3. Install dependencies: `uv sync`
4. Install pre-commit hooks: `pre-commit install`

## Linting Rules

### kwonly-defaults

Enforces that function parameters with defaults must be keyword-only. Add `*` before the first defaulted parameter.

```python
# Bad
def func(a, b=1, c=2):
    pass

# Good  
def func(a, *, b=1, c=2):
    pass
```

To ignore this rule on a specific function, add `# kwonly: ignore` to the function definition line.
