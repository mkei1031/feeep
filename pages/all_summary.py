import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import datetime

#各データの読み込み
app = pd.read_csv('https://github.com/mkei1031/feeep/raw/main/app_totall.csv' , parse_dates = ['利用開始日時','利用終了日時','予約日時'])
sm = pd.read_csv('https://github.com/mkei1031/feeep/raw/main/all_SMrecords.csv' , parse_dates = ['成約日','実施日'])
ib = pd.read_csv('https://github.com/mkei1031/feeep/raw/main/all_IBrecords.csv' , parse_dates = ['申込日時','利用開始日時','利用終了日時'])
sp = pd.read_csv('https://github.com/mkei1031/feeep/raw/main/all_SPrecords.csv' , parse_dates = ['予約確定日','利用開始日時','利用終了日時'])
invoice = pd.read_csv('https://github.com/mkei1031/feeep/raw/main/invoice.csv' , parse_dates = ['利用開始日時','利用終了日時'])
#event = pd.read_csv('/Users/keimoriyama/Desktop/DB/event.csv' , parse_dates = ['利用開始日時','利用終了日時'])
ks = pd.read_csv('https://github.com/mkei1031/feeep/raw/main/ksks.csv' , parse_dates = ['利用開始日時','利用終了日時'])
shop_open = pd.read_csv('https://github.com/mkei1031/feeep/raw/main/open.csv' , parse_dates = ['利用開始日時','利用終了日時'])

sm['新規'] = (sm['新規かリピーター'] == '新規').astype(int)
sm['リピーター'] = (sm['新規かリピーター'] == 'リピーター').astype(int)
sm['本予約'] = (sm['予約タイプ'] == '本予約').astype(int)
ib['新規'] = (ib['新規かリピーター'] == '新規').astype(int)
ib['リピーター'] = (ib['新規かリピーター'] == 'リピーター').astype(int)
ib['本予約'] = (ib['ステータス'] == '予約確定').astype(int)
sp['新規'] = (sp['新規かリピーター'] == '新規').astype(int)
sp['リピーター'] = (sp['新規かリピーター'] == 'リピーター').astype(int)
sp['本予約'] = (sp['精算額（合計）'] != 0.0 ).astype(int)


#各データからキャンセルなどを削除
app_reservations = app[app['ユーザー種別'].isin(['ユーザー' or 'FC代理店' or 'toC営業'])]
app_reservations = app_reservations[app_reservations['キャンセル'] == 0]
sm_reservations = sm[sm['予約タイプ'] == '本予約']
ib_reservations = ib[ib['ステータス'] == '予約確定']
sp_reservations = sp[sp['差引合計売上金額（税込）'] != 0]

app_reservations = app_reservations.rename(columns = {'利用料金':'売上' , 'クレカ課金額':'実質売上','利用時間':'利用時間(時間)'})
sm_reservations = sm_reservations.rename(columns = {'成約日':'予約日時','実施日':'利用開始日時','施設名':'店舗','成約金額':'売上','振込予定金額':'実質売上','スペース名':'座席タイプ','利用時間':'利用時間(時間)'})
ib_reservations = ib_reservations.rename(columns = {'申込日時':'予約日時','施設名':'店舗','予約金額 (税込)':'売上','支払金額 (税込)':'実質売上','スペース名':'座席タイプ','利用時間 (時間)':'利用時間(時間)'})
sp_reservations = sp_reservations.rename(columns = {'予約確定日':'予約日時','店舗名':'店舗','差引合計売上金額（税込）':'売上','精算額（合計）':'実質売上','スペース名':'座席タイプ','利用時間（時間）':'利用時間(時間)'})

#タイトルの見出し
st.markdown("<h2 style='text-align: center;'>予実管理</h2>", unsafe_allow_html=True)
st.write('\n')

#店舗選択ボタンの作成
selected_store = st.selectbox('店舗を選択', ['全店舗' , '渋谷駅前ビル店' , '上野店' , '秋葉原岩本町店' , 'ニュー新橋ビル店' , '新宿西口店' , '池袋東口店' , '新宿東口(新宿三丁目)店', '有楽町マルイ店' , '学芸大学東口店' , '飯田橋店' , '銀座店' , '東京八重洲(日本橋)店'])

#日次と月次切替ボタン
selected_time = st.radio('表示データ種別',['月次', '日次'])
st.text(selected_time)

if selected_time == '月次':
    freq = 'ME'
elif selected_time == '日次':
    freq = 'D'

store_conditions = {
    '渋谷駅前ビル店':['渋谷'],
    '上野店':['上野'],
    '秋葉原岩本町店':['秋葉原'],
    'ニュー新橋ビル店':['新橋'],
    '新宿西口店':['新宿西口'],
    '新宿東口(新宿三丁目)店':['新宿東口'],
    '池袋東口店':['池袋'],
    '有楽町マルイ店':['有楽町'],
    '学芸大学東口店':['学芸大学'],
    '飯田橋店':['飯田橋'],
    '銀座店':['銀座'],
    '東京八重洲(日本橋)店':['八重洲']
}

if selected_store != '全店舗':
    keywords = store_conditions.get(selected_store, [selected_store])

    app_reservations = app_reservations[app_reservations['店舗'].str.contains('|'.join(keywords), na=False)]
    sm_reservations = sm_reservations[sm_reservations['店舗'].str.contains('|'.join(keywords),na=False)]
    ib_reservations = ib_reservations[ib_reservations['店舗'].str.contains('|'.join(keywords),na=False)]
    sp_reservations = sp_reservations[sp_reservations['店舗'].str.contains('|'.join(keywords),na=False)]
    invoice = invoice[invoice['店舗'].str.contains('|'.join(keywords),na=False)]
    ks = ks[ks['店舗'].str.contains('|'.join(keywords),na=False)]
    shop_open = shop_open[shop_open['店舗'].str.contains('|'.join(keywords),na=False)]


data_list = [app_reservations, sm_reservations , ib_reservations , sp_reservations , invoice , ks]
data_names = ['App' , 'SM' , 'IB' , 'SP' , '請求書' , 'KS']
data_list_normal = [app_reservations , sm_reservations , ib_reservations ,sp_reservations]

#各データの日次と月次の売上を集計
def totall(data, date , freq , value_col , agg_func):
    amount = data.groupby(pd.Grouper(key = date , freq = freq))[value_col].agg(agg_func).reset_index()
    return amount

for i, data in enumerate(data_list):
    sales = totall(data, '利用開始日時' , freq , '売上' , 'sum')
    benefit = totall(data, '利用開始日時' , freq , '実質売上' , 'sum')
    count = totall(data, '利用開始日時' , freq , '本予約' , 'sum')

    sales.columns = ['利用開始日時', f'{data_names[i]}_売上']
    benefit.columns = ['利用開始日時', f'{data_names[i]}_実質売上']
    count.columns = ['利用開始日時' , f'{data_names[i]}_予約件数']

    if i == 0:
        all_sales = sales
        all_benefit = benefit
        all_count = count
    else:
        all_sales = pd.merge(all_sales , sales , on = '利用開始日時' , how = 'outer')
        all_benefit = pd.merge(all_benefit , benefit , on = '利用開始日時' , how = 'outer')
        all_count = pd.merge(all_count , count , on = '利用開始日時' , how = 'outer')

all_sales['合計売上'] = all_sales.iloc[:,1:].sum(axis = 1)
all_benefit['合計実質売上'] = all_benefit.iloc[:,1:].sum(axis = 1)
all_count['合計予約件数'] = all_count.iloc[:,1:].sum(axis = 1)

sales_benefit = pd.merge(all_sales[['利用開始日時' , '合計売上']], all_benefit[['利用開始日時', '合計実質売上']] , on = '利用開始日時' , how = 'inner')

new_list = []
repeat_list = []

for data in data_list_normal:
    new_list.append(data[['利用開始日時' , '新規']])
    repeat_list.append(data[['利用開始日時' , 'リピーター']])

    new = pd.concat(new_list , ignore_index = True)
    repeat = pd.concat(repeat_list , ignore_index = True)

new_users = totall(new , '利用開始日時' , freq , '新規' , 'sum')
repeat_users = totall(repeat , '利用開始日時' , freq , 'リピーター' , 'sum') 

user_type = pd.merge(new_users , repeat_users , on = '利用開始日時' )

seat_sales_list= []
seat_benefit_list = []
seat_usetime_list = []
seat_count_list = []
shop_sales_list = []
shop_benefit_list = []
shop_usetime_list = []
shop_count_list = []

for data in data_list:
    seat_sales_list.append(data[['利用開始日時','座席タイプ','売上']])
    seat_benefit_list.append(data[['利用開始日時','座席タイプ','実質売上']])
    seat_usetime_list.append(data[['利用開始日時' , '座席タイプ' , '利用時間(時間)']])
    seat_count_list.append(data[['利用開始日時', '座席タイプ' , '本予約']])

    all_seat_sales = pd.concat(seat_sales_list , ignore_index = True)
    all_seat_benefit = pd.concat(seat_benefit_list , ignore_index = True)
    all_seat_usetime = pd.concat(seat_usetime_list , ignore_index = True)
    all_seat_count = pd.concat(seat_count_list , ignore_index = True)

    shop_sales_list.append(data[['利用開始日時','店舗','売上']])
    shop_benefit_list.append(data[['利用開始日時','店舗','実質売上']])
    shop_usetime_list.append(data[['利用開始日時' , '店舗' , '利用時間(時間)']])
    shop_count_list.append(data[['利用開始日時', '店舗' , '本予約']])

    all_shop_sales = pd.concat(shop_sales_list , ignore_index = True)
    all_shop_benefit = pd.concat(shop_benefit_list , ignore_index = True)
    all_shop_usetime = pd.concat(shop_usetime_list , ignore_index = True)
    all_shop_count = pd.concat(shop_count_list , ignore_index = True)

def store(data):
    data.loc[data['店舗'].str.contains('渋谷' , na = False), '店舗'] = '渋谷駅前ビル店'
    data.loc[data['店舗'].str.contains('上野' , na = False), '店舗'] = '上野店'
    data.loc[data['店舗'].str.contains('秋葉原' , na = False), '店舗'] = '秋葉原岩本町店'
    data.loc[data['店舗'].str.contains('新橋' , na = False), '店舗'] = 'ニュー新橋ビル店'
    data.loc[data['店舗'].str.contains('新宿西口' , na = False), '店舗'] = '新宿西口店'
    data.loc[data['店舗'].str.contains('池袋' , na = False), '店舗'] = '池袋東口店'
    data.loc[data['店舗'].str.contains('新宿東' , na = False), '店舗'] = '新宿東口(新宿三丁目)店'
    data.loc[data['店舗'].str.contains('有楽町' , na = False), '店舗'] = '有楽町マルイ店'
    data.loc[data['店舗'].str.contains('学芸' , na = False), '店舗'] = '学芸大学東口店'
    data.loc[data['店舗'].str.contains('飯田橋' , na = False), '店舗'] = '飯田橋店'
    data.loc[data['店舗'].str.contains('銀座' , na = False), '店舗'] = '銀座店'
    data.loc[data['店舗'].str.contains('八重洲' , na = False), '店舗'] = '東京八重洲(日本橋)店'

    return data

all_shop_sales = store(all_shop_sales)
all_shop_benefit = store(all_shop_benefit)
all_shop_usetime = store(all_shop_usetime)
all_shop_count = store(all_shop_count)

def subtotall( data, date , freq, group_by ,value_col , agg_func):
    amount = data.groupby([pd.Grouper(key = date , freq = freq ), group_by])[value_col].agg(agg_func).reset_index()
    return amount

sales_seat = subtotall(all_seat_sales, '利用開始日時' , freq , '座席タイプ' , '売上' , 'sum')
benefit_seat = subtotall(all_seat_benefit, '利用開始日時' , freq , '座席タイプ' , '実質売上' , 'sum')
usetime_seat = subtotall(all_seat_usetime, '利用開始日時' , freq , '座席タイプ' , '利用時間(時間)' , 'sum')
count_seat = subtotall(all_seat_count , '利用開始日時' , freq , '座席タイプ' , '本予約' , 'sum')
opentime = subtotall(shop_open , '利用開始日時' , freq , '座席タイプ' , '最大稼働可能時間' , 'sum')

userate = pd.merge(usetime_seat , opentime , on = ['利用開始日時' ,'座席タイプ'], how = 'left')
userate['稼働率(%)'] = (userate['利用時間(時間)']/userate['最大稼働可能時間'])*100

shop_sales = subtotall(all_shop_sales , '利用開始日時' , freq , '店舗' , '売上' , 'sum')
shop_benefit = subtotall(all_shop_benefit , '利用開始日時' , freq , '店舗' , '実質売上' , 'sum')
shop_usetime = subtotall(all_shop_usetime , '利用開始日時' , freq , '店舗' , '利用時間(時間)' , 'sum')
shop_count = subtotall(all_shop_count , '利用開始日時' , freq , '店舗' , '本予約' , 'sum')

def graph(data , title , y_label):
    fig = go.Figure()
    for i , col in enumerate(data.columns[1:]):
        fig.add_trace(go.Scatter(
            x = data['利用開始日時'],
            y = data[col], 
            mode = 'lines + markers',
            line_shape = 'spline',
            name = col
        ))
    
    if freq == 'ME':
        fig.update_xaxes(
            tickformat = '%Y-%m'
        )
    elif freq == 'D':
        fig.update_xaxes(
            tickformat = '%Y-%m-%d'
        )
    
    fig.update_yaxes(
        tickformat = ',.0f'
    )

    fig.update_layout(
        title = {
            'text' : title,
            'x' : 0.5
        },
        xaxis_title = '日付',
        yaxis_title = y_label,
        plot_bgcolor = 'white'
    )

    return fig


top_graph = graph(sales_benefit , '売上と実質売上' , '金額')
sales_graph = graph(all_sales , '媒体別の売上' , '金額')
benefit_graph = graph(all_benefit , '媒体別の実質売上' , '金額')
count_graph = graph(all_count , '媒体別の予約件数' , '予約件数')
usertype_graph = graph(user_type , '新規・リピーター予約件数' , '予約件数')

def sub_graph(data, title , y_label , y_column , column):
    fig = go.Figure()

    for seat_type in data[column].unique():
        seat_data = data[data[column] == seat_type]
        fig.add_trace(go.Scatter(
            x = seat_data['利用開始日時'],
            y = seat_data[y_column], 
            mode = 'lines + markers',
            line_shape = 'spline',
            name = str(seat_type)
        ))
    
    if freq == 'ME':
        fig.update_xaxes(
            tickformat = '%Y-%m'
        )
    elif freq == 'D':
        fig.update_xaxes(
            tickformat = '%Y-%m-%d'
        )
    
    fig.update_yaxes(
        tickformat = ',.0f'
    )

    fig.update_layout(
        title = {
            'text' : title,
            'x' : 0.5
        },
        xaxis_title = '日付',
        yaxis_title = y_label,
        plot_bgcolor = 'white'
    )

    return fig

seat_sales_graph = sub_graph(sales_seat , '座席ごとの売上' , '金額' , '売上' , '座席タイプ')
seat_benefit_graph = sub_graph(benefit_seat , '座席ごとの実質売上' , '金額' , '実質売上' , '座席タイプ')
seat_count_graph = sub_graph(count_seat , '座席ごとの予約件数' , '予約件数' , '本予約' , '座席タイプ')
seat_usetime_graph = sub_graph(usetime_seat , '座席ごとの利用時間(時間)' , '時間' , '利用時間(時間)' , '座席タイプ')
seat_userate_graph = sub_graph(userate , '座席ごとの稼働率(%)' , '割合(%)' , '稼働率(%)' , '座席タイプ')
shop_sales_graph = sub_graph(shop_sales , '店舗ごとの売上' , '金額' , '売上' , '店舗')
shop_benefit_graph = sub_graph(shop_benefit , '店舗ごとの実質売上' , '金額' , '実質売上' , '店舗')
shop_usetime_graph = sub_graph(shop_usetime , '店舗ごとの利用時間(時間)' , '時間' , '利用時間(時間)' , '店舗')
shop_count_graph = sub_graph(shop_count , '店舗ごとの予約件数' , '予約件数' , '本予約' , '店舗')


st.plotly_chart(top_graph)
if selected_store == '全店舗':
    st.plotly_chart(shop_sales_graph)
    st.plotly_chart(shop_benefit_graph)
    st.plotly_chart(shop_usetime_graph)
    st.plotly_chart(shop_count_graph)
st.plotly_chart(sales_graph)
st.plotly_chart(benefit_graph)
st.plotly_chart(count_graph)
st.plotly_chart(usertype_graph)
st.plotly_chart(seat_sales_graph)
st.plotly_chart(seat_benefit_graph)
st.plotly_chart(seat_count_graph)
st.plotly_chart(seat_usetime_graph)
st.plotly_chart(seat_userate_graph)


# for data in data_list:
#     st.write(data)

# st.write(all_sales)
# st.write(all_benefit)
# st.write(all_count)

# st.write(user_type)

# st.write(all_shop_sales)
# st.write(all_shop_benefit)
# st.write(all_shop_usetime)
# st.write(all_shop_count)

# st.write(sales_seat)
# st.write(benefit_seat)
# st.write(usetime_seat)
# st.write(count_seat)
# st.write(opentime)
# st.write(userate)

# st.write(shop_sales)
# st.write(shop_benefit)
# st.write(shop_usetime)
# st.write(shop_count)
