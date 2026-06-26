import streamlit as st
import asyncio
import json
# --- IMPORT OUR MODULAR ECOSYSTEM ---
import sidebar
from scraper.orchestrator import LinkedInScraperSupervisor
from engine import tool
import ui_components
import agent_runner

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="LinkGent | Transparent LinkedIn Auditor",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. INJECT UI THEME
ui_components.apply_custom_css()

# 3. INITIALIZE APP-LEVEL SESSION STATE
if "raw_linkedin_data" not in st.session_state:
    st.session_state.raw_linkedin_data = None
if "target_user" not in st.session_state:
    st.session_state.target_user = ""
if "audit_report" not in st.session_state:
    st.session_state.audit_report = None

# 4. RENDER SIDEBAR & CAPTURE CALIBRATION CONSTANTS
engine_config = sidebar.render_sidebar()

# 5. RENDER MAIN HEADER
st.title("👔 LinkGent Profile Scout")
st.markdown("A transparent, mathematically-grounded auditing tool for professional LinkedIn profiles.")
st.markdown("---")

# 6. INPUT CAPTURE
col_input, col_btn = st.columns([4, 1])
with col_input:
    target_input = st.text_input("Enter LinkedIn Username (e.g., akshat-gupta-88b129325):", value=st.session_state.target_user)
with col_btn:
    st.write("") # Spacing
    st.write("")
    run_audit = st.button("Fetch LinkedIn Telemetry", type="primary", use_container_width=True)

# 7. EXECUTE DATA PIPELINE
if run_audit:
    if target_input.strip():
        st.session_state.target_user = target_input.strip()
        st.session_state.audit_report = None 
        
        with st.spinner("Initializing stealth browser & intelligent scrolling... (This takes 1-2 minutes)"):
            try:
                # Initialize the scraper in headless mode for speed
                supervisor = LinkedInScraperSupervisor(target_username=st.session_state.target_user, headless=True)
                # Run the async pipeline safely within Streamlit
                st.session_state.raw_linkedin_data = asyncio.run(supervisor.execute_pipeline())
            except Exception as e:
                st.error(f"🚨 Pipeline failure: {str(e)}")
    else:
        st.warning("Please enter a valid LinkedIn username.")

# 8. RENDER THE DASHBOARD
if st.session_state.raw_linkedin_data:
    raw_data = st.session_state.raw_linkedin_data
    # ==========================================
    # NEW CODE: The Eye Button & Download Button
    # ==========================================
    st.download_button(
        label="💾 Download Raw JSON Telemetry",
        data=json.dumps(raw_data, indent=4),
        file_name=f"{st.session_state.target_user}_telemetry.json",
        mime="application/json",
        use_container_width=True # Makes the button look great
    )
    
    with st.expander("👁️ View Raw JSON Payload (Full Width)"):
        st.json(raw_data)
        
    st.write("") # Breathing room
     # Adds a little breathing room
    # ==========================================
    # Step A: Compile the Math based on UI sliders
    compiled_context = tool.compile_linkedin_payload(raw_data, engine_config)
    
    metrics = compiled_context["hard_metrics"]
    username = compiled_context["user_target"]

    # Step B: Render Visuals (Updates instantly when sliders move)
    ui_components.render_kpi_dashboard(metrics, username)
    ui_components.render_math_explainers(metrics["breakdowns"], metrics["category_scores"])

    # Step C: The AI Engine Execution Gate
    st.markdown("---")
    st.subheader("🤖 Career Architecture Agent")
    st.markdown(f"The Agent will analyze this math using the **{engine_config['persona']}** mindset.")
    
    if not st.session_state.audit_report:
        if st.button("✨ Generate AI Narrative Audit", type="primary"):
            with st.spinner("Analyzing math and deducing career roadmap..."):
                st.session_state.audit_report = agent_runner.run_ai_auditor(compiled_context)
                st.rerun() 
    
    if st.session_state.audit_report:
        ui_components.render_markdown_viewer(st.session_state.audit_report, username)
        
        if st.button("🔄 Regenerate AI Audit (Apply New Sliders)"):
            with st.spinner("Re-analyzing with updated metrics..."):
                st.session_state.audit_report = agent_runner.run_ai_auditor(compiled_context)
                st.rerun()