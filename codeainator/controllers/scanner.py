import os
import time
import hashlib
from ..connections.database import initialize_database, get_db_connection, DB_LOCK
from ..config import EXCLUDE_DIRS, PROJECT_MANIFESTS

def scan_project(directory):
    initialize_database()
    directory = os.path.abspath(os.path.expanduser(directory))
    project_name = os.path.basename(directory)

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
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                name = file
                extension = os.path.splitext(name)[1]
                file_type = 'code' if extension in ('.py', '.js', '.ts') else 'other'

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
