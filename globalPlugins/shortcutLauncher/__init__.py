# Shortcut Launcher for NVDA
# Copyright (C) 2025 Batuhan Demir
# This add-on is licensed under the GNU General Public License version 2.

import globalPluginHandler
import addonHandler
from scriptHandler import script
import gui
import wx
import os

from .storage import ShortcutsStorage
from .ui import ShortcutLauncherDialog
from .settings import ShortcutLauncherSettingsPanel
from . import browserDetect

addonHandler.initTranslation()

# Global storage instance
_storage = None

def getStorage():
    """Get the global storage instance."""
    global _storage
    if _storage is None:
        _storage = ShortcutsStorage()
    return _storage


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    """Global plugin for launching shortcuts."""
    
    # Translators: Category name shown in Input Gestures
    scriptCategory = _("Shortcut Launcher")
    
    def __init__(self):
        super().__init__()
        self._storage = getStorage()
        self._dialog = None
        
        # Register settings panel
        gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(ShortcutLauncherSettingsPanel)
    
    def terminate(self):
        """Clean up when the plugin is terminated."""
        super().terminate()
        
        # Remove settings panel
        try:
            gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(ShortcutLauncherSettingsPanel)
        except ValueError:
            pass
        
        # Close dialog if open
        if self._dialog:
            try:
                self._dialog.Destroy()
            except:
                pass
    
    @script(
        gesture="kb:NVDA+shift+h",
        # Translators: Description for opening the shortcut launcher
        description=_("Open Shortcut Launcher")
    )
    def script_openShortcutLauncher(self, gesture):
        """Open the Shortcut Launcher dialog."""
        def openDialog():
            if self._dialog:
                try:
                    self._dialog.Raise()
                    self._dialog.SetFocus()
                    return
                except:
                    pass
            
            self._dialog = ShortcutLauncherDialog(
                gui.mainFrame,
                self._storage
            )
            self._dialog.Show()
        
        wx.CallAfter(openDialog)
