import streamlit as st
import time
import re
from google import genai
from google.genai import types
from google.genai.errors import APIError

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEMING (GORGEOUS FRONTEND)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="RoamAcademic | AI Student Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a modern, dark-mode glassmorphism aesthetic
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    .crypto-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .gradient-text {
        background: linear-gradient(90deg, #38bdf8, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
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
    p, li { color: #cbd5e1 !important; line-height: 1.6; }
    h1, h2, h3, h4 { color: #ffffff !important; }
    
    /* Ensure clean rendering of generated tables */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        background: rgba(255, 255, 255, 0.02);
    }
    th, td {
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 10px;
        text-align: left;
    }
    th { background: rgba(99, 102, 241, 0.2); }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. AUTOMATED BACKEND INITIALIZATION (UPDATED API KEY)
# -----------------------------------------------------------------------------

# Safely pointing Streamlit to the variable mapping instead of hardcoding the secret string directly.
API_KEY = st.secrets["AQ.Ab8RN6IfzT6cc0oIDPcoXGx4QoQH6tATX1onaXfN3Qzrfumiiw"]

def get_gemini_client():
    try:
        return genai.Client(api_key=API_KEY)
    except Exception as e:
        st.error(f"Failed to initialize GenAI Client: {e}")
        return None

# -----------------------------------------------------------------------------
# 3. UI LAYOUT & INPUTS
# -----------------------------------------------------------------------------
st.markdown('# ✈️ <span class="gradient-text">RoamAcademic</span>', unsafe_allow_html=True)
st.markdown('### Smart, Budget-Friendly Itineraries Designed for Students.')
st.write("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="crypto-card"><h4>📍 Trip Parameters</h4>', unsafe_allow_html=True)
    
    destination = st.text_input("Where are you heading?", placeholder="e.g., digha, kerala, goa, japan")
    origin = st.text_input("Starting from?", placeholder="e.g., kolkata, delhi")
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
# 4. RESILIENT HIGH-DETAIL GENERATION ENGINE
# -----------------------------------------------------------------------------
with col2:
    if submit_btn:
        client = get_gemini_client()
        if client and destination and origin:
            
            # Massive, direct data layout instructions
            prompt = f"""
            Generate a comprehensive, highly exhaustive, and deeply detailed {days}-day student travel itinerary from {origin} to {destination}. 
            Do not provide a generic summary or truncate the output early. Provide concrete names, actionable strategies, and specific local breakdowns.

            Trip Parameters:
            - Budget Strategy: {budget}
            - Mode of Transit: {', '.join(travel_mode)}
            - Primary Focus: {', '.join(interests)}

            You must structure your response with these explicit sections:

            ### 💰 1. Comprehensive Budget Allocation Table
            Construct a detailed markdown table estimating costs in local currency:
            | Expense Category | Estimated Cost | Money-Saving Hacks & Student Discounts |
            | :--- | :--- | :--- |
            | Accommodation (Hostels/Dorms) | | |
            | Food & Street Food Stalls | | |
            | Local Transport & Passes | | |
            | Entry Fees & Attractions | | |
            | Emergency Buffer | | |

            ### 🗺️ 2. Route Optimization & Logistics
            - Detail the exact step-by-step route from {origin} to {destination} using {', '.join(travel_mode)}.
            - Provide specific names of cheap transit passes, overnight sleeper classes, or local metro cards to purchase immediately upon arrival.

            ### 📅 3. High-Density Day-by-Day Itinerary
            For EACH of the {days} days, provide a deeply contextual timeline breaking down:
            - *Morning (8:00 AM - 12:00 PM):* Specific historical points, open-air sights, or trails. Detail how to reach them using transit.
            - *Afternoon (12:00 PM - 5:00 PM):* Off-beat exploration, student-discount museums, or walking sectors. Mention explicit cheap local food joints, markets, or cafes by name.
            - *Evening & Night (5:00 PM - 10:00 PM):* Night markets, public viewpoints, free cultural showcases, or student-friendly hubs.

            ### 💡 4. Pro Student Safety & Survival Hacks
            - List 4 distinct, highly practical location-specific tips for {destination} (e.g., tourist card apps, booking timelines, safety maps, water hacks).
            """
            
            success = False
            response_text = ""
            max_attempts = 3
            status_container = st.empty()
            
            for attempt in range(max_attempts):
                try:
                    status_container.markdown("⏳ *AI is compiling high-density route structures...*")
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.6,
                            max_output_tokens=8192,  # Expanded buffer window completely unlocks long-form writing
                            system_instruction="You are a meticulous, precise professional travel guide who exclusively writes exhaustive, multi-section itineraries with explicit names, tables, and step-by-step guidance."
                        )
                    )
                    response_text = response.text
                    if response_text and len(response_text) > 200:
                        success = True
                        break
                    
                except APIError as e:
                    err_msg = str(e)
                    if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "503" in err_msg or "UNAVAILABLE" in err_msg:
                        wait_match = re.search(r"retry in ([\d\.]+)", err_msg)
                        wait_time = float(wait_match.group(1)) if wait_match else (attempt + 1) * 8
                        wait_time = min(wait_time + 1.5, 30.0)
                        
                        status_container.warning(
                            f"⚠️ API pipeline crowded. Waiting {wait_time:.1f}s for quota block reset... (Attempt {attempt + 1}/{max_attempts})"
                        )
                        time.sleep(wait_time)
                    else:
                        status_container.error(f"❌ Connection Blocked: {err_msg}")
                        break
                except Exception as e:
                    status_container.error(f"❌ Script Exception: {e}")
                    break
            
            status_container.empty()
            
            if success and response_text:
                st.markdown('<div class="crypto-card">', unsafe_allow_html=True)
                st.markdown(f"## 🗺️ Detailed Student Plan: {destination.title()}")
                st.markdown(response_text)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("❌ Generation request did not return a full payload. Please wait a moment and try clicking Generate again.")
                        
        elif not destination or not origin:
            st.warning("⚠️ Please fill out both the Destination and Origin fields!")
    else:
        st.markdown('<div class="crypto-card" style="text-align: center; padding: 50px;">', unsafe_allow_html=True)
        st.markdown("### 🗺️ Your Customized Plan Will Appear Here")
        st.write("Fill in your parameters on the left, click *Generate*, and watch the system layout your complete roadmap.")
        st.markdown('</div>', unsafe_allow_html=True)