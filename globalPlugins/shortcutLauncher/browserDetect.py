# Shortcut Launcher for NVDA - Browser Detection Module
# Copyright (C) 2025 Batuhan Demir

import os
import subprocess
import winreg


# Known browser paths (relative to Program Files or LocalAppData)
KNOWN_BROWSERS = {
    "chrome": {
        "name": "Google Chrome",
        "paths": [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
        ]
    },
    "firefox": {
        "name": "Mozilla Firefox",
        "paths": [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Mozilla Firefox", "firefox.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Mozilla Firefox", "firefox.exe"),
        ]
    },
    "edge": {
        "name": "Microsoft Edge",
        "paths": [
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        ]
    },
    "brave": {
        "name": "Brave",
        "paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
        ]
    },
    "opera": {
        "name": "Opera",
        "paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Opera", "launcher.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Opera", "launcher.exe"),
        ]
    },
    "vivaldi": {
        "name": "Vivaldi",
        "paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Vivaldi", "Application", "vivaldi.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Vivaldi", "Application", "vivaldi.exe"),
        ]
    }
}


def detect_browsers() -> list:
    """
    Detect installed browsers on the system.
    
    Returns:
        List of dictionaries with 'id', 'name', and 'path' keys
    """
    found = []
    
    for browser_id, info in KNOWN_BROWSERS.items():
        for path in info["paths"]:
            if path and os.path.exists(path):
                found.append({
                    "id": browser_id,
                    "name": info["name"],
                    "path": path
                })
                break  # Only add the first found path for each browser
    
    # Also try to detect from registry
    try:
        found.extend(_detect_from_registry())
    except:
        pass
    
    # Remove duplicates based on browser id
    seen_ids = set()
    unique = []
    for browser in found:
        if browser["id"] not in seen_ids:
            seen_ids.add(browser["id"])
            unique.append(browser)
    
    return unique


def _detect_from_registry() -> list:
    """Detect browsers from Windows registry."""
    found = []
    
    # Check HKEY_LOCAL_MACHINE\SOFTWARE\Clients\StartMenuInternet
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Clients\StartMenuInternet"
        )
        
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, f"{subkey_name}\\shell\\open\\command")
                command, _ = winreg.QueryValueEx(subkey, "")
                
                # Extract path from command
                if command:
                    path = command.strip('"').split('"')[0]
                    if os.path.exists(path):
                        # Try to get the name
                        try:
                            name_key = winreg.OpenKey(key, subkey_name)
                            name, _ = winreg.QueryValueEx(name_key, "")
                            winreg.CloseKey(name_key)
                        except:
                            name = subkey_name
                        
                        # Create a simple ID from the name
                        browser_id = name.lower().replace(" ", "_")
                        
                        # Check if this is already in known browsers
                        is_known = False
                        for known_id, known_info in KNOWN_BROWSERS.items():
                            if known_info["name"].lower() in name.lower():
                                is_known = True
                                break
                        
                        if not is_known:
                            found.append({
                                "id": browser_id,
                                "name": name,
                                "path": path
                            })
                
                winreg.CloseKey(subkey)
                i += 1
            except WindowsError:
                break
        
        winreg.CloseKey(key)
    except WindowsError:
        pass
    
    return found


def open_url(url: str, browser_path: str = None):
    """
    Open a URL in the specified browser or the system default.
    
    Args:
        url: The URL to open
        browser_path: Optional path to browser executable
    """
    if browser_path and os.path.exists(browser_path):
        subprocess.Popen([browser_path, url])
    else:
        # Use system default browser
        os.startfile(url)


def validate_browser_path(path: str) -> bool:
    """
    Validate that a path points to an executable file.
    
    Args:
        path: Path to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not path:
        return False
    if not os.path.exists(path):
        return False
    if not os.path.isfile(path):
        return False
    # Check if it's an executable
    _, ext = os.path.splitext(path)
    return ext.lower() in ['.exe', '.bat', '.cmd']
