"""
Hindsight Plugin — Framework Lifecycle Hooks

Called automatically by the Agent Zero plugin system:
- install()      : after plugin is placed in usr/plugins/
- pre_update()   : before plugin code is updated in place
- uninstall()    : before plugin directory is deleted
"""

import subprocess
import sys

_PACKAGE = "hindsight-client>=0.4.0"


def install():
    """Install Hindsight SDK into the framework runtime."""
    print("[Hindsight] Installing dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", _PACKAGE],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[Hindsight] pip install failed:\n{result.stderr}")
        raise RuntimeError(f"Failed to install {_PACKAGE}")
    print(f"[Hindsight] Installed {_PACKAGE} successfully.")



def uninstall():
    """Clean up Hindsight SDK dependency before plugin removal."""
    print("[Hindsight] Uninstalling dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", "hindsight-client"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[Hindsight] pip uninstall warning:\n{result.stderr}")
    else:
        print("[Hindsight] Uninstalled hindsight-client successfully.")
def pre_update():
    """Re-install dependencies before an update (ensures compatibility)."""
    install()
