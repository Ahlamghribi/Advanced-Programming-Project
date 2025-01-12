import os
import json

#constants pour les fichiers json a utiliser 
USER_FILE = "users.json"
QUESTION_FILE = "questions.json"

def save_json(file_name, data):
    try:
        with open(file_name, 'w') as f:
            json.dump(data, f,indent=4)
    except Exception as e:
        print(f"Error saving {file_name}: {e}")
        
def load_json(file_name):
    try:
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
             return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {file_name} is corrupted. Creating new file.")
        return None                
    
