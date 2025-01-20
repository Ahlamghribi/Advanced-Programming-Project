from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
import json
import os
import csv
from datetime import datetime
from typing import Tuple, Dict, List
from django.core.exceptions import ValidationError
import csv
from django.http import HttpResponse
from pathlib import Path

USER_FILE = "users.json"
QUESTION_FILE = "questions.json"
USER_HISTORY_FILE = "user_history.csv"
 
# Quiz result processing and redirection
def quiz(request, user_id):
    selected_category = request.GET.get('category', 'all')
    all_questions = load_questions()
    if selected_category and selected_category != 'all':
        questions = [q for q in all_questions if q.get('category') == selected_category]
    else:
        questions = all_questions

    if request.method == 'POST':
        user_answers = []
        score = 0
        answered_all = True

        for i, question in enumerate(questions, 1):
            answer = request.POST.get(f'answer_{i}')
            if answer is None:
                answered_all = False
                break
            user_answers.append(answer)
            if answer == question['answer']:
                score += 1

        if not answered_all:
            return render(request, 'quiz.html', {
                'questions': questions,
                'user_id': user_id,
                'selected_category': selected_category,
                'error_message': "Veuillez répondre à toutes les questions avant de soumettre."
            })

        # Scale score to 20
        scaled_score = round((score / len(questions)) * 20, 2)

        # Save user history in JSON
        users = load_json(USER_FILE)
        if user_id in users:
            users[user_id]["history"].append({
                "raw_score": f"{score}/{len(questions)}",
                "scaled_score": f"{scaled_score}/20",
                "percentage": round((score / len(questions)) * 100, 2),
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "category": selected_category
            })
            save_json(USER_FILE, users)

        # Save to CSV directly
        save_user_history(user_id, scaled_score, 20)

        # Save score in session for result page
        request.session['last_score'] = {
            'raw_score': score,
            'total': len(questions),
            'scaled_score': scaled_score,
            'percentage': round((score / len(questions)) * 100, 2)
        }
        
        return redirect('result', user_id=user_id)

    return render(request, 'quiz.html', {
        'questions': questions,
        'user_id': user_id,
        'selected_category': selected_category
    })
def save_history(user_id, score, category):
    """Save a single history entry to CSV file"""
    file_path = "user_history.csv"
    file_exists = os.path.exists(file_path)
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Write header if file is new
            writer.writerow(['Username', 'Date', 'Score', 'Category'])
        writer.writerow([user_id, current_time, score, category])
def save_quiz_history(request, user_id):
    if request.method == 'POST':
        try:
            score = request.POST.get('score')
            category = request.POST.get('category', 'all')
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            file_exists = os.path.exists(USER_HISTORY_FILE)
            with open(USER_HISTORY_FILE, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(['Username', 'Date', 'Score', 'Category'])
                writer.writerow([user_id, current_time, score, category])
            
            messages.success(request, 'Your history was saved successfully!')
            return redirect('result', user_id=user_id)
            
        except Exception as e:
            messages.error(request, f'Error saving history: {str(e)}')
            return redirect('result', user_id=user_id)
            
    messages.error(request, 'Invalid request method')
    return redirect('result', user_id=user_id)

def export_history(request, user_id):
    """
    View to export user history as a downloadable CSV file.
    """
    if request.method == 'POST':
        try:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{user_id}_quiz_history.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Username', 'Date', 'Score', 'Category'])
            
            # Read existing history and filter for user
            if os.path.exists(USER_HISTORY_FILE):
                with open(USER_HISTORY_FILE, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader)  # Skip header
                    for row in reader:
                        if row[0] == user_id:
                            writer.writerow(row)
            
            return response
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
def result(request, user_id):
    users = load_json(USER_FILE)
    last_score = request.session.get('last_score')
    
    if user_id in users:
        history = users[user_id].get("history", [])
        latest_result = history[-1] if history else None
        
        # If we have a last_score, save it to CSV
        if last_score:
            save_history(
                user_id=user_id,
                score=last_score['scaled_score'],
                category=latest_result.get('category', 'all') if latest_result else 'all'
            )
    else:
        history = []
        latest_result = None

    return render(request, 'result.html', {
        'user_id': user_id,
        'history': history,
        'latest_result': latest_result,
        'last_score': last_score
    })

def load_json(file_name: str) -> List[Dict]:
    try:
        if os.path.exists(file_name):
            with open(file_name, "r", encoding='utf-8') as file:
                return json.load(file)
        return [] if file_name == QUESTION_FILE else {}
    except json.JSONDecodeError:
        print(f"Error: {file_name} is corrupted. Creating new file.")
        return [] if file_name == QUESTION_FILE else {}

def save_json(file_name: str, data: List[Dict]) -> None:
    try:
        with open(file_name, "w", encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError:
        print(f"Error: Could not save to {file_name}.")

def load_questions() -> List[Dict]:
    return load_json(QUESTION_FILE)

def get_categories() -> List[str]:
    questions = load_questions()
    categories = set(q['category'] for q in questions if 'category' in q)
    return list(categories)

def save_user_history(user_id: str, score: int, total_questions: int) -> None:
    with open(USER_HISTORY_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, score, total_questions, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

def get_user(user_id: str) -> Tuple[str, Dict, List, bool]:
    if not user_id:
        raise ValidationError("Username is required")

    users = load_json(USER_FILE)
    is_new_user = user_id not in users

    if is_new_user:
        users[user_id] = {
            "history": [],
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_json(USER_FILE, users)
        return user_id, users, [], True

    return user_id, users, users[user_id].get("history", []), False
 
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
import json
import os
import csv
from datetime import datetime
from typing import Tuple, Dict, List
from django.core.exceptions import ValidationError

def index(request):
    try:
        if request.method == "POST":
            user_id = request.POST.get('username')
            if not user_id:
                return JsonResponse({"error": "Username is required"}, status=400)

            user_id, _, history, is_new_user = get_user(user_id)
            categories = list(get_categories())

            if "all" not in categories:
                categories.append("all")

            return render(request, 'choose_category.html', {
                'user_id': user_id,
                'history': history,
                'categories': categories,
                'is_new_user': is_new_user
            })
        return render(request, 'index.html')
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)

def choose_category(request, user_id: str):
    try:
        if not user_id:
            return JsonResponse({"error": "User ID is missing"}, status=400)

        users = load_json(USER_FILE)
        if user_id not in users:
            return JsonResponse({"error": "User not found"}, status=404)

        categories = list(get_categories())
        if "all" not in categories:
            categories.append("all")

        history = users[user_id].get("history", [])
        is_new_user = not history

        if request.method == 'POST':
            selected_category = request.POST.get('category', 'all')
            if selected_category != 'all' and selected_category not in categories:
                return JsonResponse({"error": "Invalid category selected"}, status=400)

            questions = load_questions()
            if selected_category != 'all':
                questions = [q for q in questions if q['category'] == selected_category]

            if not questions:
                messages.warning(request, "No questions available for this category.")

            return render(request, 'quiz.html', {
                'questions': questions,
                'user_id': user_id,
                'selected_category': selected_category,
            })

        return render(request, 'choose_category.html', {
            'user_id': user_id,
            'categories': categories,
            'history': history,
            'is_new_user': is_new_user
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)