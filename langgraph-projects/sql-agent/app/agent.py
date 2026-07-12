import os
from typing import Any

from langchain.agents import create_agent
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.types import interrupt
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import AgentState, ContextT, ResponseT, StateT

from decouple import config

from app.tools import sql_tools


os.environ["LANGSMITH_API_KEY"] = config("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = config("LANGSMITH_TRACING")
os.environ["LANGSMITH_PROJECT"] = config("LANGSMITH_PROJECT")
os.environ["LANGSMITH_ENDPOINT"] = config("LANGSMITH_ENDPOINT")


# Initialize an LLM
OPENROUTER_API_KEY = config("OPENROUTER_API_KEY")

model = ChatOpenRouter(model="anthropic/claude-sonnet-4.6", api_key=OPENROUTER_API_KEY)


class SimpleHITLMiddleware(AgentMiddleware[StateT, ContextT, ResponseT]):
    """Simple human-in-the-loop middleware using LangGraph's interrupt().

    Resume values accepted (all equivalent):
      - "approve" / "yes" / True / 1  → approve
      - "reject" / "no" / False / 0   → reject
      - {"type": "approve"}           → approve
      - {"decisions": [{"type": "approve"}]}  → approve (Studio structured format)
    """

    def __init__(self, interrupt_on: list[str]) -> None:
        super().__init__()
        self.interrupt_on = set(interrupt_on)

    def _normalize_resume(self, raw: Any) -> str:
        """Normalize any resume value to 'approve' or 'reject'."""
        # Handle structured HITLResponse from Studio buttons
        if isinstance(raw, dict):
            if "decisions" in raw:
                decisions = raw["decisions"]
                if decisions and isinstance(decisions[0], dict):
                    return decisions[0].get("type", "reject")
            if "type" in raw:
                return raw["type"]

        # Handle plain string/bool/int
        if isinstance(raw, str):
            return "approve" if raw.lower() in ("approve", "yes", "true", "1") else "reject"
        if isinstance(raw, (bool, int)):
            return "approve" if raw else "reject"

        return "reject"

    def after_model(
        self, state: AgentState[Any], runtime: Any
    ) -> dict[str, Any] | None:
        messages = state["messages"]
        if not messages:
            return None

        last_ai_msg = next(
            (msg for msg in reversed(messages) if isinstance(msg, AIMessage)), None
        )
        if not last_ai_msg or not last_ai_msg.tool_calls:
            return None

        revised_tool_calls = []
        artificial_tool_messages = []

        for tool_call in last_ai_msg.tool_calls:
            if tool_call["name"] not in self.interrupt_on:
                revised_tool_calls.append(tool_call)
                continue

            # Pause and ask for human approval
            raw_decision = interrupt(
                {
                    "description": f"Tool execution pending approval\n\nTool: {tool_call['name']}\nArgs: {tool_call['args']}",
                    "tool": tool_call["name"],
                    "args": tool_call["args"],
                }
            )

            decision = self._normalize_resume(raw_decision)

            if decision == "approve":
                revised_tool_calls.append(tool_call)
            elif decision == "reject":
                artificial_tool_messages.append(
                    ToolMessage(
                        content=(
                            f"User rejected the tool call for `{tool_call['name']}`. "
                            "The tool was not executed. Do not retry unless the user asks."
                        ),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                        status="error",
                    )
                )
            else:
                # Unknown decision type — treat as approve to avoid blocking
                revised_tool_calls.append(tool_call)

        last_ai_msg.tool_calls = revised_tool_calls
        return {"messages": [last_ai_msg, *artificial_tool_messages]}

    async def aafter_model(
        self, state: AgentState[Any], runtime: Any
    ) -> dict[str, Any] | None:
        return self.after_model(state, runtime)


# Use create_agent
system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
    dialect="sqlite",
    top_k=5,
)

sql_agent = create_agent(
    model,
    sql_tools,
    system_prompt=system_prompt,
    # middleware=[
    #     SimpleHITLMiddleware(interrupt_on=["sql_db_query"]),
    # ],
    # checkpointer=InMemorySaver(),
)


# thread_config = {"configurable": {"thread_id": "1"}}