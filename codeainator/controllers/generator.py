# controllers/generator.py

import os
import json
from ..connections.database import initialize_database, get_db_connection, DB_LOCK
from ..connections.openai_client import openai_client
from ..config import PROMPTS
from ..utils.ProgressAnimation import ProgressAnimation

client = openai_client()

def generate_file(directory, template_path=None):
    initialize_database()
    directory = os.path.abspath(os.path.expanduser(directory))
    
    with DB_LOCK:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the project ID and summary
        cursor.execute('SELECT id, summary FROM projects WHERE path = ?', (directory,))
        project_row = cursor.fetchone()
        if project_row is None:
            print(f"No project found at '{directory}'. Please run analysis first.")
            conn.close()
            return
        project_id, project_summary = project_row
        
        result = {
            "project_summary": project_summary,
            "products": [],
            "additional_files": []
        }
        
        # Get products for the project
        cursor.execute('SELECT id, summary FROM products WHERE project_id = ?', (project_id,))
        products = cursor.fetchall()
        for product_id, product_summary in products:
            product_data = {
                "product_summary": product_summary,
                "files": []
            }
            # Get files for the product
            cursor.execute('''
                SELECT f.relative_path, fa.analysis_result
                FROM files f
                LEFT JOIN file_analysis fa ON f.id = fa.file_id
                WHERE f.product_id = ?
            ''', (product_id,))
            files = cursor.fetchall()
            for file_name, analysis_result in files:
                purpose = None
                if analysis_result:
                    # Parse the JSON analysis result
                    try:
                        analysis_data = json.loads(analysis_result)
                        purpose = analysis_data.get('purpose')
                    except (json.JSONDecodeError, TypeError):
                        pass  # Handle malformed JSON if necessary
                file_data = {
                    "file_name": file_name,
                    "analysis": purpose
                }
                product_data["files"].append(file_data)
            # Skip the product if it's empty (no summary and no files)
            if (product_summary and product_summary.strip()) or product_data["files"]:
                result["products"].append(product_data)
        
        # Get additional files not associated with any product
        cursor.execute('''
            SELECT f.relative_path, fa.analysis_result
            FROM files f
            LEFT JOIN file_analysis fa ON f.id = fa.file_id
            WHERE f.project_id = ? AND f.product_id IS NULL
        ''', (project_id,))
        files = cursor.fetchall()
        
        for file_name, analysis_result in files:
            purpose = None
            if analysis_result:
                try:
                    analysis_data = json.loads(analysis_result)
                    purpose = analysis_data.get('purpose')
                except (json.JSONDecodeError, TypeError):
                    pass
            file_data = {
                "file_name": file_name,
                "analysis": purpose
            }
            result["additional_files"].append(file_data)
        
        conn.close()
    
    project_data = json.dumps(result, indent=4)
    
    if template_path:
        template_path_expanded = os.path.abspath(os.path.expanduser(template_path))
        if not os.path.isfile(template_path_expanded):
            print(f"Template file '{template_path}' not found.")
            return
        with open(template_path_expanded, 'r') as f:
            template = f.read()
    else:
        template = "- **Primary Language(s)**: *(List the main programming languages used)*\n" \
                   "- **Frameworks/Libraries**: *(Identify any frameworks or libraries that are used)*\n" \
                   "- **Build Tools/Package Managers**: *(e.g., npm, yarn, pip, Maven, etc.)*\n" \
                   "- **Project Structure**:\n" \
                   "  - **Monorepo**: *(Yes/No)*\n" \
                   "  - **Notable Modules/Packages**: *(List any significant modules or packages)*\n" \
                   "- **Key Directories/Files**: *(Highlight important directories or files and their purposes)*\n" \
                   "- **Assumptions**: *(List any reasonable assumptions based on the data)*\n\n"
        
    messages = [
        {
            "role": "system",
            "content": PROMPTS['generate']
        },
        {
            "role": "user",
            "content": f"project_data: {project_data}\n"
                       f"template: {template}"
        }
    ]
    
    with ProgressAnimation('Analyzing'):
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
    
    summary = completion.choices[0].message.content
    return summary