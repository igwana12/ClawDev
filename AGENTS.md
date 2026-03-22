# AGENTS.md - ClawDev Project Guidelines

## Project Overview

This project (`clawdev`) is a Python wrapper for OpenClaw/ChatDev that provides an Agent PCP (Agent Communication Protocol) client for automated code generation. The main entry point is `src/main.py` and the core package is `src/openclaw_acp/`.

## Build, Lint, and Test Commands

### Running the Project
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows

# Run main entry point
python -m src.main

# Or run directly
python src/main.py
```

### Linting and Formatting
```bash
# Format code with Black
black src/

# Run Ruff linter
ruff check src/

# Fix auto-fixable issues
ruff check --fix src/
```

### Running Tests
```bash
# Install pytest first (if not in venv)
uv pip install pytest

# Run all tests
pytest tests/

# Run a single test file
pytest tests/test_agent.py

# Run a single test function
pytest tests/test_agent.py::TestOpenClawAgent::test_default_gateway_url

# Run tests matching a pattern
pytest tests/ -k "test_default"
```

## Code Style Guidelines

### General Principles
- Follow Python's PEP 8 style guide
- Use type hints for all function parameters and return values
- Write concise, readable code
- Keep functions focused and single-purpose

### Naming Conventions
- **Classes**: PascalCase (e.g., `OpenClawAgent`)
- **Functions/variables**: snake_case (e.g., `gateway_url`, `async_step`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- **Private methods**: prefix with underscore (e.g., `_initialize`)

### Import Organization
Order imports in the following groups (separate each group with a blank line):
1. Standard library imports
2. Third-party imports
3. Local application imports (relative imports)

```python
import asyncio
import json
import os
from queue import Queue, Empty
from typing import AsyncGenerator, Callable, Optional

from .utils import require_api_key
```

### Type Hints
- Use built-in types from `typing` module (Python < 3.9): `Optional[str]`, `List[int]`
- Use modern union syntax when targeting Python 3.12+: `str | None`
- Use `AsyncGenerator` for async generators
- Always specify return types for functions

### Formatting
- Line length: follow Black's default (88 characters)
- Use Black for automatic formatting: `black src/`
- Add spaces around operators: `x = 1`, not `x=1`
- Use f-strings for string formatting

### Error Handling
- Use descriptive error messages (can be in Chinese as per project convention)
- Raise specific exceptions: `RuntimeError`, `TimeoutError`, `ValueError`
- Handle exceptions appropriately with try/except blocks
- Use context managers (`with`) for resource management

```python
if not api_key:
    raise ValueError(f"API key '{key}' not provided")
```

### Async Code
- Use `async`/`await` for I/O-bound operations
- Prefer `asyncio` over threading when possible
- Use `run_in_executor` for blocking operations in async context

### Documentation
- Use docstrings for classes and complex functions
- Include usage examples in class docstrings
- Keep comments concise and meaningful

### File Structure
```
src/
├── main.py              # Entry point
└── openclaw_acp/
    ├── __init__.py      # Package exports
    ├── agent.py         # Core OpenClawAgent class
    └── utils.py         # Utility functions

tests/
├── __init__.py
├── test_agent.py        # Tests for OpenClawAgent
└── test_utils.py        # Tests for utility functions
```

## Environment Variables
- `OPENCLAW_GATEWAY_URL`: WebSocket URL for OpenClaw gateway (default: `ws://127.0.0.1:18789`)
- `OPENCLAW_GATEWAY_TOKEN`: API token for authentication
- `OPENCLAW_HIDE_BANNER`: Set to `1` to hide banner
- `OPENCLAW_SUPPRESS_NOTES`: Set to `1` to suppress notes
- Copy `.env.template` to `.env` and configure as needed

## Common Development Tasks

### Adding a New Feature
1. Create a new module in `src/openclaw_acp/`
2. Export it in `src/openclaw_acp/__init__.py`
3. Add type hints and docstrings
4. Format with Black and lint with Ruff

### Running the Agent
```python
from openclaw_acp import OpenClawAgent

agent = OpenClawAgent(auto_start=True)
response = agent("Your message here")
agent.stop()
```

### Using Async Methods
```python
import asyncio
from openclaw_acp import OpenClawAgent

async def main():
    agent = OpenClawAgent(auto_start=True)
    response = await agent.async_step("Your message")
    agent.stop()

asyncio.run(main())
```

### Using Streaming
```python
import asyncio
from openclaw_acp import OpenClawAgent

async def main():
    agent = OpenClawAgent(auto_start=True)
    async for chunk in agent.stream("Your message"):
        print(chunk, end="")
    agent.stop()

asyncio.run(main())
```

## Notes for Agentic Coding
- This project wraps the OpenClaw CLI tool via subprocess
- The agent communicates over WebSocket using JSON-RPC 2.0 protocol
- When modifying the agent, ensure proper session and request ID handling
- Test changes with actual OpenClaw gateway when possible

## OpenClaw ACP Protocol

### JSON-RPC 2.0 Message Format
```json
{
    "jsonrpc": "2.0",
    "id": "unique-request-id",
    "method": "session/prompt",
    "params": {
        "sessionId": "session-id",
        "prompt": [{"type": "text", "text": "message content"}]
    }
}
```

### Available Methods
- `initialize`: Initialize connection with gateway
- `session/new`: Create new session
- `session/prompt`: Send prompt to agent

### Agent Session
- Each OpenClawAgent creates a unique session with format: `agent:{agent_name}:{session_suffix}`
- The `cwd` parameter determines the agent's working directory
- Default workspace: `~/.openclaw/workspace-{agent_name}`

### Conversation History
- OpenClaw ACP is one-way message passing (prompt -> response)
- To maintain conversation history, inject history into the prompt text
- Example pattern:
```python
history_text = "\n".join([f"[{i}] {msg}" for i, msg in enumerate(history)])
prompt = f"[History]\n{history_text}\n\n[Current]: {new_message}"
```

## ClawDev Phase System

### Phase Configuration
Each phase in `configs/default/PhaseConfig.json` specifies:
- `assistant_role_name`: The agent role that responds
- `user_role_name`: The agent role that initiated the request
- `phase_prompt`: Template for generating prompts

### Agent Adapter
- `AgentAdapter` maps role names to OpenClaw agent names
- The `send(message, role)` method routes messages to the correct agent
- Each agent gets its own working directory based on `OPENCLAW_CONFIG_HOST`

### Agent Role Mapping
| Role | Agent Name | Workspace |
|------|------------|----------|
| Chief Executive Officer | chief_executive_officer | workspace-chief_executive_officer |
| Chief Product Officer | chief_product_officer | workspace-chief_product_officer |
| Chief Technology Officer | chief_technology_officer | workspace-chief_technology_officer |
| Programmer | programmer | workspace-programmer |
| Code Reviewer | code_reviewer | workspace-code_reviewer |
| Software Test Engineer | software_test_engineer | workspace-software_test_engineer |
| Chief Creative Officer | chief_creative_officer | workspace-chief_creative_officer |
| Counselor | counselor | workspace-counselor |
| Chief Human Resource Officer | chief_human_resource_officer | workspace-chief_human_resource_officer |

## Pending Tasks
- [ ] Implement multi-agent conversation with conversation history injection
- [ ] Support role-playing where agents interact with each other autonomously
- [ ] Add support for streaming responses in AgentAdapter
