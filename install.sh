#!/usr/bin/env bash
set -e

# Terminal formatting
BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}${CYAN}==========================================${RESET}"
echo -e "${BOLD}${CYAN}   Pokemon Fastfetch Installer (Gen 2)   ${RESET}"
echo -e "${BOLD}${CYAN}==========================================${RESET}"
echo ""

# 1. Check requirements
echo -e "${BOLD}[1/4] Checking requirements...${RESET}"

check_command() {
    if ! command -v "$1" &>/dev/null; then
        echo -e "${RED}Error: '$1' is required but not found in PATH.${RESET}"
        exit 1
    else
        echo -e "  ${GREEN}✓${RESET} Found $1"
    fi
}

check_command fastfetch
check_command fish
check_command python3

# Check Python Pillow
if ! python3 -c "import PIL" &>/dev/null; then
    echo -e "${YELLOW}Python Pillow library not found. Installing via pip...${RESET}"
    python3 -m pip install Pillow --user || {
        echo -e "${RED}Failed to install Pillow. Please install it manually (e.g. pacman -S python-pillow or pip install Pillow).${RESET}"
        exit 1
    }
else
    echo -e "  ${GREEN}✓${RESET} Found python-pillow"
fi

# 2. Generate and install sprites
echo ""
echo -e "${BOLD}[2/4] Setting up Pokemon Crystal animated sprites...${RESET}"
SPRITES_DIR="$HOME/.local/share/pokemon-sprites/animated"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -d "$SPRITES_DIR" ] && [ "$(ls -1 "$SPRITES_DIR"/*.raw 2>/dev/null | wc -l)" -ge 250 ]; then
    echo -e "  ${GREEN}✓${RESET} Found existing 251 sprite animation files in $SPRITES_DIR"
else
    echo -e "  Downloading and generating 251 Crystal animation sequences from PokeAPI..."
    python3 "$SCRIPT_DIR/scripts/generate_sprites.py" --target-dir "$SPRITES_DIR"
fi

# 3. Install Fastfetch configuration
echo ""
echo -e "${BOLD}[3/4] Installing Fastfetch configuration...${RESET}"
FASTFETCH_DIR="$HOME/.config/fastfetch"
mkdir -p "$FASTFETCH_DIR"

if [ -f "$FASTFETCH_DIR/config.jsonc" ]; then
    echo -e "  Backing up existing config to $FASTFETCH_DIR/config.jsonc.bak"
    cp "$FASTFETCH_DIR/config.jsonc" "$FASTFETCH_DIR/config.jsonc.bak"
fi

cp "$SCRIPT_DIR/config/fastfetch/config.jsonc" "$FASTFETCH_DIR/config.jsonc"
echo -e "  ${GREEN}✓${RESET} Installed $FASTFETCH_DIR/config.jsonc"

# 4. Install Fish function & greeting
echo ""
echo -e "${BOLD}[4/4] Installing Fish shell function...${RESET}"
FISH_FUNCTIONS_DIR="$HOME/.config/fish/functions"
mkdir -p "$FISH_FUNCTIONS_DIR"

cp "$SCRIPT_DIR/fish/functions/fastfetch.fish" "$FISH_FUNCTIONS_DIR/fastfetch.fish"
echo -e "  ${GREEN}✓${RESET} Installed $FISH_FUNCTIONS_DIR/fastfetch.fish"

FISH_CONFIG="$HOME/.config/fish/config.fish"
if [ -f "$FISH_CONFIG" ]; then
    if ! grep -q "fish_greeting" "$FISH_CONFIG"; then
        echo -e "\n# Pokemon Fastfetch greeting\nfunction fish_greeting\n    fastfetch\nend" >> "$FISH_CONFIG"
        echo -e "  ${GREEN}✓${RESET} Added fish_greeting to $FISH_CONFIG"
    else
        echo -e "  ${GREEN}✓${RESET} fish_greeting already configured in $FISH_CONFIG"
    fi
fi

echo ""
echo -e "${BOLD}${GREEN}==========================================${RESET}"
echo -e "${BOLD}${GREEN}   Installation completed successfully!   ${RESET}"
echo -e "${BOLD}${GREEN}==========================================${RESET}"
echo -e "Open a new ${CYAN}kitty${RESET} terminal or run ${CYAN}fastfetch${RESET} in ${CYAN}fish${RESET} to test!"
