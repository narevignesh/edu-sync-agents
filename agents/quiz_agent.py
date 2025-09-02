import os
from typing import Tuple

from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq


def create_quiz_agent() -> Tuple[ChatGroq, SystemMessage]:
	"""Create the quiz agent backed by a Groq LLM."""
	model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
	llm = ChatGroq(
		groq_api_key=os.getenv("GROQ_API_KEY"),
		model_name=model_name,
		temperature=0.4,
	)
	system_prompt = SystemMessage(
		content=(
			"You are a quiz master. Generate 3-5 relevant quiz questions with"
			" clear answers based on the provided study material."
		)
	)
	return llm, system_prompt
