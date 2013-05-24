import wx
import time

from yapsy.IPlugin import IPlugin

from Tribler.Main.vwxGUI.GuiUtility import GUIUtility
from Tribler.PluginManager.PluginManager import PluginManager

from ListCtrlComboPopup import ListCtrlComboPopup as ListViewComboPopup

class TUPTControl:
    
    def __init__(self):
        self.pluginmanager = PluginManager()
        self.pluginmanager.RegisterCategory("Matcher", IPlugin)
        self.pluginmanager.RegisterCategory("Parser", IPlugin)
        self.pluginmanager.RegisterCategory("TorrentFinder", IPlugin)
        self.pluginmanager.LoadPlugins()
        
    def CoupleGUI(self, gui):
        webview = gui.frame.webbrowser
        webview.AddLoadedListener(self)
        self.webview = webview
        
    def webpageLoaded(self, event):
        """Callback for when a webpage was loaded
            We can now start feeding our controllers
        """
        # DEBUG
        self.webview.HideInfoBar()
        if (event.GetURL() == "http://www.wxpython.org/"):
            time.sleep(1)
            self.ShowInfoBarQuality()
    
    def ShowInfoBarQuality(self):
        textlabel = wx.StaticText(self.webview.infobaroverlay)
        textlabel.SetLabelMarkup(" <b>We have found the following video qualties for you: </b>")
        
        comboCtrl = wx.ComboCtrl(self.webview.infobaroverlay)
        
        comboCtrl.SetSizeHints(-1,-1,150,-1)

        popupCtrl = ListViewComboPopup()
        
        # It is important to call SetPopupControl() as soon as possible
        comboCtrl.SetPopupControl(popupCtrl)
        
        # Populate using wx.ListView methods
        popupCtrl.lc.InsertItem(popupCtrl.lc.GetItemCount(), "Bad Quality")
        popupCtrl.lc.InsertItem(popupCtrl.lc.GetItemCount(), "Normal Quality")
        popupCtrl.lc.InsertItem(popupCtrl.lc.GetItemCount(), "High Quality")
        
        self.webview.SetInfoBarContents((textlabel,wx.CENTER), (comboCtrl, wx.CENTER | wx.ALIGN_RIGHT))
        self.webview.ShowInfoBar()