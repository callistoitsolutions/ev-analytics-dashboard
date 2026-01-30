import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Try to import ETL modules, but provide fallback if they don't exist
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

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f1419;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1f2e;
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e5e7eb;
    }
    
    /* Sidebar header */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f9fafb;
        font-weight: 600;
    }
    
    /* File uploader button */
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }
    
    /* Main content area */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 100%;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f9fafb !important;
        font-weight: 600 !important;
    }
    
    /* Metric cards container */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #94a3b8;
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        color: #f9fafb;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
    }
    
    /* Chart containers */
    .chart-container {
        background: #1a1f2e;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .chart-title {
        color: #f9fafb;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(59, 130, 246, 0.3);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: #1a1f2e;
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Multiselect */
    .stMultiSelect [data-baseweb="select"] {
        background-color: #334155;
        border-radius: 8px;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #3b82f6;
        color: white;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #334155;
        border-radius: 8px;
        padding: 1rem;
        border: 2px dashed rgba(59, 130, 246, 0.3);
    }
    
    /* Info box */
    .stAlert {
        background-color: #1e293b;
        color: #e5e7eb;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1);
        margin: 1.5rem 0;
    }
    
    /* Success message */
    .stSuccess {
        background-color: #166534;
        color: #dcfce7;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- HELPER FUNCTIONS ----------
def process_data(df):
    """Process the uploaded data - handles both ETL and direct processing"""
    
    if HAS_ETL:
        # Use ETL modules if available
        df = map_columns(df)
        df = clean_data(df)
    else:
        # Direct processing as fallback
        # Standardize column names (remove underscores for consistency)
        column_mapping = {
            'Vehicle_ID': 'VehicleID',
            'Battery_kWh': 'BatterykWh',
            'Range_km': 'Rangekm',
            'Ex_Showroom_Price_INR': 'PriceINR',
            'Avg_Charging_Time_Hours': 'ChargingTimeHours',
            'Energy_Consumed_kWh': 'EnergykWh',
            'Operating_Cost_INR': 'OperatingCostINR',
            'Revenue_INR': 'RevenueINR',
            'Usage_Type': 'UsageType',
            'Customer_Location_Type': 'LocationType'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Calculate Profit if not present
        if 'ProfitINR' not in df.columns:
            df['ProfitINR'] = df['RevenueINR'] - df['OperatingCostINR']
        
        # Clean data
        df = df.dropna(subset=['Segment', 'Manufacturer'])
        
    return df

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### 📤 Upload & Filters")
    file = st.file_uploader("Upload EV Dataset (CSV / Excel)", ["csv", "xlsx"], label_visibility="collapsed")
    
    st.markdown("---")
    
    st.markdown("### 🎯 Filter Options")
    segment_filter = st.multiselect("Select Segment", [], key="segment")
    manufacturer_filter = st.multiselect("Select Manufacturer", [], key="manufacturer")
    
    st.markdown("---")
    
    save_db = st.button("💾 Save to Database", use_container_width=True)

# ---------- MAIN DASHBOARD ----------
st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1 style='color: #f9fafb; font-size: 2.5rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem;'>
            🚗 Electric Vehicle Analytics Dashboard
        </h1>
        <p style='color: #94a3b8; font-size: 1.125rem; margin: 0;'>
            Dynamic analytics for EV datasets with live database integration.
        </p>
    </div>
""", unsafe_allow_html=True)

if file:
    try:
        # Load dataset
        df = pd.read_excel(file) if file.name.endswith("xlsx") else pd.read_csv(file)
        
        # Process data through ETL or direct processing
        df = process_data(df)

        # Update sidebar filters dynamically
        segment_filter = st.sidebar.multiselect(
            "Select Segment", 
            sorted(df["Segment"].unique()), 
            default=list(df["Segment"].unique()),
            key="segment_update"
        )
        manufacturer_filter = st.sidebar.multiselect(
            "Select Manufacturer", 
            sorted(df["Manufacturer"].unique()), 
            default=list(df["Manufacturer"].unique()),
            key="manufacturer_update"
        )

        # Apply filters
        filtered_df = df[df["Segment"].isin(segment_filter) & df["Manufacturer"].isin(manufacturer_filter)]

        # Upload to MySQL
        if save_db:
            if HAS_ETL:
                try:
                    upload_to_mysql(filtered_df)
                    st.sidebar.success("✅ Data uploaded successfully to MySQL!")
                except Exception as e:
                    st.sidebar.error(f"❌ Error uploading to database: {str(e)}")
            else:
                st.sidebar.info("ℹ️ Database module not available. Data saved locally.")

        # ---------- METRIC CARDS ----------
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-icon'>🚗</div>
                    <div class='metric-label'>Total Vehicles</div>
                    <div class='metric-value'>{len(filtered_df):,}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_revenue = filtered_df['RevenueINR'].sum()
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-icon'>₹</div>
                    <div class='metric-label'>Total Revenue</div>
                    <div class='metric-value'>₹{total_revenue/1000000:.1f}M</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_profit = filtered_df['ProfitINR'].sum()
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-icon'>💰</div>
                    <div class='metric-label'>Total Profit</div>
                    <div class='metric-value'>₹{total_profit/1000000:.1f}M</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_battery = filtered_df['BatterykWh'].mean()
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-icon'>🔋</div>
                    <div class='metric-label'>Average Battery kWh</div>
                    <div class='metric-value'>{avg_battery:.1f} kWh</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ---------- CHARTS ROW 1 ----------
        st.markdown("<div class='chart-title'>Revenue Distribution Across Segments</div>", unsafe_allow_html=True)
        
        revenue_by_segment = filtered_df.groupby("Segment")["RevenueINR"].sum().reset_index()
        revenue_by_segment = revenue_by_segment.sort_values('RevenueINR', ascending=False)
        
        fig1 = px.bar(
            revenue_by_segment, 
            x="Segment", 
            y="RevenueINR",
            color="Segment",
            text="RevenueINR",
            labels={"RevenueINR": "Revenue (₹)", "Segment": "Vehicle Segment"},
            color_discrete_sequence=["#ef4444", "#f59e0b", "#10b981", "#3b82f6", "#8b5cf6"]
        )
        fig1.update_traces(
            texttemplate="₹%{text:,.0f}", 
            textposition="outside",
            textfont=dict(size=12, color='white')
        )
        fig1.update_layout(
            plot_bgcolor='#0f1419',
            paper_bgcolor='#0f1419',
            font=dict(color='#e5e7eb'),
            xaxis=dict(showgrid=False, color='#e5e7eb'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='#e5e7eb'),
            showlegend=False,
            margin=dict(t=20, l=0, r=0, b=0),
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)

        # ---------- CHARTS ROW 2 ----------
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("<div class='chart-title'>Battery Capacity vs Range</div>", unsafe_allow_html=True)
            fig2 = px.scatter(
                filtered_df, 
                x="BatterykWh", 
                y="Rangekm",
                size="RevenueINR", 
                color="Segment",
                hover_data=["Manufacturer", "Model"],
                labels={"BatterykWh": "Battery (kWh)", "Rangekm": "Range (km)"},
                color_discrete_sequence=["#ef4444", "#f59e0b", "#10b981", "#3b82f6", "#8b5cf6"]
            )
            fig2.update_layout(
                plot_bgcolor='#0f1419',
                paper_bgcolor='#0f1419',
                font=dict(color='#e5e7eb'),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='#e5e7eb'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='#e5e7eb'),
                legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#e5e7eb')),
                margin=dict(t=20, l=0, r=0, b=0),
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col_right:
            st.markdown("<div class='chart-title'>Profit by Manufacturer</div>", unsafe_allow_html=True)
            top_manufacturers = filtered_df.groupby("Manufacturer")["ProfitINR"].sum().sort_values(ascending=False).head(10).reset_index()
            
            fig3 = px.bar(
                top_manufacturers, 
                x="Manufacturer", 
                y="ProfitINR",
                text="ProfitINR",
                labels={"ProfitINR": "Profit (₹)", "Manufacturer": "Manufacturer"},
                color="ProfitINR",
                color_continuous_scale=["#1e3a8a", "#3b82f6", "#60a5fa"]
            )
            fig3.update_traces(
                texttemplate="₹%{text:,.0f}", 
                textposition="outside",
                textfont=dict(size=11, color='white')
            )
            fig3.update_layout(
                plot_bgcolor='#0f1419',
                paper_bgcolor='#0f1419',
                font=dict(color='#e5e7eb'),
                xaxis=dict(showgrid=False, color='#e5e7eb', tickangle=-45),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='#e5e7eb'),
                showlegend=False,
                margin=dict(t=20, l=0, r=0, b=60),
                height=400
            )
            st.plotly_chart(fig3, use_container_width=True)

        # ---------- ADDITIONAL INSIGHTS ----------
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
        
        with col_metrics1:
            st.markdown("<div class='chart-title'>Usage Type Distribution</div>", unsafe_allow_html=True)
            if 'UsageType' in filtered_df.columns:
                usage_data = filtered_df.groupby('UsageType').size().reset_index(name='Count')
                fig4 = px.pie(
                    usage_data,
                    values='Count',
                    names='UsageType',
                    color_discrete_sequence=["#ef4444", "#f59e0b", "#10b981", "#3b82f6"]
                )
                fig4.update_layout(
                    plot_bgcolor='#0f1419',
                    paper_bgcolor='#0f1419',
                    font=dict(color='#e5e7eb'),
                    showlegend=True,
                    height=300,
                    margin=dict(t=20, l=0, r=0, b=0)
                )
                st.plotly_chart(fig4, use_container_width=True)
        
        with col_metrics2:
            st.markdown("<div class='chart-title'>Average Charging Time</div>", unsafe_allow_html=True)
            if 'ChargingTimeHours' in filtered_df.columns:
                charging_by_segment = filtered_df.groupby('Segment')['ChargingTimeHours'].mean().reset_index()
                fig5 = px.bar(
                    charging_by_segment,
                    x='Segment',
                    y='ChargingTimeHours',
                    color='Segment',
                    labels={'ChargingTimeHours': 'Hours'},
                    color_discrete_sequence=["#ef4444", "#f59e0b", "#10b981", "#3b82f6"]
                )
                fig5.update_layout(
                    plot_bgcolor='#0f1419',
                    paper_bgcolor='#0f1419',
                    font=dict(color='#e5e7eb'),
                    showlegend=False,
                    height=300,
                    margin=dict(t=20, l=0, r=0, b=0)
                )
                st.plotly_chart(fig5, use_container_width=True)
        
        with col_metrics3:
            st.markdown("<div class='chart-title'>Energy Consumption</div>", unsafe_allow_html=True)
            if 'EnergykWh' in filtered_df.columns:
                energy_by_segment = filtered_df.groupby('Segment')['EnergykWh'].mean().reset_index()
                fig6 = px.bar(
                    energy_by_segment,
                    x='Segment',
                    y='EnergykWh',
                    color='Segment',
                    labels={'EnergykWh': 'kWh'},
                    color_discrete_sequence=["#ef4444", "#f59e0b", "#10b981", "#3b82f6"]
                )
                fig6.update_layout(
                    plot_bgcolor='#0f1419',
                    paper_bgcolor='#0f1419',
                    font=dict(color='#e5e7eb'),
                    showlegend=False,
                    height=300,
                    margin=dict(t=20, l=0, r=0, b=0)
                )
                st.plotly_chart(fig6, use_container_width=True)

        # ---------- RAW DATA ----------
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='chart-title'>Raw Data</div>", unsafe_allow_html=True)
        st.dataframe(
            filtered_df.reset_index(drop=True), 
            height=350,
            use_container_width=True
        )
        
        # ---------- DOWNLOAD OPTION ----------
        st.markdown("<br>", unsafe_allow_html=True)
        col_download1, col_download2 = st.columns(2)
        
        with col_download1:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Filtered Data as CSV",
                data=csv,
                file_name='ev_filtered_data.csv',
                mime='text/csv',
            )
        
        with col_download2:
            # Create summary statistics
            summary = pd.DataFrame({
                'Metric': ['Total Vehicles', 'Total Revenue (₹)', 'Total Profit (₹)', 'Avg Battery (kWh)', 'Avg Range (km)'],
                'Value': [
                    len(filtered_df),
                    f"₹{filtered_df['RevenueINR'].sum():,.0f}",
                    f"₹{filtered_df['ProfitINR'].sum():,.0f}",
                    f"{filtered_df['BatterykWh'].mean():.1f}",
                    f"{filtered_df['Rangekm'].mean():.1f}"
                ]
            })
            summary_csv = summary.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Download Summary Report",
                data=summary_csv,
                file_name='ev_summary_report.csv',
                mime='text/csv',
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.error("Please make sure your Excel file has the required columns:")
        st.code("""
Required columns:
- Vehicle_ID or VehicleID
- Manufacturer
- Model
- Segment
- Battery_kWh or BatterykWh
- Range_km or Rangekm
- Revenue_INR or RevenueINR
- Operating_Cost_INR or OperatingCostINR
        """)

else:
    st.markdown("""
        <div style='
            text-align: center; 
            padding: 4rem 2rem; 
            background: #1a1f2e; 
            border-radius: 12px;
            border: 2px dashed rgba(59, 130, 246, 0.3);
            margin: 2rem 0;
        '>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>📊</div>
            <h2 style='color: #f9fafb; margin-bottom: 0.5rem;'>Get Started</h2>
            <p style='color: #94a3b8; font-size: 1.125rem;'>
                Please upload a CSV or Excel file to start analytics.
            </p>
            <p style='color: #64748b; font-size: 0.875rem; margin-top: 1rem;'>
                Supported formats: .csv, .xlsx
            </p>
        </div>
    """, unsafe_allow_html=True)