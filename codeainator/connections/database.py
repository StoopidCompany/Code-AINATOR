import sqlite3
import os
import threading

DB_DIR = os.environ.get('CODEAINATOR_DB_PATH', os.path.join(os.path.expanduser('~'), '.codeainator'))
DB_PATH = os.path.join(DB_DIR, 'codeainator.db')
DB_LOCK = threading.Lock()

def get_db_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def initialize_database():
    with DB_LOCK:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE,
                name TEXT,
                summary TEXT,
                last_scanned REAL
            )
        ''')

        # Create products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT,
                type TEXT,
                summary TEXT,
                manifest_path TEXT,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
        ''')

        # Create files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                product_id INTEGER,
                relative_path TEXT,
                name TEXT,
                extension TEXT,
                type TEXT,
                last_modified REAL,
                file_hash TEXT,
                FOREIGN KEY(project_id) REFERENCES projects(id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        ''')

        # Create file_analysis table (for future use)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                analysis_result TEXT,
                analysis_timestamp REAL,
                FOREIGN KEY(file_id) REFERENCES files(id)
            )
        ''')

        conn.commit()
        conn.close()
