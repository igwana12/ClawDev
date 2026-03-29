# ClawDev

<p align="center">
  Multi-agent software development framework based on OpenClaw ACP
</p>

## Overview

ClawDev is a multi-agent software development framework that combines OpenClaw ACP (Agent Client Protocol) with a structured development workflow. It provides AI agents with different roles (CEO, CPO, CTO, Programmer, Code Reviewer, Software Test Engineer, etc.) that collaborate through specialized phases including demand analysis, coding, testing, and documentation.

## Acknowledgment

ClawDev is inspired by and builds upon [ChatDev](https://github.com/OpenBMB/ChatDev), a virtual software company operated by intelligent agents. ChatDev was developed by the [OpenBMB](https://www.openbmb.cn/) team and introduced in their paper:

> **ChatDev: Communicative Agents for Software Development**
>
> Paper: https://arxiv.org/abs/2307.07924

We express our gratitude to the ChatDev team for their pioneering work in multi-agent collaborative software development.

## Requirements

- Python 3.10+
- Docker and Docker Compose
- OpenClaw Gateway running at `ws://127.0.0.1:18789`
- OpenClaw agents configured for each role

## Docker Setup

ClawDev requires OpenClaw Gateway and Gitea running via Docker.

### Prerequisites

Clone OpenClaw source code first:

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
docker build -t openclaw:local .
```

### Start Services

```bash
# Start gateway and Gitea
docker compose up -d

# Stop services
docker compose down
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCLAW_CONFIG_HOST` | `/home/node/.openclaw` | Host config directory |
| `OPENCLAW_GATEWAY_TOKEN` | - | Gateway API token |
| `OPENCLAW_GATEWAY_PORT` | `18789` | Gateway WebSocket port |
| `OPENCLAW_QMD_CUDA` | `false` | Enable CUDA for QMD |

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from clawdev import ChatChain, AgentAdapter

agent_configs = {
    "Chief Executive Officer": "chief_executive_officer",
    "Chief Product Officer": "chief_product_officer",
    "Chief Technology Officer": "chief_technology_officer",
    "Programmer": "programmer",
    "Code Reviewer": "code_reviewer",
    "Software Test Engineer": "software_test_engineer",
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

1. **DemandAnalysis** - Analyze requirements and determine product modality
2. **LanguageChoose** - Select appropriate programming language
3. **Coding** - Design, implement, and improve code
   - CodingDesign - Design project architecture
   - CodingInit - Initialize repository
   - CodingImprove - Implement and improve code
4. **CodeReview** - Review code quality
5. **Testing** - Write and run tests
6. **Documentation** - Create documentation

## License

Apache License 2.0 - see [LICENSE](LICENSE) file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
