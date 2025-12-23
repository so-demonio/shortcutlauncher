# Shortcut Launcher for NVDA - Settings Panel
# Copyright (C) 2025 Batuhan Demir

import wx
import os
import addonHandler
import gui
from gui import guiHelper

from .storage import ShortcutsStorage
from . import browserDetect

addonHandler.initTranslation()

# Get storage instance
def _getStorage():
    from . import getStorage
    return getStorage()


class ShortcutLauncherSettingsPanel(gui.SettingsPanel):
    """Settings panel for Shortcut Launcher in NVDA Settings dialog."""
    
    # Translators: Title of the settings panel
    title = _("Shortcut Launcher")
    
    def makeSettings(self, settingsSizer):
        """Create the settings panel controls."""
        sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        self._storage = _getStorage()
        
        # Detect available browsers
        self._browsers = browserDetect.detect_browsers()
        
        # Build browser choices list
        # Translators: Option to use system default browser
        self._browserChoices = [_("System Default")]
        self._browserIds = ["auto"]
        
        for browser in self._browsers:
            self._browserChoices.append(browser["name"])
            self._browserIds.append(browser["id"])
        
        # Translators: Option to specify a custom browser
        self._browserChoices.append(_("Custom..."))
        self._browserIds.append("custom")
        
        # Browser selection dropdown
        # Translators: Label for browser selection dropdown
        browserLabel = _("Default &browser for URLs:")
        self.browserChoice = sHelper.addLabeledControl(
            browserLabel,
            wx.Choice,
            choices=self._browserChoices
        )
        
        # Set current selection
        currentBrowser = self._storage.get_setting("defaultBrowser", "auto")
        if currentBrowser in self._browserIds:
            self.browserChoice.SetSelection(self._browserIds.index(currentBrowser))
        else:
            self.browserChoice.SetSelection(0)
        
        # Custom browser path
        # Translators: Label for custom browser path field
        customPathLabel = _("Custom browser &path:")
        self.customBrowserPath = sHelper.addLabeledControl(
            customPathLabel,
            wx.TextCtrl
        )
        self.customBrowserPath.SetValue(self._storage.get_setting("customBrowserPath", ""))
        
        # Browse button for custom path
        # Translators: Button to browse for custom browser executable
        self.browseBtn = sHelper.addItem(
            wx.Button(self, label=_("B&rowse..."))
        )
        self.browseBtn.Bind(wx.EVT_BUTTON, self._onBrowse)
        
        # Update custom path visibility
        self._updateCustomPathVisibility()
        self.browserChoice.Bind(wx.EVT_CHOICE, self._onBrowserChange)
        
        # Separator
        sHelper.addItem(wx.StaticLine(self))
        
        # Shortcut count info
        shortcutCount = len(self._storage.get_shortcuts())
        # Translators: Label showing total number of shortcuts
        infoText = _("Total shortcuts: {}").format(shortcutCount)
        self.infoLabel = sHelper.addItem(wx.StaticText(self, label=infoText))
        
        # Open manager button
        # Translators: Button to open the Shortcut Launcher dialog
        self.manageBtn = sHelper.addItem(
            wx.Button(self, label=_("&Manage Shortcuts..."))
        )
        self.manageBtn.Bind(wx.EVT_BUTTON, self._onManage)
    
    def _updateCustomPathVisibility(self):
        """Show/hide custom path controls based on browser selection."""
        selection = self.browserChoice.GetSelection()
        isCustom = self._browserIds[selection] == "custom" if selection >= 0 else False
        
        self.customBrowserPath.Enable(isCustom)
        self.browseBtn.Enable(isCustom)
    
    def _onBrowserChange(self, event):
        """Handle browser selection change."""
        self._updateCustomPathVisibility()
    
    def _onBrowse(self, event):
        """Handle browse button for custom browser."""
        # Translators: Title for browser executable selection dialog
        dlg = wx.FileDialog(
            self,
            message=_("Select Browser Executable"),
            wildcard=_("Executable files (*.exe)|*.exe|All files (*.*)|*.*"),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            self.customBrowserPath.SetValue(dlg.GetPath())
        
        dlg.Destroy()
    
    def _onManage(self, event):
        """Open the Shortcut Launcher dialog."""
        from .ui import ShortcutLauncherDialog
        
        dlg = ShortcutLauncherDialog(
            self,
            self._storage
        )
        dlg.ShowModal()
        dlg.Destroy()
        
        # Update shortcut count
        shortcutCount = len(self._storage.get_shortcuts())
        # Translators: Label showing total number of shortcuts
        self.infoLabel.SetLabel(_("Total shortcuts: {}").format(shortcutCount))
    
    def onSave(self):
        """Save settings when OK is clicked."""
        selection = self.browserChoice.GetSelection()
        if selection >= 0:
            browserId = self._browserIds[selection]
            self._storage.set_setting("defaultBrowser", browserId)
        
        customPath = self.customBrowserPath.GetValue().strip()
        self._storage.set_setting("customBrowserPath", customPath)
    
    def isValid(self):
        """Validate settings before saving."""
        selection = self.browserChoice.GetSelection()
        if selection >= 0 and self._browserIds[selection] == "custom":
            customPath = self.customBrowserPath.GetValue().strip()
            if customPath and not os.path.isfile(customPath):
                # Translators: Error message when custom browser path is invalid
                gui.messageBox(
                    _("The specified browser executable does not exist."),
                    _("Validation Error"),
                    wx.OK | wx.ICON_ERROR
                )
                return False
        return True
