# Code Quality Tools

LynrieScoop uses several code quality tools to maintain high standards across both frontend and backend codebases. This document outlines the configuration and usage of these tools.

## Frontend Tools

### ESLint

ESLint is used for JavaScript and TypeScript code linting to ensure code quality and consistency.

#### ESLint Configuration

The ESLint configuration is defined in `frontend/eslint.config.js` using the new flat config format:

```javascript
export default defineConfig([
  { files: ['**/*.{js,mjs,cjs,ts}'], plugins: { js }, extends: ['js/recommended'] },
  { files: ['**/*.{js,mjs,cjs,ts}'], languageOptions: { globals: globals.browser } },
  { files: ['**/*.json'], plugins: { json }, language: 'json/json', extends: ['json/recommended'] },
  {
    files: ['**/*.md'],
    plugins: { markdown },
    language: 'markdown/gfm',
    extends: ['markdown/recommended'],
  },
  { files: ['**/*.css'], plugins: { css }, language: 'css/css', extends: ['css/recommended'] },
  tseslint.configs.recommended,
]);
```

This configuration:

- Applies JavaScript and TypeScript linting rules
- Includes browser globals
- Supports linting for JSON, Markdown, and CSS files
- Uses TypeScript ESLint recommended rules

#### ESLint Usage

Run ESLint with the following npm scripts:

```bash
# Check for linting errors
npm run lint

# Fix automatically fixable linting errors
npm run lint:fix
```

### Prettier

Prettier is used for consistent code formatting across JavaScript, TypeScript, JSON, CSS, and HTML files.

#### Formatting Usage

Format code using the following npm scripts:

```bash
# Format all files
npm run format

# Check if files are properly formatted
npm run format:check
```

### TypeScript

TypeScript provides static type checking for the frontend codebase.

#### TypeScript Configuration

TypeScript configuration is defined in `frontend/tsconfig.json`.

#### How to Use TypeScript

Check TypeScript types without emitting files:

```bash
npm run type-check
```

## Backend Tools

### Black

Black is a Python code formatter that enforces a consistent code style.

#### Black Configuration

Black is configured in `backend/pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

#### How to Use Black

Format Python code using Black:

```bash
cd backend
black .
```

### Flake8

Flake8 is a Python linting tool that checks for style and potential errors.

#### Flake8 Configuration

Flake8 is configured in `backend/setup.cfg`:

```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,build,dist
extend-ignore = E203, W503
```

#### Flake8 Usage

Run Flake8 to check Python code:

```bash
cd backend
flake8
```

### isort

isort is a Python utility for sorting imports alphabetically and automatically separating them into sections.

#### isort Configuration

isort is configured in `backend/setup.cfg`:

```ini
[isort]
profile = black
multi_line_output = 3
include_trailing_comma = True
force_grid_wrap = 0
use_parentheses = True
ensure_newline_before_comments = True
line_length = 100
```

#### isort Usage

Sort imports in Python files:

```bash
cd backend
isort .
```

### MyPy

MyPy provides static type checking for Python code.

#### MyPy Configuration

MyPy is configured in `backend/mypy.ini` with strict type checking enabled:

```ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
explicit_package_bases = True
namespace_packages = True
mypy_path = stubs
```

#### MyPy Usage

Run MyPy for type checking:

```bash
cd backend
mypy app
```

## Git Hooks with Husky

LynrieScoop uses Husky to implement Git pre-commit hooks, which automatically check code quality standards before each commit.

### Husky Configuration

The project uses Husky in combination with lint-staged to run formatters and linters only on staged files, making the pre-commit process efficient.

#### Husky Setup

Husky is configured in the project root with a pre-commit hook:

```bash
# .husky/pre-commit
#!/bin/sh

npx lint-staged
```

#### Lint-Staged Configuration

The lint-staged configuration in `package.json` defines which tools to run on which types of files:

```json
{
  "lint-staged": {
    "{frontend,Frontend}/**/*.{js,ts,jsx,tsx,json,css,html}": "prettier --write",
    "{backend,Backend}/**/*.py": "python -m black"
  }
}
```

This configuration:

- Runs Prettier on all staged JavaScript, TypeScript, JSON, CSS, and HTML files in the frontend directory
- Runs Black on all staged Python files in the backend directory

#### NPM Scripts

The project includes extensive NPM scripts for code quality checks that can be run manually or through the CI pipeline:

```json
{
  "scripts": {
    "prepare": "husky",
    "format:backend": "npm run backend:black",
    "format:frontend": "cd frontend && npm run format",
    "format": "npm run format:backend && npm run format:frontend",
    "lint:backend": "npm run backend:flake8 && npm run backend:isort:check",
    "lint:frontend": "cd frontend && npm run lint",
    "lint": "npm run lint:backend && npm run lint:frontend",
    "check:frontend": "cd frontend && npm run lint && npm run format:check && npm run type-check",
    "check:backend": "npm run backend:black:check && npm run backend:flake8 && npm run backend:isort:check && npm run backend:mypy",
    "check": "npm run check:frontend && npm run check:backend",
    "fix": "npm run fix:frontend && npm run fix:backend"
  }
}
```

### GitHub Workflows

LynrieScoop uses GitHub Actions for continuous integration to ensure code quality across the codebase. The workflow is defined in `.github/workflows/lint.yaml`.

#### Workflow Overview

The workflow is triggered on both push and pull request events and includes the following features:

1. **Path Filtering**: Uses the `dorny/paths-filter` action to determine which parts of the codebase have changed (frontend or backend) and runs only the relevant checks.

2. **Frontend Linting Job**:
   - Runs only when changes are detected in the frontend code
   - Sets up Node.js v20
   - Installs dependencies at both the root and frontend levels
   - Executes frontend checks via npm script (`npm run check:frontend`)

3. **Backend Linting Job**:
   - Runs only when changes are detected in the backend code
   - Sets up both Node.js v20 and Python 3.12
   - Installs backend dependencies from `requirements.txt` and additional linting tools
   - Executes backend checks via npm script (`npm run check:backend`)

#### Workflow Configuration

```yaml
name: Code Linting

on:
  push:
  pull_request:

jobs:
  changes:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: read
    outputs:
      frontend: ${{ steps.filter.outputs.frontend }}
      backend: ${{ steps.filter.outputs.backend }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Filter changes
        uses: dorny/paths-filter@v2
        id: filter
        with:
          base: "main"
          filters: |
            frontend:
              - 'frontend/**'
            backend:
              - 'backend/**'

  # Frontend and backend linting jobs follow...
```

The full workflow configuration is available in the `.github/workflows/lint.yaml` file.

## Integration with Documentation

For comprehensive developer onboarding, code quality tools documentation can be integrated with MkDocs:

1. Add Code Quality Tools to MkDocs navigation in `config/mkdocs/mkdocs.yaml`:

    ```yaml
    nav:
    - Home: README.md
    - Architecture:
        - System Architecture: architecture.md
        - API Reference: api-reference.md
        - Authentication System: authentication.md
        - MQTT Integration: mqtt-integration.md
    - Implementation:
        - Frontend Guide: frontend-guide.md
        - Backend Guide: backend-guide.md
        - Code Quality Tools: code-quality-tools.md
    - Operations:
        - Deployment Guide: deployment-guide.md
    ```

2. Include code quality check steps in the deployment guide to ensure only quality code is deployed.
