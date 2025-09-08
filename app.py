import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv("walmart_clean_data.csv")

# Ensure date is in datetime format
df["date"] = pd.to_datetime(df["date"])

# Title
st.title("📊 Walmart Sales Dashboard")

# Sidebar filters
st.sidebar.header("Filter Options")

branch = st.sidebar.selectbox("Select Branch", df["Branch"].unique(), key="branch_filter")
city = st.sidebar.selectbox("Select City", df["City"].unique(), key="city_filter")
payment = st.sidebar.multiselect(
    "Select Payment Method",
    df["payment_method"].unique(),
    default=df["payment_method"].unique(),
    key="payment_filter"
)

# ---- Date Range Filter ----
min_date = df["date"].min()
max_date = df["date"].max()
date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Apply filters
filtered_df = df[
    (df["Branch"] == branch) &
    (df["City"] == city) &
    (df["payment_method"].isin(payment)) &
    (df["date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

st.subheader(f"Filtered Data (Branch: {branch}, City: {city}, Date Range: {date_range[0]} → {date_range[1]})")
st.write(filtered_df.head())

# ---- Sales by Category ----
category_sales = filtered_df.groupby("category")["total"].sum().reset_index().sort_values("total", ascending=False)

fig1 = px.bar(
    category_sales,
    x="category",
    y="total",
    title="💰 Sales by Category",
    color="total"
)
st.plotly_chart(fig1, use_container_width=True)

# ---- Sales by Payment Method ----
payment_sales = filtered_df.groupby("payment_method")["total"].sum().reset_index().sort_values("total", ascending=False)

fig2 = px.pie(
    payment_sales,
    names="payment_method",
    values="total",
    title="💳 Sales Distribution by Payment Method"
)
st.plotly_chart(fig2, use_container_width=True)

# ---- Sales by Branch ----
branch_sales = df.groupby("Branch")["total"].sum().reset_index().sort_values("total", ascending=False)

fig3 = px.bar(
    branch_sales,
    x="Branch",
    y="total",
    title="🏬 Total Sales by Branch",
    color="total"
)
st.plotly_chart(fig3, use_container_width=True)

# ---- Average Rating by Category ----
avg_rating = filtered_df.groupby("category")["rating"].mean().reset_index().sort_values("rating", ascending=False)

fig4 = px.bar(
    avg_rating,
    x="category",
    y="rating",
    title="⭐ Average Rating by Category",
    color="rating"
)
st.plotly_chart(fig4, use_container_width=True)

# ---- Sales Trend (Daily or Monthly) ----
st.subheader("📅 Sales Trend Over Time")
trend_option = st.radio("View Sales Trend By:", ["Daily", "Monthly"], horizontal=True)

if trend_option == "Daily":
    sales_trend = filtered_df.groupby("date")["total"].sum().reset_index()
    fig5 = px.line(
        sales_trend,
        x="date",
        y="total",
        title="📈 Daily Sales Trend",
        markers=True
    )
    st.plotly_chart(fig5, use_container_width=True)

else:  # Monthly trend
    filtered_df["month"] = filtered_df["date"].dt.to_period("M").astype(str)
    monthly_sales = filtered_df.groupby("month")["total"].sum().reset_index()
    fig6 = px.line(
        monthly_sales,
        x="month",
        y="total",
        title="📈 Monthly Sales Trend",
        markers=True
    )
    st.plotly_chart(fig6, use_container_width=True)

# ---- Summary KPIs ----
st.subheader("📌 Key Performance Indicators")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Sales", f"${filtered_df['total'].sum():,.2f}")

with col2:
    st.metric("Average Rating", round(filtered_df["rating"].mean(), 2))

with col3:
    st.metric("Total Quantity Sold", int(filtered_df["quantity"].sum()))
