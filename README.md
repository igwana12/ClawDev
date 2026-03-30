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
- Docker (for Gitea container)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- clawhub (OpenClaw skill manager, install via `npm i -g clawhub` or `pnpm add -g clawhub`)
- OpenClaw (run `openclaw` to configure)

## Deployment

**Prerequisite**: Complete OpenClaw onboard first (run `openclaw` and configure vendor).

### 1. Clone

```bash
git clone https://github.com/HDAnzz/ClawDev.git
cd ClawDev
```

### 2. Set OPENCLAW_CONFIG_HOST

```bash
export OPENCLAW_CONFIG_HOST=~/.openclaw
```

The script will automatically create the `.env` file.

### 3. Run Deployment Script

```bash
./scripts/deploy.sh
```

The script will automatically:
1. Check .gitignore
2. Configure openclaw.json (acp + remote)
3. Install dependencies
4. Create agents
5. Start Gitea container
6. Generate agent accounts
7. Deploy credentials
8. Install skills
9. Configure sandbox

> ⚠️ After Gitea starts, visit http://host.docker.internal:3000 to complete setup

### 4. Run ClawDev

```bash
uv run src/main.py "your task description"
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
