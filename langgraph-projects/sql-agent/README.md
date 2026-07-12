# SQL Agent

A LangGraph-powered agent that answers natural language questions against a SQLite database. It uses tool calling to list tables, inspect schemas, validate queries, and execute SQL — with a human-in-the-loop interrupt before any query runs.

## Features

- Natural language → SQL query generation
- Automatic query validation before execution via `sql_db_query_checker`
- Human-in-the-loop approval before any `SELECT` query is executed
- LangSmith tracing support
- Runs locally via LangGraph Studio or the LangGraph CLI

## Project Structure

```
sql-agent/
├── app/
│   ├── agent.py        # Agent definition and middleware
│   ├── tools.py        # SQL tools (list tables, schema, query, checker)
│   ├── load.py         # Downloads the Chinook sample database
│   ├── db.py           # Quick DB inspection script
│   ├── .env            # Your local environment variables (git-ignored)
│   └── .env_example    # Environment variable template
├── langgraph.json       # LangGraph server config
├── pyproject.toml
└── README.md
```

## Prerequisites

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — for dependency management
- [LangGraph CLI](https://langchain-ai.github.io/langgraph/cloud/reference/cli/) — installed via `uv`
- An [OpenRouter](https://openrouter.ai/) API key
- A [LangSmith](https://smith.langchain.com/) API key (for tracing)

## Installation

**1. Clone the repo and navigate to this project:**

```bash
cd langgraph-projects/sql-agent
```

**2. Install dependencies:**

```bash
uv sync
```

**3. Set up environment variables:**

Copy the example env file and fill in your keys:

```bash
cp app/.env_example app/.env
```

Edit `app/.env`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key

LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=sql-agent
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

**4. Download the Chinook sample database:**

```bash
uv run python app/load.py
```

This downloads `Chinook.db` into the `app/` directory. The database contains sample music store data including tables like `Artist`, `Album`, `Track`, `Genre`, `Customer`, and more.

To verify the database loaded correctly:

```bash
uv run python app/db.py
```

## Running the Agent

**1. Start the LangGraph development server:**

```bash
uv run langgraph dev
```

The server starts at `http://localhost:2024`.

**2. Open LangGraph Studio:**

Go to [smith.langchain.com/studio](https://smith.langchain.com/studio) in your browser and connect to your local server using the URL:

```
http://localhost:2024
```

**3. Start a new thread and ask a question**, for example:

- *"Which genre has the longest average track length?"*
- *"Who are the top 5 artists by number of albums?"*
- *"How many customers are from Brazil?"*

The agent will automatically inspect the database schema and build the appropriate SQL query before asking for your approval.

## Human-in-the-Loop

Before any SQL query is executed, the agent pauses and asks for your approval in LangGraph Studio. You will see an interrupt with the query and options to approve or reject.

To **approve**, type `approve` in the resume input box and submit.  
To **reject**, type `reject` — the agent will be informed and will not retry.

## Tools

| Tool | Description |
|---|---|
| `sql_db_list_tables` | Returns all table names in the database |
| `sql_db_schema` | Returns the schema and sample rows for given tables |
| `sql_db_query_checker` | Validates a SQL query for common mistakes before execution |
| `sql_db_query` | Executes a validated SQL query and returns results |

## Notes

- The agent only runs `SELECT` queries. All DML statements (`INSERT`, `UPDATE`, `DELETE`, `DROP`) are blocked by the system prompt.
- Results are limited to 5 rows by default unless you specify otherwise.
- The model used is `anthropic/claude-sonnet-4.6` via OpenRouter. You can change this in `app/agent.py` and `app/tools.py`.
