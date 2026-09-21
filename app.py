import streamlit as st
import pandas as pd
import plotly.express as px

# પેજ સેટઅપ
st.set_page_config(page_title="Customer Retention Dashboard", layout="wide")
st.title("Customer Engagement & Retention Analytics")

# ડેટા લોડ કરવો (અગાઉ આપણે જે Prepared_Bank_Data.csv સેવ કરી હતી)
@st.cache_data
def load_data():
    return pd.read_csv('Prepared_Bank_Data.csv')

df = load_data()

# સાઇડબાર ફિલ્ટર્સ (User Capabilities)
st.sidebar.header("Dashboard Filters")
selected_profile = st.sidebar.multiselect(
    "Select Engagement Profile",
    options=df['Engagement_Profile'].unique(),
    default=df['Engagement_Profile'].unique()
)

min_products, max_products = st.sidebar.slider(
    "Product Count",
    int(df['NumOfProducts'].min()),
    int(df['NumOfProducts'].max()),
    (1, 4)
)

min_balance = st.sidebar.number_input("Minimum Balance Threshold", value=0)

# ફિલ્ટર કરેલો ડેટા
filtered_df = df[
    (df['Engagement_Profile'].isin(selected_profile)) &
    (df['NumOfProducts'] >= min_products) &
    (df['NumOfProducts'] <= max_products) &
    (df['Balance'] >= min_balance)
]

# Core Modules (ચાર્ટ્સ)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Engagement vs Churn Overview")
    churn_counts = filtered_df.groupby(['Engagement_Profile', 'Exited']).size().reset_index(name='Count')
    churn_counts['Exited'] = churn_counts['Exited'].map({1: 'Churned', 0: 'Retained'})
    fig1 = px.bar(churn_counts, x='Engagement_Profile', y='Count', color='Exited', barmode='group')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Product Utilization Impact")
    prod_churn = filtered_df.groupby(['NumOfProducts', 'Exited']).size().reset_index(name='Count')
    prod_churn['Exited'] = prod_churn['Exited'].map({1: 'Churned', 0: 'Retained'})
    fig2 = px.bar(prod_churn, x='NumOfProducts', y='Count', color='Exited')
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Retention Strength Scoring Panels")
strength_churn = filtered_df.groupby('Relationship_Strength_Index')['Exited'].mean().reset_index()
fig3 = px.line(strength_churn, x='Relationship_Strength_Index', y='Exited', markers=True, title="Churn Rate by Relationship Score")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("High-Value Disengaged Customer Detector (Premium Risk)")
high_risk = df[(df['Engagement_Profile'] == 'Inactive High-Balance') & (df['Exited'] == 0)]
st.dataframe(high_risk[['CustomerId', 'Balance', 'NumOfProducts', 'Geography']].head(10))
