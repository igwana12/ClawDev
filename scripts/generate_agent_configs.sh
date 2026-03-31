#!/bin/bash

set -e

GITEA_CONTAINER="roger-gitea"
GITEA_URL="http://host.docker.internal:3000"
GITEA_HOST="${GITEA_URL#http://}"
GITEA_HOST="${GITEA_HOST#https://}"

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
  echo "This will delete existing 'clawdev' tokens for these users."
  echo ""
  read -p "Continue? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Skipped. Users already exist, will use existing credentials."
    exit 0
  fi
fi

echo ""
echo "=== Deleting existing clawdev tokens ==="
for agent in "${AGENTS[@]}"; do
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
  echo "Creating token for $agent..."

  token=$(docker exec --user 1000:1000 $GITEA_CONTAINER gitea admin user generate-access-token \
    --username "$agent" \
    --token-name "clawdev" \
    --scopes "read:repository,write:repository,read:issue,write:issue,read:user,write:user" \
    --raw 2>&1)

  echo "  Token: $token"

  agent_dir="$TEMP_DIR/workspace-$agent"
  mkdir -p "$agent_dir"

  echo "${GITEA_URL}" | sed "s|http://|http://${agent}:${token}@|" | sed "s|https://|https://${agent}:${token}@|" > "$agent_dir/.git-credentials"
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
    - name: $GITEA_HOST
      url: $GITEA_URL
      token: $token
      default: true
      ssh_host: $GITEA_HOST
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
