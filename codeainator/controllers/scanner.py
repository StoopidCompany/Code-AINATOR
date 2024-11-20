import fnmatch
import os
import time
import hashlib
import json
import re
import pathspec
from collections import deque

from ..utils.ProgressAnimation import ProgressAnimation
from ..connections.database import initialize_database, get_db_connection, DB_LOCK
from ..connections.openai_client import openai_client
from ..config import EXCLUDE_DIRS, EXCLUDE_FILES, PROJECT_MANIFESTS, CODE_FILE_EXTENSIONS, PROMPTS

client = openai_client()

def get_gitignore_spec(directory):
    gitignore_path = os.path.join(directory, '.gitignore')
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, 'r') as gitignore_file:
            gitignore_patterns = gitignore_file.read().splitlines()
        return pathspec.PathSpec.from_lines('gitwildmatch', gitignore_patterns)
    return None

def filter_dirs_and_files(root, dirs, files, directory, spec):
    rel_dir = os.path.relpath(root, directory)
    # Always exclude the .git directory
    if '.git' in dirs:
        dirs.remove('.git')
    if spec:
        dirs[:] = [d for d in dirs if not spec.match_file(os.path.join(rel_dir, d))]
        files[:] = [f for f in files if not spec.match_file(os.path.join(rel_dir, f))]
    else:
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        files[:] = [f for f in files if f not in EXCLUDE_FILES]

def call_openai_chat(prompt, content, retries=2):
    for attempt in range(retries):
        try:
            messages = [
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': content}
            ]
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            if attempt < retries - 1:
                print(f"Error during OpenAI call, retrying ({attempt + 1}/{retries}): {e}")
                continue
            else:
                print("Max retries reached. Error during OpenAI call:", e)
                raise

def quick_summary(directory):
    directory = os.path.abspath(os.path.expanduser(directory))
    file_list = []
    spec = get_gitignore_spec(directory)

    for root, dirs, files in os.walk(directory):
        filter_dirs_and_files(root, dirs, files, directory, spec)
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            file_list.append(relative_path)

    summary = call_openai_chat(PROMPTS['quick_summary'], f"{file_list}")
    return summary

def scan_project(directory):
    initialize_database()
    directory = os.path.abspath(os.path.expanduser(directory))
    project_name = os.path.basename(directory)
    print(f"Project '{project_name}' scan started.")

    spec = get_gitignore_spec(directory)

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

        # Initialize variables
        files_processed = set()
        product_context_stack = deque()

        for root, dirs, files in os.walk(directory):
            filter_dirs_and_files(root, dirs, files, directory, spec)
            rel_dir = os.path.relpath(root, directory)

            # Check for product manifests in the current directory
            matched_manifests = []
            for filename in files:
                for manifest_pattern, manifest_type in PROJECT_MANIFESTS.items():
                    if fnmatch.fnmatch(filename, manifest_pattern):
                        manifest_path = os.path.join(root, filename)
                        product_type = manifest_type
                        matched_manifests.append((manifest_path, product_type))
                        break

            # Process matched manifests
            for manifest_path, product_type in matched_manifests:
                relative_manifest_path = os.path.relpath(manifest_path, directory)
                product_name = os.path.basename(root)

                # Insert or update the product
                cursor.execute('''
                    INSERT OR IGNORE INTO products (project_id, name, type, manifest_path)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, product_name, product_type, relative_manifest_path))
                conn.commit()

                # Get the product ID
                cursor.execute('SELECT id FROM products WHERE project_id = ? AND manifest_path = ?', (project_id, relative_manifest_path))
                product_id = cursor.fetchone()[0]

                # Push the current product context onto the stack
                product_context_stack.append((root, product_id))

            if not matched_manifests:
                # Use the last known product context
                while product_context_stack:
                    context_root, context_product_id = product_context_stack[-1]
                    if root.startswith(context_root):
                        product_id = context_product_id
                        break
                    else:
                        product_context_stack.pop()
                else:
                    product_id = None  # No product context

            # Process files in the current directory
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                name = file
                extension = os.path.splitext(name)[1].lower()
                file_type = 'code' if extension in CODE_FILE_EXTENSIONS else 'other'

                print(f"Analyzing '{relative_path}'.")

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

                # Analyze code and manifest files
                if file_type in ('code', 'project_manifest'):
                    if file_type == 'code':
                        prompt = PROMPTS['code_analysis']
                    else:
                        prompt = PROMPTS['project_manifest']
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Analyze file content
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

        # Generate summaries for products
        cursor.execute('SELECT id, name FROM products WHERE project_id = ?', (project_id,))
        product_list = cursor.fetchall()
        for product_id, product_name in product_list:
            # Fetch analysis results for files associated with this product
            cursor.execute('''
                SELECT fa.analysis_result
                FROM file_analysis fa
                JOIN files f ON fa.file_id = f.id
                WHERE f.product_id = ?
            ''', (product_id,))
            analysis_results = cursor.fetchall()
            if analysis_results:
                product_summary = generate_product_summary(analysis_results)
                cursor.execute('''
                    UPDATE products SET summary = ?
                    WHERE id = ?
                ''', (product_summary, product_id))
                conn.commit()

        # Generate project summary
        cursor.execute('''
            SELECT summary FROM products
            WHERE project_id = ?
        ''', (project_id,))
        product_summaries = [row[0] for row in cursor.fetchall() if row[0]]
        if product_summaries:
            project_summary = generate_project_summary(product_summaries)
            cursor.execute('''
                UPDATE projects SET summary = ?
                WHERE id = ?
            ''', (project_summary, project_id))
            conn.commit()

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
            analysis_result = call_openai_chat(prompt, content)
            # Remove surrounding markdown code block if present
            analysis_result = re.sub(r"(^```json\s*|^```|```$)", "", analysis_result.strip(), flags=re.MULTILINE)
            # Validate that it's valid JSON
            json.loads(analysis_result)
            return analysis_result  # Return the valid JSON string if successful

        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print("JSON decode error, retrying analysis...")
                continue
            else:
                print("Max retries reached. JSON decode error:", e)
                raise
        except Exception as e:
            print("Error during analysis:", e)
            raise

def generate_product_summary(analysis_results):
    combined_results = "\n".join([result[0] for result in analysis_results])
    summary = call_openai_chat(PROMPTS['product_summary'], combined_results)
    return summary.strip()

def generate_project_summary(product_summaries):
    combined_summaries = "\n".join(product_summaries)
    summary = call_openai_chat(PROMPTS['project_summary'], combined_summaries)
    return summary.strip()