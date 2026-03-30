#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

print_status "Starting ClawDev deployment..."

# Check .gitignore
if git -C "$PROJECT_DIR" check-ignore -q .env 2>/dev/null; then
    print_status ".env is properly ignored by .gitignore"
else
    print_warning ".env is NOT in .gitignore, token may be exposed!"
fi

# Ask for OPENCLAW_CONFIG_HOST if not set
if [[ -z "${OPENCLAW_CONFIG_HOST:-}" ]]; then
    read -p "Enter OPENCLAW_CONFIG_HOST (default: ~/.openclaw): " config_host
    config_host="${config_host:-$HOME/.openclaw}"
    export OPENCLAW_CONFIG_HOST="$config_host"
fi

config_path="$OPENCLAW_CONFIG_HOST/openclaw.json"

if [[ ! -f "$config_path" ]]; then
    print_error "openclaw.json not found"
    print_error "Please complete OpenClaw onboard first (run 'openclaw'), then run this script again"
    exit 1
fi

print_status "Found openclaw.json, proceeding with deployment..."

# Generate random token
remote_token=$(openssl rand -hex 16 2>/dev/null || head -c 32 /dev/urandom | xxd -p)

# Get gateway port from config
gateway_port=$(python3 -c "import json; print(json.load(open('$config_path')).get('gateway', {}).get('port', 18789))")

# Write .env file
cat > .env << EOF
OPENCLAW_CONFIG_HOST=$OPENCLAW_CONFIG_HOST
OPENCLAW_GATEWAY_TOKEN=$remote_token
OPENCLAW_GATEWAY_URL=ws://127.0.0.1:$gateway_port
EOF
print_status "Created .env file"

# Backup original config with timestamp (to avoid being overwritten)
initial_backup="$config_path.bak.$(date +%Y%m%d%H%M%S)"
cp "$config_path" "$initial_backup"
print_status "Initial backup: $initial_backup"

# Configure openclaw.json
print_status "Configuring openclaw.json..."

# Add acp and remote config using python
python3 << PYEOF
import json

config_path = "$config_path"

with open(config_path, "r") as f:
    config = json.load(f)

# Add acp config
config["acp"] = {
    "enabled": True,
    "defaultAgent": "main"
}

# Add remote config under gateway
gateway_port = config.get("gateway", {}).get("port", 18789)
if "gateway" not in config:
    config["gateway"] = {}
config["gateway"]["remote"] = {
    "url": f"ws://127.0.0.1:{gateway_port}",
    "token": "$remote_token"
}

with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

print("Config updated")
PYEOF

print_warning "=========================================="
print_warning "REMOTE TOKEN GENERATED"
print_warning "=========================================="
print_warning "Token: $remote_token"
print_warning "If you forget this token, check $config_path"
print_warning ""

# Validate and restart gateway
print_status "Validating openclaw.json..."
if openclaw config validate 2>&1; then
    print_status "Config validated successfully"
else
    print_warning "Config validation failed, but continuing..."
fi

print_status "Restarting OpenClaw gateway..."
openclaw gateway restart 2>&1 || print_warning "Gateway restart failed or skipped"

# Check if .env exists
if [[ ! -f ".env" ]]; then
    print_warning ".env not found, creating from template..."
    cp .env.template .env
    print_warning "Please edit .env file with your configuration and run this script again"
    exit 1
fi

# Install dependencies
print_status "Installing dependencies..."
uv sync

# Build sandbox image
print_status "Building openclaw-sandbox:bookworm-slim..."
if docker build -t openclaw-sandbox:bookworm-slim -f Dockerfile.sandbox .; then
    print_status "Sandbox image built successfully"
else
    print_warning "Failed to build sandbox image, continuing..."
fi

# Create agents
print_status "Creating agents..."
source .venv/bin/activate
./scripts/create_agents.sh

# Start Gitea container
print_status "Starting Gitea container..."
if docker ps -a --format '{{.Names}}' | grep -q "^roger-gitea$"; then
    if docker ps --format '{{.Names}}' | grep -q "^roger-gitea$"; then
        print_warning "Gitea container already running"
    else
        print_warning "Gitea container exists but not running, starting..."
        docker start roger-gitea
    fi
else
    docker run -d --name roger-gitea \
        -e USER_UID=1000 -e USER_GID=1000 \
        -e GITEA__server__HTTP_PORT=3000 \
        -e GITEA__server__ROOT_URL=http://host.docker.internal:3000 \
        -e GITEA__database__DB_TYPE=sqlite3 \
        -e GITEA__actions__ENABLED=false \
        -e TZ=UTC \
        -e GITEA__repository__FORCE_PRIVATE=false \
        -e GITEA__repository__DEFAULT_PRIVATE=public \
        -e GITEA__service__ALLOW_ONLY_INTERNAL_REGISTRATION=true \
        -e GITEA__repository__DEFAULT_PUSH_CREATE_PRIVATE=false \
        -p 3000:3000 \
        -v ./volumes/gitea:/data \
        -v /etc/timezone:/etc/timezone:ro \
        -v /etc/localtime:/etc/localtime:ro \
        gitea/gitea:latest
fi

print_status "Gitea started at http://host.docker.internal:3000"
print_warning "Waiting for Gitea to be ready..."
until curl -sf http://localhost:3000/api/healthz >/dev/null 2>&1; do
    echo -n "."
    sleep 3
done
echo ""
print_status "Gitea is ready"
print_warning "Complete Gitea web setup at http://host.docker.internal:3000 then press Enter..."
read -r

# Wait a bit more for DB to be fully initialized
sleep 3

# Create agent accounts
print_status "Creating agent accounts in Gitea..."
rm -f /tmp/clawdev-last-credentials-dir
./scripts/generate_agent_configs.sh

# Read credentials directory from temp file
credentials_dir=$(cat /tmp/clawdev-last-credentials-dir 2>/dev/null)
rm -f /tmp/clawdev-last-credentials-dir

if [[ -z "$credentials_dir" || ! -d "$credentials_dir" ]]; then
    print_error "Failed to get credentials directory"
    exit 1
fi

# Deploy agent credentials
print_status "Deploying agent credentials..."
GENERATED_CREDENTIALS_DIR="$credentials_dir" ./scripts/deploy_agent_credentials.sh

# Deploy agent configs
print_status "Deploying agent configurations..."
./scripts/deploy_agent_configs.sh

# Install skills via clawhub
workdir="${OPENCLAW_CONFIG_HOST:-$HOME/.openclaw}/workspace"

if [ -n "${MANUAL_SKILL_INSTALL:-}" ]; then
    print_warning "MANUAL_SKILL_INSTALL is set - manual skill installation mode"
    echo ""
    echo "Please manually download skills to: $workdir/skills/"
    echo "Required skills: gitea, git-essentials, python, code, self-improving, ddgs, crawl4ai-skill"
    echo ""
    read -p "Press Enter after manually downloading skills to continue... "
else
    print_status "Installing skills via clawhub..."

    skills=(
        "gitea"
        "git-essentials"
        "python"
        "code"
        "self-improving"
        "ddgs"
        "crawl4ai-skill"
    )

    for skill in "${skills[@]}"; do
        print_status "Installing $skill..."
        clawhub install "$skill" --workdir "$workdir" 2>/dev/null || print_warning "Failed to install $skill, skipping..."
    done
fi

# Configure sandbox in openclaw.json
print_status "Configuring sandbox in openclaw.json..."

python3 << 'PYEOF'
import json
import os

config_host = os.environ.get("OPENCLAW_CONFIG_HOST", os.path.expanduser("~/.openclaw"))
config_path = os.path.join(config_host, "openclaw.json")

try:
    with open(config_path, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"Error: {config_path} not found")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in {config_path}: {e}")
    exit(1)

# Add sandbox config to agents.defaults
if "agents" not in config:
    config["agents"] = {}
if "defaults" not in config["agents"]:
    config["agents"]["defaults"] = {}

sandbox_config = {
    "mode": "non-main",
    "workspaceAccess": "ro",
    "scope": "agent"
}

config["agents"]["defaults"]["sandbox"] = sandbox_config

# Write updated config
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

print(f"Updated: {config_path}")
PYEOF

print_status "=========================================="
print_status "Deployment completed!"
print_status ""
print_status "To run ClawDev:"
echo "  uv run src/main.py \"your task description\""
