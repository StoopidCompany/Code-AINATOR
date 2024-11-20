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
    # JavaScript / Node.js
    'package.json': 'npm_package',
    'package-lock.json': 'npm_lockfile',
    'yarn.lock': 'yarn_lockfile',
    'webpack.config.js': 'webpack_config',

    # Python
    'pyproject.toml': 'python_package',
    'setup.py': 'python_package',
    'requirements.txt': 'python_requirements',
    'Pipfile': 'pipenv_project',
    'Pipfile.lock': 'pipenv_lockfile',

    # Java
    'pom.xml': 'maven_project',
    'build.gradle': 'gradle_project',
    'build.gradle.kts': 'gradle_kotlin_project',
    'settings.gradle': 'gradle_settings',
    'settings.gradle.kts': 'gradle_kotlin_settings',

    # .NET
    '.csproj': 'dotnet_cs_project',
    '.vbproj': 'dotnet_vb_project',
    '.fsproj': 'dotnet_fs_project',
    'packages.config': 'dotnet_packages',
    'project.json': 'dotnet_project_json',

    # Ruby
    'Gemfile': 'ruby_gemfile',
    'Gemfile.lock': 'ruby_lockfile',

    # Rust
    'Cargo.toml': 'rust_package',
    'Cargo.lock': 'rust_lockfile',

    # Go
    'go.mod': 'go_module',
    'go.sum': 'go_checksum',

    # PHP
    'composer.json': 'php_composer',
    'composer.lock': 'php_lockfile',

    # Haskell
    '*.cabal': 'haskell_cabal',
    'stack.yaml': 'haskell_stack',

    # C/C++
    'CMakeLists.txt': 'cmake_project',
    'Makefile': 'makefile_project',

    # Swift
    'Package.swift': 'swift_package',

    # Docker
    'Dockerfile': 'dockerfile',

    # Terraform
    '*.tf': 'terraform_module',
    '*.tf.json': 'terraform_module_json',

    # Kubernetes / Helm
    'Chart.yaml': 'helm_chart',

    # Ansible
    'ansible.cfg': 'ansible_config',
    'site.yml': 'ansible_playbook',
    'playbook.yml': 'ansible_playbook',

    # AWS CloudFormation
    '*.template': 'cloudformation_template',
    '*.template.json': 'cloudformation_template_json',
    '*.template.yaml': 'cloudformation_template_yaml',

    # Miscellaneous
    'package.xml': 'package_manifest',
    'setup.cfg': 'python_setup_config',
    'environment.yml': 'conda_environment',
    'docker-compose.yml': 'docker_compose',

    # Other config files
    'tsconfig.json': 'typescript_config',
    'babel.config.js': 'babel_config',
    '.eslintrc.js': 'eslint_config',
    '.prettierrc': 'prettier_config',
}

CODE_FILE_EXTENSIONS = [
    # Scripting languages
    '.py', '.rb', '.pl', '.lua', '.sh', '.bash', '.ps1', '.psm1', '.bat', '.cmd',

    # Web development
    '.js', '.jsx', '.ts', '.tsx', '.html', '.htm', '.css', '.scss', '.less', '.php',

    # Compiled languages
    '.java', '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hh', '.hxx',
    '.cs', '.fs', '.go', '.rs', '.swift', '.kt', '.kts', '.m', '.mm',

    # Functional programming
    '.hs', '.lhs', '.clj', '.cljs', '.scala',

    # Markup and data serialization
    '.xml', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg',

    # IaC and configuration files
    '.tf', '.tf.json', '.template', '.template.json', '.template.yaml',
    '.dockerfile', '.env',

    # Data and databases
    '.sql', '.psql', '.db', '.db3', '.sqlite', '.sqlite3', '.rdb',

    # Others
    '.r', '.sas', '.dtsx', '.erl', '.ex', '.exs', '.dart', '.md', '.markdown',
]

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
            "Provide the filled-out template as your response.",

    'code_analysis': "You are a code analysis AI tool. Your job is to review a given file and determine if its code, config file, or something else and then give a brief but adequate summary of what the file is, what it does within the overall software system it belongs to, and any other reasonable assumption that can be made from the code provided. What is most important is to analyze the file for what may be important when combined with other information on other files in the project to write documentation about the project.\n\n"
            "You will be provided the contents of the file and nothing else to perform this analysis. Respond by filling out the following JSON object:\n\n"
            "{\n"
            "  \"fileType\": \"\",\n"
            "  \"purpose\": \"\",\n"
            "  \"keyComponents\": [],\n"
            "  \"dependencies\": [],\n"
            "  \"assumptions\": []\n"
            "}\n"
            "Provide the JSON object as your response.",

    'project_manifest': "You are a code analysis AI tool. Your job is to review a given project manifest file and analyze it to determine project information. This information can include anything derived from the file including but not limited to project name, dependencies, entry point, etc.\n\n"
            "Review the file and provide a brief summary of your findings by filling out the following JSON object:\n\n"
            "{\n"
            "  \"projectName\": \"\",\n"
            "  \"version\": \"\",\n"
            "  \"dependencies\": [],\n"
            "  \"entryPoint\": \"\",\n"
            "  \"scripts\": [],\n"
            "  \"assumptions\": []\n"
            "}\n"
            "Provide the JSON object as your response.",

    'product_summary': "You are a code analysis AI tool. You will be provided data about code files from a given code product or service. You should take all of the data provided and respond with a brief summary of the product. This should be no more than 1 to 3 paragraphs.",

    'project_summary': "You are a code analysis AI tool. You will be provided information on a code project which may contain one or many code products or services. You should take the data provided and respond with a brief summary of the overall project.",

    'generate': "You are a code analysis AI tool. You will be provided a JSON object called project_data containing high-level analysis of the overall code project, sub-products, and files. You will additionally be provided a document example or template. You should generate a document based on the provided document example or template filling it out using the data provided in the JSON object. Provide the filled-out template as your response."
}
