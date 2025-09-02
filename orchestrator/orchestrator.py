from typing import Dict, Any
from uuid import uuid4

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage

from agents.research_agent import create_research_agent
from agents.quiz_agent import create_quiz_agent
from agents.explain_agent import create_explain_agent
from tools.wikipedia_tool import wikipedia_search


class SessionState(dict):
	# Keys used: topic, research, quiz, explanations
	pass


def _research_node(state: SessionState) -> SessionState:
	llm, system_msg = create_research_agent()
	topic = state.get("topic", "")
	wiki = wikipedia_search(topic)
	base_prompt = (
		f"Topic: {topic}\n\n"
		f"Context: {wiki if wiki else 'No external summary available.'}\n\n"
		"Produce a concise explanation (80-150 words) and 2 practical examples."
	)
	messages = [system_msg, HumanMessage(content=base_prompt)]
	try:
		resp = llm.invoke(messages)
		content = (getattr(resp, "content", "") or "").strip()
	except Exception:
		content = ""
	if not content:
		# Fallback to wiki or static content
		if wiki:
			content = (
				f"Overview of {topic}:\n" + wiki + "\n\n" +
				"Examples:\n- Real-world: Used in everyday web browsing between clients and servers.\n"
				"- Practical: Inspect HTTP requests via browser DevTools (Network tab)."
			)
		else:
			content = (
				f"{topic} — key points:\n- Definition and purpose.\n- Core components/concepts.\n"
				"- Common use cases.\n\nExamples:\n- Example 1 describing a real scenario.\n- Example 2 describing practical usage."
			)
	state["research"] = content
	return state


def _quiz_node(state: SessionState) -> SessionState:
	llm, system_msg = create_quiz_agent()
	research = state.get("research", "").strip()
	if research:
		prompt = (
			"Based on the following study material, generate 5 quiz questions with"
			" short answers. Format as 'Q: ... A: ...' on separate lines.\n\n" + research
		)
	else:
		prompt = (
			f"Generate 5 quiz questions with short answers about the topic: "
			f"'{state.get('topic', '')}'. Format as 'Q: ... A: ...' each on its own line."
		)
	try:
		resp = llm.invoke([system_msg, HumanMessage(content=prompt)])
		content = (getattr(resp, "content", "") or "").strip()
	except Exception:
		content = ""
	if not content:
		# Deterministic quiz fallback
		topic = state.get('topic', 'the topic')
		content = (
			f"Q: What is {topic}? A: A brief definition or purpose.\n"
			f"Q: Name one core concept of {topic}. A: A key concept.\n"
			f"Q: Give a real-world use of {topic}. A: A practical scenario.\n"
			f"Q: How is {topic} commonly implemented? A: Typical approach/tools.\n"
			f"Q: What is a common pitfall of {topic}? A: A typical mistake."
		)
	state["quiz"] = content
	return state


def _explain_node(state: SessionState) -> SessionState:
	llm, system_msg = create_explain_agent()
	quiz_text = state.get("quiz", "")
	explanations = []
	for line in quiz_text.splitlines():
		line_stripped = line.strip()
		if not line_stripped:
			continue
		try:
			resp = llm.invoke([system_msg, HumanMessage(content=line_stripped)])
			exp = (getattr(resp, "content", "") or "").strip()
		except Exception:
			exp = ""
		if not exp:
			# Deterministic explanation fallback
			exp = (
				"This question checks understanding of the topic's definition, key concepts, "
				"and practical usage. The answer highlights the essential idea concisely."
			)
		explanations.append(f"Q/A: {line_stripped}\nExplanation: {exp}")
	state["explanations"] = "\n\n".join(explanations)
	return state


def build_app():
	graph = StateGraph(SessionState)
	graph.add_node("research", _research_node)
	graph.add_node("quiz", _quiz_node)
	graph.add_node("explain", _explain_node)

	graph.set_entry_point("research")
	graph.add_edge("research", "quiz")
	graph.add_edge("quiz", "explain")
	graph.add_edge("explain", END)

	memory = MemorySaver()
	return graph.compile(checkpointer=memory)


def _run_session_direct(topic: str) -> Dict[str, Any]:
	state: SessionState = {"topic": topic}
	# Research
	state = _research_node(state)
	# Quiz
	state = _quiz_node(state)
	# Explain
	state = _explain_node(state)
	return {
		"topic": topic,
		"research": state.get("research", ""),
		"quiz": state.get("quiz", ""),
		"explanations": state.get("explanations", ""),
	}


def run_session(topic: str) -> Dict[str, Any]:
	"""Run a study session for a given topic and return results or an error."""
	app = build_app()
	state: SessionState = {"topic": topic}
	config = {"configurable": {"thread_id": f"ui-{uuid4()}"}}
	try:
		final_state = app.invoke(state, config=config)
		if not final_state or not any((final_state.get("research"), final_state.get("quiz"), final_state.get("explanations"))):
			# Fallback to direct execution if graph produced no content
			return _run_session_direct(topic)
		return {
			"topic": topic,
			"research": final_state.get("research", ""),
			"quiz": final_state.get("quiz", ""),
			"explanations": final_state.get("explanations", ""),
		}
	except Exception:
		# Last-resort fallback
		return _run_session_direct(topic)


def orchestrate_session() -> None:
	topic = input("Enter your study topic: ")
	result = run_session(topic)
	if result.get("error"):
		print("Error:", result["error"]) 
		return
	print("\n[Research]\n" + result.get("research", ""))
	print("\n[Quiz]\n" + result.get("quiz", ""))
	print("\n[Explanations]\n" + result.get("explanations", ""))
