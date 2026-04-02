#!/bin/bash

# Script to deploy ClawDev agent configurations to OpenClaw workspace

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

print_question() {
    echo -e "${BLUE}[QUESTION]${NC} $1" >&2
}

# Function to ask user for input with default value
get_user_input() {
    local prompt="$1"
    local default_value="$2"
    local user_input
    
    if [[ -n "$default_value" ]]; then
        print_question "$prompt (default: $default_value): " >&2
    else
        print_question "$prompt: " >&2
    fi
    
    read -r user_input
    
    # If user input is empty and default value is provided, use default
    if [[ -z "$user_input" && -n "$default_value" ]]; then
        echo "$default_value"
    else
        echo "$user_input"
    fi
}

# Function to ask user for confirmation
confirm() {
    local prompt="$1"
    local default="${2:-n}"  # Default to 'n' if not specified
    local answer
    
    while true; do
        if [[ "$default" == "y" ]]; then
            print_question "$prompt (Y/n): " >&2
        else
            print_question "$prompt (y/N): " >&2
        fi
        
        read -r answer
        
        # If user just presses enter, use default
        if [[ -z "$answer" ]]; then
            answer="$default"
        fi
        
        case $answer in
            [Yy]* ) return 0 ;;
            [Nn]* ) return 1 ;;
            * ) echo "Please answer yes or no." >&2 ;;
        esac
    done
}

# Function to get OpenClaw configuration directory
get_openclaw_config_dir() {
    local config_dir
    
    # Check if OPENCLAW_CONFIG_HOST environment variable is set and not empty
    if [[ -n "${OPENCLAW_CONFIG_HOST:-}" ]]; then
        config_dir="${OPENCLAW_CONFIG_HOST}"
        print_status "Using OpenClaw config directory from environment variable: $config_dir"
    else
        # Ask user for OpenClaw configuration directory
        config_dir=$(get_user_input "Enter OpenClaw configuration directory" "/home/node/.openclaw")
    fi
    
    # Validate directory exists
    if [[ ! -d "$config_dir" ]]; then
        print_error "Directory does not exist: $config_dir"
        return 1
    fi
    
    echo "$config_dir"
    return 0
}

# Function to get configuration name
get_config_name() {
    local config_name
    
    # Get the project root directory (assuming script is in scripts/ subdirectory)
    local project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    
    # Ask user for configuration name with default "default"
    config_name=$(get_user_input "Enter configuration name" "default")
    
    # Validate that the configuration directory exists
    local config_dir="$project_root/configs/$config_name"
    if [[ ! -d "$config_dir" ]]; then
        print_error "Configuration directory does not exist: $config_dir"
        return 1
    fi
    
    echo "$config_name"
    return 0
}

# Function to deploy configurations to OpenClaw workspace
deploy_configurations() {
    local openclaw_config_dir="$1"
    local config_name="$2"
    
    print_status "Deploying configurations from 'configs/$config_name' to '$openclaw_config_dir'"
    
    # Get the project root directory (assuming script is in scripts/ subdirectory)
    local project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    
    # List of agent roles
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
    
    local success_count=0
    local total_agents=${#agents[@]}
    
    for agent in "${agents[@]}"; do
        print_status "Processing agent: $agent"
        
        # Check if agent configuration already exists
        if agent_config_exists "$openclaw_config_dir" "$agent"; then
            print_warning "Configuration for agent '$agent' already exists in target directory."
            if ! confirm "Do you want to overwrite the existing configuration" "n"; then
                print_status "Skipping configuration for agent: $agent"
                continue
            fi
        fi
        
        # Source directory for this agent's configuration (using relative path)
        local source_dir="$project_root/configs/$config_name/$agent"
        
        # Check if source directory exists
        if [[ ! -d "$source_dir" ]]; then
            print_warning "Configuration directory does not exist for agent: $agent"
            continue
        fi
        
        # Target workspace directory for this agent (using user-provided config directory)
        local target_dir="$openclaw_config_dir/workspace-${agent,,}"
        
        # Create target directory if it doesn't exist
        mkdir -p "$target_dir"
        
        # Copy all contents, exclude .git
        if cp -r "$source_dir/." "$target_dir/"; then
            # Copy required skills for this agent
            copy_required_skills "$openclaw_config_dir" "$agent" "$source_dir/skills"
            success_count=$((success_count + 1))
            print_status "Successfully deployed configuration for agent: $agent"
        else
            print_error "Failed to deploy configuration for agent: $agent"
        fi
    done
    
    print_status "Configuration deployment completed. Successfully processed $success_count/$total_agents agents."
    
    if [[ $success_count -eq $total_agents ]]; then
        print_status "All agent configurations deployed successfully!"
        return 0
    else
        print_warning "Some agent configurations failed to deploy."
        return 1
    fi
}

# Function to copy required skills from default workspace to agent's workspace
copy_required_skills() {
    local openclaw_config_dir="$1"
    local agent_name="$2"
    local agent_skills_dir="$3"
    
    # Target workspace directory for this agent (using user-provided config directory)
    local target_dir="$openclaw_config_dir/workspace-${agent_name,,}"
    
    # Default workspace skills directory (using user-provided config directory)
    local default_skills_dir="$openclaw_config_dir/workspace/skills"
    
    # Check if default skills directory exists
    if [[ ! -d "$default_skills_dir" ]]; then
        print_warning "Default skills directory does not exist: $default_skills_dir"
        return 0
    fi
    
    # Check if agent skills directory exists and contains skills.json
    local skills_json="$agent_skills_dir/skills.json"
    if [[ ! -f "$skills_json" ]]; then
        print_warning "Skills configuration file does not exist: $skills_json"
        return 0
    fi
    
    # Create skills directory in target workspace
    local target_skills_dir="$target_dir/skills"
    mkdir -p "$target_skills_dir"
    
    # Read skills from skills.json and copy each required skill
    print_status "Copying required skills for agent: $agent_name"
    
    # Use Python to parse JSON properly
    python3 -c "
import json
import os
import shutil
import glob

# Read skills.json
try:
    with open('$skills_json', 'r') as f:
        skills_config = json.load(f)
    
    required_skills = skills_config.get('skills', [])
    
    # Copy each required skill
    for skill_name in required_skills:
        # Find the skill directory in default workspace
        source_skills_dir = '$default_skills_dir'
        
        # First try exact match (no version suffix)
        exact_match = os.path.join(source_skills_dir, skill_name)
        if os.path.isdir(exact_match):
            source_skill_dir = exact_match
        else:
            # Try glob pattern for versioned skills (e.g., python-*)
            skill_dirs = glob.glob(os.path.join(source_skills_dir, skill_name + '-*'))
            if not skill_dirs:
                print(f'Warning: Skill \'{skill_name}\' not found in {source_skills_dir}')
                continue
            source_skill_dir = skill_dirs[0]
        
        # Safety check: ensure source is within default skills directory
        if not source_skill_dir.startswith('$default_skills_dir'):
            print(f'Error: Invalid source path: {source_skill_dir}')
            continue
        
        # Copy skill directory to target workspace
        dest_skill_dir = os.path.join('$target_skills_dir', os.path.basename(source_skill_dir))
        # Safety check: ensure destination is within target skills directory
        if not dest_skill_dir.startswith('$target_skills_dir'):
            print(f'Error: Invalid destination path: {dest_skill_dir}')
            continue
        if os.path.exists(dest_skill_dir):
            shutil.rmtree(dest_skill_dir)
        shutil.copytree(source_skill_dir, dest_skill_dir)
        
        print(f'Copied skill: {skill_name}')
except Exception as e:
    print(f'Error reading skills.json: {e}')
"
    
    print_status "Finished copying required skills for agent: $agent_name"
}

# Function to check if agent configuration already exists in target directory
agent_config_exists() {
    local openclaw_config_dir="$1"
    local agent_name="$2"
    
    # Target workspace directory for this agent
    local target_dir="$openclaw_config_dir/workspace-${agent_name,,}"
    
    # Check if target directory exists and has configuration files
    if [[ -d "$target_dir" ]] && [[ -n "$(ls -A "$target_dir")" ]]; then
        return 0  # Agent configuration exists
    else
        return 1  # Agent configuration does not exist
    fi
}

# Main function
main() {
    print_status "ClawDev Agent Configuration Deployment Script"
    
    # Get OpenClaw configuration directory
    local openclaw_config_dir
    if ! openclaw_config_dir=$(get_openclaw_config_dir); then
        print_error "Failed to get OpenClaw configuration directory"
        return 1
    fi
    
    # Get configuration name
    local config_name
    if ! config_name=$(get_config_name); then
        print_error "Failed to get configuration name"
        return 1
    fi
    
    # Warn user about potential configuration overwrite
    print_warning "This will deploy configurations from 'configs/$config_name' to '$openclaw_config_dir'"
    print_warning "Existing configurations may be overwritten!"
    
    # Ask for confirmation
    if ! confirm "Do you want to continue with the deployment" "n"; then
        print_status "Deployment cancelled by user."
        return 0
    fi
    
    # Deploy configurations
    deploy_configurations "$openclaw_config_dir" "$config_name"
}

# Run main function
main