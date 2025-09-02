import requests


def wikipedia_search(query: str) -> str:
	url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
	resp = requests.get(url, timeout=15)
	if resp.ok:
		return resp.json().get("extract", "")
	return "No result found."
