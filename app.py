import os
import textwrap

import streamlit as st
from dotenv import load_dotenv

from orchestrator.orchestrator import run_session


load_dotenv()

st.set_page_config(
	page_title="EduSync Agents",
	page_icon="🎓",
	layout="wide",
)

# Header

st.markdown("## EduSync Agents — Multi‑Agent Study Buddy")
st.caption("Research • Quiz • Explain — powered by LangChain, LangGraph, and Groq")

# Sidebar configuration
with st.sidebar:
	st.subheader("Session Settings")
	topic = st.text_input("Study Topic", placeholder="e.g., Photosynthesis, Linear Algebra, HTTP/3")
	model = st.selectbox(
		"LLM Model",
		[
			"llama-3.3-70b-versatile",
			"llama-3.1-8b-instant",
		],
		index=0,
		help="Set GROQ_MODEL in .env to change model.",
	)
	go = st.button("Run Study Session", type="primary", use_container_width=True)

# Main content
placeholder = st.empty()

if go:
	if not topic or not topic.strip():
		st.warning("Please enter a valid topic before running the session.")
	else:
		with st.spinner("Running agents..."):
			result = run_session(topic.strip())
			placeholder.empty()
			if result.get("error"):
				st.error(result["error"]) 
			else:
				st.success("Session completed.")

				# Tabs for output
				research_tab, quiz_tab, explain_tab, raw_tab = st.tabs([
					"Research", "Quiz", "Explanations", "Raw"
				])

				with research_tab:
					st.subheader("Research Summary")
					st.write(result.get("research", ""))

				with quiz_tab:
					st.subheader("Quiz Questions")
					st.write(result.get("quiz", ""))

				with explain_tab:
					st.subheader("Detailed Explanations")
					st.write(result.get("explanations", ""))

				with raw_tab:
					st.code(textwrap.dedent(str(result)), language="python")
else:
	st.info("Enter a topic and click 'Run Study Session' to begin.")
