import os
import json
import time
import csv
from datetime import datetime
import random

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
            },
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
    user_id = input("Enter your username please: ")
    
    if user_id in users:
        print(f"Welcome back, {user_id}!")
        show_history(users[user_id].get("history", []))
    else:
        print(f"Welcome, {user_id}!")
        users[user_id] = {"history": []}
        save_json(USER_FILE, users)
    
    return user_id, users
    
def get_available_categories():
    return ["Python", "Java", "HTML", "JavaScript", "CSS", "PHP", "SQL"]

# Function to select a category of questions
def select_category(questions):
    categories = get_available_categories()
    print("\nCategories:")
    for i in range(len(categories)):
        print(f"{i+1}. {categories[i]}")
    print(f"{len(categories) + 1}. All categories")
    
    while True:
        try:
            choice = int(input("Choose a category number (or 0 to exit): "))
            if choice == 0:
                return None
            if 1 <= choice <= len(categories) + 1:
                break
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    if choice == len(categories) + 1:
        return questions
    else:
        selected_category = categories[choice - 1]
        filtered_questions = [q for q in questions if q['category'] == selected_category]
        if not filtered_questions:
            print("No questions available for this category.")
            return None
        return filtered_questions

import random
def provide_detailed_feedback(question, answer, time_taken):
    feedback = {
        True: [
            "Excellent! That's the correct answer!",
            "Perfect! You are right!",
            "Well done! That's correct!"
        ],
        False: [
            "Not quite. The correct answer was ",
            "Incorrect. The expected answer was ",
            "That's not the right answer. You should have answered "
        ]
    }
    
    is_correct = answer == question['answer']
    
    base_feedback = random.choice(feedback[is_correct])
    if is_correct:
        detail = f"{base_feedback}\nTime taken: {time_taken:.1f} seconds"
    else:
        detail = f"{base_feedback}{question['answer']}\nTime taken: {time_taken:.1f} seconds"
        
    if time_taken > question.get("time_limit", 30):
        detail += " (Time limit exceeded)"
        
    return is_correct, detail
  

def show_history(history):
    if not history:
        print("No history found")
        return
    
    print("\nYour Quiz History:")
    for entry in history:
        print(f"-Date: {entry['date']}")
        print(f"-Score: {entry['score']}")
        print(f"-Category: {entry['category']}")
        print()


def administer_qcm(user_id, users):
    # Simple quiz administration
    questions = load_questions()
    quiz_questions = select_category(questions)
    
    if quiz_questions is None:
        return False
    
    score = 0
    total_time = 0
    question_count = 0
    
    for i, question in enumerate(quiz_questions):
        if question_count >= 7:
            choice = input("You've answered 7 questions. Continue? (yes/no): ")
            if choice.lower() != 'yes':
                break
        
        print(f"\nQuestion {i+1}:")
        print(question['question'])
        for option in question['options']:
            print(option)
        
        start_time = time.time()
        while True:
            answer = input("Your answer (a/b/c) or 'exit' to quit: ").lower()
            if answer == 'exit':
                return False
            if answer in ['a', 'b', 'c']:
                break
            print("Invalid input. Please enter a, b, or c.")
        
        time_taken = time.time() - start_time
        
        if provide_detailed_feedback(question, answer, time_taken):
            score += 1
        
        total_time += time_taken
        question_count += 1
    
    if question_count > 0:
        final_score = (score / question_count) * 20
        users[user_id]["history"].append({
            "date": str(datetime.now()),
            "score": f"{final_score:.1f}/20",
            "category": quiz_questions[0]['category'] if question_count > 0 else "N/A",
            "total_time": f"{total_time:.1f}"
        })
        save_json(USER_FILE, users)
        
        print(f"\nFinal Score: {final_score:.1f}/20")
        print(f"Total Time: {total_time:.1f} seconds")
        
        # hna we ask if the user wants to save the history
        save_history_choice = input("Would you like to save your quiz history? (yes/no): ").lower()
        
        if save_history_choice == 'yes':
            export_to_csv(user_id, users)  
    
    return True

def show_menu():
    print("\nDevQuiz Menu:")
    print("1. Take Quiz")
    print("2. View History")
    print("3. View Best Users")
    print("4. Exit")
    while True:
        try:
            choice = int(input("Enter your choice (1-4): "))
            if 1 <= choice <= 4:
                return choice
            print("Invalid choice. Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")


def export_to_csv(user_id, users):
    history = users.get(user_id, {}).get("history", [])
    
    if not history:
        print("No history available to export.")
        return
    
    with open("user_history.csv", mode="a", newline="") as file: 
        writer = csv.writer(file)
        
        file.seek(0, os.SEEK_END)   
        if file.tell() == 0:  
            writer.writerow(["Date", "Score", "Category", "Total Time"])
        
        for entry in history:
            writer.writerow([entry["date"], entry["score"], entry["category"], entry["total_time"]])
    
    print("History successfully exported to user_history.csv")

def main():
    print("Welcome to DevQuiz! Test, Learn, and Conquer!")
    user_id, users = get_user()
    
    while True:
        choice = show_menu()
        
        if choice == 1:
            quiz_completed = administer_qcm(user_id, users)
            if not quiz_completed:
                print("\nQuiz terminated.")
        elif choice == 2:
            show_history(users[user_id]["history"])
        elif choice == 3:
            get_best_users(users)
        else:  # choice == 4
            print("Thank you for using DevQuiz! Goodbye!")
            break

if __name__ == "__main__":
    main()
