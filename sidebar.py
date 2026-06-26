import streamlit as st

# --- PRESET EVALUATION PERSONAS ---
PERSONAS = {
    "Default (Balanced Assessor)": {
        "weights": {"consistency": 20, "engagement": 25, "depth": 25, "authority": 20, "optimization": 10},
        "constants": {
            "epsilon": 1.0, 
            "comment_weight": 2.0, "repost_weight": 1.5, "reciprocity_bonus": 10.0,
            "alpha": 4.0, "beta": 2.0, "gamma": 1.5,
            "lambda_multiplier": 25.0, "target_features": 5.0
        }
    },
    "The Enterprise Recruiter": {
        "weights": {"consistency": 30, "engagement": 15, "depth": 40, "authority": 5, "optimization": 10},
        "constants": {
            "epsilon": 0.5, # Demands high consistency
            "comment_weight": 1.0, "repost_weight": 1.0, "reciprocity_bonus": 5.0,
            "alpha": 6.0, "beta": 4.0, "gamma": 1.0, # Values hard experience/certs over endorsements
            "lambda_multiplier": 15.0, "target_features": 5.0
        }
    },
    "The Community Builder": {
        "weights": {"consistency": 15, "engagement": 40, "depth": 10, "authority": 25, "optimization": 10},
        "constants": {
            "epsilon": 2.0, 
            "comment_weight": 4.0, "repost_weight": 3.0, "reciprocity_bonus": 20.0, # Heavily rewards deep engagement
            "alpha": 2.0, "beta": 1.0, "gamma": 3.0, 
            "lambda_multiplier": 30.0, "target_features": 5.0
        }
    }
}

def init_session_state():
    """Initializes all variables in session state to prevent UI reset errors."""
    if "persona" not in st.session_state: st.session_state.persona = "Default (Balanced Assessor)"
    
    # 1. Weights (5)
    if "w_cons" not in st.session_state: st.session_state.w_cons = 20
    if "w_eng" not in st.session_state: st.session_state.w_eng = 25
    if "w_dep" not in st.session_state: st.session_state.w_dep = 25
    if "w_auth" not in st.session_state: st.session_state.w_auth = 20
    if "w_opt" not in st.session_state: st.session_state.w_opt = 10

    # 2. Consistency Constants
    if "epsilon" not in st.session_state: st.session_state.epsilon = 1.0
    
    # 3. Engagement Constants
    if "comment_weight" not in st.session_state: st.session_state.comment_weight = 2.0
    if "repost_weight" not in st.session_state: st.session_state.repost_weight = 1.5
    if "reciprocity_bonus" not in st.session_state: st.session_state.reciprocity_bonus = 10.0

    # 4. Depth Constants
    if "alpha" not in st.session_state: st.session_state.alpha = 4.0
    if "beta" not in st.session_state: st.session_state.beta = 2.0
    if "gamma" not in st.session_state: st.session_state.gamma = 1.5

    # 5. Authority Constants
    if "lambda_multiplier" not in st.session_state: st.session_state.lambda_multiplier = 25.0

    # 6. Optimization Constants
    if "target_features" not in st.session_state: st.session_state.target_features = 5.0

def apply_persona_defaults():
    """Auto-snaps all sliders to the designated Sweet Spots when a persona is selected."""
    selected = st.session_state.persona
    p = PERSONAS[selected]
    
    st.session_state.update({
        "w_cons": p["weights"]["consistency"], "w_eng": p["weights"]["engagement"],
        "w_dep": p["weights"]["depth"], "w_auth": p["weights"]["authority"], "w_opt": p["weights"]["optimization"],
        "epsilon": p["constants"]["epsilon"], 
        "comment_weight": p["constants"]["comment_weight"], "repost_weight": p["constants"]["repost_weight"], "reciprocity_bonus": p["constants"]["reciprocity_bonus"],
        "alpha": p["constants"]["alpha"], "beta": p["constants"]["beta"], "gamma": p["constants"]["gamma"],
        "lambda_multiplier": p["constants"]["lambda_multiplier"], "target_features": p["constants"]["target_features"]
    })

def render_sidebar():
    """Renders the transparent sidebar UI and returns the compiled engine configuration."""
    init_session_state()
    
    with st.sidebar:
        st.header("⚙️ Engine Calibration")
        st.markdown("Absolute control over the LinkedIn scoring logic.")
        
        st.selectbox("Evaluation Persona", options=list(PERSONAS.keys()), key="persona", on_change=apply_persona_defaults)
        
        # --- 1. OVERALL CATEGORY WEIGHTS ---
        with st.expander("⚖️ Final Category Weights", expanded=False):
            w_cons = st.slider("Consistency", 0, 100, key="w_cons")
            w_eng = st.slider("Network Engagement", 0, 100, key="w_eng")
            w_dep = st.slider("Professional Depth", 0, 100, key="w_dep")
            w_auth = st.slider("Authority & Reach", 0, 100, key="w_auth")
            w_opt = st.slider("Optimization", 0, 100, key="w_opt")
            
            total_weight = max(w_cons + w_eng + w_dep + w_auth + w_opt, 1) 
            st.info(f"Total sums to {total_weight}. The engine auto-normalizes these to exactly 100%.")

        # --- 2. CONSISTENCY ---
        with st.expander("📅 Consistency Limits", expanded=False):
            epsilon = st.slider("Epsilon (ε) [Forgiveness]", 0.1, 5.0, key="epsilon", step=0.1,
                                help="INCREASE to forgive sporadic posting. DECREASE to ruthlessly demand high monthly volume.")

        # --- 3. ENGAGEMENT ---
        with st.expander("🤝 Network Engagement", expanded=False):
            comment_weight = st.slider("Comment Weight", 1.0, 5.0, key="comment_weight", step=0.5,
                                       help="Points awarded per comment relative to a standard 'Like'.")
            repost_weight = st.slider("Repost Weight", 1.0, 5.0, key="repost_weight", step=0.5)
            reciprocity_bonus = st.slider("Reciprocity Bonus", 0.0, 20.0, key="reciprocity_bonus", step=1.0,
                                          help="Bonus points for writing as many recommendations as received.")

        # --- 4. PROFESSIONAL DEPTH ---
        with st.expander("🛠️ Professional Depth", expanded=False):
            alpha = st.slider("Alpha (α) [Role Value]", 1.0, 10.0, key="alpha", step=0.5,
                              help="Points awarded per listed experience role.")
            beta = st.slider("Beta (β) [Cert Value]", 1.0, 10.0, key="beta", step=0.5,
                             help="Points awarded per listed certification.")
            gamma = st.slider("Gamma (γ) [Skill Multiplier]", 0.5, 5.0, key="gamma", step=0.5,
                              help="Multiplier applied to the logarithmic sum of skill endorsements.")

        # --- 5. AUTHORITY & REACH ---
        with st.expander("🚀 Authority & Reach", expanded=False):
            lambda_multiplier = st.slider("Lambda (λ) [Reach Scale]", 10.0, 50.0, key="lambda_multiplier", step=1.0,
                                          help="Scales the Base-10 logarithm of total audience size. Increase to let smaller audiences score higher.")

        # --- 6. OPTIMIZATION ---
        with st.expander("📝 Profile Optimization", expanded=False):
            target_features = st.slider("Target Features", 1.0, 5.0, key="target_features", step=1.0,
                                     help="The denominator for calculating optimization percentage.")

    engine_config = {
        "persona": st.session_state.persona,
        "weights": {
            "consistency": w_cons / total_weight, "engagement": w_eng / total_weight,
            "depth": w_dep / total_weight, "authority": w_auth / total_weight, "optimization": w_opt / total_weight
        },
        "constants": {
            "epsilon": epsilon, 
            "comment_weight": comment_weight, "repost_weight": repost_weight, "reciprocity_bonus": reciprocity_bonus,
            "alpha": alpha, "beta": beta, "gamma": gamma,
            "lambda_multiplier": lambda_multiplier, "target_features": target_features
        }
    }
    
    return engine_config