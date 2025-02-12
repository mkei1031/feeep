import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import plotly.express as px
import plotly.graph_objects as go
import datetime

current_time = datetime.datetime.now()
current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')

#インスタベースの全データを読み込む
url = 'https://github.com/mkei1031/feeep_sm/raw/main/all_IBrecords.csv'
df = pd.read_csv(url,parse_dates=['利用開始日時','利用終了日時','申込日時'])

#インスタベースのデータからキャンセルを省く
ib_reservations = df[df['ステータス']=='予約確定']

#タイトルの見出し
st.markdown("<h2 style='text-align: center;'>インスタベースサマリ</h2>", unsafe_allow_html=True)
st.write('\n')

#更新ボタン
flgButton = st.button('更新')
if flgButton:
    st.write(f'更新されました',current_time)

#店舗切替ボタン
store_options = ['全体'] + list(ib_reservations['施設名'].unique())
selected_store = st.selectbox('表示するデータを選択',store_options,index=0)

if selected_store == '全体':
    ib_reservations = ib_reservations
else:
    ib_reservations = ib_reservations[ib_reservations['施設名']==selected_store]

#日次と月次切替ボタン
selected_time = st.radio('表示データ種別',['日次', '月次'])
st.text(selected_time)

if selected_time == '日次':
    freq = 'D'
elif selected_time == '月次':
    freq = 'ME'


#全体の集計(フィルタなし)
def total( data , value_col , freq , agg_func):
    if agg_func == 'size':
        ib_data = data.groupby(pd.Grouper(key='利用開始日時', freq=freq)).size().reset_index(name='予約件数')
    else:
        ib_data = data.groupby(pd.Grouper(key='利用開始日時', freq=freq))[value_col].agg(agg_func).reset_index()
    if freq == 'D':
        ib_data['利用開始日時'] = ib_data['利用開始日時'].dt.strftime('%Y-%m-%d')
    elif freq == 'ME':
        ib_data['利用開始日時'] = ib_data['利用開始日時'].dt.strftime('%Y-%m')
    ib_data = ib_data.set_index('利用開始日時')
    return ib_data

ib_sale = total(ib_reservations , '予約金額 (税込)', freq,'sum')
ib_benefit = total(ib_reservations , '支払金額 (税込)', freq ,'sum')
ib_count = total(ib_reservations , None ,freq ,'size')
ib_usetime = total(ib_reservations, '利用時間 (時間)', freq,'sum')

#全体の集計(フィルタあり)
def filter_total(data , group_by , value_col , freq , agg_func):
    if agg_func == 'size':
        ib_data = data.groupby([pd.Grouper(key= '利用開始日時',freq= freq),group_by]).agg(agg_func).reset_index(name = '予約件数')
        if freq == 'D':
            ib_data['利用開始日時'] = ib_data['利用開始日時'].dt.strftime('%Y-%m-%d')
        elif freq == 'ME':
            ib_data['利用開始日時'] = ib_data['利用開始日時'].dt.strftime('%Y-%m')
        ib_data = ib_data.pivot(index= '利用開始日時', columns = group_by , values= '予約件数')
    else:
        ib_data = data.groupby([pd.Grouper(key='利用開始日時',freq=freq),group_by])[value_col].agg(agg_func).reset_index()
        if freq == 'D':
            ib_data['利用開始日時'] = ib_data['利用開始日時'].dt.strftime('%Y-%m-%d')
        elif freq == 'ME':
            ib_data['利用開始日時'] = ib_data['利用開始日時'].dt.strftime('%Y-%m')
        ib_data = ib_data.pivot(index= '利用開始日時', columns = group_by , values= value_col)
    return ib_data

ib_store_sale = filter_total(ib_reservations , '施設名' , '予約金額 (税込)' , freq ,'sum')
ib_store_benefit = filter_total(ib_reservations, '施設名','支払金額 (税込)',freq,'sum')
ib_seat_sale = filter_total(ib_reservations , 'スペース名' , '予約金額 (税込)' , freq ,'sum')
ib_store_count = filter_total(ib_reservations , '施設名' , None , freq , 'size')
ib_seat_count = filter_total(ib_reservations , 'スペース名' , None , freq , 'size')
ib_store_usetime = filter_total(ib_reservations , '施設名' , '利用時間 (時間)' , freq ,'sum')
ib_seat_usetime = filter_total(ib_reservations , 'スペース名' , '利用時間 (時間)' , freq ,'sum')
ib_usertype = filter_total(ib_reservations , '新規かリピーター',None,freq,'size')

def graph(data,title,y_label):
    data.index = pd.to_datetime(data.index)
    fig = go.Figure()
    for col in data.columns:
        fig.add_trace(go.Scatter(
            x = data.index,
            y = data[col],
            mode = 'lines+markers',
            name = col,
            line = dict(shape='spline' , smoothing=1.3)
        ))
    fig.update_layout(
        title = title,
        title_x = 0.5,
        xaxis_title = '日付',
        yaxis = dict(title = y_label,tickformat=',')
    )
    return fig

#全店舗の集計グラフ
all_charts = [
    graph(ib_sale, '全体の売上','金額'),
    graph(ib_benefit , '全体の収益','金額'),
    graph(ib_count,'全体の予約件数','件数'),
    graph(ib_usetime, '全体の利用時間 (時間)','時間')
]

if selected_store == '全体':
    for chart in all_charts:
        st.plotly_chart(chart)
        st.divider()
else:
    pass

charts = [
    graph(ib_store_sale,f'{selected_store}の売上','金額'),
    graph(ib_store_benefit,f'{selected_store}の収益','金額'),
    graph(ib_store_count,f'{selected_store}の予約件数','件数'),
    graph(ib_store_usetime,f'{selected_store}の利用時間','時間'),
    graph(ib_seat_sale,'座席ごとの売上','金額'),
    graph(ib_seat_count, '座席ごとの予約件数' , '件数'),
    graph(ib_seat_usetime, '座席ごとの利用時間' , '時間'),
    graph(ib_usertype, '新規リピーター件数' , '件数'),
]

for chart in charts:
    st.plotly_chart(chart)
    st.divider()
