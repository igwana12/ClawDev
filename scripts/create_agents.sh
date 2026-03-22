#!/bin/bash

# Script to create all required OpenClaw agents for the ClawDev framework.

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Function to create an OpenClaw agent
create_agent() {
    local agent_name="$1"
    print_status "Creating agent: $agent_name"
    
    # Create workspace directory
    local workspace_dir="/home/anzz/.openclaw/workspace-${agent_name,,}"
    mkdir -p "$workspace_dir"
    
    # Use openclaw agents add command to create the agent in non-interactive mode
    if openclaw agents add "$agent_name" --non-interactive --workspace "$workspace_dir"; then
        print_status "Successfully created agent: $agent_name"
        return 0
    else
        print_error "Failed to create agent: $agent_name"
        return 1
    fi
}

# Main function to create all required agents
main() {
    # List of agents to create based on RoleConfig.json
    # Each role gets its own unique agent name to avoid confusion
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
    
    for agent_name in "${agents[@]}"; do
        if create_agent "$agent_name"; then
            ((success_count++))
        fi
    done
    
    print_status "Created $success_count/$total_agents agents successfully."
    
    if [[ $success_count -eq $total_agents ]]; then
        print_status "All agents created successfully!"
        return 0
    else
        print_error "Some agents failed to create."
        return 1
    fi
}

# Run main function
main