import streamlit as st
import pandas as pd
import numpy as np
from data_loader import load_workbook

# 1. PAGE SETUP
st.set_page_config(
    page_title="Saudi Energy Planner | Vision 2030",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. WIX-STYLE CUSTOM CSS STYLING
st.markdown("""
    <style>
    /* Hide Streamlit default overhead UI & Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Center and widen main page container */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }
    
    /* Gradient Hero Header Banner */
    .hero-container {
        background: linear-gradient(135deg, #004D25 0%, #006C35 60%, #008744 100%);
        padding: 40px 30px;
        border-radius: 18px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 108, 53, 0.2);
        margin-bottom: 25px;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        opacity: 0.92;
        font-weight: 300;
    }
    .hero-badge {
        background-color: rgba(255, 255, 255, 0.18);
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 12px;
    }

    /* Modern Wix Dashboard Metric Cards */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 22px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: all 0.25s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 108, 53, 0.08);
        border-color: #006C35;
    }
    [data-testid="stMetricValue"] {
        color: #006C35 !important;
        font-weight: 700 !important;
    }

    /* Content Cards */
    .content-card {
        background: #FFFFFF;
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. HERO BANNER
st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">🌴 Vision 2030 Strategy Platform</div>
        <div class="hero-title">Saudi Energy Transition Planner</div>
        <div class="hero-subtitle">Interactive Decision Support System & Strategic Scenario Simulator</div>
    </div>
""", unsafe_allow_html=True)

# 4. TOP NAVIGATION BAR (Wix Menu Style)
selected_nav = st.radio(
    "",
    ["📊 Executive Summary", "⚡ Energy Simulator", "🔬 Tech Analysis", "🌱 Sustainability & Carbon"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

# Try loading data safely from Excel backend
try:
    wb_data = load_workbook()
    saudi_dict = wb_data.saudi_data
except Exception:
    saudi_dict = {}

# 5. DYNAMIC PAGE CONTENT
if selected_nav == "📊 Executive Summary":
    # Metric KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Target Renewables", value=f"{saudi_dict.get('Renewable Share Target 2030', 0.50)*100:.1f}%", delta="+4.2% YoY")
    with col2:
        st.metric(label="Peak Grid Demand", value=f"{saudi_dict.get('Peak Load GW', 68.4)} GW", delta="-1.8 GW Opt.")
    with col3:
        st.metric(label="Nuclear Baseline", value=f"{saudi_dict.get('Nuclear Target GW', 17.0)} GW", delta="Target 2040")
    with col4:
        st.metric(label="CO2 Abatement", value="145.2 Mt", delta="+12.4% Target")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 2026–2050 Energy Transition Projection</div>', unsafe_allow_html=True)
        
        # Generation Forecast Chart
        years = np.arange(2026, 2051)
        solar = np.linspace(15, 65, len(years))
        wind = np.linspace(5, 30, len(years))
        nuclear = np.linspace(2, 17, len(years))
        chart_df = pd.DataFrame({"Year": years, "Solar (GW)": solar, "Wind (GW)": wind, "Nuclear (GW)": nuclear}).set_index("Year")
        
        st.area_chart(chart_df, color=["#006C35", "#00A859", "#38BDF8"])
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🎯 Quick Actions</div>', unsafe_allow_html=True)
        st.info("💡 **Tip:** Click on **⚡ Energy Simulator** in the top navigation bar to run custom scenario stress-tests.")
        st.button("📥 Export Strategy Brief", use_container_width=True)
        st.button("🔄 Sync Live Model Data", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif selected_nav == "⚡ Energy Simulator":
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚡ Interactive Grid Scenario Simulator</div>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        demand_mult = st.slider("Demand Multiplier (%)", 80, 150, 100)
        renewable_pct = st.slider("Renewable Target (%)", 10, 80, 50)
    with col_b:
        water_alloc = st.slider("Desalination Power Allocation (GW)", 5, 25, 12)
        carbon_tax = st.slider("Carbon Penalty ($/Ton)", 0, 100, 25)
        
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info(f"📍 Viewing the **{selected_nav}** module.")
