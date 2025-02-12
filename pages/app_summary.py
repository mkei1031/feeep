import mysql.connector
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

#MySQLに接続
conn = mysql.connector.connect(
    host = 'localhost',
    user = 'feeep_read_only',
    password = 'r44i6cebg',
    database = 'feeep',
    port='23307'
)

cursor = conn.cursor(dictionary=True)

#予約テーブル
query = """
SELECT
    rr.shop_id,
    case 
        when rr.shop_id = 13 then '渋谷駅前ビル店'
        when rr.shop_id = 14 then '上野店'
        when rr.shop_id = 15 then '秋葉原岩本町店'
        when rr.shop_id = 16 then 'ニュー新橋ビル店'
        when rr.shop_id = 17 then '新宿西口店'
        when rr.shop_id = 18 then '池袋東口店'
        when rr.shop_id = 19 then '新宿東口(新宿三丁目)店'
        when rr.shop_id = 20 then '有楽町マルイ店'
        when rr.shop_id = 21 then '学芸大学東口店'
        when rr.shop_id = 22 then '飯田橋店'
        when rr.shop_id = 23 then '銀座店'
        when rr.shop_id = 25 then '東京八重洲(日本橋)店'
    end as 店舗,
    rr.room_id,
    case
        when mr.room_type_id = 1 then 'グループ席'
        when mr.room_type_id = 2 then 'シングル席'
        when mr.room_type_id = 3 then 'オープン席'
        when mr.room_type_id = 4 then '個室グループ席'
        when mr.room_type_id = 5 then '個室シングル席'
        when mr.room_type_id = 6 then 'カウンター席'
        when mr.room_type_id = 38 then 'リラックス席'
        when mr.room_type_id = 60 then 'リラックス席'
        when mr.room_type_id = 61 then 'リラックス席'
        when mr.room_type_id between 7 and 37 then 'ワークチェア席'
        when mr.room_type_id between 40 and 47 or 53 and 59 then 'ワークチェア席'
        when mr.room_type_id between 48 and 52 then 'ワークチェア席プレミアム'
    end as 座席タイプ,
    rr.user_id as ユーザーID,
    case
        when exists(
        select 1 from t_reserve_rooms as sub
        where sub.user_id = rr.user_id
            and sub.use_start_date < rr.use_start_date
        ) then 1
        else 0
    end as リピーター,
    case 
        when exists(
        select 1 from t_reserve_rooms as sub
        where sub.user_id = rr.user_id
            and sub.use_start_date < rr.use_start_date
        ) then 0
        else 1
    end as 新規,
    rr.use_start_date as 利用開始日時,
    rr.use_end_date as 利用終了日時,
    timestampdiff(minute , rr.use_start_date , rr.use_end_date)/60 as 利用時間,
    rr.payment_price as クレカ課金額,
    rr.use_point as ポイント,
    rr.is_extended as 延長,
    rr.is_deleted as キャンセル,
    case
        when rr.is_extended = 0 and rr.is_deleted = 0 then 1
    end as 本予約,
    rr.created_at as 予約日時,
    rr.payment_price + rr.use_point as 利用料金,
    rr.package_id as パックプラン,
    t_userlists.user_id,
    t_userlists.tag_disp_name as ユーザー種別
FROM
    t_reserve_rooms as rr
LEFT JOIN
    t_userlists 
ON 
    rr.user_id = t_userlists.user_id
LEFT JOIN
    m_rooms as mr
ON
    rr.room_id = mr.room_id

"""

cursor.execute(query)
rows = cursor.fetchall()

df = pd.DataFrame(rows)
app_reservations = df[df['ユーザー種別'].isin(['ユーザー' or 'FC代理店' or 'toC営業' or '法人プラン'])]

app_reservations['利用時間'] = pd.to_numeric(app_reservations['利用時間'],errors = 'coerce')

#タイトルの見出し
st.markdown("<h2 style='text-align: center;'>アプリサマリ</h2>", unsafe_allow_html=True)
st.write('\n')

#更新ボタン
flgButton = st.button('更新')
if flgButton:
    st.write(f'更新されました',current_time)

#店舗切替ボタン
store_options = ['全体'] + list(app_reservations['店舗'].unique())
selected_store = st.selectbox('表示するデータを選択',store_options,index=0)

if selected_store == '全体':
    app_reservations = app_reservations
else:
    app_reservations = app_reservations[app_reservations['店舗']==selected_store]

#日次と月次切替ボタン
selected_time = st.radio('表示データ種別',['日次', '月次'])
st.text(selected_time)

if selected_time == '日次':
    freq = 'D'
elif selected_time == '月次':
    freq = 'ME'

#全体の集計
def all_total( data , value_col , freq ):
    app_data = data.groupby(pd.Grouper(key='利用開始日時',freq = freq))[value_col].sum().reset_index()
    if freq == 'D':
        app_data['利用開始日時'] = app_data['利用開始日時'].dt.strftime('%Y-%m-%d')
    elif freq == 'ME':
        app_data['利用開始日時'] = app_data['利用開始日時'].dt.strftime('%Y-%m')
    app_data = app_data.set_index('利用開始日時')
    return app_data

app_sales = all_total( app_reservations , '利用料金' , freq)
app_credit = all_total( app_reservations , 'クレカ課金額' , freq)
app_point = all_total( app_reservations , 'ポイント' , freq)
app_count = all_total( app_reservations , '本予約' , freq)
app_extend = all_total( app_reservations , '延長' , freq)
app_cancel = all_total(app_reservations , 'キャンセル' , freq)
app_new = all_total(app_reservations , '新規' , freq)
app_repeat = all_total(app_reservations , 'リピーター' , freq)
app_usetime = all_total(app_reservations , '利用時間' ,freq)

#座席や店舗ごとの集計
def filter_total( data , group_by , value_col , freq):
    app_data = data.groupby([pd.Grouper(key = '利用開始日時' , freq = freq),group_by])[value_col].sum().reset_index()
    if freq == 'D':
        app_data['利用開始日時'] = app_data['利用開始日時'].dt.strftime('%Y-%m-%d')
    elif freq == 'ME':
        app_data['利用開始日時'] = app_data['利用開始日時'].dt.strftime('%Y-%m')    
    app_data = app_data.pivot(index = '利用開始日時', columns = group_by, values = value_col)
    return app_data

app_store_sale = filter_total(app_reservations , '店舗','利用料金' , freq)
app_store_credit = filter_total(app_reservations , '店舗','クレカ課金額' , freq)
app_store_point = filter_total(app_reservations , '店舗','ポイント' , freq)
app_store_count = filter_total(app_reservations , '店舗','本予約' , freq)
app_store_extend = filter_total(app_reservations , '店舗','延長' , freq)
app_store_cancel = filter_total(app_reservations , '店舗','キャンセル' , freq)
app_store_new = filter_total(app_reservations , '店舗','新規' , freq)
app_store_repeat = filter_total(app_reservations , '店舗','リピーター' , freq)
app_store_usetime = filter_total(app_reservations , '店舗','利用時間' , freq)
app_seat_sale = filter_total(app_reservations , '座席タイプ','利用料金' , freq)
app_seat_credit = filter_total(app_reservations , '座席タイプ','クレカ課金額' , freq)
app_seat_point = filter_total(app_reservations , '座席タイプ','ポイント' , freq)
app_seat_count = filter_total(app_reservations , '座席タイプ','本予約' , freq)
app_seat_extend = filter_total(app_reservations , '座席タイプ','延長' , freq)
app_seat_cancel = filter_total(app_reservations , '座席タイプ','キャンセル' , freq)
app_seat_new = filter_total(app_reservations , '座席タイプ','新規' , freq)
app_seat_repeat = filter_total(app_reservations , '座席タイプ','リピーター' , freq)
app_seat_usetime = filter_total(app_reservations , '座席タイプ','利用時間' , freq)

app_list=[
    app_sales , app_credit , app_point , app_count , app_extend , app_cancel , app_new , app_repeat , app_usetime,
    app_store_sale , app_store_credit , app_store_point , app_store_count , app_store_extend , app_store_cancel ,
    app_store_new , app_store_repeat , app_store_usetime , app_seat_sale , app_seat_credit , app_seat_point ,
    app_seat_count , app_seat_extend , app_seat_cancel , app_seat_new , app_seat_repeat , app_seat_usetime
]

app_store_list = [
    app_store_sale , app_store_credit , app_store_point , app_store_count , app_store_extend , app_store_cancel,
    app_store_new , app_store_repeat , app_store_usetime
]

#グラフの作成
def graph(data,title,y_label):
    fig = go.Figure()
    if isinstance(data,list):
        for data_item in data:
            for col in data_item.columns:
                fig.add_trace(go.Scatter(
                    x = data_item.index,
                    y = data_item[col],
                    mode = 'lines +markers',
                    name = col,
                    line = dict(shape='spline' , smoothing=1.3)
                ))
    else:
        for col in data.columns:
            fig.add_trace(go.Scatter(
                x = data.index,
                y = data[col],
                mode = 'lines + markers',
                name = col,
                line = dict(shape = 'spline' , smoothing = 1.3)
            ))
    fig.update_layout(
                title = title,
                title_x = 0.5,
                xaxis_title = '日付',
                yaxis = dict(title = y_label,tickformat=',')
    )
    return fig

app_sales_list = [app_sales, app_credit , app_point]
app_count_list = [app_count, app_extend , app_cancel]
app_usertype_list = [app_new , app_repeat]

store_charts = [
    graph(app_store_sale , '店舗ごとの売上' , '金額'),
    graph(app_store_credit, '店舗ごとのクレカ課金額', '金額'),
    graph(app_store_point, '店舗ごとのポイント利用額' , '金額'),
    graph(app_store_count , '店舗ごとの予約件数' , '件数'),
    graph(app_store_usetime , '店舗ごとの利用時間' , '時間')
]

charts = [
    graph(app_sales_list , f'{selected_store}の売上' , '金額'),
    graph(app_count_list , f'{selected_store}の予約件数' , '件数'),
    graph(app_usertype_list , f'{selected_store}の新規リピーター割合' , '件数'),
    graph(app_usetime , f'{selected_store}の利用時間', '時間'),
    graph(app_seat_sale , '座席ごとの売上' , '金額'),
    graph(app_seat_credit , '座席ごとのクレカ課金額' , '金額'),
    graph(app_seat_point , '座席ごとのポイント利用額' , '金額'),
    graph(app_seat_count , '座席ごとの予約件数' , '予約件数'),
    graph(app_seat_usetime , '座席ごとの利用時間' , '利用時間'),
]

for chart in charts:
    st.plotly_chart(chart)

if selected_store == '全体':
    for chart in store_charts:
        st.plotly_chart(chart)
else:
    pass

#for app in app_list:
    st.write(app)

#for app in app_store_list:
    st.write(app)

#st.write(app_reservations)

#予実系
#日次・月次集計(全体)
    #売上(クレカ・ポイント)
    #予約件数(延長件数)
    #キャンセル件数
    #予約件数(新規リピーター)
    #利用時間
    #店舗ごとの売上
    #店舗ごとのクレカ
    #店舗ごとのポイント
    #店舗ごとの予約件数
    #店舗ごとの利用時間
    #座席ごとの売上
    #座席ごとのクレカ
    #座席ごとのポイント
    #座席ごとの予約件数
    #座席ごとの利用時間

#日次・月次集計(店舗)
    #売上(クレカ・ポイント)
    #予約件数(延長件数)
    #キャンセル件数
    #予約件数(新規リピーター)
    #利用時間
    #座席ごとの売上
    #座席ごとのクレカ
    #座席ごとのポイント
    #座席ごとの予約件数
    #座席ごとの利用時間
