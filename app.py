#!/usr/bin/python3
# =============================================================================
# EXEC LAUNCHER - Lightweight Script Launcher for Linux Desktop
# Platform: Debian 13 / GNOME / GTK4
# =============================================================================

import os
import sys
import subprocess
import threading
import shutil
from pathlib import Path

# --- Dependency Check ---
try:
    import yaml
except ImportError:
    print("ERROR: python3-yaml is not installed.")
    print("Install it with: sudo apt install python3-yaml")
    sys.exit(1)

try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    gi.require_version('Notify', '0.7')
    from gi.repository import Gtk, Gio, GLib, Notify, Adw
except (ImportError, ValueError) as e:
    print(f"ERROR: GTK4 dependencies are missing: {e}")
    print("Install them with: sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 libnotify-bin")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================
APP_ID = "com.example.execlauncher"
APP_NAME = "Exec Launcher"
APP_VERSION = "1.0.0"

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "exec_launcher"
PROFILES_DIR = CONFIG_DIR / "profiles"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
PROFILES_DIR.mkdir(parents=True, exist_ok=True)

# Terminal emulators to try (in order of preference)
TERMINAL_CANDIDATES = [
    "gnome-terminal",
    "xfce4-terminal",
    "konsole",
    "kitty",
    "alacritty",
    "xterm",
]


# =============================================================================
# CONFIG MANAGER
# =============================================================================
class ConfigManager:
    """Manages loading and validating YAML profile configurations."""

    REQUIRED_FIELDS = {"name", "script"}

    @staticmethod
    def get_profiles():
        """Scan profiles directory and return list of valid profile dicts."""
        profiles = []
        if not PROFILES_DIR.exists():
            return profiles

        for ext in ("*.yaml", "*.yml"):
            for filepath in PROFILES_DIR.glob(ext):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)

                    if not isinstance(data, dict):
                        print(f"[WARN] Skipping {filepath.name}: not a valid YAML mapping")
                        continue

                    # Validate required fields
                    missing = ConfigManager.REQUIRED_FIELDS - set(data.keys())
                    if missing:
                        print(f"[WARN] Skipping {filepath.name}: missing fields {missing}")
                        continue

                    data["_file_path"] = str(filepath)
                    profiles.append(data)

                except yaml.YAMLError as e:
                    print(f"[ERROR] YAML parse error in {filepath.name}: {e}")
                except Exception as e:
                    print(f"[ERROR] Failed to read {filepath.name}: {e}")

        return sorted(profiles, key=lambda p: p.get("name", ""))

    @staticmethod
    def create_template():
        """Create an example profile YAML file if it doesn't exist."""
        template_path = PROFILES_DIR / "example.yaml"
        if template_path.exists():
            return False

        content = (
            'name: "System Check Example"\n'
            'script: "/bin/bash"\n'
            "sudo_mode: 0\n"
            "args:\n"
            '  - "-c"\n'
            "  - \"echo '========================================'; "
            "echo '  Exec Launcher - Test Profile'; "
            "echo '========================================'; "
            "echo ''; "
            "echo 'Hostname:' $(hostname); "
            "echo 'Kernel:' $(uname -r); "
            "echo 'Uptime:' $(uptime -p); "
            "echo ''; "
            "echo 'Done! Press Enter to close.'; "
            'read"\n'
        )
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True


# =============================================================================
# EXECUTOR
# =============================================================================
class Executor:
    """Handles launching scripts in external terminal windows."""

    @staticmethod
    def detect_terminal():
        """Auto-detect available terminal emulator."""
        # Check environment variable first
        env_term = os.environ.get("TERMINAL")
        if env_term and shutil.which(env_term):
            return env_term

        # Try candidates
        for term in TERMINAL_CANDIDATES:
            if shutil.which(term):
                return term

        return None

    @staticmethod
    def build_terminal_command(terminal, script_cmd):
        """Build the command list for the detected terminal emulator."""
        term_basename = os.path.basename(terminal)

        if "gnome-terminal" in term_basename:
            return [terminal, "--", *script_cmd]
        elif "xfce4-terminal" in term_basename:
            # xfce4-terminal uses -e with a single string command
            return [terminal, "-e", " ".join(script_cmd)]
        elif "konsole" in term_basename:
            return [terminal, "-e", *script_cmd]
        elif "kitty" in term_basename:
            return [terminal, "--", *script_cmd]
        elif "alacritty" in term_basename:
            return [terminal, "-e", *script_cmd]
        else:
            return [terminal, "-e", *script_cmd]

    @staticmethod
    def run_profile(profile, show_toast):
        """Execute a profile's script in a new terminal window."""
        script = profile.get("script", "")
        sudo_mode = profile.get("sudo_mode", 0)
        args = profile.get("args", [])
        work_dir = profile.get("work_dir", None)
        name = profile.get("name", "Unknown")
        terminal_override = profile.get("terminal", None)

        # Validate script path
        if not script:
            show_toast(f"❌ Error: No script path in profile '{name}'")
            return

        # For absolute paths, check existence; for commands, check in PATH
        if os.path.isabs(script):
            if not os.path.exists(script):
                show_toast(f"❌ Error: Script not found '{script}'")
                return
            if not os.access(script, os.X_OK) and sudo_mode != 1:
                show_toast(f"⚠️ Warning: Script not executable '{script}'")
                return

        # Validate work_dir
        if work_dir and not os.path.isdir(work_dir):
            show_toast(f"⚠️ Warning: work_dir not found '{work_dir}'")
            work_dir = None

        # Detect terminal
        terminal = None
        if terminal_override and shutil.which(terminal_override):
            terminal = terminal_override
        else:
            terminal = Executor.detect_terminal()

        if not terminal:
            show_toast("❌ Error: No terminal emulator found!")
            return

        # Build script command
        script_cmd = []
        if sudo_mode == 1:
            script_cmd.append("sudo")
        script_cmd.append(script)
        script_cmd.extend([str(a) for a in args])

        # Build full terminal command
        command = Executor.build_terminal_command(terminal, script_cmd)

        def thread_target():
            try:
                subprocess.Popen(
                    command,
                    cwd=work_dir,
                    start_new_session=True,  # Detach from parent process
                    stdin=subprocess.DEVNULL,
                )
                GLib.idle_add(show_toast, f"✅ Launched: {name}", True)
            except FileNotFoundError:
                GLib.idle_add(show_toast, f"❌ Terminal not found: {terminal}")
            except PermissionError:
                GLib.idle_add(show_toast, f"❌ Permission denied: {script}")
            except Exception as e:
                GLib.idle_add(show_toast, f"❌ Error running '{name}': {e}")

        threading.Thread(target=thread_target, daemon=True).start()


# =============================================================================
# GTK4 APPLICATION WINDOW
# =============================================================================
class AppWindow(Gtk.ApplicationWindow):
    """Main application window with profile selector and action buttons."""

    def __init__(self, app):
        super().__init__(application=app, title=APP_NAME)
        self.set_default_size(460, 180)
        self.set_resizable(True)

        # --- Toast overlay (wraps entire window content) ---
        self.toast_overlay = Gtk.ToastOverlay()
        self.set_child(self.toast_overlay)

        # --- Main vertical box ---
        main_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_start=20,
            margin_end=20,
            margin_top=20,
            margin_bottom=20,
        )
        self.toast_overlay.set_child(main_box)

        # --- Header label ---
        header = Gtk.Label(label="⚡ Exec Launcher")
        header.add_css_class("title-2")
        header.set_halign(Gtk.Align.START)
        main_box.append(header)

        # --- Profile selector row ---
        row_profile = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.dropdown = Gtk.DropDown()
        self.dropdown.set_hexpand(True)
        row_profile.append(self.dropdown)

        self.btn_run = Gtk.Button(label="▶ Run")
        self.btn_run.add_css_class("suggested-action")
        self.btn_run.set_size_request(90, -1)
        self.btn_run.connect("clicked", self.on_run_clicked)
        row_profile.append(self.btn_run)

        main_box.append(row_profile)

        # --- Control buttons row ---
        row_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row_ctrl.set_homogeneous(True)

        self.btn_reload = Gtk.Button(label="🔄 Reload")
        self.btn_reload.connect("clicked", self.on_reload_clicked)
        row_ctrl.append(self.btn_reload)

        self.btn_setup = Gtk.Button(label="📂 Open Config")
        self.btn_setup.connect("clicked", self.on_setup_clicked)
        row_ctrl.append(self.btn_setup)

        self.btn_template = Gtk.Button(label="📝 New Template")
        self.btn_template.connect("clicked", self.on_template_clicked)
        row_ctrl.append(self.btn_template)

        main_box.append(row_ctrl)

        # --- Status bar ---
        self.status_label = Gtk.Label(label="")
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.add_css_class("dim-label")
        self.status_label.add_css_class("caption")
        main_box.append(self.status_label)

        # --- Initialize ---
        self.profile_data = []
        self.load_profiles()

        # Init system notifications
        Notify.init(APP_NAME)

    def show_toast(self, message, is_success=False):
        """Show a toast notification in-app and send a system notification."""
        toast = Gtk.Toast.new(message)
        toast.set_timeout(3)
        if is_success:
            toast.set_priority(Gtk.ToastPriority.HIGH)
        self.toast_overlay.add_toast(toast)

        # System notification
        try:
            icon = "dialog-information" if is_success else "dialog-warning"
            notification = Notify.Notification.new(APP_NAME, message, icon)
            notification.show()
        except Exception:
            pass  # Don't crash if notification fails

    def load_profiles(self):
        """Load profiles from config directory and populate dropdown."""
        profiles = ConfigManager.get_profiles()
        self.profile_data = profiles

        store = Gio.ListStore.new(Gtk.StringObject)
        for p in profiles:
            store.append(Gtk.StringObject.new(p["name"]))

        self.dropdown.set_model(store)

        count = len(profiles)
        if count > 0:
            self.dropdown.set_selected(0)
            self.status_label.set_text(f"📋 {count} profile(s) loaded from {PROFILES_DIR}")
        else:
            self.status_label.set_text("No profiles found. Click 'New Template' to create one.")

    # --- Button Handlers ---

    def on_run_clicked(self, button):
        """Handle Run button click."""
        if not self.profile_data:
            self.show_toast("⚠️ No profile selected")
            return

        selected = self.dropdown.get_selected()
        if selected < 0 or selected >= len(self.profile_data):
            self.show_toast("⚠️ Please select a profile")
            return

        profile = self.profile_data[selected]
        Executor.run_profile(profile, self.show_toast)

    def on_reload_clicked(self, button):
        """Handle Reload button click."""
        self.load_profiles()
        self.show_toast("🔄 Profiles reloaded", True)

    def on_setup_clicked(self, button):
        """Open the profiles config directory in the file manager."""
        try:
            subprocess.Popen(["xdg-open", str(PROFILES_DIR)])
        except Exception as e:
            self.show_toast(f"❌ Cannot open folder: {e}")

    def on_template_clicked(self, button):
        """Create a template profile and reload."""
        created = ConfigManager.create_template()
        self.load_profiles()
        if created:
            self.show_toast("📝 Created example.yaml template", True)
        else:
            self.show_toast("ℹ️ example.yaml already exists")


# =============================================================================
# APPLICATION
# =============================================================================
class ExecLauncherApp(Gtk.Application):
    """GTK4 Application class."""

    def __init__(self):
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

    def do_activate(self):
        win = AppWindow(self)
        win.present()


# =============================================================================
# MAIN
# =============================================================================
def main():
    # Create template on first run
    ConfigManager.create_template()

    app = ExecLauncherApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
