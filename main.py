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
        
def load_questions():
    questions= load_json(QUESTION_FILE)
    if not questions:
        initialize_questions()
        questions = load_json(QUESTION_FILE)
        if not questions:
            print("Error : Could not initialize questions.Please check file permissions")
            exit()
    return questions               
           
def get_user():
    users = load_json(USER_FILE)
    while True:
        user_id = input("Enter your username or ID: ").strip()
        if user_id:
            break
        print("Username cannot be empty. Please try again.")
    if user_id not in users:
        users[user_id] = {"history": []}
        save_json(USER_FILE, users)
    return user_id, users

def get_available_categories(questions):
    return sorted(set(q.get("category", "Uncategorized") for q in questions))

def select_category(questions):
    categories = get_available_categories(questions)
    print("\nAvailable categories:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category}")
    print(f"{len(categories) + 1}. All categories")
    while True:
        try:
            choice = int(input("Choose a category: "))
            if 1 <= choice <= len(categories):
                selected_category = categories[choice- 1]
                return [q for q in questions if q.get("category") == selected_category]
            elif choice == len(categories) + 1:
                return questions
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")