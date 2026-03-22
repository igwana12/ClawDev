# ClawDev Package

ClawDev is a multi-agent software development framework based on OpenClaw ACP. It provides a structured approach to software development using AI agents, following a waterfall model with phases for demand analysis, coding, testing, and documentation.

## Installation

To install ClawDev, run:

```bash
pip install -e .
```

## Usage

Here's a basic example of how to use ClawDev:

```python
from openclaw_acp import OpenClawAgent
from clawdev import ChatChain, AgentAdapter

# Create an OpenClaw agent
agent = OpenClawAgent(agent="programmer-a")

# Create an adapter for the agent
adapter = AgentAdapter(agent)

# Create a ChatChain with the adapter
chain = ChatChain(adapter, config_name="default")

# Define a task
task = "Create a simple Python script that calculates the Fibonacci sequence up to n numbers and prints the result."

# Run the development chain
chain.run(task, project_name="fibonacci_calculator")

# Clean up
agent.stop()
```

## Package Structure

- `clawdev/` - Main package directory
  - `__init__.py` - Package initialization and exports
  - `adapter/` - Agent adapter for OpenClaw ACP
  - `chain/` - ChatChain orchestrator
  - `env/` - Environment management
  - `phases/` - Development phases (demand analysis, coding, testing, etc.)

## Configuration

ClawDev uses configuration files located in the `configs/` directory:

- `ChatChainConfig.json` - Defines the development process flow
- `PhaseConfig.json` - Contains prompts and settings for each phase
- `RoleConfig.json` - Defines roles and their responsibilities

## Examples

See the `examples/` directory for usage examples.