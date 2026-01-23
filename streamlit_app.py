import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date

# --- 1. Supabase接続設定 ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
except FileNotFoundError:
    st.error("Secretsが見つかりません。")
    st.stop()

supabase: Client = create_client(url, key)

# ページ設定（ワイド表示）
st.set_page_config(page_title="課題管理ダッシュボード", layout="wide")

# --- 2. サイドバー：新規課題の追加 ---
with st.sidebar:
    st.header("📝 新しい課題を追加")
    with st.form("add_assignment_form", clear_on_submit=True):
        subject = st.text_input("科目名", placeholder="例: 線形代数")
        title = st.text_input("課題名", placeholder="例: 中間レポート")
        deadline = st.date_input("締切日", date.today())
        
        submitted = st.form_submit_button("追加する", use_container_width=True)

        if submitted and subject and title:
            try:
                data = {
                    "subject": subject,
                    "title": title,
                    "deadline": str(deadline),
                    "is_submitted": False
                }
                supabase.table("assignments").insert(data).execute()
                st.success("追加しました！")
                st.rerun()
            except Exception as e:
                st.error(f"エラー: {e}")

# --- 3. メイン画面：ダッシュボード ---
st.title("🎓 University Task Dashboard")

# データの取得（未完了を優先表示したいが、まずは日付順で全部取る）
try:
    response = supabase.table("assignments").select("*").order("deadline", desc=False).execute()
    all_tasks = response.data
except Exception as e:
    st.error(f"データ取得エラー: {e}")
    all_tasks = []

# 集計
if all_tasks:
    incomplete_tasks = [t for t in all_tasks if not t["is_submitted"]]
    count_incomplete = len(incomplete_tasks)
    
    # メトリクス表示
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("残りの課題", f"{count_incomplete} 件")
    
    if incomplete_tasks:
        # 直近の課題の締切を表示
        next_deadline = datetime.strptime(incomplete_tasks[0]['deadline'], '%Y-%m-%d').date()
        days_left = (next_deadline - date.today()).days
        if days_left < 0:
            col_m2.metric("直近の締切", "期限切れあり", delta="-⚠️", delta_color="inverse")
        else:
            col_m2.metric("直近の締切", f"あと {days_left} 日", delta="Fight!", delta_color="normal")
    else:
        col_m2.metric("直近の締切", "なし", delta="Perfect!")

st.divider()

# --- 4. 課題リストの表示 ---
st.subheader("課題リスト")

# フィルタリング機能
filter_option = st.radio("表示切り替え", ["全て", "未提出のみ", "提出済みのみ"], horizontal=True)

if not all_tasks:
    st.info("課題は登録されていません。サイドバーから追加してください。")
else:
    for item in all_tasks:
        # フィルタリングロジック
        if filter_option == "未提出のみ" and item["is_submitted"]:
            continue
        if filter_option == "提出済みのみ" and not item["is_submitted"]:
            continue

        # 日付計算
        deadline_date = datetime.strptime(item['deadline'], '%Y-%m-%d').date()
        today = date.today()
        days_remaining = (deadline_date - today).days

        # カード表示
        # 枠線の色を期限によって変える（st.containerには色指定がないので、絵文字で表現）
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([0.05, 0.15, 0.4, 0.2, 0.2])
            
            # チェックボックス
            is_checked = c1.checkbox("", value=item["is_submitted"], key=f"chk_{item['id']}")
            if is_checked != item["is_submitted"]:
                supabase.table("assignments").update({"is_submitted": is_checked}).eq("id", item["id"]).execute()
                st.rerun()

            # 科目
            c2.caption("Subject")
            c2.write(f"**{item['subject']}**")

            # 課題名
            c3.caption("Task")
            if item["is_submitted"]:
                c3.markdown(f"~~{item['title']}~~")
            else:
                c3.write(item["title"])

            # 期限表示ロジック
            c4.caption("Deadline")
            if item["is_submitted"]:
                c4.write(f"{item['deadline']}")
            else:
                if days_remaining < 0:
                    c4.markdown(f":red[**{item['deadline']}**]")
                elif days_remaining <= 3:
                    c4.markdown(f":orange[**{item['deadline']}**]")
                else:
                    c4.write(f"{item['deadline']}")

            # ステータスバッジ
            if item["is_submitted"]:
                c5.success("提出済")
            else:
                if days_remaining < 0:
                    c5.error(f"遅延 {abs(days_remaining)}日")
                elif days_remaining == 0:
                    c5.warning("今日締切！")
                else:
                    c5.info(f"あと {days_remaining}日")

            # 削除ボタン（Expanderに隠して誤操作防止）
            with st.expander("操作"):
                if st.button("この課題を削除", key=f"del_{item['id']}"):
                    supabase.table("assignments").delete().eq("id", item["id"]).execute()
                    st.rerun()
