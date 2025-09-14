import pandas as pd

# Load CSV files
facebook = pd.read_csv('dataset/Facebook.csv')
google = pd.read_csv('dataset/Google.csv')
tiktok = pd.read_csv('dataset/TikTok.csv')
business = pd.read_csv('dataset/business.csv')

# Preview the first few rows
print(facebook.head())
print(google.head())
print(tiktok.head())
print(business.head())


# Add 'channel' column to each dataset
facebook['channel'] = 'Facebook'
google['channel'] = 'Google'
tiktok['channel'] = 'TikTok'

# Combine all marketing data
marketing = pd.concat([facebook, google, tiktok], ignore_index=True)

# Standardize column names (if needed)
marketing.columns = [col.strip().lower().replace(' ', '_') for col in marketing.columns]
business.columns = [col.strip().lower().replace(' ', '_') for col in business.columns]


# Convert 'date' columns to datetime
marketing['date'] = pd.to_datetime(marketing['date'])
business['date'] = pd.to_datetime(business['date'])

# Check date ranges
print("Marketing date range:", marketing['date'].min(), "to", marketing['date'].max())
print("Business date range:", business['date'].min(), "to", business['date'].max())


# Group marketing data by date
daily_marketing = marketing.groupby('date').agg({
    'impression': 'sum',
    'clicks': 'sum',
    'spend': 'sum',
    'attributed_revenue': 'sum'
}).reset_index()

# Merge on 'date'
merged = pd.merge(daily_marketing, business, on='date', how='inner')

# Preview merged data
print(merged.head())

# Avoid division by zero
merged['ctr'] = merged['clicks'] / merged['impression'].replace(0, pd.NA)
merged['cpc'] = merged['spend'] / merged['clicks'].replace(0, pd.NA)
merged['roas'] = merged['attributed_revenue'] / merged['spend'].replace(0, pd.NA)
merged['gross_margin_%'] = merged['gross_profit'] / merged['total_revenue'].replace(0, pd.NA) * 100
merged['spend_per_order'] = merged['spend'] / merged['#_of_orders'].replace(0, pd.NA)
merged['customer_acquisition_cost'] = merged['spend'] / merged['new_customers'].replace(0, pd.NA)

# Fill or drop missing values if needed
merged.fillna(0, inplace=True)

# Sort by date
merged.sort_values(by='date', inplace=True)

# Save cleaned data (optional)
# merged.to_csv('cleaned_data.csv', index=False)




import pandas as pd
import plotly.express as px
import streamlit as st

# Load the prepared dataset
# merged = pd.read_csv('cleaned_data.csv')
# merged['date'] = pd.to_datetime(merged['date'])

# Calculate summary metrics
total_spend = merged['spend'].sum()
total_revenue = merged['total_revenue'].sum()
total_orders = merged['#_of_orders'].sum()
avg_roas = merged['roas'].mean()

# Display KPIs
st.title("📈 Marketing Intelligence Dashboard")
st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Spend", f"${total_spend:,.0f}")
col2.metric("Total Revenue", f"${total_revenue:,.0f}")
col3.metric("Total Orders", f"{total_orders:,}")
col4.metric("Avg ROAS", f"{avg_roas:.2f}")

fig = px.line(merged, x='date', y=['spend', 'total_revenue'],
              labels={'value': 'USD', 'variable': 'Metric'},
              title="📅 Daily Spend vs Revenue")
st.plotly_chart(fig, use_container_width=True)

# Aggregate by channel
channel_summary = marketing.groupby('channel').agg({
    'spend': 'sum',
    'attributed_revenue': 'sum'
}).reset_index()
channel_summary['roas'] = channel_summary['attributed_revenue'] / channel_summary['spend']

# Bar chart
fig = px.bar(channel_summary, x='channel', y='roas',
             title="📊 ROAS by Channel", text='roas',
             labels={'roas': 'Return on Ad Spend'})
st.plotly_chart(fig, use_container_width=True)

# Optional: Add filters
selected_channel = st.selectbox("Select Channel", marketing['channel'].unique())
filtered = marketing[marketing['channel'] == selected_channel]

# Show campaign table
st.subheader(f"📋 Campaign Performance: {selected_channel}")
st.dataframe(filtered[['date', 'campaign', 'impression', 'clicks', 'spend', 'attributed_revenue']])

fig = px.scatter(merged, x='spend', y='#_of_orders',
                 trendline='ols',
                 title="🔄 Marketing Spend vs Orders")
st.plotly_chart(fig, use_container_width=True)

fig = px.line(merged, x='date', y='gross_margin_%',
              title="📈 Gross Margin Over Time")
st.plotly_chart(fig, use_container_width=True)


st.title("📊 Executive Summary")

# High-level KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${merged['total_revenue'].sum():,.0f}")
col2.metric("Total Spend", f"${merged['spend'].sum():,.0f}")
col3.metric("Avg ROAS", f"{merged['roas'].mean():.2f}")

# Strategic Insight
st.markdown("#### 💡 Insight")
st.markdown("Marketing spend is generating an average ROAS of {:.2f}. Consider reallocating budget toward channels with ROAS > 3.0.".format(merged['roas'].mean()))


st.header("📈 Campaign Optimization")

# Filters
channel = st.selectbox("Select Channel", marketing['channel'].unique(), key="channel_selectbox_1")
state = st.selectbox("Select State", marketing['state'].unique())

# Filtered data
filtered = marketing[(marketing['channel'] == channel) & (marketing['state'] == state)]

# Campaign table
st.dataframe(filtered[['date', 'campaign', 'impression', 'clicks', 'spend', 'attributed_revenue']])

# Campaign-level ROAS
campaign_roas = filtered.groupby('campaign').agg({
    'spend': 'sum',
    'attributed_revenue': 'sum'
}).reset_index()
campaign_roas['roas'] = campaign_roas['attributed_revenue'] / campaign_roas['spend']

fig = px.bar(campaign_roas, x='campaign', y='roas', title="📊 ROAS by Campaign")
st.plotly_chart(fig, use_container_width=True)


st.header("📦 Business Impact")

# Time series: Orders vs Spend
fig = px.line(merged, x='date', y=['#_of_orders', 'spend'],
              labels={'value': 'Count / USD', 'variable': 'Metric'},
              title="📅 Daily Orders vs Marketing Spend")
st.plotly_chart(fig, use_container_width=True,key="r_s_chart")

# Gross Margin Trend
fig2 = px.line(merged, x='date', y='gross_margin_%', title="📈 Gross Margin Over Time")
st.plotly_chart(fig2, use_container_width=True,key="gross_margin_chart")


st.header("💰 Budget Allocation Insights")

# Channel-level summary
channel_summary = marketing.groupby('channel').agg({
    'spend': 'sum',
    'attributed_revenue': 'sum'
}).reset_index()
channel_summary['roas'] = channel_summary['attributed_revenue'] / channel_summary['spend']

# Highlight top-performing channels
top_channels = channel_summary[channel_summary['roas'] > 3.0]

st.markdown("#### ✅ Recommended Channels")
st.dataframe(top_channels)

st.markdown("Consider shifting budget toward these high-performing channels to maximize ROI.")


# Date range filter
start_date = st.date_input("Start Date", merged['date'].min())
end_date = st.date_input("End Date", merged['date'].max())

# Apply date filter
filtered_data = merged[(merged['date'] >= pd.to_datetime(start_date)) & (merged['date'] <= pd.to_datetime(end_date))]

# Show filtered KPIs
st.metric("Filtered Revenue", f"${filtered_data['total_revenue'].sum():,.0f}")
st.metric("Filtered Spend", f"${filtered_data['spend'].sum():,.0f}")




