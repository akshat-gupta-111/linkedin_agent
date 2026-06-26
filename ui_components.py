import streamlit as st
import pandas as pd
import math

def apply_custom_css():
    """
    Injects custom CSS to guarantee stark contrast.
    Strictly enforces black text on white backgrounds as requested.
    """
    st.markdown("""
        <style>
        /* Main background */
        .main { background-color: #F8FAFC; }
        
        /* Metric Cards */
        .stMetric { 
            background-color: #FFFFFF !important; 
            padding: 15px !important; 
            border-radius: 10px !important; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important; 
        }
        div[data-testid="stMetricValue"] > div { color: #000000 !important; font-weight: 800 !important; }
        label[data-testid="stMetricLabel"] > div > p { color: #333333 !important; font-weight: 600 !important; }
        
        /* Glass Box Explainers */
        .math-explainer { 
            background-color: #FFFFFF !important; 
            color: #000000 !important; 
            border-left: 5px solid #3B82F6 !important; 
            padding: 20px !important; 
            border-radius: 5px !important; 
            margin-bottom: 15px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        }
        .math-explainer p, .math-explainer b, .math-explainer span, .math-explainer div { 
            color: #000000 !important; 
        }
        
        /* Report Viewer Box */
        .report-viewer {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            padding: 30px !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.02) !important;
        }
        .report-viewer h1, .report-viewer h2, .report-viewer h3, .report-viewer p, .report-viewer li {
            color: #000000 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def render_kpi_dashboard(metrics: dict, username: str):
    """Renders the top-level metric scorecards and progress bars."""
    cats = metrics["category_scores"]
    
    st.subheader(f"📊 Professional Telemetry for {username}")
    col_main, _ = st.columns([1, 3])
    with col_main:
        st.metric(label="🏆 Final Agent Score", value=f"{metrics['final_score']} / 100")
    
    st.write(" ")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Consistency", f"{cats['consistency']}%")
        st.progress(cats['consistency'] / 100.0)
    with c2:
        st.metric("Engagement", f"{cats['engagement']}%")
        st.progress(cats['engagement'] / 100.0)
    with c3:
        st.metric("Prof. Depth", f"{cats['depth']}%")
        st.progress(cats['depth'] / 100.0)
    with c4:
        st.metric("Authority", f"{cats['authority']}%")
        st.progress(cats['authority'] / 100.0)
    with c5:
        st.metric("Optimization", f"{cats['optimization']}%")
        st.progress(cats['optimization'] / 100.0)

def render_math_explainers(breakdowns: dict, category_scores: dict):
    """Renders the 5 interactive mathematical explainers with Step-by-Step Logic, LaTeX, and Charts."""
    st.markdown("### 🔍 The Glass Box: Mathematical Audit Breakdown")
    
    # 1. CONSISTENCY
    with st.expander("1. Show Consistency Calculation"):
        d = breakdowns['consistency']
        # Extract epsilon safely since we didn't pass it into the breakdown explicitly earlier
        # Assuming epsilon was 1.0 if not found, but we will frame the math clearly.
        st.markdown(f"""<div class='math-explainer'>
            <b>Goal:</b> Rewards steady, predictable posting over erratic bursting.<br><br>
            <b>Step 1: Logarithmic Dampening & Mean (μ)</b><br>
            To prevent a single viral week from unfairly ruining the score, we compress your raw posts ({d['total_posts']}) using a Base-2 Logarithm. Your Log-Mean is <b>{d['mu']}</b>.<br><br>
            <b>Step 2: Calculate Variance (σ²) & Deviation (σ)</b><br>
            We measure how far each month deviates from the Log-Mean. Your Standard Deviation is <b>{d['sigma']}</b><br><br>
            <b>Step 3: Apply the Penalty Coefficient</b><br>
            We divide the Deviation by the Mean (plus an Epsilon floor) and subtract from 1.
        </div>""", unsafe_allow_html=True)
        st.latex(r"S_{consistency} = \max\left(0, 100 \times \left(1 - \frac{\sigma}{\mu + \epsilon}\right)\right)")
        st.latex(rf"Score = {category_scores['consistency']}")

    # 2. ENGAGEMENT
    with st.expander("2. Show Network Engagement Calculation"):
        d = breakdowns['engagement']
        st.markdown(f"""<div class='math-explainer'>
            <b>Goal:</b> Measures true community interaction, weighting deep text engagement over shallow 'likes'.<br><br>
            <b>Step 1: Calculate Average Depth Ratio</b><br>
            Across your recent activity, we weigh the ratio of comments and reposts against base likes. Your average depth ratio is <b>{d['avg_depth']}</b>.<br><br>
            <b>Step 2: Calculate Reciprocity Bonus</b><br>
            Networking is a two-way street. By comparing recommendations you've given vs. received, you earned <b>{d['reciprocity']} pts</b>.<br><br>
            <b>Step 3: Final Sum</b><br>
            (Depth Ratio × 100) + Reciprocity Bonus
        </div>""", unsafe_allow_html=True)
        st.latex(r"\text{Depth Ratio} = \frac{(\text{Comments} \times W_c) + (\text{Reposts} \times W_r)}{\text{Likes} + 1}")
        st.latex(r"S_{engagement} = \min\left(100, (\text{Avg Depth} \times 100) + \text{Reciprocity}\right)")
        st.latex(rf"Score = {category_scores['engagement']}")

    # 3. PROFESSIONAL DEPTH (WITH CHART)
    with st.expander("3. Show Professional Depth Calculation"):
        d = breakdowns['depth']
        st.markdown(f"""<div class='math-explainer'>
            <b>Goal:</b> Balances structured career experience against community-validated skills.<br><br>
            <b>Step 1: Calculate Experience & Certification Points</b><br>
            Experience Roles generated <b>{d['experience_points']} pts</b>.<br>
            Certifications generated <b>{d['cert_points']} pts</b>.<br><br>
            <b>Step 2: Calculate Skill Endorsement Points (Diminishing Returns)</b><br>
            We take the Base-2 Logarithm of your skill endorsements to prevent a single highly-endorsed skill from breaking the scale (see curve below).<br>
            Logarithmic Sum of Endorsements generated <b>{d['skill_points']} pts</b>.<br><br>
            <b>Step 3: Sum and Cap</b><br>
            {d['experience_points']} + {d['cert_points']} + {d['skill_points']} = <b>{round(d['experience_points'] + d['cert_points'] + d['skill_points'], 2)}</b>
        </div>""", unsafe_allow_html=True)
        
        # Generate Logarithmic Curve Data for visual explanation
        x_vals = list(range(0, 100, 5))
        y_vals = [math.log2(x + 1) for x in x_vals]
        chart_data = pd.DataFrame({"Raw Endorsements on a Single Skill": x_vals, "Yielded Depth Points": y_vals}).set_index("Raw Endorsements on a Single Skill")
        st.line_chart(chart_data)
        
        st.latex(r"S_{depth} = \min\left(100, (\alpha \cdot \text{Roles}) + (\beta \cdot \text{Certs}) + (\gamma \cdot \sum \log_2(\text{Endorsements} + 1))\right)")
        st.latex(rf"Score = {category_scores['depth']}")

    # 4. AUTHORITY & REACH
    with st.expander("4. Show Authority & Reach Calculation"):
        d = breakdowns['authority']
        st.markdown(f"""<div class='math-explainer'>
            <b>Goal:</b> Normalizes massive audience sizes using a Base-10 Logarithm.<br><br>
            <b>Step 1: Total Audience Calculation</b><br>
            Followers + Connections = <b>{d['audience']}</b>.<br><br>
            <b>Step 2: Logarithmic Scaling</b><br>
            Because the gap between 1k and 2k followers is mathematically more significant than the gap between 100k and 101k, we apply a $\log_{{10}}$ scale and multiply by the Lambda constant ({d.get('lambda', 'N/A')}).
        </div>""", unsafe_allow_html=True)
        st.latex(r"S_{authority} = \min\left(100, \lambda \cdot \log_{10}(\text{Audience} + 1)\right)")
        st.latex(rf"Score = {category_scores['authority']}")

    # 5. OPTIMIZATION
    with st.expander("5. Show Optimization Calculation"):
        d = breakdowns['optimization']
        st.markdown(f"""<div class='math-explainer'>
            <b>Goal:</b> Evaluates platform utilization based on profile completeness.<br><br>
            <b>Step 1: Count Active Features</b><br>
            You have successfully utilized <b>{d['active_features']}</b> out of the <b>{d['target_features']}</b> target profile features (About, Banner, Featured, URL, Education).<br><br>
            <b>Step 2: Calculate Ratio</b><br>
            ({d['active_features']} ÷ {d['target_features']}) × 100
        </div>""", unsafe_allow_html=True)
        st.latex(r"S_{optimization} = \left( \frac{F_{active}}{F_{target}} \right) \times 100")
        st.latex(rf"Score = {category_scores['optimization']}")
            
def render_markdown_viewer(md_string: str, username: str):
    """Renders a beautiful inline Markdown viewer and provides the download button."""
    st.markdown("---")
    st.subheader("📄 Formal Audit Report")
    st.write("Preview your formal audit below. The downloaded Markdown file can be printed directly to PDF via any browser (CTRL+P) for a perfect stark-white background.")
    
    # The Interactive Viewer Box
    st.markdown(f"<div class='report-viewer'>{md_string}</div>", unsafe_allow_html=True)
    
    st.write(" ")
    st.download_button(
        label="⬇️ Download Markdown Report (.md)",
        data=md_string,
        file_name=f"{username}_audit_report.md",
        mime="text/markdown",
        type="primary"
    )