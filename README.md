# 🎓 University Task Dashboard Pro

大学の課題を一元管理し、提出忘れを防ぐためのタスク管理アプリケーションです。
Streamlit と Supabase を連携させ、データの永続化とリアルタイム更新を実現しています。

## 🚀 アプリを試す
[👉 デモアプリはこちらからアクセス](https://blank-app-f17wmkkv9j.streamlit.app/)

## ✨ 主な機能

- **課題のCRUD操作**: 科目名、課題名、締切日、優先度、関連URL、メモを登録・編集・削除できます。
- **優先度管理**: 課題の重要度（高・中・低）を設定し、可視化できます。
- **締切アラート**: 締切までの残り日数を自動計算し、期限が迫ると色を変えて警告します。
- **進捗の可視化**: 全体の進捗率をプログレスバーで表示し、完了時には演出が入ります。
- **詳細情報の管理**: 課題の提出ページURLや詳細なメモを保存し、必要な時にすぐにアクセスできます。

## 🛠 使用技術

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Database**: [Supabase](https://supabase.com/) (PostgreSQL)
- **Language**: Python 3.x

## 📦 データベース構成

Supabase上に `assignments` テーブルを作成し、以下のカラムを使用しています。

| カラム名 | データ型 | 説明 |
| --- | --- | --- |
| id | int8 | プライマリキー |
| subject | text | 科目名 |
| title | text | 課題名 |
| deadline | date | 締切日 |
| is_submitted | bool | 提出状態 |
| priority | text | 優先度 (高/中/低) |
| url | text | 関連URL |
| memo | text | メモ |

## 👨‍💻 開発者
蒲牟田倫朗
