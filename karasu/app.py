from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'taskapp-secret-key-2024'

DB_PATH = 'tasks.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            deadline TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'password');
        INSERT OR IGNORE INTO users (username, password) VALUES ('user', '1234');
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('tasks'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('tasks'))
        else:
            flash('ユーザー名またはパスワードが違います', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/tasks')
def tasks():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    all_tasks = conn.execute(
        'SELECT * FROM tasks WHERE user_id = ? ORDER BY deadline ASC, created_at DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    total = len(all_tasks)
    completed = sum(1 for t in all_tasks if t['completed'])
    progress = int((completed / total * 100) if total > 0 else 0)
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('tasks.html', tasks=all_tasks, progress=progress,
                           completed=completed, total=total, today=today)

@app.route('/tasks/add', methods=['GET', 'POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        deadline = request.form.get('deadline', '').strip()
        if not title:
            flash('課題名を入力してください', 'error')
        else:
            conn = get_db()
            conn.execute(
                'INSERT INTO tasks (user_id, title, deadline) VALUES (?, ?, ?)',
                (session['user_id'], title, deadline or None)
            )
            conn.commit()
            conn.close()
            flash('課題を追加しました', 'success')
            return redirect(url_for('tasks'))
    return render_template('add_task.html')

@app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    task = conn.execute(
        'SELECT * FROM tasks WHERE id = ? AND user_id = ?',
        (task_id, session['user_id'])
    ).fetchone()
    if task:
        conn.execute(
            'UPDATE tasks SET completed = ? WHERE id = ?',
            (0 if task['completed'] else 1, task_id)
        )
        conn.commit()
    conn.close()
    return redirect(url_for('tasks'))

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute(
        'DELETE FROM tasks WHERE id = ? AND user_id = ?',
        (task_id, session['user_id'])
    )
    conn.commit()
    conn.close()
    flash('課題を削除しました', 'success')
    return redirect(url_for('tasks'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
