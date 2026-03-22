import asyncio
import logging
import sys
from dotenv import load_dotenv
from openclaw_acp import OpenClawAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("openclaw_acp.agent")


async def main():
    load_dotenv()

    agent = OpenClawAgent(agent="programmer-a")

    while (user_input := input("User: ")) != "/exit":
        print("Agent: ", end="", flush=True)
        async for chunk in agent.stream(user_input):
            print(chunk, end="", flush=True)
        print()
    agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
