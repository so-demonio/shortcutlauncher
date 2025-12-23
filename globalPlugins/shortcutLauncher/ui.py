# Shortcut Launcher for NVDA - Main UI Dialog
# Copyright (C) 2025 Batuhan Demir

import wx
import addonHandler
import gui
import ui

addonHandler.initTranslation()


class ShortcutLauncherDialog(wx.Dialog):
    """Main dialog for managing shortcuts with list and filter radio buttons."""
    
    # Filter type to storage value mapping
    FILTER_MAP = ["all", "program", "folder", "url"]
    
    def __init__(self, parent, storage):
        """
        Initialize the Shortcuts Manager dialog.
        
        Args:
            parent: Parent window
            storage: ShortcutsStorage instance
        """
        # Translators: Title of the Shortcuts Manager dialog
        super().__init__(parent, title=_("Shortcut Launcher"), 
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self._storage = storage
        self._shortcuts = []  # Current list of shortcuts (filtered)
        
        self._createControls()
        self._layoutControls()
        self._bindEvents()
        
        # Load last filter and populate list
        lastFilter = self._storage.get_setting("lastFilter", "all")
        filterIndex = self.FILTER_MAP.index(lastFilter) if lastFilter in self.FILTER_MAP else 0
        self.filterRadio.SetSelection(filterIndex)
        self._populateList()
        
        # Set initial focus to the list
        self.shortcutsList.SetFocus()
        
        # Set minimum size
        self.SetMinSize((400, 350))
        self.SetSize((450, 400))
        self.CenterOnParent()
    
    def _createControls(self):
        """Create all UI controls."""
        # Filter radio buttons
        # Translators: Label for filter radio buttons
        filterLabel = _("&Filter:")
        self.filterChoices = [
            # Translators: Filter option to show all shortcuts
            _("All"),
            # Translators: Filter option to show only program shortcuts
            _("Programs"),
            # Translators: Filter option to show only folder shortcuts
            _("Folders"),
            # Translators: Filter option to show only URL shortcuts
            _("URLs")
        ]
        self.filterRadio = wx.RadioBox(
            self,
            label=filterLabel,
            choices=self.filterChoices,
            style=wx.RA_SPECIFY_ROWS,
            majorDimension=2
        )
        
        # Shortcuts list
        # Translators: Label for the shortcuts list
        self.listLabel = wx.StaticText(self, label=_("&Shortcuts:"))
        self.shortcutsList = wx.ListBox(self, style=wx.LB_SINGLE)
        
        # Buttons
        # Translators: Button to add a new shortcut
        self.addBtn = wx.Button(self, label=_("&Add..."))
        # Translators: Button to edit the selected shortcut
        self.editBtn = wx.Button(self, label=_("&Edit..."))
        # Translators: Button to delete the selected shortcut
        self.deleteBtn = wx.Button(self, label=_("&Delete"))
        # Translators: Button to run/execute the selected shortcut
        self.runBtn = wx.Button(self, label=_("&Run"))
        # Translators: Button to close the dialog
        self.closeBtn = wx.Button(self, wx.ID_CLOSE, label=_("&Close"))
        
        # Initially disable edit, delete, run buttons
        self.editBtn.Disable()
        self.deleteBtn.Disable()
        self.runBtn.Disable()
    
    def _layoutControls(self):
        """Layout all controls using sizers."""
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Filter section
        mainSizer.Add(self.filterRadio, 0, wx.EXPAND | wx.ALL, 5)
        
        # List section
        mainSizer.Add(self.listLabel, 0, wx.LEFT | wx.TOP, 10)
        mainSizer.Add(self.shortcutsList, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # Buttons section
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.addBtn, 0, wx.ALL, 5)
        buttonSizer.Add(self.editBtn, 0, wx.ALL, 5)
        buttonSizer.Add(self.deleteBtn, 0, wx.ALL, 5)
        buttonSizer.Add(self.runBtn, 0, wx.ALL, 5)
        buttonSizer.AddStretchSpacer()
        buttonSizer.Add(self.closeBtn, 0, wx.ALL, 5)
        
        mainSizer.Add(buttonSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(mainSizer)
    
    def _bindEvents(self):
        """Bind event handlers."""
        self.filterRadio.Bind(wx.EVT_RADIOBOX, self._onFilterChange)
        self.shortcutsList.Bind(wx.EVT_LISTBOX, self._onListSelect)
        self.shortcutsList.Bind(wx.EVT_LISTBOX_DCLICK, self._onRun)
        
        self.addBtn.Bind(wx.EVT_BUTTON, self._onAdd)
        self.editBtn.Bind(wx.EVT_BUTTON, self._onEdit)
        self.deleteBtn.Bind(wx.EVT_BUTTON, self._onDelete)
        self.runBtn.Bind(wx.EVT_BUTTON, self._onRun)
        self.closeBtn.Bind(wx.EVT_BUTTON, self._onClose)
        
        self.Bind(wx.EVT_CLOSE, self._onClose)
        # Use CHAR_HOOK for better keyboard handling with NVDA
        self.Bind(wx.EVT_CHAR_HOOK, self._onCharHook)
    
    def _populateList(self):
        """Populate the shortcuts list based on current filter."""
        self.shortcutsList.Clear()
        
        filterIndex = self.filterRadio.GetSelection()
        filterType = self.FILTER_MAP[filterIndex]
        
        self._shortcuts = self._storage.get_shortcuts(filterType)
        
        for shortcut in self._shortcuts:
            name = shortcut.get("name", "")
            self.shortcutsList.Append(name)
        
        # Update button states
        self._updateButtonStates()
    
    def _updateButtonStates(self):
        """Enable/disable buttons based on selection."""
        hasSelection = self.shortcutsList.GetSelection() != wx.NOT_FOUND
        self.editBtn.Enable(hasSelection)
        self.deleteBtn.Enable(hasSelection)
        self.runBtn.Enable(hasSelection)
    
    def _getSelectedShortcut(self):
        """Get the currently selected shortcut."""
        selection = self.shortcutsList.GetSelection()
        if selection != wx.NOT_FOUND and selection < len(self._shortcuts):
            return self._shortcuts[selection]
        return None
    
    def _onFilterChange(self, event):
        """Handle filter radio button change."""
        filterIndex = self.filterRadio.GetSelection()
        filterType = self.FILTER_MAP[filterIndex]
        self._storage.set_setting("lastFilter", filterType)
        self._populateList()
    
    def _onListSelect(self, event):
        """Handle list selection change."""
        self._updateButtonStates()
    
    def _onCharHook(self, event):
        """Handle key press at dialog level."""
        keycode = event.GetKeyCode()
        focused = self.FindFocus()
        
        # ESC closes the dialog
        if keycode == wx.WXK_ESCAPE:
            self.Close()
            return
        
        # Only handle Enter/Delete when list has focus
        if focused == self.shortcutsList:
            if keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER:
                if self.shortcutsList.GetSelection() != wx.NOT_FOUND:
                    self._onRun(event)
                    return
            elif keycode == wx.WXK_DELETE:
                if self.shortcutsList.GetSelection() != wx.NOT_FOUND:
                    self._onDelete(event)
                    return
        
        event.Skip()
    
    def _onAdd(self, event):
        """Handle Add button click."""
        from .dialogs import AddEditShortcutDialog
        
        dlg = AddEditShortcutDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.getData()
            self._storage.add_shortcut(
                name=data["name"],
                shortcut_type=data["type"],
                target=data["target"]
            )
            self._populateList()
        dlg.Destroy()
    
    def _onEdit(self, event):
        """Handle Edit button click."""
        shortcut = self._getSelectedShortcut()
        if not shortcut:
            return
        
        from .dialogs import AddEditShortcutDialog
        
        dlg = AddEditShortcutDialog(self, shortcut=shortcut)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.getData()
            self._storage.update_shortcut(
                shortcut_id=shortcut["id"],
                name=data["name"],
                shortcut_type=data["type"],
                target=data["target"]
            )
            self._populateList()
        dlg.Destroy()
    
    def _onDelete(self, event):
        """Handle Delete button click."""
        shortcut = self._getSelectedShortcut()
        if not shortcut:
            return
        
        # Confirm deletion
        # Translators: Confirmation message when deleting a shortcut
        message = _("Are you sure you want to delete '{}'?").format(shortcut.get("name", ""))
        # Translators: Title of delete confirmation dialog
        title = _("Confirm Delete")
        
        if gui.messageBox(message, title, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING) == wx.YES:
            self._storage.delete_shortcut(shortcut["id"])
            self._populateList()
            # Translators: Message announced when a shortcut is deleted
            ui.message(_("Shortcut deleted"))
    
    def _onRun(self, event):
        """Handle Run button click or double-click on list item."""
        shortcut = self._getSelectedShortcut()
        if not shortcut:
            return
        
        # Close dialog first
        self.Close()
        
        # Import here to avoid circular import
        import os
        import subprocess
        from . import browserDetect
        
        shortcut_type = shortcut.get("type", "")
        target = shortcut.get("target", "")
        name = shortcut.get("name", "")
        
        if not target:
            # Translators: Error message when shortcut target is empty
            ui.message(_("Shortcut target is empty"))
            return
        
        try:
            if shortcut_type == "program":
                if os.path.exists(target):
                    subprocess.Popen([target])
                    # Translators: Message announced when launching a program
                    ui.message(_("Launching {}").format(name))
                else:
                    # Translators: Error message when program is not found
                    ui.message(_("Program not found: {}").format(target))
            
            elif shortcut_type == "folder":
                if os.path.exists(target):
                    os.startfile(target)
                    # Translators: Message announced when opening a folder
                    ui.message(_("Opening {}").format(name))
                else:
                    # Translators: Error message when folder is not found
                    ui.message(_("Folder not found: {}").format(target))
            
            elif shortcut_type == "url":
                browser_setting = self._storage.get_setting("defaultBrowser", "auto")
                custom_path = self._storage.get_setting("customBrowserPath", "")
                
                if browser_setting == "custom" and custom_path:
                    browserDetect.open_url(target, custom_path)
                elif browser_setting != "auto":
                    browsers = browserDetect.detect_browsers()
                    browser_path = None
                    for b in browsers:
                        if b["id"] == browser_setting:
                            browser_path = b["path"]
                            break
                    browserDetect.open_url(target, browser_path)
                else:
                    browserDetect.open_url(target)
                
                # Translators: Message announced when opening a URL
                ui.message(_("Opening {}").format(name))
        
        except Exception as e:
            # Translators: Error message when shortcut execution fails
            ui.message(_("Error: {}").format(str(e)))
    
    def _onClose(self, event):
        """Handle Close button or window close."""
        self.Destroy()
