# Code-AINATOR

Because writing documentation is for suckers.

## Overview

The 'codeainator' is a Python package that streamlines automated code analysis and documentation generation through a command-line interface (CLI). It includes a setup script for easy configuration and a variety of functionalities, enabling users to scan project directories, generate summaries, and perform database operations, with enhanced analysis powered by the OpenAI API. The package also provides pre-commit hooks for code quality, along with templates for managing pull requests, bug reports, and tasks, thereby promoting clean coding practices. Overall, 'codeainator' aims to enhance software development workflows by automating routine tasks and fostering adherence to best practices in collaborative environments.

## Setup

To use this tool you must have an OpenAI API key set to a `OPENAI_API_KEY` environment variable on your system. Please see their documentation for more information: https://platform.openai.com/docs/api-reference/introduction

### Instructions for macOS
1. Install Python (version 3.6 or higher) if it's not already installed. You can do this via Homebrew:
   ```bash
   brew install python
   ```
2. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/codeainator.git
   cd codeainator
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Instructions for Windows
1. Install Python (version 3.6 or higher) from the official website.
2. Clone the repository using Git Bash or Command Prompt:
   ```bash
   git clone https://github.com/your-repo/codeainator.git
   cd codeainator
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Instructions for WSL2 setup on Windows if needed
1. Install WSL2 and a Linux distribution of your choice (e.g., Ubuntu) from the Microsoft Store.
2. Open the WSL terminal and install Python:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
3. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/codeainator.git
   cd codeainator
   ```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Instructions for Linux
1. Install Python (version 3.6 or higher) using your package manager. For example, on Ubuntu:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
2. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/codeainator.git
   cd codeainator
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Once you have completed the setup, you can use the 'codeainator' CLI to scan project directories, generate summaries, and manage database operations. Run the following command to see available options:
```bash
python -m codeainator.cli.py -h
```

This will provide you with details about the command-line options and functionalities available.

## Troubleshooting

If you encounter issues during installation or while using the application, consider the following steps:

1. **Ensure dependencies are installed**: Confirm that you have installed all the required packages listed in `requirements.txt`.
2. **Verify Python version**: 'codeainator' is designed for Python version 3.6 or higher. Check your version with:
   ```bash
   python --version
   ```
3. **File permissions**: If you face permission issues, ensure you have the correct permissions for the directories you are scanning or generating files in.
4. **File paths**: Check that file paths you are entering are correct and exist.
5. **Seeking help**: If you continue to experience problems, consider filing a bug report using the provided template in `.github/ISSUE_TEMPLATE/bug-report.md`. Include detailed information about the issue, including any error messages received.
