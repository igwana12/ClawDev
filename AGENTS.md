# AGENTS.md - ClawDev Project Guidelines

## Project Overview

This project (`clawdev`) is a Python framework that combines OpenClaw ACP (Agent Client Protocol) with a multi-agent collaboration system for automated code generation. It provides:
- ACP client for communicating with OpenClaw agents
- ChatChain orchestration for managing multi-agent dialog workflows
- Phase-based development process (demand analysis, coding, review, testing, etc.)

The main entry point is `src/main.py` and the core packages are `src/openclaw_acp/` and `src/clawdev/`.

## Build, Lint, and Test Commands

### Running Tests and Linting in Docker Container
The project runs in Docker. Code directory is mounted at `/app/ClawDev` in the container. Always use docker exec to run tools from the project's virtual environment to avoid corrupting the local venv.

```bash
# Run all tests in docker container
docker exec -w /app/ClawDev clawdev-openclaw-gateway-1 /app/ClawDev/.venv/bin/pytest tests/ -v

# Run a single test file
docker exec -w /app/ClawDev clawdev-openclaw-gateway-1 /app/ClawDev/.venv/bin/pytest tests/test_agent.py -v

# Run linting in docker container
docker exec -w /app/ClawDev clawdev-openclaw-gateway-1 /app/ClawDev/.venv/bin/ruff check src/ tests/
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
├── main.py                  # Entry point
├── openclaw_acp/            # OpenClaw ACP client
│   ├── __init__.py
│   ├── agent.py             # OpenClawAgent class
│   └── utils.py
└── clawdev/                 # ClawDev multi-agent framework
    ├── __init__.py
    ├── adapter/
    │   └── agent_adapter.py # Agent communication adapter
    ├── chain/
    │   └── chain.py         # ChatChain orchestration
    ├── env/
    │   └── env.py           # ChatEnv state management
    └── phases/
        ├── base.py          # Phase abstract base class
        ├── simple_phase.py # SimplePhase single dialog
        └── composed_phase.py # ComposedPhase multi-subphase

tests/
├── __init__.py
├── test_agent.py            # Tests for OpenClawAgent
├── test_agent_routing.py    # Tests for agent routing
├── test_clawdev.py          # Basic functionality tests
├── test_clawdev_workflow.py # Workflow integration tests
└── test_utils.py

configs/default/
├── ChatChainConfig.json     # Chain configuration with session context
└── PhaseConfig.json          # Phase configurations with prompts
```

## Environment Variables
- `OPENCLAW_GATEWAY_URL`: WebSocket URL for OpenClaw gateway (default: `ws://127.0.0.1:18789`)
- `OPENCLAW_GATEWAY_TOKEN`: API token for authentication
- `OPENCLAW_HIDE_BANNER`: Set to `1` to hide banner
- `OPENCLAW_SUPPRESS_NOTES`: Set to `1` to suppress notes
- Copy `.env.template` to `.env` and configure as needed

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

## ClawDev Multi-Agent System

### Dialog-Based Phase Execution

Each phase executes a dialog between two agents:
1. **user_role**: Initiates the conversation by sending instructions
2. **assistant_role**: Receives instructions and responds

The dialog continues until the `<result>` tag is detected in a response.

### Phase Architecture

#### Phase Base Class (`src/clawdev/phases/base.py`)
- Abstract base class for all phases
- Handles dialog execution, environment updates, and result detection
- Key method: `_should_end_dialog()` - detects `<result>` tags

#### SimplePhase (`src/clawdev/phases/simple_phase.py`)
- Single dialog phase execution
- Executes one conversation between two agents
- Terminates when `<result>` tag is detected

#### ComposedPhase (`src/clawdev/phases/composed_phase.py`)
- Multiple sub-phases executed in sequence
- Each sub-phase is a complete phase
- Continues until all sub-phases complete or max iterations reached

### Phase Configuration

Each phase in `configs/default/PhaseConfig.json` specifies:
```json
{
    "assistant_role_name": "Chief Product Officer",
    "user_role_name": "Chief Executive Officer",
    "max_dialog_turns": 6,
    "initiator_prompt": [
        "[MESSAGE] Send a message to {assistant_role} to begin discussing the current task.",
        "[CRITICAL] Write ONLY a message to instruct {assistant_role}. Do NOT simulate any response.",
        "[RESULT TAGS] Both parties must NOT use <result> tags until reaching agreement.",
        "[TASK] Analyze user requirements and recommend the best product modality.",
        "[CONTEXT] {context}"
    ],
    "context": "User Request: {task}\n\nAvailable Modalities:\n- Image\n- Application\n- ...",
    "dialog_prompt": "{the_other_role} said: {content}"
}
```

### Dialog Termination

The dialog ends when a message contains `<result>` tags:
```xml
<result>Done</result>
```

**Quote Detection Rules:**
- Only checks characters immediately surrounding `<result>`
- If `<result>` is inside quotes (`"`, `'`, `` ` ``), it does NOT end the dialog
- Handles edge cases: `<result>` at start of text

Agents should:
- Only use `<result>` tags when they have reached a conclusion
- Not include `<result>` in messages until discussion is complete

### Session Context

Session context is sent to agents during initialization via `ChatChain.make_recruitment()`:
```json
"session_context_template": [
    "[Session Context]",
    "Hello! {role_name} from ClawDev.",
    "This is a system message sent by an automated program.",
    "",
    "[Mission]",
    "The mission is to successfully complete the task assigned by the customer.",
    "",
    "[Gitea Workflow]",
    "- Use 'tea' CLI to interact with Gitea at http://host.docker.internal:3000",
    "- All code changes should go through PR workflow"
]
```

### Coding Workflow

The Coding phase is a ComposedPhase consisting of:

1. **CodingInit**: CTO creates Gitea repository
   - Creates public repo using `tea repo create`
   - Adds Programmer as repository member
   - Notifies Programmer of repository URL

2. **CodingImprove**: Programmer writes code and creates PR
   - Creates new branch for each task
   - Writes/modifies code
   - Creates PR using `tea pr create`
   - CTO reviews and approves PR

### Agent Adapter

- `AgentAdapter` maps role names to OpenClaw agent names
- The `send(message, role)` method routes messages to the correct agent
- Each agent gets its own working directory

### Agent Role Mapping
| Role | Agent Name |
|------|------------|
| Chief Executive Officer | chief_executive_officer |
| Chief Product Officer | chief_product_officer |
| Chief Technology Officer | chief_technology_officer |
| Programmer | programmer |
| Code Reviewer | code_reviewer |
| Software Test Engineer | software_test_engineer |
| Chief Creative Officer | chief_creative_officer |
| Counselor | counselor |
| Chief Human Resource Officer | chief_human_resource_officer |

## Agent Configuration Files

Each agent has its own configuration in `configs/default/{Role}/`:

| File | Purpose |
|------|---------|
| **IDENTITY.md** | Identity card (name, emoji, avatar) |
| **SOUL.md** | Personality and communication style |
| **USER.md** | User profile and communication targets |
| **AGENTS.md** | Work protocol, environment, colleagues, boundaries |
| **TOOLS.md** | Environment mapping (paths, tools) |

## Notes for Agentic Coding

- This project combines OpenClaw agents with a dialog orchestration layer
- The agent communicates over WebSocket using JSON-RPC 2.0 protocol
- Each phase manages a dialog between two agents
- Test changes with actual OpenClaw gateway when possible
