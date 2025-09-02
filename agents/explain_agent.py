import os
from typing import Tuple

from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq


def create_explain_agent() -> Tuple[ChatGroq, SystemMessage]:
	"""Create the explanation agent backed by a Groq LLM."""
	model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
	llm = ChatGroq(
		groq_api_key=os.getenv("GROQ_API_KEY"),
		model_name=model_name,
		temperature=0.3,
	)
	system_prompt = SystemMessage(
		content=(
			"You are a teaching assistant. Explain why an answer is correct or "
			"incorrect using step-by-step reasoning and simplified notes."
		)
	)
	return llm, system_prompt
