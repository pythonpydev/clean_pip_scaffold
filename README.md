# clean_pip_scaffold
Script that uses pip to setup a new Python project scaffold with templates separated out for source code.

Here is a complete `README.md` file for your `clean_scaffold_pip.py` script:

---

# 🧪 Python Project Scaffold Tool (`scaffold_pip.py`)

This tool automates the creation of a modern, pip-based Python project with documentation, virtual environment, testing, linting, and GitHub integration — in a single command.

---

## ✅ Features

* 📁 `src/` layout for clean packaging
* 🧪 Unit test scaffold with `pytest`
* 🖤 Code formatting with `black` and `isort`
* 🐍 Virtual environment via `venv`
* 📚 Documentation via `Sphinx`
* 🚀 GitHub repo creation and push (via `gh`)
* 🤖 GitHub Actions CI workflow setup
* 📄 Standard project files: `README.md`, `.gitignore`, `pyproject.toml`, etc.

---

## 🚀 How to Use

### 1. **Run the script**

```bash
python clean_scaffold_pip.py <project_name>
```

You’ll be prompted to:

* Detect or input your GitHub username
* Choose public/private repo visibility

This generates a new project in a folder called `<project_name>`.

---

## 🧰 What It Does

1. Creates a `venv`-based isolated environment
2. Generates this project structure:

```
<project_name>/
│
├── .venv/
├── src/<project_name>/        ← Python package
├── tests/                     ← Unit tests
├── docs/                      ← Sphinx documentation
├── .github/workflows/ci.yml   ← GitHub Actions CI
├── pyproject.toml
├── requirements.txt
├── README.md
├── .gitignore
```

3. Installs dev tools via `requirements.txt`
4. Sets up `pytest`, `black`, `isort`, `Sphinx`
5. Initializes Git repo, optionally pushes to GitHub

---

## 🔧 Requirements

* Python 3.7+
* `gh` CLI installed and authenticated:

  ```bash
  gh auth login
  ```
* Internet access to install dependencies

---

## 🛠 Next Steps After Generation

Inside your new project folder:

### 1. Activate your virtual environment

```bash
# On Linux/macOS:
source .venv/bin/activate

# On Windows (CMD):
.\\.venv\\Scripts\\activate.bat

# On Windows (PowerShell):
.\\.venv\\Scripts\\Activate.ps1
```

### 2. Install dependencies (if needed)

```bash
pip install -r requirements.txt
```

### 3. Development tasks

```bash
pytest                       # Run tests
black src tests             # Format code
isort src tests             # Sort imports
sphinx-build -b html docs _build  # Build documentation
```

### 4. Install the project in editable mode

```bash
pip install -e .
```

---

## 🔗 GitHub

If `gh` was enabled and authentication successful, your project is already pushed. Otherwise:

```bash
git remote add origin https://github.com/<username>/<project_name>.git
git push -u origin main
```

---

## 📄 License

This script is provided under the MIT License. Customize freely for your workflow.

---

