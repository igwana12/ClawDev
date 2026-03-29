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
