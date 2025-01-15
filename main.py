import os
import json
import time

#constants pour les fichiers json a utiliser 
USER_FILE = "users.json"
QUESTION_FILE = "questions.json"

def save_json(file_name, data):
    try:
        with open(file_name, 'w',encoding="utf-8") as f:
            json.dump(data, f,indent=4)
    except Exception as e:
        print(f"Error saving {file_name}: {e}")
        
def load_json(file_name):
    try:
        if os.path.exists(file_name):
            with open(file_name, 'r',encoding='utf-8') as f:
             return json.load(f)
        return [] if file_name == QUESTION_FILE else {} 
    except json.JSONDecodeError:
        print(f"Error: {file_name} is corrupted. Creating new file.")
        return [] if file_name == QUESTION_FILE else {}               
def initialize_questions():
    if not os.path.exists(QUESTION_FILE):
        questions = [
            {
               "question": "What is the data type in Python for representing text?",
                "options": ["a) int", "b) str", "c) list"],
                "answer": "b",
                "time_limit": 30 
            }
            {
                "question": "What is the average complexity of searching in a sorted array?",
                "options": ["a) O(1)", "b) O(log n)", "c) O(n)"],
                "answer": "b",
                "time_limit": 30    
            }      
     ] 
        save_json(QUESTION_FILE, questions)
           
