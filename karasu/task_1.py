import sqlite3
import sys
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'tasks.db')

RED    = '\033[91m'
GREEN  = '\033[92m'
YELLOW = '\033[93m'
GRAY   = '\033[90m'
BOLD   = '\033[1m'
RESET  = '\033[0m'

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
    ''')
    conn.commit()
    conn.close()

def get_user():
    conn = get_db()
    user = conn.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
    conn.close()
    return user['id'] if user else None

def get_tasks():
    conn = get_db()
    tasks = conn.execute(
        'SELECT * FROM tasks WHERE user_id = ? ORDER BY deadline ASC, created_at DESC',
        (get_user(),)
    ).fetchall()
    conn.close()
    return tasks

def print_tasks(tasks=None):
    if tasks is None:
        tasks = get_tasks()
    today = datetime.now().strftime('%Y-%m-%d')
    total = len(tasks)
    completed = sum(1 for t in tasks if t['completed'])
    progress = int((completed / total * 100) if total > 0 else 0)

    print(f"\n{BOLD}📋 課題一覧{RESET}")
    print('─' * 50)
    if not tasks:
        print(f"{GRAY}  課題がありません{RESET}")
    else:
        for task in tasks:
            is_done = task['completed'] == 1
            check = f"{GREEN}✓{RESET}" if is_done else f"{GRAY}○{RESET}"
            title = f"{GRAY}{task['title']}{RESET}" if is_done else task['title']
            deadline_str = ''
            if task['deadline']:
                if is_done:
                    deadline_str = f" {GRAY}({task['deadline']}){RESET}"
                elif task['deadline'] < today:
                    deadline_str = f" {RED}({task['deadline']} 期限超過){RESET}"
                elif task['deadline'] == today:
                    deadline_str = f" {YELLOW}({task['deadline']} 本日){RESET}"
                else:
                    deadline_str = f" {GRAY}({task['deadline']}){RESET}"
            print(f"  {BOLD}[{task['id']}]{RESET} {check} {title}{deadline_str}")
    print('─' * 50)
    bar = ('█' * (progress // 5)).ljust(20)
    print(f"  進捗: {GREEN}{bar}{RESET} {progress}% ({completed}/{total})\n")

def do_add(title, deadline=None):
    if not title.strip():
        print(f"{RED}エラー: 課題名を入力してください{RESET}")
        return
    if deadline:
        try:
            datetime.strptime(deadline, '%Y-%m-%d')
        except ValueError:
            print(f"{RED}エラー: 日付は YYYY-MM-DD 形式で入力してください{RESET}")
            return
    conn = get_db()
    conn.execute('INSERT INTO tasks (user_id, title, deadline) VALUES (?, ?, ?)',
                 (get_user(), title.strip(), deadline or None))
    conn.commit()
    conn.close()
    print(f"{GREEN}✓ 追加しました: {title}{RESET}" + (f" (締切: {deadline})" if deadline else ""))

def do_done(task_id):
    conn = get_db()
    task = conn.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?',
                        (task_id, get_user())).fetchone()
    if not task:
        print(f"{RED}エラー: ID {task_id} の課題が見つかりません{RESET}")
        conn.close()
        return
    new_status = 0 if task['completed'] else 1
    conn.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_status, task_id))
    conn.commit()
    conn.close()
    icon = f"{GREEN}✓ 完了{RESET}" if new_status else f"{YELLOW}○ 未完了に戻した{RESET}"
    print(f"{icon}: {task['title']}")

def do_delete(task_id):
    conn = get_db()
    task = conn.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?',
                        (task_id, get_user())).fetchone()
    if not task:
        print(f"{RED}エラー: ID {task_id} の課題が見つかりません{RESET}")
        conn.close()
        return
    confirm = input(f"  「{task['title']}」を削除しますか？ (y/N): ")
    if confirm.lower() == 'y':
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        print(f"{RED}✕ 削除しました{RESET}")
    else:
        print("キャンセルしました")
    conn.close()

# ─── 対話モード ───────────────────────────────────────
def interactive_mode():
    print(f"\n{BOLD}🎯 TaskFlow 対話モード{RESET}  （終了: q）\n")
    while True:
        print_tasks()
        print(f"  {BOLD}a{RESET} 追加   {BOLD}d{RESET} 完了切替   {BOLD}x{RESET} 削除   {BOLD}q{RESET} 終了")
        cmd = input("\n> ").strip().lower()

        if cmd == 'q':
            print("終了します")
            break

        elif cmd == 'a':
            title = input("  課題名: ").strip()
            deadline = input("  締切日 (YYYY-MM-DD、なければそのままEnter): ").strip()
            do_add(title, deadline if deadline else None)

        elif cmd == 'd':
            try:
                task_id = int(input("  完了にするID: "))
                do_done(task_id)
            except ValueError:
                print(f"{RED}数字を入力してください{RESET}")

        elif cmd == 'x':
            try:
                task_id = int(input("  削除するID: "))
                do_delete(task_id)
            except ValueError:
                print(f"{RED}数字を入力してください{RESET}")

        else:
            print(f"{YELLOW}a / d / x / q を入力してください{RESET}")

# ─── メイン ───────────────────────────────────────────
def main():
    init_db()
    args = sys.argv[1:]

    # 引数なし → 対話モード
    if not args:
        interactive_mode()
        return

    cmd = args[0]

    if cmd in ('l', 'list'):
        print_tasks()

    elif cmd in ('a', 'add'):
        if len(args) < 2:
            print(f"{RED}例: python task.py a \"レポート提出\" 2024-12-20{RESET}")
        else:
            do_add(args[1], args[2] if len(args) >= 3 else None)

    elif cmd in ('d', 'done'):
        if len(args) < 2:
            print(f"{RED}例: python task.py d 1{RESET}")
        else:
            do_done(int(args[1]))

    elif cmd in ('x', 'delete'):
        if len(args) < 2:
            print(f"{RED}例: python task.py x 1{RESET}")
        else:
            do_delete(int(args[1]))

    elif cmd in ('h', 'help'):
        print(f"""
{BOLD}TaskFlow CLI{RESET}

{BOLD}引数なしで起動 → 対話モード（一番簡単）{RESET}
  python task.py

{BOLD}コマンドモード:{RESET}
  python task.py l                       一覧表示
  python task.py a "課題名"              追加
  python task.py a "課題名" 2024-12-20   締切付きで追加
  python task.py d <ID>                  完了/未完了を切替
  python task.py x <ID>                  削除
""")
    else:
        print(f"{RED}不明なコマンド: {cmd}{RESET}  (ヘルプ: python task.py h)")

if __name__ == '__main__':
    main()
