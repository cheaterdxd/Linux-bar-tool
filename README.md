# Exec Launcher

A lightweight GTK4 GUI application for Linux that manages and executes system scripts through configurable YAML profiles.

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![GTK](https://img.shields.io/badge/GTK-4.0-green)
![Python](https://img.shields.io/badge/python-3.x-yellow)

## Features

- **Profile-based script execution** — Define scripts as YAML profiles and launch them with one click
- **Terminal integration** — Auto-detects your terminal emulator (GNOME Terminal, Konsole, Kitty, Xfce4, Alacritty)
- **Sudo support** — Run scripts with elevated privileges (authentication handled by terminal)
- **Concurrent execution** — Run multiple scripts simultaneously without UI blocking
- **Desktop integration** — Appears in your Applications Menu with proper `.desktop` entry
- **Toast + System notifications** — Feedback via in-app toasts and OS notifications
- **XDG compliant** — Config stored in `~/.config/exec_launcher/profiles/`

## Installation

### Prerequisites

- Debian 13 / Ubuntu or compatible Linux distribution
- GNOME or GTK4-compatible desktop environment

### Quick Install

```bash
git clone https://github.com/cheaterdxd/Linux-bar-tool.git
cd Linux-bar-tool
bash install.sh
```

The installer will automatically:
1. Install required system packages (`python3-gi`, `gir1.2-gtk-4.0`, `python3-yaml`, etc.)
2. Copy the application to `~/.local/share/exec-launcher/`
3. Create a `.desktop` entry in your Applications Menu
4. Set up an example profile

## Usage

### Launch the App

```bash
# From Applications Menu
# Or directly:
~/.local/share/exec-launcher/app.py
```

### Creating Profiles

Profiles are YAML files in `~/.config/exec_launcher/profiles/`. Each file defines one script:

```yaml
name: "System Update"
script: "/usr/bin/apt"
sudo_mode: 1
args:
  - "update"
  - "-y"
```

#### Profile Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String | **Yes** | Display name in the dropdown |
| `script` | String (Path) | **Yes** | Path to the script/executable |
| `sudo_mode` | Integer (0/1) | No | Run with sudo (default: 0) |
| `work_dir` | String (Path) | No | Working directory for execution |
| `args` | List[String] | No | Arguments passed to the script |
| `terminal` | String | No | Override terminal emulator |

### App Controls

| Button | Action |
|--------|--------|
| **▶ Run** | Execute the selected profile in a new terminal |
| **🔄 Reload** | Rescan profiles directory and update dropdown |
| **📂 Open Config** | Open the profiles folder in your file manager |
| **📝 New Template** | Create an `example.yaml` template file |

## Uninstall

```bash
bash remove.sh
```

## License

See [LICENSE](LICENSE) for details.
