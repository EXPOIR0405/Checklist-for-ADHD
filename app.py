from flask import Flask, render_template, request, redirect, url_for, send_file
from datetime import datetime, date
import hashlib
import json
import os
import random

app = Flask(__name__)

DATA_FILE = 'tasks_data.json'
IMAGES_FOLDER = 'static/images'
LAST_RESET_FILE = 'last_reset.txt'

# Load tasks from file if exists, otherwise use default tasks
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        tasks = data.get('tasks', [])
        additional_tasks = data.get('additional_tasks', [])
        completed_tasks = data.get('completed_tasks', [])
else:
    tasks = []
    additional_tasks = []
    completed_tasks = []

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'tasks': tasks, 'additional_tasks': additional_tasks, 'completed_tasks': completed_tasks}, f, ensure_ascii=False, indent=4)

def encrypt_user_id(user_id):
    return hashlib.sha256(user_id.encode()).hexdigest()

def reset_daily_data():
    global tasks, additional_tasks, completed_tasks
    today = date.today().strftime('%Y-%m-%d')
    if not os.path.exists(LAST_RESET_FILE) or open(LAST_RESET_FILE, 'r').read() != today:
        tasks = []  # or load default tasks here
        additional_tasks = []
        completed_tasks = []
        save_data()
        with open(LAST_RESET_FILE, 'w') as f:
            f.write(today)

@app.route('/')
def index():
    reset_daily_data()
    today = datetime.today().strftime('%Y-%m-%d')
    total_tasks = sum(len(category['tasks']) for category in tasks) + len(additional_tasks)
    task_times = [task['time'] for task in completed_tasks] if completed_tasks else []
    return render_template('index.html', tasks=tasks, additional_tasks=additional_tasks, completed_tasks=completed_tasks, today=today, task_times=task_times, total_tasks=total_tasks)

@app.route('/complete', methods=['POST'])
def complete_task():
    category = request.form['category']
    title = request.form['title']
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    completed_tasks.append({'category': category, 'title': title, 'time': current_time})
    
    for category_obj in tasks:
        if category_obj['category'] == category:
            category_obj['tasks'] = [task for task in category_obj['tasks'] if task['title'] != title]
            break

    additional_tasks[:] = [task for task in additional_tasks if task['title'] != title]
    save_data()
    return redirect(url_for('index'))

@app.route('/add_task', methods=['POST'])
def add_task():
    new_task_title = request.form['title']
    additional_tasks.append({'title': new_task_title, 'steps': []})
    save_data()
    return redirect(url_for('index'))

@app.route('/delete_task', methods=['POST'])
def delete_task():
    title = request.form['title']
    additional_tasks[:] = [task for task in additional_tasks if task['title'] != title]
    save_data()
    return redirect(url_for('index'))

@app.route('/reset_all_tasks', methods=['POST'])
def reset_all_tasks():
    global tasks, additional_tasks, completed_tasks
    tasks = []
    additional_tasks = []
    completed_tasks = []
    save_data()
    return redirect(url_for('index'))

@app.route('/random_image')
def random_image():
    images = os.listdir(IMAGES_FOLDER)
    random_image = random.choice(images)
    return send_file(os.path.join(IMAGES_FOLDER, random_image))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=19993)
