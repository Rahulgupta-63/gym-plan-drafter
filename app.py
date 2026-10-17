import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from plan_logic import is_allowed, generate_plan

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

MODEL = "openai/gpt-oss-20b"

st.set_page_config(page_title="Gym Plan Drafter", page_icon="🏋️")
st.title("🏋️ Gym Plan Drafter")
st.write("For trainers: enter a client's details and get a draft weekly plan in seconds. "
         "You review and edit it before the client sees it.")

name = st.text_input("Client name (optional)")
age = st.number_input("Age", min_value=10, max_value=80, value=25)
gender = st.selectbox("Gender", ["Male", "Female", "Prefer not to say"])
job = st.selectbox("Job type", ["Desk job", "Standing / field work", "Student", "Homemaker"])
goal = st.selectbox("Goal", ["Fat loss", "Muscle gain", "General fitness", "Strength"])
experience = st.selectbox("Experience", ["Beginner", "Some experience", "Regular"])
days = st.slider("Days per week", 2, 6, 4)
minutes = st.slider("Minutes per session", 30, 120, 60, step=5)
diet = st.selectbox("Diet type", ["Vegetarian", "Eggs + vegetarian", "Non-vegetarian"])
budget = st.selectbox("Daily food budget", ["Low", "Medium", "Flexible"])
issues = st.text_input("Injuries or health issues (optional)")

if st.button("Draft the plan"):
    st.session_state.pop("plan", None)
    st.session_state.pop("problems", None)
    if not api_key:
        st.error("API key not found. Check your .env file or Streamlit secrets.")
    elif not is_allowed(age):
        st.warning("Under 14: please ask a doctor or a school PE teacher. "
                   "This tool does not draft plans for young children.")
    else:
        client_data = {"name": name, "age": age, "gender": gender, "job": job, "goal": goal,
                       "experience": experience, "days": days, "minutes": minutes,
                       "diet": diet, "budget": budget, "issues": issues}
        try:
            client = Groq(api_key=api_key, timeout=90)
            with st.spinner("Drafting and checking the plan..."):
                plan, problems = generate_plan(client, MODEL, client_data)
            st.session_state["plan"] = plan
            st.session_state["problems"] = problems
        except Exception as e:
            st.error(f"Something went wrong: {e}")

if st.session_state.get("plan"):
    if st.session_state.get("problems"):
        st.warning("The auto-check still flagged: " + "; ".join(st.session_state["problems"]) +
                   ". Please review this plan carefully before using it.")
    else:
        st.success("Auto-check passed (days, diet, budget, safety rules).")
    st.markdown(st.session_state["plan"])
    st.download_button("Download plan (.txt)", st.session_state["plan"], file_name="plan.txt")
    st.caption("Draft for trainer review. Not medical advice.")