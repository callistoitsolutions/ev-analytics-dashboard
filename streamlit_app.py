import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Try ETL imports
try:
    from etl.column_mapper import map_columns
    from etl.data_cleaner import clean_data
    from etl.mysql_uploader import upload_to_mysql
    HAS_ETL = True
except ImportError:
    HAS_ETL = False
    st.warning("⚠️ ETL modules not found. Using basic data processing.")

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="EV Analytics Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CSS ----------
st.markdown("""
<style>
/* Main & Sidebar styling */
.stApp { background-color: #0f1419; color: #e5e7eb; }
[data-testid="stSidebar"] { background-color: #1a1f2e; padding: 2rem 1rem; }
.stButton>button { background: linear-gradient(135deg,#3b82f6,#2563eb); color:white; border:none; border-radius:8px; padding:0.75rem 1.5rem; width:100%; }
.stButton>button:hover { transform: translateY(-2px); }
/* Metric cards */
.metric-card { background: linear-gradient(135deg,#1e293b,#334155); border-radius:12px; padding:1rem; text-align:center; color:white; height:100%; box-shadow:0 4px 6px rgba(0,0,0,0.3); }
.metric-value { font-size:2rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ---------- HELPER FUNCTION ----------
def process_data(df):
    if HAS_ETL:
        df = map_columns(df)
        df = clean_data(df)
    else:
        mapping = {
            'Vehicle_ID':'VehicleID','Battery_kWh':'BatterykWh','Range_km':'Rangekm',
            'Ex_Showroom_Price_INR':'PriceINR','Avg_Charging_Time_Hours':'ChargingTimeHours',
            'Energy_Consumed_kWh':'EnergykWh','Operating_Cost_INR':'OperatingCostINR',
            'Revenue_INR':'RevenueINR','Usage_Type':'UsageType','Customer_Location_Type':'LocationType'
        }
        df = df.rename(columns=mapping)
        if 'ProfitINR' not in df.columns:
            df['ProfitINR'] = df['RevenueINR'] - df['OperatingCostINR']
        df = df.dropna(subset=['Segment','Manufacturer'])
    return df

# ---------- SIDEBAR ----------
with st.sidebar:
    file = st.file_uploader("Upload EV Dataset (CSV / Excel)", ["csv","xlsx"])
    save_db = st.button("💾 Save to Database")

# ---------- DASHBOARD ----------
st.title("🚗 EV Analytics Dashboard")

if file:
    try:
        df = pd.read_excel(file) if file.name.endswith("xlsx") else pd.read_csv(file)
        df = process_data(df)
        
        # Filters
        segments = st.sidebar.multiselect("Segment", sorted(df["Segment"].unique()), default=list(df["Segment"].unique()))
        manufacturers = st.sidebar.multiselect("Manufacturer", sorted(df["Manufacturer"].unique()), default=list(df["Manufacturer"].unique()))
        filtered_df = df[df["Segment"].isin(segments) & df["Manufacturer"].isin(manufacturers)]
        
        # Metrics
        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Total Vehicles", f"{len(filtered_df):,}")
        col2.metric("Total Revenue", f"₹{filtered_df['RevenueINR'].sum():,.0f}")
        col3.metric("Total Profit", f"₹{filtered_df['ProfitINR'].sum():,.0f}")
        col4.metric("Avg Battery (kWh)", f"{filtered_df['BatterykWh'].mean():.1f}")
        
        # Charts
        revenue_seg = filtered_df.groupby("Segment")["RevenueINR"].sum().reset_index()
        fig1 = px.bar(revenue_seg,x="Segment",y="RevenueINR",color="Segment",text="RevenueINR")
        st.plotly_chart(fig1,use_container_width=True)
        
        battery_range = px.scatter(filtered_df,x="BatterykWh",y="Rangekm",size="RevenueINR",color="Segment",
                                   hover_data=["Manufacturer","Model"])
        st.plotly_chart(battery_range,use_container_width=True)
        
        profit_man = filtered_df.groupby("Manufacturer")["ProfitINR"].sum().sort_values(ascending=False).head(10).reset_index()
        fig3 = px.bar(profit_man,x="Manufacturer",y="ProfitINR",text="ProfitINR",color="ProfitINR",color_continuous_scale="Blues")
        st.plotly_chart(fig3,use_container_width=True)
        
        # Download
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv_data, file_name="ev_filtered.csv", mime="text/csv")
        
        # MySQL upload
        if save_db:
            if HAS_ETL:
                try:
                    upload_to_mysql(filtered_df)
                    st.success("✅ Data uploaded to MySQL successfully!")
                except Exception as e:
                    st.error(f"❌ MySQL Upload Failed: {e}")
            else:
                st.info("ℹ️ MySQL module not available. Data saved locally.")
                
    except Exception as e:
        st.error(f"❌ File processing error: {e}")
else:
    st.info("Upload a CSV or Excel file to start analytics.")
