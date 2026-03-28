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

TEMP_DIR=$(mktemp -d)
echo "Generating configs to: $TEMP_DIR"

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
