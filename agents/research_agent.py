import os
from typing import Tuple

from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq


def create_research_agent() -> Tuple[ChatGroq, SystemMessage]:
	"""Create the research agent backed by a Groq LLM."""
	model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
	llm = ChatGroq(
		groq_api_key=os.getenv("GROQ_API_KEY"),
		model_name=model_name,
		temperature=0.2,
	)
	system_prompt = SystemMessage(
		content=(
			"You are a research expert. Provide clear, concise explanations and "
			"practical examples for the given study topic. Prefer factual, "
			"beginner-friendly language and cite simple examples."
		)
	)
	return llm, system_prompt
