#!/bin/bash

# Script to create all required OpenClaw agents for the ClawDev framework.

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_question() {
    echo -e "${BLUE}[QUESTION]${NC} $1"
}

# Function to ask user for confirmation
confirm() {
    local prompt="$1"
    while true; do
        print_question "$prompt (y/n): "
        read -r answer
        case $answer in
            [Yy]* ) return 0 ;;
            [Nn]* ) return 1 ;;
            * ) echo "Please answer yes or no." ;;
        esac
    done
}

# Function to check if agent already exists
agent_exists() {
    local agent_name="$1"
    if openclaw agents list 2>/dev/null | grep -q "^- ${agent_name,,} ("; then
        return 0
    else
        return 1
    fi
}

# Function to remove existing agent
remove_agent() {
    local agent_name="$1"
    print_status "Removing existing agent: $agent_name"
    if openclaw agents delete "$agent_name" --force; then
        print_status "Successfully removed agent: $agent_name"
        return 0
    else
        print_error "Failed to remove agent: $agent_name"
        return 1
    fi
}

# Function to configure sandbox for agent
configure_agent_sandbox() {
    local agent_id="$1"
    
    python3 << EOF
import json
import os

config_path = os.path.expanduser(os.environ.get("OPENCLAW_CONFIG_HOST", "~/.openclaw/openclaw.json"))
with open(config_path, "r") as f:
    config = json.load(f)

agents_list = config.get("agents", {}).get("list", [])
for agent in agents_list:
    if agent.get("id") == "$agent_id":
        agent["sandbox"] = {
            "workspaceAccess": "rw",
            "docker": {
                "network": "bridge"
            }
        }
        break

with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

print("Config updated for agent: $agent_id")
EOF
}

# Function to create an OpenClaw agent
create_agent() {
    local agent_name="$1"
    print_status "Processing agent: $agent_name"
    
    # Check if agent already exists
    if agent_exists "$agent_name"; then
        print_warning "Agent '$agent_name' already exists."
        if confirm "Do you want to remove the existing agent and create a new one"; then
            if ! remove_agent "$agent_name"; then
                print_error "Failed to remove existing agent. Skipping creation."
                return 1
            fi
        else
            print_status "Skipping creation of agent: $agent_name"
            return 0
        fi
    fi
    
    # Create workspace directory - convert to lowercase, keep underscores
    local agent_id=$(echo "$agent_name" | tr '[:upper:]' '[:lower:]')
    local workspace_dir="${OPENCLAW_CONFIG_HOST:-$HOME/.openclaw}/workspace-${agent_id}"
    mkdir -p "$workspace_dir"
    
    # Use openclaw agents add command to create the agent in non-interactive mode
    if openclaw agents add "$agent_name" --non-interactive --workspace "$workspace_dir"; then
        print_status "Successfully created agent: $agent_name"
        
        # Configure sandbox settings for this specific agent
        print_status "Configuring sandbox for agent: $agent_id"
        configure_agent_sandbox "$agent_id"
        
        return 0
    else
        print_error "Failed to create agent: $agent_name"
        return 1
    fi
}

# Main function to create all required agents
main() {
    # List of agents to create based on RoleConfig.json
    local agents=(
        "Chief_Executive_Officer"
        "Chief_Product_Officer"
        "Chief_Technology_Officer"
        "Programmer"
        "Code_Reviewer"
        "Software_Test_Engineer"
        "Chief_Creative_Officer"
        "Counselor"
        "Chief_Human_Resource_Officer"
    )
    
    print_status "Creating OpenClaw agents for ClawDev framework..."
    
    local success_count=0
    local total_agents=${#agents[@]}
    local skipped_count=0
    
    for agent_name in "${agents[@]}"; do
        if create_agent "$agent_name"; then
            if agent_exists "$agent_name"; then
                ((success_count++))
            else
                ((skipped_count++))
            fi
        fi
    done
    
    print_status "Agent creation process completed."
    print_status "Successfully created: $success_count"
    print_status "Skipped: $skipped_count"
    print_status "Total processed: $((success_count + skipped_count))/$total_agents"
    
    if [[ $success_count -eq $total_agents ]]; then
        print_status "All agents created successfully!"
        return 0
    elif [[ $((success_count + skipped_count)) -eq $total_agents ]]; then
        print_status "All agents processed (some skipped by user choice)."
        return 0
    else
        print_error "Some agents failed to process."
        return 1
    fi
}

# Run main function
main