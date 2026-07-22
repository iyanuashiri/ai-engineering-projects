import os
from datetime import datetime

from deepagents import create_deep_agent

from decouple import config

from app.tools import tavily_search
from app.prompts import RESEARCH_WORKFLOW_INSTRUCTIONS, RESEARCHER_INSTRUCTIONS, SUBAGENT_DELEGATION_INSTRUCTIONS

os.environ["LANGSMITH_API_KEY"] = config("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = config("LANGSMITH_TRACING")
os.environ["LANGSMITH_PROJECT"] = config("LANGSMITH_PROJECT")
os.environ["LANGSMITH_ENDPOINT"] = config("LANGSMITH_ENDPOINT")
os.environ["TAVILY_API_KEY"] = config("TAVILY_API_KEY")
os.environ["OPENROUTER_API_KEY"] = config("OPENROUTER_API_KEY")
os.environ["HTTPX_DISABLE_HTTP2"] = "1"



max_concurrent_research_units = 3
max_researcher_iterations = 3

current_date = datetime.now().strftime("%Y-%m-%d")

INSTRUCTIONS = (
    RESEARCH_WORKFLOW_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + SUBAGENT_DELEGATION_INSTRUCTIONS.format(
        max_concurrent_research_units=max_concurrent_research_units,
        max_researcher_iterations=max_researcher_iterations,
    )
)

print(INSTRUCTIONS)

research_sub_agent = {
    "name": "research-agent",
    "description": "Delegate research to the sub-agent. Give one topic at a time.",
    "system_prompt": RESEARCHER_INSTRUCTIONS.format(date=current_date),
    "tools": [tavily_search],
}


deep_research_agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    tools=[tavily_search],
    system_prompt=INSTRUCTIONS,
    subagents=[research_sub_agent],

)
