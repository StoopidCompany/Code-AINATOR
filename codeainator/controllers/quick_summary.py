import os
import pathspec
import json
from ..utils.ProgressAnimation import ProgressAnimation
from ..connections.openai_client import openai_client
from ..config import EXCLUDE_DIRS, EXCLUDE_FILES, PROMPTS

client = openai_client()

def quick_summary(directory):
    directory = os.path.abspath(os.path.expanduser(directory))

    # Initialize file list
    file_list = []

    # Read .gitignore patterns if available
    gitignore_path = os.path.join(directory, '.gitignore')
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, 'r') as gitignore_file:
            gitignore_patterns = gitignore_file.read().splitlines()
        # Create a PathSpec object
        spec = pathspec.PathSpec.from_lines('gitwildmatch', gitignore_patterns)
    else:
        spec = None

    for root, dirs, files in os.walk(directory):
        # Calculate relative paths for directories
        rel_dir = os.path.relpath(root, directory)

        # Always exclude the .git directory
        if '.git' in dirs:
            dirs.remove('.git')

        # Exclude directories and files matching .gitignore patterns
        if spec:
            dirs[:] = [d for d in dirs if not spec.match_file(os.path.join(rel_dir, d))]
            files[:] = [f for f in files if not spec.match_file(os.path.join(rel_dir, f))]
        else:
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            files[:] = [f for f in files if f not in EXCLUDE_FILES]

        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            file_list.append(relative_path)

    # Rest of your existing code...
    messages = [
        {
            "role": "system",
            "content": PROMPTS['quick_summary']
        },
        {
            "role": "user",
            "content": f"{file_list}"
        }
    ]

    with open('filelist.json', 'w') as json_file:
        json.dump(file_list, json_file, indent=4)

    with ProgressAnimation('Analyzing'):
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

    summary = completion.choices[0].message.content
    return summary