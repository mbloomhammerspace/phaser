#!/bin/bash

# Preflight Checker for Kubernetes RAG Installer
# Automatically discovers hardware capabilities and builds deployment plans

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFLIGHT_CHECKER="${SCRIPT_DIR}/preflight_checker.py"
LOG_FILE="${SCRIPT_DIR}/../preflight.log"
NODES_FILE=""
SSH_KEY_PATH="~/.ssh/id_rsa"
USERNAME="ubuntu"
OUTPUT_DIR="${SCRIPT_DIR}/../discovery"

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[INFO]${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
        "DEBUG")
            echo -e "${BLUE}[DEBUG]${NC} $message"
            ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Print banner
print_banner() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                Preflight Checker                              ║
║                                                              ║
║  Automatic Hardware Discovery & Deployment Planning          ║
╚══════════════════════════════════════════════════════════════╝
EOF
}

# Check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Python dependencies
    log "INFO" "Checking Python dependencies..."
    python3 -c "import paramiko, yaml" 2>/dev/null || {
        log "INFO" "Installing required Python packages..."
        pip3 install paramiko pyyaml
    }
    
    # Check SSH key
    if [[ ! -f "$(eval echo $SSH_KEY_PATH)" ]]; then
        log "ERROR" "SSH key not found: $SSH_KEY_PATH"
        exit 1
    fi
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    log "INFO" "Prerequisites check completed"
}

# Interactive node input
get_nodes_interactive() {
    log "INFO" "Starting interactive node discovery..."
    
    local nodes=()
    local node_count=0
    
    echo -e "\n${BLUE}=== Node Discovery ===${NC}\n"
    
    while true; do
        echo -e "${YELLOW}Node $((node_count + 1)):${NC}"
        
        read -p "Hostname (or 'done' to finish): " hostname
        if [[ "$hostname" == "done" ]]; then
            break
        fi
        
        if [[ -z "$hostname" ]]; then
            log "ERROR" "Hostname is required"
            continue
        fi
        
        read -p "IP Address: " ip_address
        if [[ -z "$ip_address" ]]; then
            log "ERROR" "IP address is required"
            continue
        fi
        
        read -p "Username [$USERNAME]: " username
        username=${username:-$USERNAME}
        
        # Test SSH connection
        log "INFO" "Testing SSH connection to $hostname ($ip_address)..."
        if ssh -i "$(eval echo $SSH_KEY_PATH)" -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$username@$ip_address" "echo 'SSH connection successful'" 2>/dev/null; then
            log "INFO" "✓ SSH connection successful"
        else
            log "ERROR" "✗ SSH connection failed"
            read -p "Continue anyway? (y/n): " continue_anyway
            if [[ "$continue_anyway" != "y" ]]; then
                continue
            fi
        fi
        
        nodes+=("$hostname:$ip_address:$username")
        node_count=$((node_count + 1))
        
        echo ""
    done
    
    if [[ $node_count -eq 0 ]]; then
        log "ERROR" "No nodes specified"
        exit 1
    fi
    
    # Save nodes to file
    NODES_FILE="$OUTPUT_DIR/nodes.txt"
    for node in "${nodes[@]}"; do
        echo "$node" >> "$NODES_FILE"
    done
    
    log "INFO" "Saved $node_count nodes to $NODES_FILE"
}

# Load nodes from file
load_nodes_from_file() {
    log "INFO" "Loading nodes from $NODES_FILE"
    
    if [[ ! -f "$NODES_FILE" ]]; then
        log "ERROR" "Nodes file not found: $NODES_FILE"
        exit 1
    fi
    
    local node_count=0
    while IFS= read -r line; do
        if [[ -n "$line" && ! "$line" =~ ^# ]]; then
            node_count=$((node_count + 1))
        fi
    done < "$NODES_FILE"
    
    if [[ $node_count -eq 0 ]]; then
        log "ERROR" "No valid nodes found in $NODES_FILE"
        exit 1
    fi
    
    log "INFO" "Found $node_count nodes in $NODES_FILE"
}

# Run preflight discovery
run_discovery() {
    log "INFO" "Starting hardware discovery..."
    
    # Convert nodes file to JSON for Python
    local nodes_json="$OUTPUT_DIR/nodes.json"
    echo "[" > "$nodes_json"
    
    local first=true
    while IFS=: read -r hostname ip_address username; do
        if [[ -n "$hostname" && ! "$hostname" =~ ^# ]]; then
            if [[ "$first" == "true" ]]; then
                first=false
            else
                echo "," >> "$nodes_json"
            fi
            
            cat >> "$nodes_json" << EOF
  {
    "hostname": "$hostname",
    "ip_address": "$ip_address",
    "username": "$username"
  }
EOF
        fi
    done < "$NODES_FILE"
    
    echo "]" >> "$nodes_json"
    
    # Run Python preflight checker
    log "INFO" "Running hardware discovery..."
    python3 "$PREFLIGHT_CHECKER" discover "$nodes_json" "$SSH_KEY_PATH" "$OUTPUT_DIR"
    
    if [[ $? -eq 0 ]]; then
        log "INFO" "✓ Hardware discovery completed successfully"
    else
        log "ERROR" "✗ Hardware discovery failed"
        exit 1
    fi
}

# Display discovery results
display_results() {
    log "INFO" "Displaying discovery results..."
    
    local report_file="$OUTPUT_DIR/discovery_report.md"
    local plan_file="$OUTPUT_DIR/deployment_plan.json"
    local inventory_file="$OUTPUT_DIR/inventory.yml"
    
    if [[ -f "$report_file" ]]; then
        echo -e "\n${CYAN}=== Hardware Discovery Report ===${NC}"
        cat "$report_file"
        echo ""
    fi
    
    if [[ -f "$plan_file" ]]; then
        echo -e "\n${CYAN}=== Deployment Plan Summary ===${NC}"
        python3 -c "
import json
with open('$plan_file', 'r') as f:
    plan = json.load(f)
print(f'Master Node: {plan[\"master_node\"][\"hostname\"]} ({plan[\"master_node\"][\"ip_address\"]})')
print(f'GPU Worker Nodes: {len(plan[\"gpu_worker_nodes\"])}')
for node in plan['gpu_worker_nodes']:
    print(f'  - {node[\"hostname\"]} ({node[\"ip_address\"]})')
print(f'Regular Worker Nodes: {len(plan[\"worker_nodes\"])}')
for node in plan['worker_nodes']:
    print(f'  - {node[\"hostname\"]} ({node[\"ip_address\"]})')
print(f'Total GPUs: {plan[\"summary\"][\"total_gpus\"]}')
print(f'Total GPU Memory: {plan[\"summary\"][\"total_gpu_memory_gb\"]:.1f} GB')
"
        echo ""
    fi
    
    if [[ -f "$inventory_file" ]]; then
        echo -e "\n${CYAN}=== Generated Inventory File ===${NC}"
        echo "Location: $inventory_file"
        echo ""
        cat "$inventory_file"
        echo ""
    fi
}

# Generate deployment files
generate_deployment_files() {
    log "INFO" "Generating deployment files..."
    
    local plan_file="$OUTPUT_DIR/deployment_plan.json"
    local inventory_file="$OUTPUT_DIR/inventory.yml"
    
    if [[ ! -f "$plan_file" ]]; then
        log "ERROR" "Deployment plan not found. Run discovery first."
        exit 1
    fi
    
    # Generate inventory file
    python3 "$PREFLIGHT_CHECKER" generate-inventory "$plan_file" "$USERNAME" "$SSH_KEY_PATH" > "$inventory_file"
    
    # Generate Kubespray configuration
    local kubespray_config="$OUTPUT_DIR/kubespray_config.yml"
    python3 "$PREFLIGHT_CHECKER" generate-kubespray-config "$plan_file" > "$kubespray_config"
    
    # Generate RAG configuration
    local rag_config="$OUTPUT_DIR/rag_config.yml"
    python3 "$PREFLIGHT_CHECKER" generate-rag-config "$plan_file" > "$rag_config"
    
    log "INFO" "✓ Deployment files generated:"
    log "INFO" "  - Inventory: $inventory_file"
    log "INFO" "  - Kubespray Config: $kubespray_config"
    log "INFO" "  - RAG Config: $rag_config"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --nodes)
                NODES_FILE="$2"
                shift 2
                ;;
            --ssh-key)
                SSH_KEY_PATH="$2"
                shift 2
                ;;
            --username)
                USERNAME="$2"
                shift 2
                ;;
            --output-dir)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --discover-only)
                DISCOVER_ONLY=true
                shift
                ;;
            --generate-only)
                GENERATE_ONLY=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Show help
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    --nodes FILE           Path to nodes file (hostname:ip:username format)
    --ssh-key PATH         SSH private key path (default: ~/.ssh/id_rsa)
    --username USER        SSH username (default: ubuntu)
    --output-dir DIR       Output directory (default: ../discovery)
    --discover-only        Only run hardware discovery
    --generate-only        Only generate deployment files (requires discovery)
    --help                 Show this help message

Examples:
    $0                                    # Interactive mode
    $0 --nodes my-nodes.txt              # Use nodes file
    $0 --discover-only --nodes nodes.txt # Only discover hardware
    $0 --generate-only                   # Generate deployment files

Nodes file format:
    hostname1:192.168.1.10:ubuntu
    hostname2:192.168.1.11:ubuntu
    # Comments start with #
EOF
}

# Main execution
main() {
    print_banner
    
    # Parse arguments
    parse_args "$@"
    
    # Check prerequisites
    check_prerequisites
    
    # Get nodes (interactive or from file)
    if [[ -z "$NODES_FILE" ]]; then
        get_nodes_interactive
    else
        load_nodes_from_file
    fi
    
    # Run discovery
    if [[ "${DISCOVER_ONLY:-false}" != "true" ]]; then
        run_discovery
        display_results
    fi
    
    # Generate deployment files
    if [[ "${GENERATE_ONLY:-false}" != "true" ]]; then
        generate_deployment_files
    fi
    
    log "INFO" "Preflight checker completed successfully!"
    log "INFO" "Output directory: $OUTPUT_DIR"
    log "INFO" "Log file: $LOG_FILE"
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
