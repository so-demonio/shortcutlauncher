# Shortcut Launcher for NVDA - Storage Module
# Copyright (C) 2025 Batuhan Demir

import json
import os
import uuid
import globalVars


class ShortcutsStorage:
    """Manages storage of shortcuts and settings in JSON format."""
    
    def __init__(self):
        """Initialize storage with config directory path."""
        self._configPath = os.path.join(globalVars.appArgs.configPath, "shortcutsManager")
        os.makedirs(self._configPath, exist_ok=True)
        self._dataFile = os.path.join(self._configPath, "shortcuts.json")
        self._data = self._load()
    
    def _load(self) -> dict:
        """Load data from JSON file."""
        if os.path.exists(self._dataFile):
            try:
                with open(self._dataFile, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self._getDefaultData()
    
    def _getDefaultData(self) -> dict:
        """Return default data structure."""
        return {
            "shortcuts": [],
            "settings": {
                "lastFilter": "all",
                "defaultBrowser": "auto",
                "customBrowserPath": ""
            }
        }
    
    def save(self):
        """Save data to JSON file."""
        try:
            with open(self._dataFile, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise Exception(f"Failed to save shortcuts: {e}")
    
    def get_shortcuts(self, filter_type: str = "all") -> list:
        """
        Get shortcuts, optionally filtered by type.
        
        Args:
            filter_type: "all", "program", "folder", or "url"
        
        Returns:
            List of shortcut dictionaries
        """
        shortcuts = self._data.get("shortcuts", [])
        if filter_type == "all":
            return shortcuts
        return [s for s in shortcuts if s.get("type") == filter_type]
    
    def get_shortcut_by_id(self, shortcut_id: str) -> dict:
        """Get a single shortcut by its ID."""
        for shortcut in self._data.get("shortcuts", []):
            if shortcut.get("id") == shortcut_id:
                return shortcut
        return None
    
    def add_shortcut(self, name: str, shortcut_type: str, target: str, gesture: str = "") -> dict:
        """
        Add a new shortcut.
        
        Args:
            name: Display name for the shortcut
            shortcut_type: "program", "folder", or "url"
            target: Path or URL
            gesture: Optional keyboard gesture string
        
        Returns:
            The created shortcut dictionary
        """
        shortcut = {
            "id": str(uuid.uuid4()),
            "name": name,
            "type": shortcut_type,
            "target": target,
            "gesture": gesture
        }
        
        if "shortcuts" not in self._data:
            self._data["shortcuts"] = []
        
        self._data["shortcuts"].append(shortcut)
        self.save()
        return shortcut
    
    def update_shortcut(self, shortcut_id: str, name: str = None, shortcut_type: str = None, 
                        target: str = None, gesture: str = None) -> bool:
        """
        Update an existing shortcut.
        
        Args:
            shortcut_id: ID of the shortcut to update
            name: New name (optional)
            shortcut_type: New type (optional)
            target: New target (optional)
            gesture: New gesture (optional)
        
        Returns:
            True if updated, False if not found
        """
        for shortcut in self._data.get("shortcuts", []):
            if shortcut.get("id") == shortcut_id:
                if name is not None:
                    shortcut["name"] = name
                if shortcut_type is not None:
                    shortcut["type"] = shortcut_type
                if target is not None:
                    shortcut["target"] = target
                if gesture is not None:
                    shortcut["gesture"] = gesture
                self.save()
                return True
        return False
    
    def delete_shortcut(self, shortcut_id: str) -> bool:
        """
        Delete a shortcut by its ID.
        
        Returns:
            True if deleted, False if not found
        """
        shortcuts = self._data.get("shortcuts", [])
        for i, shortcut in enumerate(shortcuts):
            if shortcut.get("id") == shortcut_id:
                shortcuts.pop(i)
                self.save()
                return True
        return False
    
    def get_setting(self, key: str, default=None):
        """Get a setting value."""
        return self._data.get("settings", {}).get(key, default)
    
    def set_setting(self, key: str, value):
        """Set a setting value."""
        if "settings" not in self._data:
            self._data["settings"] = {}
        self._data["settings"][key] = value
        self.save()
    
    def reload(self):
        """Reload data from disk."""
        self._data = self._load()
