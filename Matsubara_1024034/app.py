import argparse
import json
import os
import time
import hashlib
from datetime import datetime

# データ設計に基づき、ローカルのJSONファイルにデータを保存します
DATA_FILE = "storage.json"

# --- 1. データ管理用の関数（データストレージ設計） ---
def load_data():
    """JSONファイルからデータを読み込む（ファイルがない場合は初期構造を返す）"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # 初期データ構造（design.mdのデータ設計に準拠）
    return {"users": {}, "tasks": [], "records": [], "current_user": None}

def save_data(data):
    """データをJSONファイルに書き込む"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def hash_password(password):
    """セキュリティ要件：パスワードをSHA-256でハッシュ化（平文保存の禁止）"""
    return hashlib.sha256(password.encode()).hexdigest()


# --- 2. 各コマンドの処理（ロジック設計） ---
def cmd_register(args):
    """新規ユーザー登録 (register)"""
    data = load_data()
    username = input("希望するユーザー名を入力してください: ")
    if username in data["users"]:
        print("エラー: そのユーザー名は既に存在します。")
        return
    password = input("パスワードを入力してください: ")
    
    data["users"][username] = {
        "password": hash_password(password),
        "token": None
    }
    save_data(data)
    print(f"ユーザー '{username}' の登録が完了しました。")

def cmd_login(args):
    """ログイン (login)"""
    data = load_data()
    username = input("ユーザー名: ")
    password = input("パスワード: ")
    
    if username in data["users"] and data["users"][username]["password"] == hash_password(password):
        token = hashlib.md5(str(time.time()).encode()).hexdigest()
        data["users"][username]["token"] = token
        data["current_user"] = username
        save_data(data)
        print(f"ログイン成功！ こんにちは、{username}さん。")
    else:
        print("エラー: ユーザー名またはパスワードが正しくありません。")

def cmd_add(args):
    """学習タスク追加 (add)"""
    data = load_data()
    if not data["current_user"]:
        print("エラー: タスクを追加するには先にログインしてください。")
        return
    
    task_id = len(data["tasks"]) + 1
    # 仕様書のデータ設計に合わせて「締切日(deadline)」をデフォルトで設定
    new_task = {
        "task_id": task_id,
        "title": args.title,
        "deadline": "2026-06-30", 
        "priority": args.priority,
        "completed": False,
        "user": data["current_user"]
    }
    data["tasks"].append(new_task)
    save_data(data)
    print(f"タスクを追加しました: [ID: {task_id}] {args.title} (優先度: {args.priority})")

def cmd_list(args):
    """未完了タスク一覧表示 (list / ls)"""
    data = load_data()
    if not data["current_user"]:
        print("エラー: ログインしてください。")
        return
    
    user_tasks = [t for t in data["tasks"] if t["user"] == data["current_user"] and not t["completed"]]
    
    if not user_tasks:
        print("未完了のタスクはありません。")
        return
    
    print(f"{'ID':<4} | {'タスクタイトル':<25} | {'優先度':<6}")
    print("-" * 45)
    for t in user_tasks:
        print(f"{t['task_id']:<4} | {t['title']:<25} | {t['priority']:<6}")

def cmd_done(args):
    """タスク完了マーク (done)"""
    data = load_data()
    for t in data["tasks"]:
        if t["task_id"] == args.id and t["user"] == data["current_user"]:
            t["completed"] = True
            save_data(data)
            print(f"タスク ID {args.id} を完了にしました！")
            return
    print("エラー: 指定されたタスクが見つかりません。")

def cmd_delete(args):
    """【仕様追加】タスク削除 (delete)"""
    data = load_data()
    if not data["current_user"]:
        print("エラー: ログインしてください。")
        return
    
    # 指定されたIDかつ自分のタスク以外のものを残す（＝削除する）
    original_count = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if not (t["task_id"] == args.id and t["user"] == data["current_user"])]
    
    if len(data["tasks"]) < original_count:
        save_data(data)
        print(f"タスク ID {args.id} を削除しました。")
    else:
        print("エラー: 指定されたタスクが見つかりません。")

def cmd_start(args):
    """【仕様追加】学習タイマー機能（一時停止・再開に対応）"""
    data = load_data()
    if not data["current_user"]:
        print("エラー: ログインしてください。")
        return
    
    duration = args.seconds
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"ポモドーロタイマーを開始します ({duration}秒)...")
    print("※ カウントダウン中に [Ctrl + C] を押すと一時停止（stop）できます。")
    
    remaining = duration
    try:
        while remaining > 0:
            print(f"\r残り時間: {remaining}秒 ", end="", flush=True)
            time.sleep(1)
            remaining -= 1
            
    except KeyboardInterrupt:
        # 仕様書の「タイマーストップ」を再現
        print("\n\n--- タイマー一時停止 (timer stop) ---")
        choice = input("再開しますか？ (y: 再開(restart) / n: 中断して終了): ").strip().lower()
        if choice == 'y':
            print("タイマーを再開します (timer restart)...")
            try:
                while remaining > 0:
                    print(f"\r残り時間: {remaining}秒 ", end="", flush=True)
                    time.sleep(1)
                    remaining -= 1
            except KeyboardInterrupt:
                print("\nタイマーが完全に中断されました。")
                return
        else:
            print("タイマーを終了しました。")
            return

    # タイマー正常終了処理（通知要件）
    print("\n\a時間です！休憩に入りましょう。 (通知テキスト＆ベル音)")
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 仕様書のデータ設計に合わせて「対応タスクID(task_id)」を記録（デフォルト1、argsから指定も可能）
    record_id = len(data["records"]) + 1
    new_record = {
        "record_id": record_id,
        "start_time": start_time,
        "end_time": end_time,
        "duration_seconds": duration,
        "task_id": args.task_id,
        "user": data["current_user"]
    }
    data["records"].append(new_record)
    save_data(data)
    print("学習記録をデータストレージに保存しました。")

def cmd_summary(args):
    """学習履歴・進捗確認機能 (summary / stats)"""
    data = load_data()
    if not data["current_user"]:
        print("エラー: ログインしてください。")
        return
    
    user_records = [r for r in data["records"] if r["user"] == data["current_user"]]
    total_time = sum(r["duration_seconds"] for r in user_records)
    
    print("=== 学習状況レポート ===")
    print(f"総学習回数: {len(user_records)} 回")
    print(f"総学習時間: {total_time} 秒")
    
    # 仕様書要件：達成率をアスキーアートの進捗バーで表示
    goal = 60
    progress = min(int((total_time / goal) * 10), 10)
    bar = "■" * progress + "□" * (10 - progress)
    percent = min(int((total_time / goal) * 100), 100)
    print(f"目標達成率: [{bar}] {percent}% (目標: 60秒)")


# --- 3. コマンドライン引数の設定 ---
def main():
    parser = argparse.ArgumentParser(description="自作CLI学習管理ソフト")
    subparsers = parser.add_subparsers(dest="command")

    # auth関連
    subparsers.add_parser("register", help="新規アカウント作成")
    subparsers.add_parser("login", help="ログイン")

    # タスク関連
    p_add = subparsers.add_parser("add", help="新しいタスクを登録")
    p_add.add_argument("title", type=str, help="タスクのタイトル")
    p_add.add_argument("--priority", type=str, choices=["高", "中", "低"], default="中", help="優先度")

    subparsers.add_parser("list", aliases=["ls"], help="未完了タスクを一覧表示")
    
    p_done = subparsers.add_parser("done", help="タスクを完了状態にする")
    p_done.add_argument("id", type=int, help="完了にするタスクのID")

    # 【仕様追加】タスク削除コマンド
    p_delete = subparsers.add_parser("delete", help="タスクを削除する")
    p_delete.add_argument("id", type=int, help="削除するタスクのID")

    # タイマー関連
    p_start = subparsers.add_parser("start", help="ポモドーロタイマーの開始")
    p_start.add_argument("-s", "--seconds", type=int, default=10, help="タイマーの時間(秒)")
    p_start.add_argument("-t", "--task_id", type=int, default=1, help="対応するタスクのID")

    # レポート関連
    subparsers.add_parser("summary", aliases=["stats"], help="学習時間の統計を表示")

    args = parser.parse_args()

    # コマンドの振り分け実行
    if args.command == "register":
        cmd_register(args)
    elif args.command == "login":
        cmd_login(args)
    elif args.command in ["list", "ls"]:
        cmd_list(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "done":
        cmd_done(args)
    elif args.command == "delete":
        cmd_delete(args)
    elif args.command == "start":
        cmd_start(args)
    elif args.command in ["summary", "stats"]:
        cmd_summary(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
