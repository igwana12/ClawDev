# TOOLS.md - Environment Mapping

## Skills

Before writing or reviewing code, read the relevant skill files:

- **Python:** Read `skills/python/SKILL.md` before writing or reviewing Python code
- **Gitea:** Read `skills/gitea/SKILL.md` for tea CLI usage
- **Git:** Read `skills/git-essentials/SKILL.md` for git commands

## Gitea

- **URL:** http://host.docker.internal:3000
- **CLI:** tea
- **Config:** `~/.config/tea/config.yml`

### Important: URL Translation

When running in sandbox, tea CLI commands return URLs with `localhost:3000` (e.g., http://localhost:3000/chief_technology_officer/calculator). These URLs are NOT accessible from the sandbox. Always translate `localhost` to `host.docker.internal` when reporting URLs to colleagues or accessing them from sandbox.

Example:
- tea returns: http://localhost:3000/chief_technology_officer/calculator
- Use instead: http://host.docker.internal:3000/chief_technology_officer/calculator

### Gitea Skill

Refer to `gitea` skill for detailed tea CLI usage. Key commands:

```bash
tea repo create          # Create a new repository
tea repos list           # List repositories
tea pulls               # Manage pull requests
tea pr create           # Create a pull request
tea api                 # Make API requests
```

### API Reference

For API endpoints not covered by tea CLI:

```bash
# Use tea api or fetch from:
# http://host.docker.internal:3000/api/swagger
```

## Git

- **Config:** `~/.gitconfig`
- **Credentials:** `~/.git-credentials`

## Python

- **Package Manager:** uv

## Self-Improving Memory Files

| 文件 | 用途 | 读写 |
|------|------|------|
| ~/self-improving/memory.md | 热层，≤80行，每次 session 必读 | 追加写 |
| ~/self-improving/index.md | 主题索引，WARM/COLD 层目录 | 追加写 |
| ~/self-improving/heartbeat-state.md | 上次维护时间戳 | 覆盖写 |
| ~/self-improving/archive/ | 冷层存档，低频条目 | 追加写 |
| ~/self-improving/projects/ | 按项目的学习记录 | 追加写 |
