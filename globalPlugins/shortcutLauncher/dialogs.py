# Shortcut Launcher for NVDA - Add/Edit Dialogs
# Copyright (C) 2025 Batuhan Demir

import wx
import os
import addonHandler
import gui

addonHandler.initTranslation()


class AddEditShortcutDialog(wx.Dialog):
    """Dialog for adding or editing a shortcut."""
    
    # Type choices mapping
    TYPE_MAP = ["program", "folder", "url"]
    
    def __init__(self, parent, shortcut=None):
        """
        Initialize the Add/Edit Shortcut dialog.
        
        Args:
            parent: Parent window
            shortcut: Existing shortcut dict to edit, or None for new
        """
        self._isEdit = shortcut is not None
        self._shortcut = shortcut or {}
        
        # Translators: Title for edit shortcut dialog
        editTitle = _("Edit Shortcut")
        # Translators: Title for add shortcut dialog
        addTitle = _("Add Shortcut")
        title = editTitle if self._isEdit else addTitle
        
        super().__init__(parent, title=title, 
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self._createControls()
        self._layoutControls()
        self._bindEvents()
        self._loadData()
        
        self.SetMinSize((400, 200))
        self.SetSize((450, 220))
        self.CenterOnParent()
        
        # Set initial focus
        self.nameText.SetFocus()
    
    def _createControls(self):
        """Create all UI controls."""
        # Name
        # Translators: Label for shortcut name field
        self.nameLabel = wx.StaticText(self, label=_("&Name:"))
        self.nameText = wx.TextCtrl(self)
        
        # Type
        # Translators: Label for shortcut type dropdown
        self.typeLabel = wx.StaticText(self, label=_("&Type:"))
        self.typeChoices = [
            # Translators: Shortcut type option
            _("Program"),
            # Translators: Shortcut type option
            _("Folder"),
            # Translators: Shortcut type option
            _("URL")
        ]
        self.typeChoice = wx.Choice(self, choices=self.typeChoices)
        self.typeChoice.SetSelection(0)
        
        # Target
        # Translators: Label for shortcut target field
        self.targetLabel = wx.StaticText(self, label=_("&Target:"))
        self.targetText = wx.TextCtrl(self)
        # Translators: Button to browse for file/folder
        self.browseBtn = wx.Button(self, label=_("&Browse..."))
        
        # OK and Cancel buttons
        self.okBtn = wx.Button(self, wx.ID_OK)
        self.cancelBtn = wx.Button(self, wx.ID_CANCEL)
    
    def _layoutControls(self):
        """Layout all controls using sizers."""
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Use a FlexGridSizer for labels and controls
        gridSizer = wx.FlexGridSizer(rows=3, cols=2, hgap=10, vgap=10)
        gridSizer.AddGrowableCol(1, 1)
        
        # Name row
        gridSizer.Add(self.nameLabel, 0, wx.ALIGN_CENTER_VERTICAL)
        gridSizer.Add(self.nameText, 1, wx.EXPAND)
        
        # Type row
        gridSizer.Add(self.typeLabel, 0, wx.ALIGN_CENTER_VERTICAL)
        gridSizer.Add(self.typeChoice, 1, wx.EXPAND)
        
        # Target row
        gridSizer.Add(self.targetLabel, 0, wx.ALIGN_CENTER_VERTICAL)
        targetSizer = wx.BoxSizer(wx.HORIZONTAL)
        targetSizer.Add(self.targetText, 1, wx.EXPAND)
        targetSizer.Add(self.browseBtn, 0, wx.LEFT, 5)
        gridSizer.Add(targetSizer, 1, wx.EXPAND)
        
        mainSizer.Add(gridSizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Buttons
        buttonSizer = wx.StdDialogButtonSizer()
        buttonSizer.AddButton(self.okBtn)
        buttonSizer.AddButton(self.cancelBtn)
        buttonSizer.Realize()
        
        mainSizer.Add(buttonSizer, 0, wx.EXPAND | wx.ALL, 10)
        
        self.SetSizer(mainSizer)
    
    def _bindEvents(self):
        """Bind event handlers."""
        self.typeChoice.Bind(wx.EVT_CHOICE, self._onTypeChange)
        self.browseBtn.Bind(wx.EVT_BUTTON, self._onBrowse)
        self.okBtn.Bind(wx.EVT_BUTTON, self._onOK)
        self.Bind(wx.EVT_CHAR_HOOK, self._onCharHook)
    
    def _onCharHook(self, event):
        """Handle ESC key to close dialog."""
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
            return
        event.Skip()
    
    def _loadData(self):
        """Load existing shortcut data if editing."""
        if self._isEdit:
            self.nameText.SetValue(self._shortcut.get("name", ""))
            
            shortcut_type = self._shortcut.get("type", "program")
            if shortcut_type in self.TYPE_MAP:
                self.typeChoice.SetSelection(self.TYPE_MAP.index(shortcut_type))
            
            self.targetText.SetValue(self._shortcut.get("target", ""))
        
        self._updateBrowseButton()
    
    def _updateBrowseButton(self):
        """Update browse button visibility based on type."""
        typeIndex = self.typeChoice.GetSelection()
        shortcut_type = self.TYPE_MAP[typeIndex] if typeIndex >= 0 else "program"
        
        # Show browse button only for program and folder types
        self.browseBtn.Enable(shortcut_type in ["program", "folder"])
    
    def _onTypeChange(self, event):
        """Handle type selection change."""
        self._updateBrowseButton()
        
        # Update target label hint
        typeIndex = self.typeChoice.GetSelection()
        shortcut_type = self.TYPE_MAP[typeIndex] if typeIndex >= 0 else "program"
        
        if shortcut_type == "program":
            # Translators: Hint for program target field
            self.targetText.SetHint(_("Path to executable..."))
        elif shortcut_type == "folder":
            # Translators: Hint for folder target field
            self.targetText.SetHint(_("Path to folder..."))
        elif shortcut_type == "url":
            # Translators: Hint for URL target field
            self.targetText.SetHint(_("https://example.com"))
    
    def _onBrowse(self, event):
        """Handle Browse button click."""
        typeIndex = self.typeChoice.GetSelection()
        shortcut_type = self.TYPE_MAP[typeIndex] if typeIndex >= 0 else "program"
        
        if shortcut_type == "program":
            # File dialog for programs
            # Translators: Title for program file selection dialog
            dlg = wx.FileDialog(
                self,
                message=_("Select Program"),
                wildcard=_("Executable files (*.exe)|*.exe|All files (*.*)|*.*"),
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
            )
        elif shortcut_type == "folder":
            # Directory dialog for folders
            # Translators: Title for folder selection dialog
            dlg = wx.DirDialog(
                self,
                message=_("Select Folder"),
                style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
            )
        else:
            return
        
        if dlg.ShowModal() == wx.ID_OK:
            self.targetText.SetValue(dlg.GetPath())
        
        dlg.Destroy()
    
    def _onOK(self, event):
        """Handle OK button click with validation."""
        name = self.nameText.GetValue().strip()
        target = self.targetText.GetValue().strip()
        typeIndex = self.typeChoice.GetSelection()
        
        # Validate name
        if not name:
            # Translators: Error message when name is empty
            gui.messageBox(_("Please enter a name for the shortcut."), 
                          _("Validation Error"), wx.OK | wx.ICON_ERROR)
            self.nameText.SetFocus()
            return
        
        # Validate target
        if not target:
            # Translators: Error message when target is empty
            gui.messageBox(_("Please enter a target for the shortcut."), 
                          _("Validation Error"), wx.OK | wx.ICON_ERROR)
            self.targetText.SetFocus()
            return
        
        shortcut_type = self.TYPE_MAP[typeIndex] if typeIndex >= 0 else "program"
        
        # Validate target exists for program/folder
        if shortcut_type == "program" and not os.path.isfile(target):
            # Translators: Error message when program file doesn't exist
            gui.messageBox(_("The specified program file does not exist."), 
                          _("Validation Error"), wx.OK | wx.ICON_ERROR)
            self.targetText.SetFocus()
            return
        
        if shortcut_type == "folder" and not os.path.isdir(target):
            # Translators: Error message when folder doesn't exist
            gui.messageBox(_("The specified folder does not exist."), 
                          _("Validation Error"), wx.OK | wx.ICON_ERROR)
            self.targetText.SetFocus()
            return
        
        self.EndModal(wx.ID_OK)
    
    def getData(self) -> dict:
        """
        Get the entered data.
        
        Returns:
            Dictionary with name, type, and target
        """
        typeIndex = self.typeChoice.GetSelection()
        return {
            "name": self.nameText.GetValue().strip(),
            "type": self.TYPE_MAP[typeIndex] if typeIndex >= 0 else "program",
            "target": self.targetText.GetValue().strip()
        }
