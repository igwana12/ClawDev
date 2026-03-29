# TOOLS.md - Environment Mapping

## Sandbox

- **Email:** software_test_engineer@openclaw.com
- **Python:** Using uv for package management

## Configuration

- Do NOT modify Gitea login configuration
- Do NOT modify git user configuration (name, email)
- Do NOT modify git stored remote credentials

## Skills

Before writing or reviewing code, read the relevant skill files:

- **Python:** Read `skills/python/SKILL.md` before writing or reviewing Python code
- **Gitea:** Read `skills/gitea/SKILL.md` for tea CLI usage
- **Git:** Read `skills/git-essentials/SKILL.md` for git commands

## Gitea

- **URL:** http://host.docker.internal:3000
- **CLI:** tea
- **Config:** `~/.config/tea/config.yml`

### Team Gitea Accounts

All team members have Gitea accounts:
- chief_executive_officer
- chief_product_officer
- chief_technology_officer
- chief_creative_officer
- programmer
- code_reviewer
- software_test_engineer
- counselor
- chief_human_resource_officer

## Git

- **Config:** `~/.gitconfig`
- **Credentials:** `~/.git-credentials`

## Python

- **Package Manager:** uv
- **Testing:** pytest

## Self-Improving Memory Files

| 文件 | 用途 | 读写 |
|------|------|------|
| ~/self-improving/memory.md | 热层，≤80行，每次 session 必读 | 追加写 |
| ~/self-improving/index.md | 主题索引，WARM/COLD 层目录 | 追加写 |
| ~/self-improving/heartbeat-state.md | 上次维护时间戳 | 覆盖写 |
| ~/self-improving/archive/ | 冷层存档，低频条目 | 追加写 |
| ~/self-improving/projects/ | 按项目的学习记录 | 追加写 |
