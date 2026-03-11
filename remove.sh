#!/bin/bash

# =============================================================================
# EXEC LAUNCHER - UNINSTALL SCRIPT
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="$HOME/.local/share/exec-launcher"
CONFIG_DIR="$HOME/.config/exec_launcher"
DESKTOP_FILE="$HOME/.local/share/applications/exec-launcher.desktop"

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}  Exec Launcher - Uninstall${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

echo -e "This will remove:"
echo -e "  - ${BLUE}$INSTALL_DIR${NC}"
echo -e "  - ${BLUE}$CONFIG_DIR${NC} (including all profiles!)"
echo -e "  - ${BLUE}$DESKTOP_FILE${NC}"
echo ""

read -p "Are you sure? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$INSTALL_DIR"
    rm -rf "$CONFIG_DIR"
    rm -f "$DESKTOP_FILE"

    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    fi

    echo ""
    echo -e "${GREEN}✓ Exec Launcher has been uninstalled.${NC}"
else
    echo ""
    echo -e "${YELLOW}Uninstall cancelled.${NC}"
fi