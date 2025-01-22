import os
import json
import time
from datetime import datetime

# Simple file names
USER_FILE = "users.json"
QUESTION_FILE = "questions.json"

def save_json(file_name, data):
    # Simple file saving without error handling
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)

def load_json(file_name):
    # Simple file loading
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            return json.load(file)
    return {} if file_name == USER_FILE else []

def initialize_questions():
    # Basic questions setup
    if not os.path.exists(QUESTION_FILE):
        questions = [
            {
                "question": "What is the data type in Python for representing text?",
                "options": ["a) int", "b) str", "c) list"],
                "answer": "b",
                "category": "Python",
                "time_limit": 30
            },
            {
                "question": "What is the average complexity of searching in a sorted array?",
                "options": ["a) O(1)", "b) O(log n)", "c) O(n)"],
                "answer": "b",
                "category": "Algorithms",
                "time_limit": 30    
            }      
        ]
        save_json(QUESTION_FILE, questions)

def load_questions():
    # Simple question loading
    questions = load_json(QUESTION_FILE)
    if not questions:
        initialize_questions()
        questions = load_json(QUESTION_FILE)
    return questions

def get_user():
    # Simple user management
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
    # Simple category list
    return ["Python", "Java", "HTML", "JavaScript", "CSS", "PHP", "SQL"]

def select_category(questions):
    # Simple category selection
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

def provide_detailed_feedback(question, answer, time_taken):
    # Simple feedback system
    is_correct = answer == question['answer']
    
    if is_correct:
        print(f"Correct! Time taken: {time_taken:.1f} seconds")
    else:
        print(f"Wrong! The correct answer was {question['answer']}")
        print(f"Time taken: {time_taken:.1f} seconds")
    
    return is_correct

def show_history(history):
    # Simple history display
    if not history:
        print("No history found")
        return
    
    print("\nYour Quiz History:")
    for entry in history:
        print(f"Date: {entry['date']}")
        print(f"Score: {entry['score']}")
        print(f"Category: {entry['category']}")
        print()

def get_best_users(users):
    # Calculate average scores for each user
    user_scores = []
    for username, data in users.items():
        if data["history"]:
            scores = [float(entry["score"].split('/')[0]) for entry in data["history"]]
            avg_score = sum(scores) / len(scores)
            user_scores.append((username, avg_score))
    
    # Sort by average score and get top 5
    user_scores.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop Performers:")
    if not user_scores:
        print("No quiz results recorded yet.")
        return
    
    for i, (username, avg_score) in enumerate(user_scores[:5], 1):
        print(f"{i}. {username}: {avg_score:.1f}/20 average")
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

    total_time_in_seconds = int(total_time)  # Convert to seconds
    hours = total_time_in_seconds // 3600
    minutes = (total_time_in_seconds % 3600) // 60
    seconds = total_time_in_seconds % 60
    formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"
    
    # Format the date to only show YYYY-MM-DD HH:MM:SS
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if question_count > 0:
        final_score = (score / question_count) * 20
        users[user_id]["history"].append({
            "date": current_time,  # Use formatted current time
            "score": f"{final_score:.1f}/20",
            "category": quiz_questions[0]['category'] if question_count > 0 else "N/A",
            "total_time": formatted_time  # Save formatted time
        })
        save_json(USER_FILE, users)
        
        print(f"\nFinal Score: {final_score:.1f}/20")
        print(f"Total Time: {total_time:.1f} seconds")
        
        # Ask if the user wants to save the history
        save_history_choice = input("Would you like to save your quiz history? (yes/no): ").lower()
        
        if save_history_choice == 'yes':
            export_to_csv(user_id, users)  # Call to export history to CSV
    
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
import csv
def export_to_csv(user_id, users):
    history = users.get(user_id, {}).get("history", [])
    
    if not history:
        print("No history available to export.")
        return
    
    with open("user_history.csv", mode="a", newline="") as file:  # Changement de "w" à "a"
        writer = csv.writer(file)
        
        # Écrire les en-têtes seulement si le fichier est vide
        file.seek(0, os.SEEK_END)  # Aller à la fin du fichier
        if file.tell() == 0:  # Si le fichier est vide
            writer.writerow(["Date", "Score", "Category", "Total Time"])
        
        for entry in history:
            writer.writerow([entry["date"], entry["score"], entry["category"], entry["total_time"]])
    
    print("History successfully exported to user_history.csv")

if __name__ == "__main__":
    main()