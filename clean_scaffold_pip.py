"""
Run using: python scaffold_pip.py <project_name>
Automatically installs: gh (GitHub CLI) if missing
Supports: Linux and Windows
"""

import os
import shutil
import subprocess
import sys
import platform
from pathlib import Path

# Global variables for virtual environment paths
VENV_DIR = ".venv"
VENV_PYTHON_BIN = ""  # Will be set dynamically after venv creation
VENV_PIP_BIN = ""     # Will be set dynamically after venv creation

def run(command, cwd=None):
    """Runs a shell command."""
    print(f"🔧 Running: {command}")
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with code {e.returncode}: {command}")
        sys.exit(1)

def install_missing_tools():
    """Installs missing tools like GitHub CLI."""
    system = platform.system().lower()

    if shutil.which("gh") is None:
        print("⬇️ GitHub CLI ('gh') not found.")
        if shutil.which("apt"):
            print("⬇️ Installing GitHub CLI via apt (Linux)...")
            run("sudo apt update && sudo apt install gh -y")
        elif system == "windows":
            print("⚠️ Please install GitHub CLI manually from:\nhttps://cli.github.com")
            print("   It's recommended for automatic GitHub repo creation and pushing.")
        else:
            print("❌ Unsupported OS for automatic GitHub CLI install. Please install 'gh' manually.")

def load_template(template_name):
    """Loads a template file from the templates directory."""
    template_path = Path(__file__).parent / "templates" / template_name
    if not template_path.exists():
        print(f"❌ Template file not found: {template_path}")
        sys.exit(1)
    return template_path.read_text()

def create_file(path, content=""):
    """Creates a file with specified content, creating parent directories if necessary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\n")

def get_github_username():
    """Retrieves GitHub username using gh CLI."""
    try:
        result = subprocess.run([
            "gh", "api", "user", "--jq", ".login"
        ], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Could not auto-detect GitHub username. 'gh' CLI might not be installed or authorized.")
        return None

def prompt_for_visibility():
    """Prompts user for GitHub repository visibility."""
    while True:
        answer = input("Should the GitHub repo be public? (y/n) [default: n]: ").strip().lower()
        if answer in ("y", "yes"):
            return "public"
        elif answer in ("n", "no", ""):
            return "private"
        print("Please enter 'y' or 'n'.")

def prompt_for_github_user():
    """Prompts user to auto-detect or manually enter GitHub username."""
    auto_detect_answer = input("Do you want to try auto-detecting your GitHub username using `gh`? (y/n) [default: y]: ").strip().lower()
    if auto_detect_answer in ("n", "no"):
        return input("Enter your GitHub username: ").strip()

    gh_user = get_github_username()
    if gh_user:
        print(f"✅ Auto-detected GitHub username: {gh_user}")
        return gh_user
    else:
        print("Auto-detection failed.")
        return input("Enter your GitHub username: ").strip()

def get_current_branch():
    """Gets the current Git branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def setup_git_and_push(github_user, project_name, visibility):
    """Handles Git initialization and pushing to GitHub."""
    repo_pushed_to_github = False
    gh_available = shutil.which("gh") is not None

    if not (Path(".git").exists() and Path(".git").is_dir()):
        print("🛠 Initializing local Git repo...")
        run("git init")
        run("git config init.defaultBranch main")
        run("git checkout -b main")
        run("git add .")
        
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if result.returncode != 0:
            run("git commit -m 'Initial project scaffold'")
        else:
            print("📝 No changes to commit for initial scaffold.")

        if gh_available:
            print(f"🌐 Attempting to create GitHub repo '{github_user}/{project_name}' and push...")
            try:
                visibility_flag = f"--{visibility}"
                run(f"gh repo create {github_user}/{project_name} {visibility_flag} --source=. --remote=origin --push")
                repo_pushed_to_github = True
                print(f"✅ GitHub repo created and code pushed successfully!")
            except subprocess.CalledProcessError:
                print("⚠️ GitHub repo creation/push failed using 'gh'. This might be due to permissions or an existing repo.")
                print("   You may need to create the repository manually on GitHub.")
                print(f"   Setting up remote for manual push to: https://github.com/{github_user}/{project_name}.git")
                run(f"git remote add origin https://github.com/{github_user}/{project_name}.git")
                current_branch = get_current_branch()
                if current_branch:
                    print(f"   To push manually later: git push -u origin {current_branch}")
                else:
                    print("   Could not determine current branch. Please push manually.")
        else:
            print("⚠️ GitHub CLI ('gh') not available. Skipping automatic repo creation and push.")
            print(f"   To push manually, create a repo named '{project_name}' on GitHub (as {visibility}):")
            print(f"   https://github.com/new")
            print(f"   Then run:")
            print(f"   git remote add origin https://github.com/{github_user}/{project_name}.git")
            print(f"   git push -u origin main")
    else:
        print("📂 Git repository already exists. Adding new files and committing...")
        run("git add .")
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if result.returncode != 0:
            run("git commit -m 'Scaffold update'")
            current_branch = get_current_branch()
            if current_branch:
                print(f"📤 Pushing updates to branch: {current_branch}")
                run(f"git push origin {current_branch}")
                repo_pushed_to_github = True
            else:
                print("⚠️ Could not determine current branch name. Please push manually.")
        else:
            print("📝 No new changes to commit.")

    return repo_pushed_to_github

def scaffold_pip_project(project_name):
    """Scaffolds a new Python project using pip and venv."""
    global VENV_PYTHON_BIN, VENV_PIP_BIN

    github_user = prompt_for_github_user()
    if not github_user:
        print("❌ GitHub username is required to proceed.")
        sys.exit(1)

    visibility = prompt_for_visibility()

    base_path = Path(project_name).resolve()
    src_path = base_path / "src" / project_name
    tests_path = base_path / "tests"
    docs_path = base_path / "docs"

    print("📁 Creating project root...")
    base_path.mkdir(parents=True, exist_ok=True)
    os.chdir(base_path)

    print("🐍 Creating virtual environment...")
    run(f"{sys.executable} -m venv {VENV_DIR}")

    # Set virtual environment paths based on OS
    if platform.system().lower() == "windows":
        VENV_PYTHON_BIN = str(base_path / VENV_DIR / "Scripts" / "python.exe")
        VENV_PIP_BIN = str(base_path / VENV_DIR / "Scripts" / "pip.exe")
    else:
        VENV_PYTHON_BIN = str(base_path / VENV_DIR / "bin" / "python")
        VENV_PIP_BIN = str(base_path / VENV_DIR / "bin" / "pip")

    print(f"Using Python: {VENV_PYTHON_BIN}")
    print(f"Using Pip: {VENV_PIP_BIN}")

    print("📁 Creating source and test directories...")
    src_path.mkdir(parents=True, exist_ok=True)
    tests_path.mkdir(exist_ok=True)
    docs_path.mkdir(exist_ok=True)

    # Create files from templates
    print("📄 Creating project files from templates...")
    
    # Create __init__.py
    create_file(src_path / "__init__.py")
    
    # Create main.py from template
    main_content = load_template("main_py_template").format(project_name=project_name)
    create_file(src_path / "main.py", main_content)

    # Create test file from template
    test_content = load_template("test_main_py_template").format(project_name=project_name)
    create_file(tests_path / "test_main.py", test_content)

    # Create pyproject.toml from template
    project_name_normalized = project_name.replace('_', '-')
    pyproject_content = load_template("pyproject_toml_template").format(
        project_name_normalized=project_name_normalized,
        project_name=project_name
    )
    create_file(base_path / "pyproject.toml", pyproject_content)

    # Create requirements.txt from template
    requirements_content = load_template("requirements_txt_template")
    create_file(base_path / "requirements.txt", requirements_content)

    # Create README from template
    readme_content = load_template("README_md_template").format(project_name=project_name)
    create_file(base_path / "README.md", readme_content)

    # Create .gitignore from template
    gitignore_content = load_template(".gitignore_template")
    create_file(base_path / ".gitignore", gitignore_content)

    print("📦 Installing development dependencies from requirements.txt...")
    run(f"{VENV_PIP_BIN} install -r requirements.txt")

    print("📚 Setting up Sphinx docs...")
    run(f"{VENV_PYTHON_BIN} -m sphinx.cmd.quickstart -q -p {project_name} -a 'Your Name' -v 0.1.0 {docs_path}")

    # Replace conf.py with our template
    conf_py_path = docs_path / "conf.py"
    if conf_py_path.exists():
        print("🔧 Configuring Sphinx conf.py...")
        conf_content = load_template("conf_py_template").format(project_name=project_name)
        create_file(conf_py_path, conf_content)
    else:
        print(f"⚠️ Warning: conf.py not found at {conf_py_path}. Autodoc setup might fail.")

    print("🤖 Adding GitHub Actions CI workflow...")
    ci_content = load_template("ci_yml_template")
    create_file(base_path / ".github" / "workflows" / "ci.yml", ci_content)

    print("🌐 Handling Git and GitHub repo...")
    repo_pushed_to_github = setup_git_and_push(github_user, project_name, visibility)

    # Final success message and next steps
    print(f"\n✅ Project '{project_name}' scaffolded, documented, CI-enabled" +
          (" and pushed to GitHub!" if repo_pushed_to_github else " (local only)!"))
    print("➡️ Next steps:")
    print(f"   cd {project_name}")
    print(f"   # 1. Activate virtual environment (important for all subsequent commands):")
    print(f"   #    On Linux/macOS: source {VENV_DIR}/bin/activate")
    print(f"   #    On Windows (Command Prompt): .\\{VENV_DIR}\\Scripts\\activate.bat")
    print(f"   #    On Windows (PowerShell): .\\{VENV_DIR}\\Scripts\\Activate.ps1")
    print(f"   # 2. After activation, you can run these commands:")
    print(f"   pip install -r requirements.txt      # Install development dependencies (already run, but useful if env is rebuilt)")
    print(f"   pytest                               # Run tests")
    print(f"   black src tests                      # Format code with Black")
    print(f"   isort src tests                      # Sort imports with isort")
    print(f"   sphinx-build -b html docs _build     # Build documentation (HTML pages will be in '{base_path / '_build'}')")
    print("   # To install your package in editable mode for development:")
    print("   pip install -e .")

    if repo_pushed_to_github:
        print(f"   📁 View on GitHub: https://github.com/{github_user}/{project_name}")
    else:
        print("   🌐 Push to GitHub when ready:")
        print(f"      git remote add origin https://github.com/{github_user}/{project_name}.git")
        print(f"      git push -u origin main")

if __name__ == "__main__":
    print("✅ Running scaffold_pip.py")
    if len(sys.argv) != 2:
        print("Usage: python scaffold_pip.py <project_name>")
    else:
        if shutil.which(sys.executable) is None:
            print("❌ Python interpreter not found in PATH.")
            print("Please ensure Python 3 is installed and accessible via 'python' or 'python3' command.")
            sys.exit(1)

        install_missing_tools()
        scaffold_pip_project(sys.argv[1])
