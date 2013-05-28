import wx
import time
import urlparse

from Tribler.Main.vwxGUI.GuiUtility import GUIUtility
from Tribler.PluginManager.PluginManager import PluginManager


from Tribler.TUPT.Parser.IParserPlugin import IParserPlugin
from Tribler.TUPT.Parser.ParserControl import ParserControl

from Tribler.TUPT.TorrentFinder.ITorrentFinderPlugin import ITorrentFinderPlugin

from ListCtrlComboPopup import ListCtrlComboPopup as ListViewComboPopup

class TUPTControl:
    '''Class that controls the flow for parsing, matching and finding movies'''
    
    def __init__(self, pluginManager = PluginManager()):
        self.pluginmanager = pluginManager
        self.parserControl = ParserControl(pluginManager)
        
        #Setup the plugins.
        self.pluginmanager.RegisterCategory("Matcher", object)
        self.pluginmanager.RegisterCategory("Parser", IParserPlugin)
        self.pluginmanager.RegisterCategory("TorrentFinder", ITorrentFinderPlugin)
        self.pluginmanager.LoadPlugins()
        
    def CoupleGUI(self, gui):
        webview = gui.frame.webbrowser
        webview.AddLoadedListener(self)
        self.webview = webview
        
    def webpageLoaded(self, event, html):
        """Callback for when a webpage was loaded
            We can now start feeding our parser controller
        """
        netloc = urlparse.urlparse(event.GetURL()).netloc   #The url identifier, ex 'www.google.com'   
        #Parse the Website.
        if self.parserControl.HasParser(netloc):
            results = self.parserControl.ParseWebsite(netloc, html)
            if results is not None:
                #Find torrents corresponding to the movie.
                self.ShowInfoBar(results)
    
    def __CreateStdComboCtrl(self, width = 150):
        """Create a dropdown control set (comboCtrl and popupCtrl) in our theme
        """
        comboCtrl = wx.ComboCtrl(self.webview.infobaroverlay)
        comboCtrl.SetSizeHints(-1,-1,width,-1)
        
        comboCtrl.SetBackgroundColour(self.webview.infobaroverlay.COLOR_BACKGROUND_SEL)
        comboCtrl.SetForegroundColour(self.webview.infobaroverlay.COLOR_FOREGROUND)

        popupCtrl = ListViewComboPopup()
        
        popupCtrl.SetBackgroundColour(self.webview.infobaroverlay.COLOR_BACKGROUND)
        popupCtrl.SetForegroundColour(self.webview.infobaroverlay.COLOR_FOREGROUND)
        
        comboCtrl.SetPopupControl(popupCtrl)

        return comboCtrl, popupCtrl
        
    def ShowInfoBar(self,results):
        '''Display found movies and their corresponding torrents.
        Args:
            results (movie,[torrents]) = all found movies and their corresponding movie.
        '''
        #Add movie to the infobar
        textlabel = wx.StaticText(self.webview.infobaroverlay)
        textlabel.SetLabelMarkup(" <b>We have found the following movie: " + results[0].dictionary['title'] + " </b>")
        #Create play button.
        button = wx.Button(self.webview.infobaroverlay)
        button.SetLabel("Play!")
        button.SetBackgroundColour(self.webview.infobaroverlay.COLOR_BACKGROUND_SEL)
        button.SetSizeHints(-1,-1,150,-1)
        #Register action
        self.webview.Bind(wx.EVT_BUTTON, self.piracyButtonPressed, button)
        
        self.webview.SetInfoBarContents((textlabel,), (button,))
        self.webview.ShowInfoBar()  
        
        
    def ShowInfoBarMovie(self, Movie):
        '''Display the result for the movie'''
        textlabel = wx.StaticText(self.webview.infobaroverlay)
        textlabel.SetLabelMarkup(" <b>We have found the following movie for you: " + Movie[0].dictionary['title'] + " </b>")
                
        self.webview.SetInfoBarContents((textlabel,wx.CENTER))
        self.webview.ShowInfoBar()
        pass
            
    def piracyButtonPressed(self, event):
        """Callback for when the user wants to commit piracy.
            We can patch our parser result through the Matcher and
            the TorrentFinder now.
        """
        pass
        
          
