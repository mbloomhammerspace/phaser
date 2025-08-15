#!/bin/bash

# Enhanced Error Handler with AI Integration
# Wraps commands and provides intelligent error analysis

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
LOG_FILE="${SCRIPT_DIR}/../install.log"
AI_DEBUGGER="${SCRIPT_DIR}/ai_debugger.py"
ERROR_HISTORY_FILE="${SCRIPT_DIR}/../error_history.json"
MAX_RETRIES=3
RETRY_DELAY=10

# Initialize error history
if [[ ! -f "$ERROR_HISTORY_FILE" ]]; then
    echo '{"errors": [], "timestamp": "'$(date -Iseconds)'"}' > "$ERROR_HISTORY_FILE"
fi

# Logging function with AI integration
log_with_ai() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Standard logging
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
        "AI")
            echo -e "${PURPLE}[AI]${NC} $message"
            ;;
        "DEBUG")
            echo -e "${BLUE}[DEBUG]${NC} $message"
            ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# AI-powered error analysis
analyze_error_with_ai() {
    local error_message="$1"
    local context="$2"
    local command="$3"
    
    log_with_ai "AI" "Analyzing error with OpenAI API..."
    
    # Create context JSON
    local context_json=$(cat << EOF
{
    "command": "$command",
    "timestamp": "$(date -Iseconds)",
    "exit_code": "$4",
    "stdout": "$5",
    "stderr": "$6",
    "additional_context": "$context"
}
EOF
)
    
    # Call AI debugger
    local analysis_result=$(python3 "$AI_DEBUGGER" analyze_error "$error_message" "$context_json" 2>/dev/null || echo '{"severity": "UNKNOWN", "summary": "AI analysis failed"}')
    
    # Parse and display results
    local severity=$(echo "$analysis_result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('severity', 'UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
    local summary=$(echo "$analysis_result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('summary', 'No summary available'))" 2>/dev/null || echo "No summary available")
    
    log_with_ai "AI" "Analysis complete - Severity: $severity"
    log_with_ai "AI" "Summary: $summary"
    
    # Display solutions if available
    local solutions=$(echo "$analysis_result" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    solutions = data.get('solutions', [])
    if isinstance(solutions, list):
        for i, solution in enumerate(solutions, 1):
            if isinstance(solution, dict):
                print(f'{i}. {solution.get(\"description\", \"No description\")}')
                cmd = solution.get(\"command\", \"\")
                if cmd:
                    print(f'   Command: {cmd}')
            else:
                print(f'{i}. {solution}')
    else:
        print('1. Manual troubleshooting required')
except:
    print('1. Manual troubleshooting required')
" 2>/dev/null)
    
    if [[ -n "$solutions" ]]; then
        log_with_ai "AI" "Suggested solutions:"
        echo -e "${CYAN}$solutions${NC}"
    fi
    
    # Store in error history
    local error_entry=$(cat << EOF
{
    "timestamp": "$(date -Iseconds)",
    "error": "$error_message",
    "command": "$command",
    "context": $context_json,
    "ai_analysis": $analysis_result
}
EOF
)
    
    # Append to error history
    python3 -c "
import json
with open('$ERROR_HISTORY_FILE', 'r') as f:
    data = json.load(f)
data['errors'].append($error_entry)
with open('$ERROR_HISTORY_FILE', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null
    
    return "$severity"
}

# Enhanced command execution with error handling
execute_with_ai_error_handling() {
    local description="$1"
    local command="$2"
    local context="$3"
    local retry_count=0
    
    log_with_ai "INFO" "Executing: $description"
    log_with_ai "DEBUG" "Command: $command"
    
    while [[ $retry_count -lt $MAX_RETRIES ]]; do
        # Capture command output
        local stdout_file=$(mktemp)
        local stderr_file=$(mktemp)
        local exit_code=0
        
        # Execute command
        if eval "$command" > "$stdout_file" 2> "$stderr_file"; then
            log_with_ai "INFO" "✓ $description completed successfully"
            rm -f "$stdout_file" "$stderr_file"
            return 0
        else
            exit_code=$?
            local stdout=$(cat "$stdout_file" 2>/dev/null || echo "")
            local stderr=$(cat "$stderr_file" 2>/dev/null || echo "")
            rm -f "$stdout_file" "$stderr_file"
            
            retry_count=$((retry_count + 1))
            
            log_with_ai "ERROR" "✗ $description failed (attempt $retry_count/$MAX_RETRIES)"
            log_with_ai "ERROR" "Exit code: $exit_code"
            
            if [[ -n "$stderr" ]]; then
                log_with_ai "ERROR" "Error output: $stderr"
            fi
            
            # Analyze with AI
            local severity=$(analyze_error_with_ai "$stderr" "$context" "$command" "$exit_code" "$stdout" "$stderr")
            
            # Handle based on severity
            case $severity in
                "CRITICAL")
                    log_with_ai "ERROR" "Critical error detected. Stopping execution."
                    return $exit_code
                    ;;
                "HIGH")
                    if [[ $retry_count -lt $MAX_RETRIES ]]; then
                        log_with_ai "WARN" "High severity error. Retrying in $RETRY_DELAY seconds..."
                        sleep $RETRY_DELAY
                    else
                        log_with_ai "ERROR" "Maximum retries reached for high severity error."
                        return $exit_code
                    fi
                    ;;
                "MEDIUM"|"LOW")
                    if [[ $retry_count -lt $MAX_RETRIES ]]; then
                        log_with_ai "INFO" "Retrying in $RETRY_DELAY seconds..."
                        sleep $RETRY_DELAY
                    else
                        log_with_ai "ERROR" "Maximum retries reached."
                        return $exit_code
                    fi
                    ;;
                *)
                    if [[ $retry_count -lt $MAX_RETRIES ]]; then
                        log_with_ai "WARN" "Unknown error severity. Retrying in $RETRY_DELAY seconds..."
                        sleep $RETRY_DELAY
                    else
                        log_with_ai "ERROR" "Maximum retries reached."
                        return $exit_code
                    fi
                    ;;
            esac
        fi
    done
    
    return 1
}

# Cluster diagnostics with AI analysis
run_cluster_diagnostics() {
    log_with_ai "INFO" "Running comprehensive cluster diagnostics..."
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        log_with_ai "ERROR" "kubectl not found. Cannot run cluster diagnostics."
        return 1
    fi
    
    # Collect diagnostics
    local diagnostics_file=$(mktemp)
    
    # Get cluster info
    kubectl cluster-info > "$diagnostics_file" 2>&1 || true
    kubectl get nodes >> "$diagnostics_file" 2>&1 || true
    kubectl get pods --all-namespaces >> "$diagnostics_file" 2>&1 || true
    kubectl get events --all-namespaces --sort-by=.metadata.creationTimestamp >> "$diagnostics_file" 2>&1 || true
    
    # Analyze with AI
    local diagnostics=$(cat "$diagnostics_file")
    log_with_ai "AI" "Analyzing cluster diagnostics..."
    
    # Call AI debugger for suggestions
    local suggestions=$(python3 "$AI_DEBUGGER" suggest_fixes "$diagnostics" 2>/dev/null || echo "[]")
    
    log_with_ai "AI" "Diagnostic analysis complete"
    
    # Display key findings
    local node_count=$(kubectl get nodes --no-headers 2>/dev/null | wc -l || echo "0")
    local pod_count=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null | wc -l || echo "0")
    local failed_pods=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null | grep -E "(Error|CrashLoopBackOff|ImagePullBackOff)" | wc -l || echo "0")
    
    log_with_ai "INFO" "Cluster Status:"
    log_with_ai "INFO" "  - Nodes: $node_count"
    log_with_ai "INFO" "  - Total Pods: $pod_count"
    log_with_ai "INFO" "  - Failed Pods: $failed_pods"
    
    if [[ $failed_pods -gt 0 ]]; then
        log_with_ai "WARN" "Found $failed_pods failed pods. Check diagnostics for details."
    fi
    
    rm -f "$diagnostics_file"
}

# Interactive error resolution
interactive_error_resolution() {
    local error_message="$1"
    local context="$2"
    
    log_with_ai "AI" "Starting interactive error resolution..."
    
    # Get AI analysis
    local analysis_result=$(python3 "$AI_DEBUGGER" analyze_error "$error_message" "$context" 2>/dev/null || echo '{"severity": "UNKNOWN"}')
    local severity=$(echo "$analysis_result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('severity', 'UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
    
    echo -e "\n${PURPLE}=== AI Error Analysis ===${NC}"
    echo -e "Severity: ${severity}"
    echo -e "Error: $error_message"
    
    # Extract solutions
    local solutions=$(echo "$analysis_result" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    solutions = data.get('solutions', [])
    if isinstance(solutions, list):
        for i, solution in enumerate(solutions, 1):
            if isinstance(solution, dict):
                print(f'{i}. {solution.get(\"description\", \"No description\")}')
                cmd = solution.get(\"command\", \"\")
                if cmd:
                    print(f'   Command: {cmd}')
            else:
                print(f'{i}. {solution}')
    else:
        print('1. Manual troubleshooting required')
except:
    print('1. Manual troubleshooting required')
" 2>/dev/null)
    
    if [[ -n "$solutions" ]]; then
        echo -e "\n${CYAN}Suggested Solutions:${NC}"
        echo -e "$solutions"
        
        read -p $'\nWould you like to apply a solution? (y/n): ' apply_solution
        
        if [[ "$apply_solution" =~ ^[Yy]$ ]]; then
            read -p $'Enter solution number to apply: ' solution_number
            
            # Extract and execute the selected solution
            local selected_command=$(echo "$analysis_result" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    solutions = data.get('solutions', [])
    solution_num = int('$solution_number') - 1
    if 0 <= solution_num < len(solutions):
        solution = solutions[solution_num]
        if isinstance(solution, dict):
            print(solution.get('command', ''))
        else:
            print('')
    else:
        print('')
except:
    print('')
" 2>/dev/null)
            
            if [[ -n "$selected_command" ]]; then
                log_with_ai "INFO" "Executing AI-suggested command: $selected_command"
                if eval "$selected_command"; then
                    log_with_ai "INFO" "✓ AI-suggested solution applied successfully"
                    return 0
                else
                    log_with_ai "ERROR" "✗ AI-suggested solution failed"
                    return 1
                fi
            else
                log_with_ai "ERROR" "Invalid solution number or no command available"
                return 1
            fi
        fi
    fi
    
    return 1
}

# Export functions for use in other scripts
export -f log_with_ai
export -f analyze_error_with_ai
export -f execute_with_ai_error_handling
export -f run_cluster_diagnostics
export -f interactive_error_resolution

# Main function for standalone usage
main() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: $0 <command> [description] [context]"
        echo "Example: $0 'kubectl get nodes' 'Check cluster nodes' 'Cluster validation'"
        exit 1
    fi
    
    local command="$1"
    local description="${2:-$command}"
    local context="${3:-No additional context}"
    
    execute_with_ai_error_handling "$description" "$command" "$context"
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
