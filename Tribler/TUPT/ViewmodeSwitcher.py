"""This file contains the ViewmodeSwitcher class."""

import wx

class ViewmodeSwitcher(object):
    """ViewmodeSwitcher
        Handles switching between 'simple' TUPT view mode and normal Tribler
        'advanced' view mode.
    
    Depends on: WX
    """
    
    # View mode states
    SIMPLE_MODE = 0
    ADVANCED_MODE = 1
    
    # The following are identifiers for the tabs we want to see in
    # the simple view mode.
    #    Label values as seen in the menu list (on the left)
    SIMPLE_PAGES_TREE_VALUES = ['Downloads', 'Videoplayer', 'Webbrowser']
    #    Tribler GUI page identifiers as reported by Main.vwxGUI.GuiUtility
    SIMPLE_PAGES_GUIUTIL_VALUES = ['my_files', 'videoplayer', 'webbrowser']
    
    __currentMode = -1  # The current view mode (SIMPLE_MODE or ADVANCED_MODE)
    __children = None  # List of children to Show()/Hide()
    __guiUtility = None  # The GUIUtility class used in this session
    __settingsCallback = None  # The callback that opens the settings dialog (before we override the button)
    
    def __init__(self, guiUtility):
        """Initialize member variables, hook into GUIUtility and
            set the current view mode to SIMPLE_VIEW
        Args:
            guiUtility (Main.vwxGUI.GuiUtility) : GUIUtility instance
        """
        self.__guiUtility = guiUtility
        self.__collectChildren()
        self.SetSimpleMode()
    
    def __collectChildren(self):
        """Set up our __children variable. This scans through some Tribler
            GUI classes to find the ones that we will Hide() and Show() through
            view mode switches.
        """
        guiUtility = self.__guiUtility
        children = []
        children.append(guiUtility.frame.SRstatusbar)  # Bottom grey info bar
        children.append(guiUtility.frame.top_bg.searchFieldPanel)  # Top search textfield
        children.append(guiUtility.frame.top_bg.go)  # Top search button
        children.append(guiUtility.frame.top_bg.add_btn)  # Top add external torrent button
        for child in guiUtility.frame.actlist.list.GetItems():  # The menu tree items
            if child.data[0] not in ViewmodeSwitcher.SIMPLE_PAGES_TREE_VALUES:  #  ActivityListItems store a string in their data
                children.append(child)  #    as the first list item.
        self.__children = children
    
    def __OnSettingsOverride(self, event):#IGNORE:W0613 event always given.
        """Override callback for the settings button in simple mode.
            When pressed, switch to Advanced mode.
        Args:
            event (wx.EVT_BUTTON) : the button press event
        """
        self.SetAdvancedMode()
    
    def SetSimpleMode(self):
        """If not already in simple mode:
            Hide all 'advanced' features of Tribler.
            Then hook up the settings button to our own switch-to-advanced-mode
            functionality (SetAdvancedMode).
        """
        wx.CallAfter(self.__SetSimpleMode)
    
    def __SetSimpleMode(self):
        """Wx thread-unsafe method backend for SetSimpleMode().
            For description see public member SetSimpleMode()
        """
        # If we are already in simple mode return
        if self.__currentMode == ViewmodeSwitcher.SIMPLE_MODE:
            return
        self.__currentMode = ViewmodeSwitcher.SIMPLE_MODE
        # Hide all our children
        for child in self.__children:
            child.Hide()
        # If we are on a page that has just been hidden, switch
        # to the webbrowser page
        if self.__guiUtility.guiPage not in ViewmodeSwitcher.SIMPLE_PAGES_GUIUTIL_VALUES:
            self.__guiUtility.ShowPage('webbrowser')
        # Hook up the settings button to our own callback
        # We store the original callback here to be hooked up again later, when we leave simple mode
        topSearch = self.__guiUtility.frame.top_bg
        self.__settingsCallback = topSearch.OnSettings
        topSearch.SetButtonHandler(topSearch.settings_btn, self.__OnSettingsOverride, 'Switch to advanced mode.')
    
    def SetAdvancedMode(self):
        """If not already in advanced mode:
            Show all (previously hidden) 'advanced' features of Tribler.
            Then hook up the settings button to its original callback (for
            opening the actual settings dialog).
        """
        wx.CallAfter(self.__SetAdvancedMode)
    
    def __SetAdvancedMode(self):
        """Wx thread-unsafe method backend for SetAdvancedMode().
            For description see public member SetAdvancedMode()
        """
        # If we are already in advanced mode return
        if self.__currentMode == ViewmodeSwitcher.ADVANCED_MODE:
            return
        self.__currentMode = ViewmodeSwitcher.ADVANCED_MODE
        # Show all our children
        for child in self.__children:
            child.Show()
        # Hook the settings button back up to its original callback for opening the settings dialog.
        topSearch = self.__guiUtility.frame.top_bg
        topSearch.SetButtonHandler(topSearch.settings_btn, self.__settingsCallback, 'Change settings.')
    
