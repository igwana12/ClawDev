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

### Gitea Skill

Refer to `gitea` skill for detailed tea CLI usage. Key commands:

```bash
tea pulls               # List pull requests
tea pull review        # Review a pull request
tea api                # Make API requests
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
