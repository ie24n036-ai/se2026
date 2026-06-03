# TaskFlow — 課題管理アプリ

シンプルで使いやすい課題管理アプリです。

## 構成

```
taskapp/
├── app.py              # Flask バックエンド
├── requirements.txt    # 依存パッケージ
├── tasks.db            # SQLite データベース（自動生成）
└── templates/
    ├── base.html       # 共通テンプレート
    ├── login.html      # ログイン画面
    ├── tasks.html      # 課題一覧画面
    └── add_task.html   # 課題追加画面
```

## セットアップ・起動方法

### 1. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

### 2. アプリを起動

```bash
python app.py
```

### 3. ブラウザでアクセス

```
http://localhost:5000
```

## デモアカウント

| ユーザー名 | パスワード |
|-----------|----------|
| admin     | password |
| user      | 1234     |

## 機能

- ログイン / ログアウト
- 課題の一覧表示（完了率をプログレスバーで表示）
- 課題の追加（課題名・締切日）
- 課題の完了切替（チェックボタン）
- 課題の削除
- 期限超過・本日締切の色分け表示

## 技術スタック

- **フロントエンド**: HTML / CSS（Jinja2 テンプレート）
- **バックエンド**: Python / Flask
- **データベース**: SQLite
