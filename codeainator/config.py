# config.py

EXCLUDE_DIRS = {
    'node_modules', 'bower_components', 'vendor',        # JavaScript, PHP
    'venv', '.venv', '__pycache__', 'env', '.env',       # Python
    'dist', 'build', 'out', 'target',                    # General build directories
    'bin', 'obj', 'lib', 'libs', 'include',              # C/C++, C#, Go
    '.git', '.svn', '.hg', '.bzr', 'CVS', '.idea',       # Version control and IDE
    '.vscode', '.vs', '.gradle', '.mvn',                 # IDE and build tools
    '_build', 'deps',                                    # Elixir, Erlang
    '.stack-work', 'dist-newstyle',                      # Haskell
    '.gem', '.bundle', 'spec', 'test',                   # Ruby
    'logs', 'tmp', 'temp', 'cache', '.cache',            # Temporary and log files
    '.next', '.nuxt', '.meteor',                         # JavaScript frameworks
    '.dart_tool', 'packages',                            # Dart/Flutter
    '.pytest_cache', '.mypy_cache', '.tox',              # Python testing tools
    'coverage', 'htmlcov', 'lcov-report',                # Coverage reports
    '.Rproj.user', '.Rhistory', '.RData', '.Ruserdata',  # R
    '.ipynb_checkpoints',                                # Jupyter notebooks
    '.spago', '.psc-package', '.pulp-cache',             # PureScript
    '.pnp', '.yarn-cache', '.yarn',                      # Yarn
    '.nyc_output',                                       # JavaScript test coverage
    '.cargo',                                            # Rust
    '.serverless', '.webpack',                           # Serverless framework
    '.terraform',                                        # Terraform
    'Pods',                                              # iOS (CocoaPods)
    'DerivedData', 'Archives', 'Products',               # Xcode
    '.jekyll-cache',                                     # Jekyll
    '.DS_Store', 'Thumbs.db',                            # OS-generated files
}

EXCLUDE_FILES = {
    '.env', 'secret.key', 'config.py'
}

PROJECT_MANIFESTS = {
    'package.json': 'npm_package',
    'pyproject.toml': 'python_package',
    'setup.py': 'python_package',
    'requirements.txt': 'python_requirements'
}

PROMPTS = {
    'quick_summary': "You are a code analysis AI tool. Your job is to review the list of files in a code "
            "project and determine what type of project it probably is. This includes identifying "
            "the programming languages used, the project's structure, and any other reasonable "
            "assumptions that can be made from the file list alone.\n\n"
            "You will be provided the list of files only. Based on the file list, perform your "
            "analysis and respond by filling out the following template:\n\n"
            "# Project Quick Summary\n\n"
            "- **Project Type**: *(e.g., Web Application, Library, Mobile App, etc.)*\n"
            "- **Primary Language(s)**: *(List the main programming languages used)*\n"
            "- **Frameworks/Libraries**: *(Identify any frameworks or libraries that are likely used)*\n"
            "- **Build Tools/Package Managers**: *(e.g., npm, yarn, pip, Maven, etc.)*\n"
            "- **Project Structure**:\n"
            "  - **Monorepo**: *(Yes/No)*\n"
            "  - **Notable Modules/Packages**: *(List any significant modules or packages)*\n"
            "- **Key Directories/Files**: *(Highlight important directories or files and their purposes)*\n"
            "- **Assumptions**: *(List any reasonable assumptions based on the file list)*\n\n"
            "---\n\n"
            "Provide the filled-out template as your response."
}
