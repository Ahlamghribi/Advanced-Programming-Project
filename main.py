import os
import json
import time
import csv
from datetime import datetime

#constants pour les fichiers json a utiliser 
USER_FILE = "users.json"
QUESTION_FILE = "questions.json"

def save_json(file_name, data):
    try:
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving to {file_name}: {e}")
        
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
            
def provide_detailed_feedback(question, answer, time_taken):
    is_correct = answer == question["answer"]
    feedback = "Correct!" if is_correct else f"Wrong! Correct answer: {question['answer']}"
    if time_taken > question.get("time_limit", 30):
        feedback += " (Time limit exceeded)"
    return is_correct, feedback    

def administer_qcm(user_id, users):
    questions = load_questions()
    selected_questions = select_category(questions)
    max_total_time = 600
    total_time = 0
    score = 0

    for question in selected_questions:
        print("\nQuestion:", question["question"])
        for option in question["options"]:
            print(option)

        question_start = time.time()
        answer = input("Your answer: ").strip()
        question_time = time.time() - question_start

        total_time += question_time
        if total_time > max_total_time:
            print("You have exceeded the total test time!")
            break

        is_correct, feedback = provide_detailed_feedback(question, answer, question_time)
        print(feedback)
        if is_correct:
            score += 1

    save_results(user_id, users, score, total_time)
    print(f"\nTest completed! Your score: {score}/{len(selected_questions)}")


def save_results(user_id, users, score, total_time):
    users[user_id]["history"].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "score": score,
        "total_time": f"{total_time:.2f} seconds"
    })
    save_json(USER_FILE, users)

def export_to_csv(users):
    with open("user_history.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Username", "Date", "Score"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user, data in users.items():
            for entry in data["history"]:
                writer.writerow({
                    "Username": user,
                    "Date": entry["date"],
                    "Score": entry["score"]
                })
