import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# Load data
df = pd.read_excel('Fury_Friends data set_clean.xlsx', sheet_name='Sheet1')
df['Date'] = pd.to_datetime(df['Date'])  # Ensure 'Date' is datetime

st.set_page_config(page_title="Fury Friends Dashboard", layout="wide")

# Title
st.title("🐾 Fury Friends UK - Pet Store Profit Dashboard")
st.markdown("Analysis of profitability by pet type, store location, and sales performance across the UK.")

# ---------- KPI Cards ----------
total_profit = df['Profit'].sum()
total_revenue = df['Revenue'].sum()
total_cost = df['Cost'].sum()
total_units = df['Units Sld'].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💸 Total Profit", f"€{int(total_profit):,}")
col2.metric("📈 Total Revenue", f"€{int(total_revenue):,}")
col3.metric("💰 Total Cost", f"€{int(total_cost):,}")
col4.metric("📦 Units Sold", f"{int(total_units):,}")

st.markdown("---")

# ---------- View Option ----------
view_option = st.radio("🔍 Select View Mode", ("Overview", "Filtered View"), horizontal=True)

if view_option == "Filtered View":
    selected_area = st.selectbox("🏪 Select Store Area", df['Area'].unique())
    st.markdown(f"**Showing data for:** {selected_area}")
    filtered = df[df['Area'] == selected_area].copy()
else:
    filtered = df.copy()

# ---------- Date Filter ----------
min_date = filtered['Date'].min().date()
max_date = filtered['Date'].max().date()

col5, col6 = st.columns(2)
start_date = col5.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
end_date   = col6.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

filtered_time = filtered[
    (filtered['Date'].dt.date >= start_date) &
    (filtered['Date'].dt.date <= end_date)
].copy()

# ---------- Chart 1: Profit by Area and Pet ----------
profit_by_area_pet = filtered.groupby(['Area', 'Pet'])['Profit'].sum().unstack()
custom_colors = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F']

fig1 = go.Figure()
for pet, color in zip(profit_by_area_pet.columns, custom_colors):
    fig1.add_trace(go.Bar(x=profit_by_area_pet.index, y=profit_by_area_pet[pet], name=pet, marker_color=color))

fig1.update_layout(
    title='Profit by Store Location and Pet Type',
    xaxis_title='Store Area',
    yaxis_title='Total Profit (€)',
    barmode='stack',
    legend_title='Pet Type',
    template="plotly_dark"
)
st.plotly_chart(fig1, use_container_width=True)

# ---------- Chart 2: Pie Chart - Total Profit by Pet ----------
pet_profit = filtered.groupby('Pet')['Profit'].sum().sort_values(ascending=False)
fig2 = px.pie(
    pet_profit,
    names=pet_profit.index,
    values=pet_profit,
    title='💰 Total Profit Distribution by Pet Type',
    hole=0.35,
    color_discrete_sequence=custom_colors
)
fig2.update_traces(textinfo='label+percent+value', pull=[0.1]*len(pet_profit))
st.plotly_chart(fig2, use_container_width=True)

# ---------- Chart 3: Cost, Revenue, Profit Line Chart ----------
store_metrics = filtered.groupby('Area')[['Cost', 'Revenue', 'Profit']].sum().reset_index()
store_metrics.set_index('Area', inplace=True)

fig3, ax3 = plt.subplots(figsize=(12, 5))
ax3.plot(store_metrics.index, store_metrics['Cost'], marker='o', label='Cost', color='#FF6666')
ax3.plot(store_metrics.index, store_metrics['Revenue'], marker='s', label='Revenue', color='#66B2FF')
ax3.plot(store_metrics.index, store_metrics['Profit'], marker='^', label='Profit', color='#66FF66')
ax3.set_title('Cost, Revenue, and Profit by Area')
ax3.set_xlabel('Store Area')
ax3.set_ylabel('Amount (€)')
ax3.legend()
ax3.grid(True)
st.pyplot(fig3)

# ---------- Chart 4: Monthly Profit Trend ----------
monthly = (
    filtered_time
    .groupby(filtered_time['Date'].dt.to_period('M'))['Profit']
    .sum()
    .reset_index()
)
monthly['Month'] = monthly['Date'].astype(str)

fig_month = px.line(
    monthly,
    x='Month', y='Profit',
    title='📆 Monthly Profit Trend (Filtered)',
    labels={'Profit': 'Monthly Profit (€)', 'Month': 'Month'},
    template="plotly_dark"
)
st.plotly_chart(fig_month, use_container_width=True)

# ---------- Chart 5: Units Sold vs Profit - Chart Type Switch ----------
chart_type = st.radio("📊 Select Chart Type", ["Scatter Plot", "Box Plot"], horizontal=True)

if chart_type == "Scatter Plot":
    fig5 = px.scatter(filtered, x="Units Sld", y="Profit", color="Pet", title="Units Sold vs Profit", template="plotly")
else:
    fig5 = px.box(filtered, x="Pet", y="Profit", title="Profit Distribution by Pet Type", template="plotly_dark")

st.plotly_chart(fig5, use_container_width=True)

# ---------- Chart 6: Heatmap by Area and Pet ----------
heatmap_data = filtered.pivot_table(index="Area", columns="Pet", values="Profit", aggfunc="sum")

fig6, ax6 = plt.subplots(figsize=(10, 5))
sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5, ax=ax6)
ax6.set_title("💡 Heatmap: Total Profit by Store and Pet Type")
st.pyplot(fig6)

# ---------- Chart 7: Top 5 Profitable Areas ----------
top_areas = df.groupby('Area')['Profit'].sum().nlargest(5).reset_index()

fig_top_areas = px.bar(
    top_areas,
    x='Area',
    y='Profit',
    title='🏆 Top 5 Most Profitable Store Areas',
    color='Profit',
    color_continuous_scale='Viridis',
    labels={'Profit': 'Total Profit (€)'}
)
st.plotly_chart(fig_top_areas, use_container_width=True)

# ---------- Chart 8: Profit by Area for Selected Pet ----------
selected_pet = st.selectbox("🐶 Select Pet Type for Area-wise Profit", df['Pet'].unique())
pet_by_area = df[df['Pet'] == selected_pet].groupby('Area')['Profit'].sum().reset_index()

fig_pet_area = px.bar(
    pet_by_area,
    x='Area',
    y='Profit',
    title=f'Profit from {selected_pet} by Store Area',
    color='Profit',
    color_continuous_scale='Sunset'
)
st.plotly_chart(fig_pet_area, use_container_width=True)
