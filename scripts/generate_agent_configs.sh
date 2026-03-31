#!/bin/bash

set -e

GITEA_CONTAINER="roger-gitea"
# GITEA_URL is used for external access (health checks, user-facing messages)
GITEA_URL="${GITEA_URL:-http://localhost:3000}"

# Validate GITEA_URL - only allow localhost, 127.0.0.1, and host.docker.internal
validate_gitea_host() {
    local url="$1"
    # Extract host from URL
    local host
    host=$(echo "$url" | sed -E 's|^https?://||' | sed -E 's|[:/].*||')
    
    # Check if host is in whitelist
    case "$host" in
        localhost|127.0.0.1|host.docker.internal)
            return 0
            ;;
        *)
            echo "Error: Invalid GITEA_URL host '$host'. Only localhost, 127.0.0.1, and host.docker.internal are allowed." >&2
            return 1
            ;;
    esac
}

# Validate the URL before proceeding
if ! validate_gitea_host "$GITEA_URL"; then
    exit 1
fi

# AGENT_GITEA_URL is used for agent credentials (agents run in sandbox, need docker internal address)
# Derive from GITEA_URL by replacing host with host.docker.internal, keeping protocol and port
if [[ "$GITEA_URL" =~ ^(https?)://([^/:]+)(:[0-9]+)?(/.*)?$ ]]; then
    protocol="${BASH_REMATCH[1]}"
    port="${BASH_REMATCH[3]:-:3000}"
    path="${BASH_REMATCH[4]:-}"
    AGENT_GITEA_URL="${protocol}://host.docker.internal${port}${path}"
else
    AGENT_GITEA_URL="http://host.docker.internal:3000"
fi
GITEA_HOST="${GITEA_URL#http://}"
GITEA_HOST="${GITEA_HOST#https://}"
# Extract host from AGENT_GITEA_URL for tea config name
AGENT_GITEA_HOST="${AGENT_GITEA_URL#http://}"
AGENT_GITEA_HOST="${AGENT_GITEA_HOST#https://}"

AGENTS=(
  "chief_creative_officer"
  "chief_executive_officer"
  "chief_human_resource_officer"
  "chief_product_officer"
  "chief_technology_officer"
  "code_reviewer"
  "counselor"
  "programmer"
  "software_test_engineer"
)

echo "=== Checking Gitea users ==="
echo ""

existing_users=()
missing_users=()

for agent in "${AGENTS[@]}"; do
  if docker exec --user 1000:1000 $GITEA_CONTAINER gitea admin user list 2>/dev/null | grep -q "^.*[[:space:]]$agent[[:space:]]"; then
    existing_users+=("$agent")
    echo "[EXISTS] $agent"
  else
    missing_users+=("$agent")
    echo "[MISSING] $agent"
  fi
done

echo ""

if [[ ${#missing_users[@]} -gt 0 ]]; then
  echo "Creating missing users..."
  for agent in "${missing_users[@]}"; do
    echo "  Creating $agent..."
    docker exec --user 1000:1000 $GITEA_CONTAINER gitea admin user create \
      --username "$agent" \
      --password "test123456" \
      --email "${agent}@clawdev.com" \
      --must-change-password=false 2>/dev/null
    echo "    Created: $agent"
  done
fi

if [[ ${#existing_users[@]} -gt 0 ]]; then
  echo ""
  echo "Warning: ${#existing_users[@]} users already exist: ${existing_users[*]}"
  echo "Options:"
  echo "  [r] Delete existing tokens and regenerate (recommended)"
  echo "  [s] Skip these agents (keep existing tokens)"
  echo "  [a] Abort deployment"
  echo ""
  read -p "Choice (r/s/a): " -n 1 -r choice
  echo
  case "$choice" in
    [Rr])
      echo "Will regenerate tokens for all users."
      ;;
    [Ss])
      echo "Skipping token generation for existing users."
      echo "${existing_users[*]}" > /tmp/clawdev-skipped-agents
      ;;
    *)
      echo "Aborted."
      exit 1
      ;;
  esac
fi

SKIPPED_AGENTS=()
if [[ -f /tmp/clawdev-skipped-agents ]]; then
  read -ra SKIPPED_AGENTS < /tmp/clawdev-skipped-agents
  echo "Skipping agents: ${SKIPPED_AGENTS[*]}"
fi

echo ""
echo "=== Deleting existing clawdev tokens ==="
for agent in "${AGENTS[@]}"; do
  # Skip if agent is in skipped list
  if [[ " ${SKIPPED_AGENTS[*]} " =~ " $agent " ]]; then
    echo "  [SKIP] $agent: in skipped list"
    continue
  fi

  user_id=$(docker exec $GITEA_CONTAINER sh -c "sqlite3 /data/gitea/gitea.db 'SELECT id FROM user WHERE name=\"$agent\";'" 2>/dev/null)
  if [[ -n "$user_id" ]]; then
    docker exec $GITEA_CONTAINER sh -c "sqlite3 /data/gitea/gitea.db 'PRAGMA busy_timeout=5000; DELETE FROM access_token WHERE uid=$user_id AND name=\"clawdev\";'" 2>/dev/null || echo "  Warning: failed to delete token for $agent, continuing..."
    echo "  Deleted clawdev token for: $agent"
  fi
done

echo ""
echo "=== Generating tokens and configs ==="

TEMP_DIR=$(mktemp -d)
echo "Output: $TEMP_DIR"
echo ""

for agent in "${AGENTS[@]}"; do
  # Skip if agent is in skipped list
  if [[ " ${SKIPPED_AGENTS[*]} " =~ " $agent " ]]; then
    echo "Skipping $agent (user chose to skip)"
    continue
  fi

  echo "Creating token for $agent..."

  token=$(docker exec --user 1000:1000 $GITEA_CONTAINER gitea admin user generate-access-token \
    --username "$agent" \
    --token-name "clawdev" \
    --scopes "read:repository,write:repository,read:issue,write:issue,read:user,write:user" \
    --raw 2>&1)

  echo "  Token: $token"

  agent_dir="$TEMP_DIR/workspace-$agent"
  mkdir -p "$agent_dir"

  # Use AGENT_GITEA_URL for credentials (agents run in sandbox)
  echo "${AGENT_GITEA_URL}" | sed "s|http://|http://${agent}:${token}@|" | sed "s|https://|https://${agent}:${token}@|" > "$agent_dir/.git-credentials"
  chmod 600 "$agent_dir/.git-credentials"

  cat > "$agent_dir/.gitconfig" << EOF
[user]
	name = $agent
	email = $agent@clawdev.com
[credential]
	helper = store --file /workspace/.git-credentials
EOF

  mkdir -p "$agent_dir/.config/tea"
  cat > "$agent_dir/.config/tea/config.yml" << EOF
logins:
    - name: $AGENT_GITEA_HOST
      url: $AGENT_GITEA_URL
      token: $token
      default: true
      ssh_host: $AGENT_GITEA_HOST
      ssh_key: ""
      insecure: false
      ssh_certificate_principal: ""
      ssh_agent: false
      ssh_key_agent_pub: ""
      version_check: true
      user: $agent
      created: $(date +%s)
      refresh_token: ""
      token_expiry: 0
preferences:
    editor: false
    flag_defaults:
        remote: ""
EOF

  echo "  Generated: $agent"
done

echo ""
echo "Done! Total: ${#AGENTS[@]} agents"
echo "Output: $TEMP_DIR"

# Write credentials dir to temp file for other scripts to read
echo "$TEMP_DIR" > /tmp/clawdev-last-credentials-dir

echo ""
echo "To deploy to workspace, run:"
echo "  GENERATED_CREDENTIALS_DIR=$TEMP_DIR ./scripts/deploy_agent_credentials.sh"
