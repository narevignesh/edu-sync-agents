import os
from dotenv import load_dotenv

from orchestrator.orchestrator import orchestrate_session


def main() -> None:
	load_dotenv()
	orchestrate_session()


if __name__ == "__main__":
	main()
