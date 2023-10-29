import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st
from babel.numbers import format_currency
import plotly.express as px

st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title="Abie Dashboard Shopee", page_icon="📊")

df = pd.read_csv(r'D:\abie\Coding\Analisis Data - Dicoding\all_data.csv')

def create_daily_orders_df(df):
    daily_orders_df = df.groupby('order_date').agg({
        "order_id": "nunique",
        "total_price": "sum"
    }).reset_index()

    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_price": "Revenue"
    }, inplace = True)

    return daily_orders_df

def create_sum_order_df(df) :
    sum_order_df = df.groupby('product_name').agg({
        "quantity_x": "sum"
    }).reset_index().sort_values(by = 'quantity_x', ascending = False)

    return sum_order_df

def create_by_gender(df) :
    by_gender = df.groupby('gender').agg({
        "customer_id" : "nunique",
    }).reset_index()

    by_gender.rename(columns={
        "customer_id": "Customer_count"
    }, inplace = True)

    return by_gender

def create_by_age(df) :
    by_age = df.groupby('age_group').agg({
        "customer_id" : "nunique",
    }).reset_index()

    by_age.rename(columns={
        "customer_id": "Customer_count"
    }, inplace = True)

    by_age['age_group'] = pd.Categorical(by_age['age_group'], ["Youth", "Adults", "Seniors"])
    return by_age

def create_bystate_df(df) :
    by_state = df.groupby('state').agg({
        "customer_id" : "nunique",
    }).reset_index()

    by_state.rename(columns={
        "customer_id": "Customer_count"
    }, inplace = True)

    return by_state.sort_values(by = 'Customer_count', ascending = False)

def create_rfm_df(df) :
    rfm_df= df.groupby('customer_id').agg({
        "order_date" : "max",
        "order_id" : "nunique",
        "total_price" : "sum"
    }).reset_index()

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df['max_order_timestamp'] = rfm_df['max_order_timestamp'].astype('datetime64[ns]')
    recent_date = df['order_date'].astype('datetime64[ns]').max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

datetime_columns = ['order_date', 'delivery_date']
df.sort_values(by = 'order_date', inplace = True)
df.reset_index(inplace=True)

for column in datetime_columns:
    df[column] = pd.to_datetime(df[column])

## Side Bar rentang waktu

min_date = df["order_date"].min()
max_date = df["order_date"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Flogodownload.org%2Fwp-content%2Fuploads%2F2021%2F03%2Fshopee-logo-0.png&f=1&nofb=1&ipt=dc43311dfd162585178c02845855355577ca778becc46c70b38458fa0bdcdcc9&ipo=images")

    try:
        # Mengambil start_date & end_date dari date_input
        start_date, end_date = st.date_input(
            label='Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except ValueError:
        # Penanganan kesalahan jika pengguna hanya memilih satu tanggal
        start_date = '2021/01/01'
        end_date = '2021/01/01'

    st.caption('Copyright (c) Abie 2023')


main_df = df[(df["order_date"] >= str(start_date)) & (df["order_date"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_df(main_df)
bygender_df = create_by_gender(main_df)
byage_df = create_by_age(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

st.markdown('# Shopee Collection Dashboard :sparkles:') # see #*

# Membuat header
st.header('')

st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.Revenue.sum(), "AU$", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig = px.line(daily_orders_df, x="order_date", y="order_count", markers=True, line_shape='linear', labels={"order_date": "Date", "order_count": "Total Orders"})
fig.update_traces(
    line=dict(width = 2, color = '#ff7f00'),
    marker=dict(size=7, color="#407EE6"),
    )
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Total Orders",
    xaxis_tickfont_size=15,
    yaxis_tickfont_size=15,
    width=1350,  # Atur lebar grafik
    height=400,   # Atur tinggi grafik
)

st.plotly_chart(fig)

st.markdown('# ')

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        sum_order_items_df.head(5),
        x="quantity_x",
        y="product_name",
        orientation="h",
        title="Best Performing Product",
        labels={"quantity_x": "Number of Sales",
                "product_name": "Product"},
    )
    fig1.update_xaxes(title_font=dict(size=20), tickfont=dict(size=15),range=[0, 600])
    fig1.update_yaxes(title_font=dict(size=20), tickfont=dict(size=17))
    fig1.update_layout(title_font=dict(size=30), title_x=0.35, title_y=0.95)  # Adjust title_x and title_y
    fig1.update_traces(marker_color="#26AA99")
    st.plotly_chart(fig1)


with col2:
    fig2 = px.bar(
        sum_order_items_df.sort_values(by="quantity_x", ascending=True).head(5),
        x="quantity_x",
        y="product_name",
        orientation="h",
        title="Worst Performing Product",
        labels={"quantity_x": "Number of Sales",
                "product_name": "Product"},
    )
    fig2.update_xaxes(title_font=dict(size=20), tickfont=dict(size=15), range=[0, 600])
    fig2.update_yaxes(title_font=dict(size=20), tickfont=dict(size=17))
    fig2.update_layout(title_font=dict(size=30), title_x=0.35, title_y=0.95)  # Adjust title_x and title_y
    fig2.update_traces(marker_color="#D0011B")
    st.plotly_chart(fig2)

st.markdown('# ')
st.subheader('Customer Demographics')
col1, col2,col3,col4,col5 = st.columns([1,5,2,5,1])
 
with col2:
    fig1 = px.bar(
        bygender_df.sort_values(by="Customer_count", ascending=False),
        x="gender",
        y="Customer_count",
        title="Number of Customers by Gender",
        labels={"gender": "Gender", "Customer_count": "Number of Customers"},
        color_discrete_sequence=["#0053D1"]
    )
    fig1.update_xaxes(title_font=dict(size=25), tickfont=dict(size=20))
    fig1.update_yaxes(title_font=dict(size=20), tickfont=dict(size=20))
    fig1.update_layout(
        title_font=dict(size=25),
        title_x=0.2,  # Center the title horizontally
        title_y=0.9,  # Adjust title vertical position
        width=500,      # Set the width of the chart (adjust to your preferred value)
        height=600      # Set the height of the chart (adjust to your preferred value)
    )
    st.plotly_chart(fig1)


with col4:
    fig2 = px.bar(
        byage_df.sort_values(by="age_group", ascending=False),
        x="age_group",
        y="Customer_count",
        title="Number of Customers by Age",
        labels={"age_group": "Age Group", "Customer_count": "Number of Customers"},
        color_discrete_sequence=["#0053D1"]
    )
    fig2.update_xaxes(title_font=dict(size=25), tickfont=dict(size=20))
    fig2.update_yaxes(title_font=dict(size=20), tickfont=dict(size=20))
    fig2.update_layout(
        title_font=dict(size=25),
        title_x=0.25,  # Center the title horizontally
        title_y=0.9,  # Adjust title vertical position
        width=500,    # Set the width of the chart
        height=600    # Set the height of the chart
    )
    st.plotly_chart(fig2)

bystate_df_sorted = bystate_df.sort_values(by="Customer_count", ascending=True)
max_value = bystate_df_sorted["Customer_count"].max()

fig = px.bar(
    bystate_df.sort_values(by="Customer_count", ascending=True),
    y="state",
    x="Customer_count",
    title="Number of Customers by States",
    labels={"state": "State", "Customer_count": "Number of Customers"},
)
fig.update_yaxes(title_font=dict(size=20), tickfont=dict(size=17))
fig.update_xaxes(title_font=dict(size=20), tickfont=dict(size=15))
fig.update_layout(
    title_font=dict(size=30),
    title_x=0.45,  # Center the title horizontally
    title_y=0.95,  # Adjust title vertical position
    width=1300,    # Set the width of the chart
    height=600    # Set the height of the chart
)
fig.update_traces(marker_color=["#EE4D2D" if value == max_value else "#B3B9C2" for value in bystate_df_sorted["Customer_count"]])

# Display the Plotly figure in your Streamlit app
st.plotly_chart(fig)

st.subheader("Best Customer Based on RFM Parameters")



col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AU$", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)




col1, col2, col3 = st.columns(3)



with col1:
    top_5_recency = rfm_df.sort_values(by="recency", ascending=True).head(5)
    top_5_recency['customer_id'] = top_5_recency['customer_id'].astype('str')
    top_5_recency['customer_id'] = top_5_recency['customer_id'].apply(lambda x: '‎' + x + '‎')
    fig1 = px.bar(
        top_5_recency,
        x='customer_id',
        y='recency',
        title="Top 5 Customers by Recency",
        labels={'recency': 'Recency (days'},
        color_discrete_sequence=["#26AA99"]
    )
    fig1.update_xaxes(title_font=dict(size=25), tickfont=dict(size=20))
    fig1.update_yaxes(title_font=dict(size=20), tickfont=dict(size=20))
    fig1.update_layout(
        title_font=dict(size=25),
        title_x=0.19,  # Center the title horizontally
        title_y=0.9,  # Adjust title vertical position
        width=400,    # Set the width of the chart
        height=600    # Set the height of the chart
    )
    st.plotly_chart(fig1)

with col2:
    top_5_frequency = rfm_df.sort_values(by="frequency", ascending=False).head(5)
    top_5_frequency['customer_id'] = top_5_frequency['customer_id'].astype('str')
    top_5_frequency['customer_id'] = top_5_frequency['customer_id'].apply(lambda x: '‎' + x + '‎')
    # Create a Plotly bar chart
    fig1 = px.bar(
        top_5_frequency,
        x='customer_id',
        y='frequency',
        title="Top 5 Customers by Frequency",
        labels={'frequency': 'Frequency'},
        color_discrete_sequence=["#26AA99"]
    )

    # Customize the layout and appearance of the chart
    fig1.update_xaxes(title_font=dict(size=25), tickfont=dict(size=20))
    fig1.update_yaxes(title_font=dict(size=20), tickfont=dict(size=20))
    fig1.update_layout(
        title_font=dict(size=25),
        title_x=0.14,  # Center the title horizontally
        title_y=0.9,  # Adjust title vertical position
        width=400,    # Set the width of the chart
        height=600    # Set the height of the chart
    )
    st.plotly_chart(fig1)

with col3:
    top_5_monetary = rfm_df.sort_values(by="monetary", ascending=False).head(5)
    top_5_monetary['customer_id'] = top_5_monetary['customer_id'].astype('str')
    top_5_monetary['customer_id'] = top_5_monetary['customer_id'].apply(lambda x: '‎' + x + '‎')
    fig1 = px.bar(
        top_5_monetary,
        x='customer_id',
        y='monetary',
        title="Top 5 Customers by Monetary Value",
        labels={'monetary': 'Monetary Value'},
        color_discrete_sequence=["#26AA99"]
    )

    # Customize the layout and appearance of the chart
    fig1.update_xaxes(title_font=dict(size=25), tickfont=dict(size=20))
    fig1.update_yaxes(title_font=dict(size=20), tickfont=dict(size=20))
    fig1.update_layout(
        title_font=dict(size=25),
        title_x=0.18,  # Center the title horizontally
        title_y=0.9,  # Adjust title vertical position
        width=400,    # Set the width of the chart
        height=600    # Set the height of the chart
    )
    st.plotly_chart(fig1)


st.caption('Copyright (c) Abie 2023')
