# TOOLS.md - Environment Mapping

## Sandbox

- **Email:** chief_technology_officer@openclaw.com
- **Python:** Using uv for package management

## Gitea

- **URL:** http://host.docker.internal:3000
- **External URL:** tea commands return localhost:3000 but actual access requires host.docker.internal:3000
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
tea api                 # Make API requests
```

### API Reference

For API endpoints not covered by tea CLI, use `tea api`:

```bash
# Example: Add collaborator
tea api -X PUT -f permission=write /repos/{owner}/{repo}/collaborators/{username}

# Example: GET request
tea api "/repos/{owner}/{repo}"

# Get API documentation
# Use crawl4ai-skill or fetch from:
# http://host.docker.internal:3000/api/swagger
```

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

### tea api -f Flag

When sending data via `tea api`, use `-f` flag for string fields:

```bash
tea api -X PUT -f permission=write /repos/{owner}/{repo}/collaborators/{username}
```

### Repository Verification After Creation

After creating a repository and adding collaborators, always verify:

```bash
# Verify repository exists and configuration
tea api "/repos/{owner}/{repo}"

# Verify collaborator was added (returns collaborator details if successful)
tea api "/repos/{owner}/{repo}/collaborators/{username}"

# List all collaborators
tea api "/repos/{owner}/{repo}/collaborators"
```

## Git

- **Config:** `~/.gitconfig`
- **Credentials:** `~/.git-credentials`

## Self-Improving Memory Files

| 文件 | 用途 | 读写 |
|------|------|------|
| ~/self-improving/memory.md | 热层，≤80行，每次 session 必读 | 追加写 |
| ~/self-improving/index.md | 主题索引，WARM/COLD 层目录 | 追加写 |
| ~/self-improving/heartbeat-state.md | 上次维护时间戳 | 覆盖写 |
| ~/self-improving/archive/ | 冷层存档，低频条目 | 追加写 |
| ~/self-improving/projects/ | 按项目的学习记录 | 追加写 |
