
import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from datetime import datetime

# --- Configuration ---
st.set_page_config(
    page_title="COI V2 - Professional Athlete Agent",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Styles ---
# Attempt to mimic the dark/premium look
st.markdown("""
    <style>
        .stApp {
            background-color: #0a0a0b;
            color: white;
        }
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: #18181b;
            color: white;
            border-color: #27272a;
        }
        div[data-testid="stMetric"] {
            background-color: #121214;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 1rem;
            border-radius: 0.75rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, I've synchronized your career history. I'm here to help optimize your path. What can I analyze for you?"}
    ]

if "selected_player" not in st.session_state:
    st.session_state.selected_player = "LeBron James"

# --- Helper Functions ---
def get_api_key():
    # Try to get from st.secrets, then env var, then prompt
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except:
            pass
    return api_key

API_KEY = get_api_key()

if not API_KEY:
    with st.sidebar:
        st.warning("⚠️ GEMINI_API_KEY not found.")
        API_KEY = st.text_input("Enter Gemini API Key", type="password")
        if API_KEY:
            os.environ["GEMINI_API_KEY"] = API_KEY
            st.rerun()

if API_KEY:
    genai.configure(api_key=API_KEY)

def get_gemini_response(prompt, model_name="gemini-1.5-flash"):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to AI core: {str(e)}"

# --- Components ---

def render_dashboard(player_name):
    st.title(f"Welcome back, {player_name.split(' ')[0]}")
    st.caption(f"Your career trajectory is currently **OPTIMAL**")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Valuation", "$52.4M", "+12%")
    with col2:
        st.metric("Global Rank", "#4", "Top 1%")
    with col3:
        st.metric("Brand Power", "92.1", "Elite")
    with col4:
        st.metric("Usage Optimization", "31.4%", "-2.1%")

    st.markdown("---")
    
    # Charts
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Value Projection vs Performance Peaks")
        # Mock Data
        data = pd.DataFrame({
            'Year': ['2019', '2020', '2021', '2022', '2023', '2024'],
            'Valuation ($M)': [35, 42, 38, 48, 52, 60],
            'PPG': [25.3, 27.1, 26.8, 28.5, 29.7, 31.4]
        })
        
        # Dual axis chart using Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Year'], y=data['Valuation ($M)'], name="Valuation ($M)", fill='tozeroy', line=dict(color='#3b82f6')))
        fig.add_trace(go.Scatter(x=data['Year'], y=data['PPG'], name="PPG", fill='tozeroy', line=dict(color='#10b981')))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Historical Peaks")
        milestones = [
            {'year': '2023-24', 'event': 'NBA All-Star Starter', 'type': 'award'},
            {'year': '2022-23', 'event': 'Scoring Title (31.4 PPG)', 'type': 'milestone'},
            {'year': '2021-22', 'event': 'All-NBA First Team', 'type': 'award'},
            {'year': '2020-21', 'event': 'Western Conference Finals', 'type': 'milestone'},
            {'year': '2019-20', 'event': 'Contract Extension Signed', 'type': 'milestone'},
        ]
        
        for m in milestones:
            color = "🟠" if m['type'] == 'award' else "🔵"
            st.markdown(f"**{m['year']}** {color}  \n{m['event']}")
            st.markdown("---")


def render_contract_analysis(player_name):
    st.title("Strategic Decision Modeling")
    st.write(f"Evaluating high-probability career paths for {player_name}")
    
    col1, col2 = st.columns([1, 1])
    
    scenarios = {
        'Lakers': {'salary': 45.2, 'fit': 94, 'market': 98, 'total': 143.4},
        'Heat': {'salary': 38.5, 'fit': 88, 'market': 92, 'total': 130.5},
        'Suns': {'salary': 42.1, 'fit': 82, 'market': 85, 'total': 126.3},
        'Warriors': {'salary': 40.0, 'fit': 91, 'market': 95, 'total': 135.0},
    }
    
    with col1:
        st.subheader("Tradeoff Scenario Explorer")
        selected_team = st.radio("Select Offer", list(scenarios.keys()))
        s = scenarios[selected_team]
        
        st.info(f"""
        **{selected_team} Offer**  
        Salary: ${s['salary']}M/yr  
        Fit Score: {s['fit']}  
        Brand ROI: {s['market']}  
        Total Value: ${s['total']}M
        """)

    with col2:
        st.subheader("Comparative Archetype Fit")
        # Radar Chart
        categories = ['Financial Value', 'Team Fit', 'Market Growth', 'Winning Prob.', 'Longevity', 'Brand ROI']
        # Mock values based on selection slightly randomized or static for demo
        values = [95, 85, 92, 78, 65, 98] if selected_team == 'Lakers' else [88, 92, 85, 95, 75, 90]
        
        fig = go.Figure(data=go.Scatterpolar(
          r=values,
          theta=categories,
          fill='toself',
          name=player_name
        ))
        fig.update_layout(
          polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
          showlegend=False,
          paper_bgcolor='rgba(0,0,0,0)',
          font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown("### 💡 COI Intelligence Insight")
    st.info("Our neural networks indicate that while the Suns offer a higher immediate base salary, the Lakers' scenario yields a 34% higher long-tail realized value due to tax efficiencies and regional endorsement density.")

def render_performance(player_name):
    st.title("Archetype Analysis")
    st.subheader("'The Dynamic Engine'")
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"{player_name} is currently classified within the top 2% of NBA players in the 'Primary Engine' archetype.")
        perf_data = {
            'Offensive Efficiency (PPP)': '1.14 (98th %)',
            'Defensive Impact (EPM)': '+2.1 (84th %)',
            'Usage Rate Delta': '-4.2 (Optimal)',
            'TS% Over Expectation': '+8.4 (92nd %)'
        }
        for k, v in perf_data.items():
            st.metric(k, v)
            
    with c2:
        # Placeholder for complex cluster visualization
        st.image("https://placehold.co/400x400/121214/FFF?text=K-Means+Cluster+Map", caption="Spatial Representation")

    st.subheader("Regression Forecasts")
    # Simple bar chart
    chart_data = pd.DataFrame({
        'Age': range(24, 32),
        'Performance': [40, 65, 85, 95, 90, 80, 60, 45]
    })
    st.bar_chart(chart_data.set_index('Age'))

# --- Main Layout ---

# Sidebar
with st.sidebar:
    st.title("COI V2")
    st.write("Professional Athlete Agent")
    
    st.session_state.selected_player = st.selectbox(
        "Active Profile",
        ["LeBron James", "Kevin Durant", "Stephen Curry", "Luka Doncic", "Shai Gilgeous-Alexander"],
        index=0
    )
    
    page = st.radio("Navigation", ["Dashboard", "Contract Analysis", "Performance", "Comparison", "Chat with Agent"])

# Routing
if page == "Dashboard":
    render_dashboard(st.session_state.selected_player)
elif page == "Contract Analysis":
    render_contract_analysis(st.session_state.selected_player)
elif page == "Performance":
    render_performance(st.session_state.selected_player)
elif page == "Comparison":
    st.title("Comparative Analysis")
    st.caption("Direct performance benchmark vs league peers")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        comp_player = st.selectbox("Benchmark Target", 
                                   [p for p in ["LeBron James", "Kevin Durant", "Stephen Curry", "Luka Doncic", "Giannis Antetokounmpo"] 
                                    if p != st.session_state.selected_player])

    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Statistical Delta")
        # Mock Comparison Data
        comp_data = pd.DataFrame({
            'Metric': ['Points', 'Rebounds', 'Assists', 'FG%', '3P%'],
            st.session_state.selected_player: [28.4, 8.1, 7.4, 54.0, 41.0],
            comp_player: [33.9, 9.2, 9.8, 48.7, 37.5]
        })
        
        # In Plotly, grouped bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(y=comp_data['Metric'], x=comp_data[st.session_state.selected_player], orientation='h', name=st.session_state.selected_player, marker_color='#3b82f6'))
        fig.add_trace(go.Bar(y=comp_data['Metric'], x=comp_data[comp_player], orientation='h', name=comp_player, marker_color='#a855f7'))
        fig.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Archetype Overlap")
        # Radar Chart
        categories = ['Scoring', 'Playmaking', 'Defense', 'Rebounding', 'Gravity']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[92, 88, 75, 82, 95], theta=categories, fill='toself', name=st.session_state.selected_player, marker_color='#3b82f6'))
        fig.add_trace(go.Scatterpolar(r=[98, 95, 65, 89, 90], theta=categories, fill='toself', name=comp_player, marker_color='#a855f7'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=30, r=30, t=30, b=30), legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

    # Cards
    st.markdown("---")
    k1, k2, k3 = st.columns(3)
    k1.metric("Marketability Variance", "+14.2%", "Endorsement potential")
    k2.metric("Winning Impact", "High", "Net rating similarity < 1.2pts")
    k3.metric("Longevity Comp", "92%", "Matches peak profiles")
elif page == "Chat with Agent":
    st.title("COI Intelligence Agent")
    st.caption(f"Active Profile: {st.session_state.selected_player}")
    
    # Display chat messages
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "assistant"
        with st.chat_message(role):
            st.write(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask your agent..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # If last message is user, generate response
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                if API_KEY:
                    response_text = get_gemini_response(
                        f"Act as COI, an elite athlete agent for {st.session_state.selected_player}. Query: {st.session_state.messages[-1]['content']}"
                    )
                    st.write(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    st.error("Please provide an API Key.")

