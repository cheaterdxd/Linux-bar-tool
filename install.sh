#!/bin/bash

# =============================================================================
# EXEC LAUNCHER - INSTALLATION SCRIPT
# Platform: Debian 13 / Linux (GTK4)
# =============================================================================

set -e

# --- COLORS ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- CONFIGURATION ---
APP_NAME="Exec Launcher"
INSTALL_DIR="$HOME/.local/share/exec-launcher"
CONFIG_DIR="$HOME/.config/exec_launcher"
PROFILES_DIR="$CONFIG_DIR/profiles"
DESKTOP_FILE="$HOME/.local/share/applications/exec-launcher.desktop"
ICON_NAME="utilities-terminal"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  $APP_NAME - Installation${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# --- 1. CHECK DEPENDENCIES ---
echo -e "${YELLOW}[1/6] Checking dependencies...${NC}"

MISSING_PKGS=()

if ! command -v python3 &> /dev/null; then
    MISSING_PKGS+=("python3")
fi

if ! python3 -c "import gi; gi.require_version('Gtk', '4.0')" 2> /dev/null; then
    MISSING_PKGS+=("python3-gi" "gir1.2-gtk-4.0")
fi

if ! python3 -c "import gi; gi.require_version('Adw', '1')" 2> /dev/null; then
    MISSING_PKGS+=("gir1.2-adw-1")
fi

if ! python3 -c "import yaml" 2> /dev/null; then
    MISSING_PKGS+=("python3-yaml")
fi

if ! command -v notify-send &> /dev/null; then
    MISSING_PKGS+=("libnotify-bin")
fi

# Also need GObject introspection for Notify
if ! python3 -c "import gi; gi.require_version('Notify', '0.7')" 2> /dev/null; then
    MISSING_PKGS+=("gir1.2-notify-0.7")
fi

if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    echo -e "${YELLOW}Missing packages: ${MISSING_PKGS[@]}${NC}"
    echo -e "${YELLOW}Installing... (sudo password required)${NC}"
    sudo apt update
    sudo apt install -y "${MISSING_PKGS[@]}"
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ All dependencies ready${NC}"
fi

# --- 2. CREATE DIRECTORIES ---
echo ""
echo -e "${YELLOW}[2/6] Creating directories...${NC}"

mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$PROFILES_DIR"

echo -e "${GREEN}✓ Directories created:${NC}"
echo "   - App: $INSTALL_DIR"
echo "   - Config: $CONFIG_DIR"
echo "   - Profiles: $PROFILES_DIR"

# --- 3. INSTALL APPLICATION ---
echo ""
echo -e "${YELLOW}[3/6] Installing application...${NC}"

# Copy the app from repository
if [ -f "$SCRIPT_DIR/app.py" ]; then
    cp "$SCRIPT_DIR/app.py" "$INSTALL_DIR/app.py"
    chmod +x "$INSTALL_DIR/app.py"
    echo -e "${GREEN}✓ Installed app.py${NC}"
else
    echo -e "${RED}✗ app.py not found in $SCRIPT_DIR${NC}"
    echo -e "${RED}  Make sure you run this script from the repository directory.${NC}"
    exit 1
fi

# --- 4. CREATE .DESKTOP FILE ---
echo ""
echo -e "${YELLOW}[4/6] Creating desktop launcher...${NC}"

mkdir -p "$(dirname "$DESKTOP_FILE")"
cat > "$DESKTOP_FILE" << DESKTOP_EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=Manage and launch scripts via profiles
Exec=$INSTALL_DIR/app.py
Icon=$ICON_NAME
Terminal=false
Categories=Utility;System;
StartupNotify=true
DESKTOP_EOF

chmod +x "$DESKTOP_FILE"
echo -e "${GREEN}✓ Created $DESKTOP_FILE${NC}"

# --- 5. UPDATE DESKTOP DATABASE ---
echo ""
echo -e "${YELLOW}[5/6] Updating desktop database...${NC}"

if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    echo -e "${GREEN}✓ Desktop database updated${NC}"
else
    echo -e "${YELLOW}! update-desktop-database not found (skipping)${NC}"
fi

# --- 6. CREATE EXAMPLE PROFILE ---
echo ""
echo -e "${YELLOW}[6/6] Creating example profile...${NC}"

if [ -d "$SCRIPT_DIR/profiles" ]; then
    cp -n "$SCRIPT_DIR/profiles/"*.yaml "$PROFILES_DIR/" 2>/dev/null || true
    echo -e "${GREEN}✓ Example profiles copied${NC}"
else
    # Fallback: create via Python
    python3 -c "
import sys
sys.path.insert(0, '$INSTALL_DIR')
from app import ConfigManager
ConfigManager.create_template()
print('✓ Created example profile')
"
fi

# --- DONE ---
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  INSTALLATION COMPLETE!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "How to launch:"
echo -e "  1. Find '${APP_NAME}' in your Applications Menu"
echo -e "  2. Or run: ${BLUE}$INSTALL_DIR/app.py${NC}"
echo ""
echo -e "Profile config directory:"
echo -e "  ${BLUE}$PROFILES_DIR${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} If the icon doesn't appear in the menu, log out and log back in."
echo ""