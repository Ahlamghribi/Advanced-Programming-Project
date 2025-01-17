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
  

def administer_qcm(user_id, users): 
    all_questions = load_questions()
    selected_questions = select_category(all_questions)
    
    if not selected_questions:
        print("No questions available in this category.")
        return
    
    score = 0
    total = len(selected_questions)
    total_time = 0
    question_count = 0
    max_total_time = 600  # Total time limit in seconds (e.g., 10 minutes)
    
    print("\nStarting the quiz. Answer carefully!\n")
    print(f"Time limit per question: 30 seconds")
    print(f"Total available time: {max_total_time // 60} minutes\n")
    
    start_test_time = time.time()  # Start time for the entire test
    
    for i, question in enumerate(selected_questions, 1):
        if question_count >= 7:  # Limit the number of questions to 7
            choice = input("\nYou have answered 7 questions. Do you want to continue with another category or stop? (cont/stop): ").strip().lower()
            if choice == 'stop':
                break
            else:
                selected_questions = select_category(all_questions)
                question_count = 0  # Reset question counter for a new category
                        print(f"Question {i}/{total} [{question['category']}]:")
        print(question['question'])
        for option in question['options']:
            print(option)
        
        question_start_time = time.time()
        while True:
            total_elapsed_time = time.time() - start_test_time
            if total_elapsed_time > max_total_time:
                print("\nTotal time exceeded. The test is finished.")
                break
            
            time_taken_for_question = time.time() - question_start_time
            if time_taken_for_question > question.get("time_limit", 30):  # 30 seconds default time limit
                print(f"\nTime's up for this question. You didn't answer in time.")
                break
            
            answer = input(f"Your answer (a/b/c) [{30 - int(time_taken_for_question)} seconds remaining]: ").strip().lower()
            if answer in ['a', 'b', 'c']:
                break
            print("Please enter a valid option (a, b, or c)")
        
        end_time = time.time()
        time_taken = end_time - question_start_time
        total_time += time_taken
        question_count += 1
        
        is_correct, feedback = provide_detailed_feedback(question, answer, time_taken)
        print(feedback)
        
        if time_taken <= question.get("time_limit", 30) and is_correct:
            score += 1
        
        if total_elapsed_time > max_total_time:
            break
                adjusted_score = (score / total) * 20
    adjusted_score = round(adjusted_score, 1)
    
    final_score = f"{adjusted_score}/20"
    average_time = total_time / question_count if question_count else 0
    
    print(f"\nFinal Results:")
    print(f"Score: {final_score}")
    print(f"Total time: {total_time:.1f} seconds")
    print(f"Average time per question: {average_time:.1f} seconds")
        users[user_id]["history"].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "score": final_score,
        "total_time": f"{total_time:.1f}",
        "category": "All" if len(selected_questions) == len(all_questions) else selected_questions[0]['category']
    })
    save_json(USER_FILE, users)




def save_results(user_id, users, score, total_time):
    users[user_id]["history"].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "score": score,
        "total_time": f"{total_time:.2f} seconds"
    })
    save_json(USER_FILE, users)

def export_to_csv(users):
    try:
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
        print("Data successfully exported to 'user_history.csv'.")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")

def main():
    try:
        print("Welcome to the QCM Application!")
        user_id, users = get_user()
        administer_qcm(user_id, users)

        if input("\nDo you want to export your history to CSV? (y/n): ").strip().lower() == 'y':
            export_to_csv(users)
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
