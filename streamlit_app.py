import streamlit as st
from supabase import create_client, Client
import datetime

# --- 1. Supabase接続設定 ---
try:
    url = st.secrets["https://wbxwedzdmyhvlayfobmx.supabase.co"]
    key = st.secrets["sb_publishable_Qz2OZH2PYWoS8oUnLxaY-g_iIhCXsZg"]
except FileNotFoundError:
    st.error("Secretsが見つかりません。Streamlit Cloudの設定を確認してください。")
    st.stop()

supabase: Client = create_client(url, key)

# --- 2. アプリのUIレイアウト ---
st.title("🎓 大学課題管理アプリ")
st.markdown("締め切りを守って単位を取得しましょう！")

# --- 3. 新規課題の追加フォーム ---
with st.form("add_assignment_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("科目名 (例: 統計学)")
    with col2:
        deadline = st.date_input("締切日", datetime.date.today())
    
    title = st.text_input("課題の内容 (例: 第3回レポート)")
    
    submitted = st.form_submit_button("課題を追加する")

    if submitted and subject and title:
        try:
            # データを辞書型で準備 (日付は文字列に変換して送信)
            data = {
                "subject": subject,
                "title": title,
                "deadline": str(deadline),
                "is_submitted": False
            }
            supabase.table("assignments").insert(data).execute()
            st.success(f"「{subject}」の課題を追加しました！")
            st.rerun()
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# --- 4. 課題一覧の表示 ---
st.subheader("📋 提出待ち・完了した課題")

# 締切日が近い順（昇順）でデータを取得
try:
    response = supabase.table("assignments").select("*").order("deadline", desc=False).execute()
    assignments = response.data
except Exception as e:
    st.error(f"データ取得エラー: {e}")
    assignments = []

if not assignments:
    st.info("現在、登録されている課題はありません。")
else:
    for item in assignments:
        # カードのような見た目で表示
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([0.1, 0.2, 0.5, 0.2])
            
            # 1. 提出済みチェックボックス
            is_checked = c1.checkbox("", value=item["is_submitted"], key=f"chk_{item['id']}")
            
            # チェック状態が変わったらDB更新
            if is_checked != item["is_submitted"]:
                supabase.table("assignments").update({"is_submitted": is_checked}).eq("id", item["id"]).execute()
                st.rerun()

            # 2. 表示内容（提出済みなら取り消し線）
            display_text = f"**{item['subject']}**: {item['title']}"
            display_date = f"締切: {item['deadline']}"
            
            if item["is_submitted"]:
                c2.markdown(f"~~{display_date}~~")
                c3.markdown(f"~~{display_text}~~")
                c3.caption("提出済み 🎉")
            else:
                # 締切が今日より前（遅延）なら赤字にする装飾
                deadline_date = datetime.datetime.strptime(item['deadline'], '%Y-%m-%d').date()
                if deadline_date < datetime.date.today():
                    c2.markdown(f":red[**{display_date}**]")
                else:
                    c2.markdown(f"**{display_date}**")
                c3.markdown(display_text)

            # 3. 削除ボタン
            if c4.button("削除", key=f"del_{item['id']}"):
                supabase.table("assignments").delete().eq("id", item["id"]).execute()
                st.rerun()
