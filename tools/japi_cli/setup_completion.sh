#!/bin/bash
# Setup script for japi_cli shell auto-completion
# Supports bash, zsh, and fish shells

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect the user's actual shell (not the script's shell)
detect_shell() {
    # First, check parent process to see what shell invoked this script
    local parent_shell=$(ps -p $PPID -o comm= 2>/dev/null | tr -d ' ')
    
    case "$parent_shell" in
        fish)
            echo "fish"
            return
            ;;
        bash)
            echo "bash"
            return
            ;;
        zsh)
            echo "zsh"
            return
            ;;
    esac
    
    # Fallback: check $SHELL environment variable
    case "$SHELL" in
        */fish)
            echo "fish"
            ;;
        */zsh)
            echo "zsh"
            ;;
        */bash)
            echo "bash"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Get the absolute path to japi_cli.py
# Handle both bash/zsh (using BASH_SOURCE) and fish/other shells
if [ -n "${BASH_SOURCE[0]}" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    # Fallback for fish and other shells
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

JAPI_CLI_PATH="$SCRIPT_DIR/japi_cli.py"

if [ ! -f "$JAPI_CLI_PATH" ]; then
    echo -e "${RED}Error: japi_cli.py not found at $JAPI_CLI_PATH${NC}"
    exit 1
fi

SHELL_TYPE=$(detect_shell)

print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  JAPI CLI Auto-Completion Setup${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
}

setup_bash() {
    echo -e "${GREEN}Setting up auto-completion for Bash...${NC}"
    echo ""
    
    # Check if argcomplete is installed
    if ! python3 -c "import argcomplete" 2>/dev/null; then
        echo -e "${YELLOW}Installing argcomplete...${NC}"
        pip install argcomplete
    fi
    
    BASHRC="$HOME/.bashrc"
    
    # Check if already configured
    if grep -q "japi_cli completion" "$BASHRC" 2>/dev/null; then
        echo -e "${YELLOW}Auto-completion already configured in $BASHRC${NC}"
    else
        echo "" >> "$BASHRC"
        echo "# japi_cli completion setup" >> "$BASHRC"
        echo "export JAPI_CLI_SCRIPT_DIR=\"$SCRIPT_DIR\"" >> "$BASHRC"
        echo "" >> "$BASHRC"
        echo "# Completion function for japi_cli using full path" >> "$BASHRC"
        echo "_japi_cli_completion() {" >> "$BASHRC"
        echo "    local IFS=\$'\\013'" >> "$BASHRC"
        echo "    COMPREPLY=( \$(COMP_WORDS=\${COMP_WORDS} \\\\" >> "$BASHRC"
        echo "                  COMP_CWORD=\$COMP_CWORD \\\\" >> "$BASHRC"
        echo "                  COMP_LINE=\$COMP_LINE \\\\" >> "$BASHRC"
        echo "                  COMP_POINT=\$COMP_POINT \\\\" >> "$BASHRC"
        echo "                  _ARGCOMPLETE_COMP_WORDBREAKS=\$COMP_WORDBREAKS \\\\" >> "$BASHRC"
        echo "                  _ARGCOMPLETE=1 \\\\" >> "$BASHRC"
        echo "                  python3 \"\$JAPI_CLI_SCRIPT_DIR/japi_cli.py\" 8>&1 9>&2 1>/dev/null 2>&1) )" >> "$BASHRC"
        echo "}" >> "$BASHRC"
        echo "complete -o nospace -o default -F _japi_cli_completion japi_cli" >> "$BASHRC"
        echo -e "${GREEN}✓ Added auto-completion to $BASHRC${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}To activate in your current shell, run:${NC}"
    echo -e "  source ~/.bashrc"
    echo ""
    echo -e "${BLUE}Or start a new shell session.${NC}"
}

setup_zsh() {
    echo -e "${GREEN}Setting up auto-completion for Zsh...${NC}"
    echo ""
    
    # Check if argcomplete is installed
    if ! python3 -c "import argcomplete" 2>/dev/null; then
        echo -e "${YELLOW}Installing argcomplete...${NC}"
        pip install argcomplete
    fi
    
    ZSHRC="$HOME/.zshrc"
    
    # Zsh requires autoload and bashcompinit
    if ! grep -q "autoload -U bashcompinit" "$ZSHRC" 2>/dev/null; then
        echo "" >> "$ZSHRC"
        echo "# Enable bash completion compatibility" >> "$ZSHRC"
        echo "autoload -U bashcompinit" >> "$ZSHRC"
        echo "bashcompinit" >> "$ZSHRC"
    fi
    
    # Check if already configured
    if grep -q "japi_cli completion" "$ZSHRC" 2>/dev/null; then
        echo -e "${YELLOW}Auto-completion already configured in $ZSHRC${NC}"
    else
        echo "" >> "$ZSHRC"
        echo "# japi_cli completion setup" >> "$ZSHRC"
        echo "export JAPI_CLI_SCRIPT_DIR=\"$SCRIPT_DIR\"" >> "$ZSHRC"
        echo "" >> "$ZSHRC"
        echo "# Completion function for japi_cli using full path" >> "$ZSHRC"
        echo "_japi_cli_completion() {" >> "$ZSHRC"
        echo "    local IFS=\$'\\013'" >> "$ZSHRC"
        echo "    COMPREPLY=( \$(COMP_WORDS=\${COMP_WORDS} \\\\" >> "$ZSHRC"
        echo "                  COMP_CWORD=\$COMP_CWORD \\\\" >> "$ZSHRC"
        echo "                  COMP_LINE=\$COMP_LINE \\\\" >> "$ZSHRC"
        echo "                  COMP_POINT=\$COMP_POINT \\\\" >> "$ZSHRC"
        echo "                  _ARGCOMPLETE_COMP_WORDBREAKS=\$COMP_WORDBREAKS \\\\" >> "$ZSHRC"
        echo "                  _ARGCOMPLETE=1 \\\\" >> "$ZSHRC"
        echo "                  python3 \"\$JAPI_CLI_SCRIPT_DIR/japi_cli.py\" 8>&1 9>&2 1>/dev/null 2>&1) )" >> "$ZSHRC"
        echo "}" >> "$ZSHRC"
        echo "complete -o nospace -o default -F _japi_cli_completion japi_cli" >> "$ZSHRC"
        echo -e "${GREEN}✓ Added auto-completion to $ZSHRC${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}To activate in your current shell, run:${NC}"
    echo -e "  source ~/.zshrc"
    echo ""
    echo -e "${BLUE}Or start a new shell session.${NC}"
}

setup_fish() {
    echo -e "${GREEN}Setting up auto-completion for Fish...${NC}"
    echo ""
    
    # Check if argcomplete is installed
    if ! python3 -c "import argcomplete" 2>/dev/null; then
        echo -e "${YELLOW}Installing argcomplete...${NC}"
        pip install argcomplete
    fi
    
    FISH_CONFIG_DIR="$HOME/.config/fish"
    FISH_COMPLETIONS_DIR="$FISH_CONFIG_DIR/completions"
    
    # Create completions directory if it doesn't exist
    mkdir -p "$FISH_COMPLETIONS_DIR"
    
    # Generate completion files for both japi_cli.py and japi_cli (wrapper script)
    COMPLETION_FILE_PY="$FISH_COMPLETIONS_DIR/japi_cli.py.fish"
    COMPLETION_FILE="$FISH_COMPLETIONS_DIR/japi_cli.fish"
    
    # Generate fish completion script using absolute path
    echo -e "${BLUE}Generating completion files...${NC}"
    
    # Change to the directory containing japi_cli.py to ensure proper path resolution
    cd "$SCRIPT_DIR"
    
    # Generate completion for japi_cli.py
    register-python-argcomplete --shell fish japi_cli.py > "$COMPLETION_FILE_PY"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Created completion file: $COMPLETION_FILE_PY${NC}"
        
        # Also create completion for the wrapper script (japi_cli without .py)
        # We need to modify the generated completion to use the full path
        cat > "$COMPLETION_FILE" << 'EOF'
# Auto-completion for japi_cli wrapper script
# Generated from japi_cli.py completions with modified paths

# Store the script directory
EOF
        echo "set -g __japi_cli_script_dir \"$SCRIPT_DIR\"" >> "$COMPLETION_FILE"
        cat >> "$COMPLETION_FILE" << 'EOF'

function __fish_japi_cli_complete
    set -x _ARGCOMPLETE 1
    set -x _ARGCOMPLETE_DFS \t
    set -x _ARGCOMPLETE_IFS \n
    set -x _ARGCOMPLETE_SUPPRESS_SPACE 1
    set -x _ARGCOMPLETE_SHELL fish
    set -x COMP_LINE (commandline -p)
    set -x COMP_POINT (string length (commandline -cp))
    set -x COMP_TYPE
    if set -q _ARC_DEBUG
        python3 "$__japi_cli_script_dir/japi_cli.py" 8>&1 9>&2 1>&9 2>&1
    else
        python3 "$__japi_cli_script_dir/japi_cli.py" 8>&1 9>&2 1>/dev/null 2>&1
    end
end
complete --command japi_cli -f -a '(__fish_japi_cli_complete)'
EOF
        
        echo -e "${GREEN}✓ Created completion file: $COMPLETION_FILE${NC}"
        echo ""
        echo -e "${BLUE}Auto-completion is now active for both:${NC}"
        echo -e "  • japi_cli.py"
        echo -e "  • japi_cli (wrapper script)"
        echo ""
        echo -e "${BLUE}Completions will be available after restarting your Fish shell.${NC}"
        echo ""
        echo -e "${YELLOW}Note: For 'uv run japi_cli.py', argcomplete must be installed in the uv environment${NC}"
    else
        echo -e "${RED}✗ Failed to generate completion file${NC}"
        echo -e "${YELLOW}You may need to run this script from bash or zsh${NC}"
        exit 1
    fi
}

print_manual_instructions() {
    echo ""
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  Manual Setup Instructions${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
    
    echo -e "${YELLOW}Bash:${NC}"
    echo "  Add to ~/.bashrc:"
    echo "    export JAPI_CLI_SCRIPT_DIR=\"$SCRIPT_DIR\""
    echo "    _japi_cli_completion() {"
    echo "        local IFS=\$'\\013'"
    echo "        COMPREPLY=( \$(COMP_WORDS=\${COMP_WORDS} \\\\"
    echo "                      COMP_CWORD=\$COMP_CWORD \\\\"
    echo "                      COMP_LINE=\$COMP_LINE \\\\"
    echo "                      COMP_POINT=\$COMP_POINT \\\\"
    echo "                      _ARGCOMPLETE_COMP_WORDBREAKS=\$COMP_WORDBREAKS \\\\"
    echo "                      _ARGCOMPLETE=1 \\\\"
    echo "                      python3 \"\$JAPI_CLI_SCRIPT_DIR/japi_cli.py\" 8>&1 9>&2 1>/dev/null 2>&1) )"
    echo "    }"
    echo "    complete -o nospace -o default -F _japi_cli_completion japi_cli"
    echo ""
    
    echo -e "${YELLOW}Zsh:${NC}"
    echo "  Add to ~/.zshrc:"
    echo "    autoload -U bashcompinit"
    echo "    bashcompinit"
    echo "    export JAPI_CLI_SCRIPT_DIR=\"$SCRIPT_DIR\""
    echo "    _japi_cli_completion() {"
    echo "        local IFS=\$'\\013'"
    echo "        COMPREPLY=( \$(COMP_WORDS=\${COMP_WORDS} \\\\"
    echo "                      COMP_CWORD=\$COMP_CWORD \\\\"
    echo "                      COMP_LINE=\$COMP_LINE \\\\"
    echo "                      COMP_POINT=\$COMP_POINT \\\\"
    echo "                      _ARGCOMPLETE_COMP_WORDBREAKS=\$COMP_WORDBREAKS \\\\"
    echo "                      _ARGCOMPLETE=1 \\\\"
    echo "                      python3 \"\$JAPI_CLI_SCRIPT_DIR/japi_cli.py\" 8>&1 9>&2 1>/dev/null 2>&1) )"
    echo "    }"
    echo "    complete -o nospace -o default -F _japi_cli_completion japi_cli"
    echo ""
    
    echo -e "${YELLOW}Fish:${NC}"
    echo "  Run:"
    echo "    mkdir -p ~/.config/fish/completions"
    echo "    # Create completions as shown in the setup script"
    echo ""
}

# Main script
print_header

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Setup auto-completion for japi_cli in your shell."
    echo ""
    echo "Options:"
    echo "  --auto         Automatically detect shell and setup (default)"
    echo "  --bash         Setup for Bash"
    echo "  --zsh          Setup for Zsh"
    echo "  --fish         Setup for Fish"
    echo "  --manual       Show manual setup instructions"
    echo "  --help, -h     Show this help message"
    echo ""
    exit 0
fi

case "$1" in
    --bash)
        setup_bash
        ;;
    --zsh)
        setup_zsh
        ;;
    --fish)
        setup_fish
        ;;
    --manual)
        print_manual_instructions
        ;;
    --auto|"")
        echo -e "${BLUE}Detected shell: $SHELL_TYPE${NC}"
        echo ""
        
        case "$SHELL_TYPE" in
            bash)
                setup_bash
                ;;
            zsh)
                setup_zsh
                ;;
            fish)
                setup_fish
                ;;
            *)
                echo -e "${RED}Could not detect shell type.${NC}"
                print_manual_instructions
                exit 1
                ;;
        esac
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo "Use --help for usage information."
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo -e "${BLUE}Try it out:${NC}"
echo -e "  ${YELLOW}japi_cli.py <TAB>${NC}         - See available commands"
echo -e "  ${YELLOW}japi_cli.py set_input <TAB>${NC} - See available channels"
echo -e "  ${YELLOW}japi_cli.py get_ <TAB>${NC}    - See all get commands"
