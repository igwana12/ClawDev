from dotenv import load_dotenv
from openclaw_acp import OpenClawAgent


if __name__ == "__main__":
    load_dotenv()

    agent = OpenClawAgent(agent="programmer-a")
    print(agent.step("hello from acp"))
