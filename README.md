# ClawDev

<p align="center">
  <img src='misc/logo.png' width=400>
</p>

<p align="center">
  Multi-agent software development framework based on OpenClaw ACP
</p>

## Overview

ClawDev is a multi-agent software development framework that combines OpenClaw ACP (Agent Client Protocol) with a structured development workflow. It provides AI agents with different roles (CEO, CTO, Programmer, Reviewer, Tester) that collaborate through specialized phases including demand analysis, coding, testing, and documentation.

## Acknowledgment

ClawDev is inspired by and builds upon [ChatDev](https://github.com/OpenBMB/ChatDev), a virtual software company operated by intelligent agents. ChatDev was developed by the [OpenBMB](https://openbmb.thudm.cn/) team and introduced in their paper:

> **ChatDev: Communicative Agents for Software Development**
> 
> Paper: https://arxiv.org/abs/2307.07924

We express our gratitude to the ChatDev team for their pioneering work in multi-agent collaborative software development.

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from openclaw_acp import OpenClawAgent
from clawdev import ChatChain, AgentAdapter

agent_configs = {
    "Chief Executive Officer": "chief_executive_officer",
    "Chief Product Officer": "chief_product_officer",
    "Chief Technology Officer": "chief_technology_officer",
    "Programmer": "programmer",
}

adapter = AgentAdapter(agent_configs)
chain = ChatChain(adapter, config_name="default")

task = "Create a simple Python calculator application"
chain.run(task, project_name="calculator")

adapter.reset()
```

## Architecture

```
clawdev/
├── adapter/          # Agent communication adapter
├── chain/            # ChatChain orchestrator
├── env/              # Environment state management
└── phases/           # Development phases
    ├── base.py       # Phase base class
    ├── simple_phase.py    # Single dialog phase
    └── composed_phase.py  # Multi-phase composition
```

## Development Phases

1. **Demand Analysis** - Analyze requirements and determine product modality
2. **Language Choose** - Select appropriate programming language
3. **Coding** - Design, implement, and improve code
4. **Code Review** - Review code quality
5. **Testing** - Write and run tests
6. **Documentation** - Create documentation

## License

Apache License 2.0 - see [LICENSE](LICENSE) file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
