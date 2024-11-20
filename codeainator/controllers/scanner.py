import os
import time
import hashlib
import json
import re
import pathspec
from ..utils.ProgressAnimation import ProgressAnimation
from ..connections.database import initialize_database, get_db_connection, DB_LOCK
from ..connections.openai_client import openai_client
from ..config import EXCLUDE_DIRS, EXCLUDE_FILES, PROJECT_MANIFESTS, PROMPTS

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

    with ProgressAnimation('Analyzing'):
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

    summary = completion.choices[0].message.content
    return summary

def scan_project(directory):
    initialize_database()
    directory = os.path.abspath(os.path.expanduser(directory))
    project_name = os.path.basename(directory)

    print(f"Project '{project_name}' scan started.")

    # Read .gitignore patterns if available
    gitignore_path = os.path.join(directory, '.gitignore')
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, 'r') as gitignore_file:
            gitignore_patterns = gitignore_file.read().splitlines()
        # Create a PathSpec object
        spec = pathspec.PathSpec.from_lines('gitwildmatch', gitignore_patterns)
    else:
        spec = None

    with DB_LOCK:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert or update the project
        cursor.execute('''
            INSERT OR REPLACE INTO projects (id, path, name, last_scanned)
            VALUES (
                (SELECT id FROM projects WHERE path = ?),
                ?, ?, ?
            )
        ''', (directory, directory, project_name, time.time()))
        conn.commit()

        # Get the project ID
        cursor.execute('SELECT id FROM projects WHERE path = ?', (directory,))
        project_id = cursor.fetchone()[0]

        products = {}
        files_processed = set()

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
                name = file
                extension = os.path.splitext(name)[1]
                file_type = 'code' if extension in ('.py', '.js', '.ts') else 'other'

                print(f"Analyzing '{name}'.")

                # Check for project manifest
                if name in PROJECT_MANIFESTS:
                    file_type = 'project_manifest'
                    product_type = PROJECT_MANIFESTS[name]

                    # Insert or update the product
                    cursor.execute('''
                        INSERT OR IGNORE INTO products (project_id, name, type, manifest_path)
                        VALUES (?, ?, ?, ?)
                    ''', (project_id, project_name, product_type, relative_path))
                    conn.commit()

                    # Get the product ID
                    cursor.execute('SELECT id FROM products WHERE project_id = ? AND manifest_path = ?', (project_id, relative_path))
                    product_id = cursor.fetchone()[0]

                    products[relative_path] = product_id
                else:
                    product_id = None

                # Insert or update the file
                last_modified = os.path.getmtime(file_path)
                file_hash = compute_file_hash(file_path)

                cursor.execute('''
                    INSERT OR REPLACE INTO files (
                        id, project_id, product_id, relative_path, name, extension, type, last_modified, file_hash
                    ) VALUES (
                        (SELECT id FROM files WHERE project_id = ? AND relative_path = ?),
                        ?, ?, ?, ?, ?, ?, ?, ?
                    )
                ''', (
                    project_id, relative_path,
                    project_id, product_id, relative_path, name, extension, file_type, last_modified, file_hash
                ))
                conn.commit()

                # Get the file ID
                cursor.execute('SELECT id FROM files WHERE project_id = ? AND relative_path = ?', (project_id, relative_path))
                file_id = cursor.fetchone()[0]

                # Only analyze code and project_manifest files
                if file_type in ('code', 'project_manifest'):
                    if file_type == 'code':
                        prompt = PROMPTS['code_analysis']
                    else:
                        prompt = PROMPTS['project_manifest']
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Analyze file content with retry on JSON decode error
                        analysis_result = analyze_file_content(content, prompt)

                        # Insert analysis result into database
                        cursor.execute('''
                            INSERT INTO file_analysis (file_id, analysis_result, analysis_timestamp)
                            VALUES (?, ?, ?)
                        ''', (file_id, analysis_result, time.time()))
                        conn.commit()
                    except Exception as e:
                        print(f"Error analyzing file {relative_path}: {e}")

                files_processed.add(relative_path)

        conn.close()
    print(f"Project '{project_name}' scanned successfully.")
    print(f"Total files processed: {len(files_processed)}")

def delete_project(directory):
    initialize_database()
    directory = os.path.abspath(os.path.expanduser(directory))
    
    with DB_LOCK:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the project ID
        cursor.execute('SELECT id FROM projects WHERE path = ?', (directory,))
        result = cursor.fetchone()
        if result is None:
            print(f"No project found at '{directory}' to delete.")
            conn.close()
            return
        project_id = result[0]

        # Delete related entries
        cursor.execute('DELETE FROM file_analysis WHERE file_id IN (SELECT id FROM files WHERE project_id = ?)', (project_id,))
        cursor.execute('DELETE FROM files WHERE project_id = ?', (project_id,))
        cursor.execute('DELETE FROM products WHERE project_id = ?', (project_id,))
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))

        conn.commit()
        conn.close()
    print(f"Project at '{directory}' and its related data have been deleted from the database.")

def compute_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            buf = f.read(65536)
            if not buf:
                break
            hasher.update(buf)
    return hasher.hexdigest()

def analyze_file_content(content, prompt, max_retries=2):
    for attempt in range(max_retries):
        try:
            # Prepare messages
            messages = [
                {
                    'role': 'system',
                    'content': prompt
                },
                {
                    'role': 'user',
                    'content': content
                }
            ]

            # Get analysis result from OpenAI
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            analysis_result = completion.choices[0].message.content

            # Remove surrounding markdown code block if present
            analysis_result = re.sub(r"(^```json\s*|^```|```$)", "", analysis_result.strip(), flags=re.MULTILINE)

            # Validate that it's valid JSON
            analysis_result_json = json.loads(analysis_result)
            return analysis_result  # Return the valid JSON string if successful

        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print("JSON decode error, retrying analysis...")
                continue  # Retry
            else:
                print("Max retries reached. JSON decode error:", e)
                raise
        except Exception as e:
            print("Error during analysis:", e)
            raise
