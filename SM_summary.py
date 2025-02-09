import streamlit as st
import pandas as pd
import numpy as np
import plotly
import datetime

current_time = datetime.datetime.now()
current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')

#スペースマーケットの全データを読み込む
url = 'https://github.com/mkei1031/feeep_sm/blob/main/all_SMrecords.csv'
df = pd.read_csv(url)

#スペースマーケットのデータからキャンセルを省く
sm_reservations = df[df['予約タイプ']=='本予約']

#タイトルの見出し
st.markdown("<h2 style='text-align: center;'>スペースマーケットサマリ</h2>", unsafe_allow_html=True)
st.write('\n')

#更新ボタン
flgButton = st.button('更新')
if flgButton:
    st.write(f'更新されました',current_time)

#店舗切替ボタン
store_options = ['全体'] + list(sm_reservations['施設名'].unique())
selected_store = st.selectbox('表示するデータを選択',store_options,index=0)

if selected_store == '全体':
    sm_reservations = sm_reservations
else:
    sm_reservations = sm_reservations[sm_reservations['施設名']==selected_store]

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
        sm_data = data.groupby(pd.Grouper(key='実施日', freq=freq)).size().reset_index(name='予約件数')
    else:
        sm_data = data.groupby(pd.Grouper(key='実施日', freq=freq))[value_col].agg(agg_func).reset_index()
    if freq == 'D':
        sm_data['実施日'] = sm_data['実施日'].dt.strftime('%Y-%m-%d')
    elif freq == 'ME':
        sm_data['実施日'] = sm_data['実施日'].dt.strftime('%Y-%m')
    sm_data = sm_data.set_index('実施日')
    return sm_data

sm_sale = total(sm_reservations , '成約金額', freq,'sum')
sm_benefit = total(sm_reservations , '振込予定金額', freq ,'sum')
sm_count = total(sm_reservations , None ,freq ,'size')
sm_usetime = total(sm_reservations, '利用時間', freq,'sum')

#全体の集計(フィルタあり)
def filter_total(data , group_by , value_col , freq , agg_func):
    if agg_func == 'size':
        sm_data = data.groupby([pd.Grouper(key= '実施日',freq= freq),group_by]).agg(agg_func).reset_index(name = '予約件数')
        if freq == 'D':
            sm_data['実施日'] = sm_data['実施日'].dt.strftime('%Y-%m-%d')
        elif freq == 'ME':
            sm_data['実施日'] = sm_data['実施日'].dt.strftime('%Y-%m')
        sm_data = sm_data.pivot(index= '実施日', columns = group_by , values= '予約件数')
    else:
        sm_data = data.groupby([pd.Grouper(key='実施日',freq=freq),group_by])[value_col].agg(agg_func).reset_index()
        if freq == 'D':
            sm_data['実施日'] = sm_data['実施日'].dt.strftime('%Y-%m-%d')
        elif freq == 'ME':
            sm_data['実施日'] = sm_data['実施日'].dt.strftime('%Y-%m')
        sm_data = sm_data.pivot(index= '実施日', columns = group_by , values= value_col)
    return sm_data

sm_store_sale = filter_total(sm_reservations , '施設名' , '成約金額' , freq ,'sum')
sm_store_benefit = filter_total(sm_reservations, '施設名','振込予定金額',freq,'sum')
sm_seat_sale = filter_total(sm_reservations , 'スペース名' , '成約金額' , freq ,'sum')
sm_store_count = filter_total(sm_reservations , '施設名' , None , freq , 'size')
sm_seat_count = filter_total(sm_reservations , 'スペース名' , None , freq , 'size')
sm_store_usetime = filter_total(sm_reservations , '施設名' , '利用時間' , freq ,'sum')
sm_seat_usetime = filter_total(sm_reservations , 'スペース名' , '利用時間' , freq ,'sum')
sm_usertype = filter_total(sm_reservations , '新規かリピーター',None,freq,'size')
sm_timing = filter_total(sm_reservations , '当日かどうか',None,freq,'size')

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
    graph(sm_sale, '全体の売上','金額'),
    graph(sm_benefit , '全体の収益','金額'),
    graph(sm_count,'全体の予約件数','件数'),
    graph(sm_usetime, '全体の利用時間','時間')
]

if selected_store == '全体':
    for chart in all_charts:
        st.plotly_chart(chart)
        st.divider()
else:
    pass

charts = [
    graph(sm_store_sale,f'{selected_store}の売上','金額'),
    graph(sm_store_benefit,f'{selected_store}の収益','金額'),
    graph(sm_store_count,f'{selected_store}の予約件数','件数'),
    graph(sm_store_usetime,f'{selected_store}の利用時間','時間'),
    graph(sm_seat_sale,'座席ごとの売上','金額'),
    graph(sm_seat_count, '座席ごとの予約件数' , '件数'),
    graph(sm_seat_usetime, '座席ごとの利用時間' , '時間'),
    graph(sm_usertype, '新規リピーター件数' , '件数'),
    graph(sm_timing, '当日予約の件数' , '件数'),
]

for chart in charts:
    st.plotly_chart(chart)
    st.divider()
