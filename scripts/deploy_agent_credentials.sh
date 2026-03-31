#!/bin/bash

set -e

SKIPPED_AGENTS=()
if [[ -f /tmp/clawdev-skipped-agents ]]; then
  read -ra SKIPPED_AGENTS < /tmp/clawdev-skipped-agents
fi

if [[ -n "${GENERATED_CREDENTIALS_DIR:-}" ]]; then
  SOURCE_DIR="$GENERATED_CREDENTIALS_DIR"
elif [[ -n "${1:-}" ]]; then
  SOURCE_DIR="$1"
else
  latest_dir=$(ls -td /tmp/workspace-* 2>/dev/null | head -1)
  if [[ -n "$latest_dir" ]]; then
    echo "Found latest config directory: $latest_dir"
    read -p "Use this directory? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
      SOURCE_DIR="$latest_dir"
    else
      read -p "Enter config directory path: " SOURCE_DIR
    fi
  else
    read -p "Enter config directory path: " SOURCE_DIR
  fi
fi

TARGET_DIR="${OPENCLAW_CONFIG_HOST:-$HOME/.openclaw}"

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

echo "Deploying agent configs from: $SOURCE_DIR"
echo "To: $TARGET_DIR"
echo ""

for agent in "${AGENTS[@]}"; do
  # Skip if agent is in skipped list
  if [[ " ${SKIPPED_AGENTS[*]} " =~ " $agent " ]]; then
    echo "[SKIP] $agent: in skipped list"
    continue
  fi

  src="$SOURCE_DIR/workspace-$agent"
  tgt="$TARGET_DIR/workspace-$agent"

  if [[ ! -d "$src" ]]; then
    echo "[SKIP] $agent: source not found"
    continue
  fi

  if [[ ! -d "$tgt" ]]; then
    echo "[SKIP] $agent: target workspace not found"
    continue
  fi

  echo "Deploying $agent..."

  if [[ -f "$src/.git-credentials" ]]; then
    cp "$src/.git-credentials" "$tgt/"
    chmod 600 "$tgt/.git-credentials"
    echo "  .git-credentials"
  fi

  if [[ -f "$src/.gitconfig" ]]; then
    cp "$src/.gitconfig" "$tgt/"
    echo "  .gitconfig"
  fi

  if [[ -f "$src/.config/tea/config.yml" ]]; then
    mkdir -p "$tgt/.config/tea"
    cp "$src/.config/tea/config.yml" "$tgt/.config/tea/"
    echo "  .config/tea/config.yml"
  fi
done

echo ""
echo "Done!"
