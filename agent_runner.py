import os
import json
import operator
from typing import TypedDict, Annotated
from dotenv import load_dotenv

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AnyMessage
from langgraph.graph import StateGraph, START, END

# Load environment variables securely
load_dotenv()
os.environ["AZURE_OPENAI_API_KEY"] = os.environ.get("AZURE_OPENAI_API_KEY", "")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.environ.get("ENDPOINT", "")
os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

# Initialize the Azure OpenAI Model
model = init_chat_model(
    "azure_openai:gpt-4o",
    azure_deployment="gpt-4o",
    temperature=0.2,
    max_tokens=1500,
    max_retries=2,
    timeout=30,
)

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    compiled_context: dict

def profiling_node(state: AgentState):
    """
    The core LLM reasoning node. Translates the mathematical LinkedIn telemetry into 
    strategic, persona-driven career and networking advice.
    """
    context = state['compiled_context']
    persona = context.get('evaluation_persona', 'Default')
    
    # 1. Assign dynamic behavioral instructions based on the UI selection
    if "Enterprise Recruiter" in persona:
        persona_instructions = "You are an Elite Enterprise Engineering Recruiter. Demand a highly professional presence, rigorous depth of certifications/experience, and strict profile optimization. Be highly critical of poor documentation or shallow engagement."
    elif "Community Builder" in persona:
        persona_instructions = "You are a Developer Relations (DevRel) Manager. Praise deep engagement, reciprocity in recommendations, and consistency in posting. Forgive a lack of formal certifications if their audience reach and community metrics are high."
    else:
        persona_instructions = "You are a balanced, objective Professional Career Architect. Provide a well-rounded, objective review of their network reach, professional depth, and content consistency."

    # 2. Compile the Master System Prompt configured for LinkedIn
    system_prompt = f"""You are a Technical Career Architect and Senior Recruiter.
Your task is to ingest a candidate's structured LinkedIn analytics payload and produce a highly accurate, strategic professional profile.

EVALUATION PERSONA:
{persona_instructions}

Strict Evaluation Directives:
1. Core Competencies: Identify their primary domain expertise based on their top skills and certifications.
2. Career Trajectory: Analyze their footprint to deduce their professional trajectory (e.g., transitioning to AI, established senior leadership, active open-source contributor).
3. Actionable Roadmap: Give 2-3 specific recommendations to optimize their sub-optimal metrics. Align these strictly with your persona context!

METRIC DEFINITIONS (DO NOT HALLUCINATE MEANINGS):
- 'Consistency': Frequency and steady spread of content posting.
- 'Engagement': True community interaction (comments, reposts) and reciprocity (giving recommendations).
- 'Depth': Formal career structure measured by the sheer volume of experience roles, certifications, and validated skill endorsements.
- 'Authority': Absolute network reach (Followers + Connections) scaled logarithmically.
- 'Optimization': Utilization of platform features (Banner, About Section, Custom URL, etc.).

OUTPUT FORMAT:
Return clean, professional Markdown. 
Sections must include: Executive Summary, Core Competency Profiling, Score Diagnostics, Next-Action Roadmap."""

    # 3. Strip the heavy math breakdowns to save LLM tokens (The UI handles the math explainers)
    llm_context = {
        "user_target": context.get("user_target"),
        "hard_metrics": {
            "final_score": context.get("hard_metrics", {}).get("final_score"),
            "category_scores": context.get("hard_metrics", {}).get("category_scores")
        },
        "narrative_context": context.get("narrative_context") # Contains top_skills, total_experience_roles, total_certifications
    }

    human_content = f"Please evaluate the following compiled profile context:\n\n{json.dumps(llm_context, indent=4)}"
    
    # 4. Invoke the LLM
    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_content)
    ])
    
    return {"messages": [response]}

def run_ai_auditor(compiled_context: dict) -> str:
    """
    Public entry point for the Streamlit UI to trigger the AI Agent.
    Builds the LangGraph pipeline, executes it, and returns the markdown string.
    """
    # Define the execution graph
    workflow = StateGraph(AgentState)
    workflow.add_node("profiler", profiling_node)
    workflow.add_edge(START, "profiler")
    workflow.add_edge("profiler", END)
    
    agent_pipeline = workflow.compile()

    # Initialize State and Run
    initial_state = {"messages": [], "compiled_context": compiled_context}
    
    try:
        output_state = agent_pipeline.invoke(initial_state)
        final_markdown = output_state["messages"][-1].content
        return final_markdown
    except Exception as e:
        return f"**Error executing AI Agent:** {str(e)}\n\nPlease check your API keys and network connection."