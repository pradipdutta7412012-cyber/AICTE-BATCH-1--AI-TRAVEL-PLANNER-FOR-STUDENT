Set-Content -Path "C:\Users\Pradip Dutta\Documents\IBM\app.py" -Value @'
import streamlit as st
import time
from google import genai
from google.genai import types

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEMING (GORGEOUS FRONTEND)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="RoamAcademic | AI Student Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a modern, dark-mode glassmorphism aesthetic
st.markdown("""
    <style>
    /* Main background and font */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Modern Glassmorphism Cards */
    .crypto-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Gradients for Headers */
    .gradient-text {
        background: linear-gradient(90deg, #38bdf8, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Custom buttons */
    .stButton>button {
        background: linear-gradient(90deg, #6366f1, #a855f7) !important;
        color: white !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4);
    }
    
    /* Fix standard text outputs readability */
    p, li {
        color: #cbd5e1 !important;
        line-height: 1.6;
    }
    h1, h2, h3 {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BACKEND INITIALIZATION (GEMINI API WITH EMBEDDED KEY FALLBACK)
# -----------------------------------------------------------------------------
DEFAULT_KEY = "AQ.Ab8RN6IfzT6cc0oIDPcoXGx4QoQH6tATX1onaXfN3Qzrfumiiw"

GEMINI_API_KEY = st.sidebar.text_input(
    "🔑 Gemini API Key", 
    value=DEFAULT_KEY,
    type="password"
)

def get_gemini_client():
    if not GEMINI_API_KEY:
        st.info("💡 Please enter your Gemini API Key in the sidebar to get started.")
        return None
    try:
        return genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Failed to connect to Gemini: {e}")
        return None

# -----------------------------------------------------------------------------
# 3. UI LAYOUT & INPUTS
# -----------------------------------------------------------------------------
st.markdown('# ✈️ <span class="gradient-text">RoamAcademic</span>', unsafe_allow_html=True)
st.markdown('### Smart, Budget-Friendly Itineraries Designed for Students.')
st.write("---")

# Layout columns for inputs
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="crypto-card"><h4>📍 Trip Parameters</h4>', unsafe_allow_html=True)
    
    destination = st.text_input("Where are you heading?", placeholder="e.g., Goa, Kyoto, Prague")
    origin = st.text_input("Starting from?", placeholder="e.g., Delhi, Mumbai")
    
    days = st.slider("Trip Duration (Days)", min_value=1, max_value=10, value=3)
    
    budget = st.selectbox(
        "Budget Level (Per Person)", 
        ["Shoestring (Backpacker/Hostels)", "Moderate Student (Budget Hotels/Street Food)", "Comfortable"]
    )
    
    travel_mode = st.multiselect(
        "Preferred Transport", 
        ["Trains", "Buses", "Shared Cabs", "Walking/Public Metro"],
        default=["Walking/Public Metro", "Trains"]
    )
    
    interests = st.multiselect(
        "Primary Interests",
        ["Nature & Hikes", "History & Culture", "Nightlife & Cafes", "Photography Hotspots", "Local Food Hidden Gems"],
        default=["History & Culture", "Local Food Hidden Gems"]
    )
    
    submit_btn = st.button("✨ Generate AI Itinerary")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. AI ITINERARY GENERATION & DISPLAY WITH AUTO-RETRY LOOP
# -----------------------------------------------------------------------------
with col2:
    if submit_btn:
        client = get_gemini_client()
        
        if client and destination and origin:
            with st.spinner("🤖 Crafting your budget-friendly itinerary... Please wait..."):
                
                # Formulate our prompt
                prompt = f"""
                You are an expert student travel consultant specializing in hyper-budget, highly efficient travel itineraries.
                Create a highly detailed, scannable, and realistic {days}-day travel itinerary for a student traveling from {origin} to {destination}.
                
                Constraints & Context:
                - Budget Tier: {budget}
                - Preferred Transport Modes: {', '.join(travel_mode)}
                - Core Interests: {', '.join(interests)}
                
                Please structure your response exactly with these headers:
                1. 💰 Budget Overview & Hidden Costs (Provide rough estimates for hostels, public transport passes, and cheap eats)
                2. 🗺️ Route Efficiency & Logistics (How to get there cheaply from {origin} and best local transit hacks)
                3. 📅 Day-by-Day Smart Itinerary (Break down morning, afternoon, and evening. Focus heavily on free student discounts and cheap local street food stalls)
                4. 💡 Pro Student Safety & Survival Hacks
                """
                
                # Execution variables
                models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash']
                success = False
                response_text = ""
                
                # Robust retry system looping through both models with multiple attempts
                for model_name in models_to_try:
                    if success:
                        break
                        
                    for attempt in range(3):  # Try each model up to 3 times
                        try:
                            response = client.models.generate_content(
                                model=model_name,
                                contents=prompt,
                            )
                            response_text = response.text
                            success = True
                            break  # Break the inner retry loop on success
                        except Exception as e:
                            err_msg = str(e)
                            if "503" in err_msg or "UNAVAILABLE" in err_msg or "ResourceExhausted" in err_msg:
                                # Progressive waiting time: 2s, 4s, 6s...
                                wait_time = (attempt + 1) * 2 
                                st.toast(f"⚠️ {model_name} is busy. Retrying in {wait_time}s... (Attempt {attempt+1}/3)")
                                time.sleep(wait_time)
                            else:
                                # If it's a completely different error, display it and halt
                                st.error(f"API Error: {e}")
                                break
                
                # Display Results
                if success:
                    st.markdown('<div class="crypto-card">', unsafe_allow_html=True)
                    st.markdown(f"## 🗺️ Optimized Itinerary for {destination.title()}")
                    st.markdown(response_text)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("❌ The public API servers are heavily overloaded right now. Please wait a minute and try clicking Generate again.")
                        
        elif not destination or not origin:
            st.warning("⚠️ Please fill out both the Destination and Origin fields!")
    else:
        # Placeholder view when the app first loads
        st.markdown('<div class="crypto-card" style="text-align: center; padding: 50px;">', unsafe_allow_html=True)
        st.markdown("### 🗺️ Your Customized Plan Will Appear Here")
        st.write("Fill in your budget constraints and destination on the left panel, click *Generate*, and let our generative AI model map out your perfect student getaway.")
        st.markdown('</div>', unsafe_allow_html=True)
'@