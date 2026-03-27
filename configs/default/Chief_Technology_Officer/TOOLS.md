# TOOLS.md - Environment Mapping

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
# Example: Add collaborator (with JSON payload)
echo '{"permission":"write"}' | tea api --method PUT --header "Content-Type: application/json" "/repos/{owner}/{repo}/collaborators/{username}"

# Example: GET request
tea api "/repos/{owner}/{repo}"

# Get API documentation
# Use crawl4ai-skill or fetch from:
# http://host.docker.internal:3000/api/swagger
```

### Important: tea API JSON Payload Syntax

When sending JSON data via `tea api`:
- Do NOT use `--body` or `--data` flags (not recognized)
- Pipe JSON data to stdin using `echo '...' | tea api ...`
- Use `--header "Content-Type: application/json"` for proper content type
- Use double quotes for JSON keys and string values

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
