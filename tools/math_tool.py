from typing import Any


def do_math(expression: str) -> Any:
	try:
		# Very restricted eval environment
		allowed_names = {
			"__builtins__": {},
		}
		return eval(expression, allowed_names, {})
	except Exception:
		return "Invalid expression."
