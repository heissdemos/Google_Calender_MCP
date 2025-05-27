import asyncio
from agents.extensions.models.litellm_model import LitellmModel

from typing import Any
from agents import Agent, Runner, gen_trace_id, trace,AsyncOpenAI,OpenAIChatCompletionsModel
from agents.mcp import MCPServer, MCPServerSse , MCPServerStdio
from agents.model_settings import ModelSettings
# from dotenv import load_dotenv

# load_dotenv()

async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions=""" use tools to help user query:""",
        mcp_servers=[mcp_server],
        # model=LitellmModel(model="gemini/gemini-2.0-flash-exp", api_key="AIzaSyCyMdOXtL52eSLZDzHoY6WrpXcDSlA4-bg"),
        

    )

    history = []
    while True:
    
        message = input("Enter a question (or type 'exit' to quit): ")
        history.append({"role": "user", "content": message})
        if message.lower() == 'exit':
            print("Exiting...")
            break
        print(f"Running: {message}")
        result = await Runner.run(starting_agent=agent, input=history)
        history.append({"role": "assistant", "content": result.final_output})
        print(result.final_output)



async def main():
    async with MCPServerSse(
        params={"url": "http://localhost:8000/sse"},
        client_session_timeout_seconds=120
    ) as server:
        await run(server)

if __name__ == "__main__":
    asyncio.run(main())