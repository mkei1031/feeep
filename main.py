import streamlit as st

st.set_page_config(page_title='FEEEPレポート')

# 他のページへのリンクを作成
st.sidebar.title('目次')
pages = {
    '予実管理',
    'アプリサマリ',
    'スペースマーケットサマリ',
    'インスタベースサマリ',
    'スペイシーサマリ'
}

#page = st.sidebar.radio("ページを選んでください", list(pages))
# if page == 'アプリサマリ':
#     st.write("app_summary.py の内容が表示されます")
#     # app_summary.pyのインポートを行う場合もあります
# elif page == "スペースマーケットサマリ":
#     st.write("SM_summary.py の内容が表示されます")
#     # SM_summary.pyのインポートを行う場合もあります

st.write("左のサイドバーからページを選択してください。")
st.wirte("all summary : アプリ・外部PFの統合データ")
st.write("app summary : アプリデータ")
st.write("IB summary : インスタベースデータ")
st.write("SM summary : スペースマーケットデータ")
st.write("SP summary : スペイシーデータ")
