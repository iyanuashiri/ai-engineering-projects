import os

from deepagents import create_deep_agent

from decouple import config

from app.tools import internet_search


os.environ["LANGSMITH_API_KEY"] = config("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = config("LANGSMITH_TRACING")
os.environ["LANGSMITH_PROJECT"] = config("LANGSMITH_PROJECT")
os.environ["LANGSMITH_ENDPOINT"] = config("LANGSMITH_ENDPOINT")
os.environ["TAVILY_API_KEY"] = config("TAVILY_API_KEY")
os.environ["OPENROUTER_API_KEY"] = config("OPENROUTER_API_KEY")

# model = ChatOpenRouter(model="anthropic/claude-sonnet-4.6", api_key=OPENROUTER_API_KEY)



# System prompt to steer the agent to be an expert researcher
research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

research_agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    tools=[internet_search],
    system_prompt=research_instructions,
)


result = research_agent.invoke({"messages": [{"role": "user", "content": "What is langgraph?"}]})

# thread_config = {"configurable": {"thread_id": "1"}}