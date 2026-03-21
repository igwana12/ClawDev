from dotenv import load_dotenv
from openclaw_acp import OpenClawAgent


if __name__ == "__main__":
    load_dotenv()

    agent = OpenClawAgent(agent="programmer-a")
    while (user_input := input("User: ")) != "/exit":
        response = agent.step(user_input)
        print(f"Agent: {response}")
    agent.stop()
