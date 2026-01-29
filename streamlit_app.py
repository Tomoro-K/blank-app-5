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

# ページ設定
st.set_page_config(page_title="課題管理Pro", layout="wide")

# --- 2. サイドバー：新規課題の追加 ---
with st.sidebar:
    st.header("📝 新しい課題を追加")
    with st.form("add_assignment_form", clear_on_submit=True):
        subject = st.text_input("科目名", placeholder="例: 線形代数")
        title = st.text_input("課題名", placeholder="例: 中間レポート")
        deadline = st.date_input("締切日", date.today())
        
        # === 追加機能: 優先度・URL・メモ ===
        priority = st.selectbox("優先度", ["高", "中", "低"], index=1)
        url_link = st.text_input("関連URL", placeholder="提出ページや資料のリンク")
        memo = st.text_area("メモ", placeholder="詳細や要件など")
        # ==================================

        submitted = st.form_submit_button("追加する", use_container_width=True)

        if submitted and subject and title:
            try:
                data = {
                    "subject": subject,
                    "title": title,
                    "deadline": str(deadline),
                    "is_submitted": False,
                    # 新しいカラムに対応
                    "priority": priority,
                    "url": url_link,
                    "memo": memo
                }
                supabase.table("assignments").insert(data).execute()
                st.toast("課題を追加しました！", icon="🎉") # successより控えめな通知
                st.rerun()
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- 3. メイン画面：ダッシュボード ---
st.title("🎓 University Task Dashboard Pro")

# データの取得
try:
    # 締切日が近い順に並べる
    response = supabase.table("assignments").select("*").order("deadline", desc=False).execute()
    all_tasks = response.data
except Exception as e:
    st.error(f"データ取得エラー: {e}")
    all_tasks = []

# --- 4. メトリクス表示 ---
if all_tasks:
    incomplete_tasks = [t for t in all_tasks if not t["is_submitted"]]
    
    # 優先度「高」の残数を計算
    high_priority_count = len([t for t in incomplete_tasks if t.get("priority") == "高"])
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("残りの課題", f"{len(incomplete_tasks)} 件")
    
    # 優先度「高」がある場合は警告表示
    if high_priority_count > 0:
        col_m2.metric("優先度「高」", f"{high_priority_count} 件", delta="急げ！", delta_color="inverse")
    else:
        col_m2.metric("優先度「高」", "0 件", delta="順調", delta_color="normal")

    # 直近の締切計算
    if incomplete_tasks:
        next_deadline = datetime.strptime(incomplete_tasks[0]['deadline'], '%Y-%m-%d').date()
        days_left = (next_deadline - date.today()).days
        msg = "期限切れ" if days_left < 0 else f"あと {days_left} 日"
        col_m3.metric("直近の締切", msg)

st.divider()

# --- 5. 課題リストの表示 ---
st.subheader("課題リスト")
filter_option = st.radio("表示切り替え", ["全て", "未提出のみ", "提出済みのみ"], horizontal=True)

if not all_tasks:
    st.info("課題は登録されていません。サイドバーから追加してください。")
else:
    for item in all_tasks:
        # フィルタリング
        if filter_option == "未提出のみ" and item["is_submitted"]: continue
        if filter_option == "提出済みのみ" and not item["is_submitted"]: continue

        # 日付計算
        deadline_date = datetime.strptime(item['deadline'], '%Y-%m-%d').date()
        days_remaining = (deadline_date - date.today()).days

        # カード表示
        # 優先度に応じた枠線の色の代わりに、絵文字を変える
        priority_icon = {"高": "🔴", "中": "🟡", "低": "🔵"}.get(item.get("priority", "中"), "🟡")

        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([0.05, 0.15, 0.4, 0.2, 0.2])
            
            # チェックボックス
            is_checked = c1.checkbox("", value=item["is_submitted"], key=f"chk_{item['id']}")
            if is_checked != item["is_submitted"]:
                supabase.table("assignments").update({"is_submitted": is_checked}).eq("id", item["id"]).execute()
                st.rerun()

            # 科目と優先度
            c2.caption("Subject")
            c2.write(f"{priority_icon} **{item['subject']}**")

            # 課題名
            c3.caption("Task")
            if item["is_submitted"]:
                c3.markdown(f"~~{item['title']}~~")
            else:
                c3.write(item["title"])

            # 期限
            c4.caption("Deadline")
            # 期限切れや直前は赤字/太字にする
            if not item["is_submitted"] and days_remaining <= 3:
                c4.markdown(f":red[**{item['deadline']}**]")
            else:
                c4.write(f"{item['deadline']}")

            # ステータス/アクション
            if item["is_submitted"]:
                c5.success("完了")
            else:
                if days_remaining < 0: c5.error(f"{abs(days_remaining)}日遅れ")
                elif days_remaining == 0: c5.warning("今日！")
                else: c5.info(f"あと{days_remaining}日")

            # === 詳細情報（URL, メモ, 削除ボタン）をExpanderに格納 ===
            with st.expander("詳細・操作"):
                e1, e2 = st.columns([0.8, 0.2])
                with e1:
                    # URLがあればリンク表示
                    if item.get("url"):
                        st.markdown(f"🔗 [関連リンクを開く]({item['url']})")
                    # メモがあれば表示
                    if item.get("memo"):
                        st.info(f"📝 メモ: {item['memo']}")
                    if not item.get("url") and not item.get("memo"):
                        st.caption("詳細情報はありません")
                
                with e2:
                    if st.button("削除", key=f"del_{item['id']}", type="primary"):
                        supabase.table("assignments").delete().eq("id", item["id"]).execute()
                        st.rerun()
