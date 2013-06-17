import wx
import wx.html2
import urlparse
import urllib2
import time
import thread
import sys
import traceback
import os
        
from threading import Event
from threading import Thread

from Tribler.Main.vwxGUI.list import XRCPanel
from Tribler.Main.vwxGUI.GuiUtility import GUIUtility
from Tribler.Core.Libtorrent.LibtorrentMgr import LibtorrentMgr

class WebBrowser(XRCPanel):
    '''WebView is a class that allows you to browse the worldwideweb.'''    
 
    __allowBrowsing = None
    __dhtFound = 0
    __evtUserChangedText = None
 
    def __init__(self, parent=None):
        XRCPanel.__init__(self, parent)
        
        vSizer = wx.BoxSizer(wx.VERTICAL)
             
        '''Create the toolbar'''
        toolBarPanel = wx.Panel(self)
        toolBarPanel.SetBackgroundColour(wx.Colour(255,255,255))
        toolBar = wx.BoxSizer(wx.HORIZONTAL)
        toolBarPanel.SetSizer(toolBar)
        #Create the toolbar buttons.
        backwardButton = wx.Button(toolBarPanel, label="Backward")
        forwardButton = wx.Button(toolBarPanel, label="Forward")    
        goButton = wx.Button(toolBarPanel, label="Go")
        #Register the actions
        self.Bind(wx.EVT_BUTTON, self.goBackward, backwardButton)
        self.Bind(wx.EVT_BUTTON, self.goForward, forwardButton)
        self.Bind(wx.EVT_BUTTON, self.loadURLFromAdressBar, goButton)
        #Create the adressbar.
        self.adressBar = wx.TextCtrl(toolBarPanel,1, style = wx.TE_PROCESS_ENTER)
        #Register the enterkey.
        self.Bind(wx.EVT_TEXT_ENTER, self.loadURLFromAdressBar, self.adressBar)
        #Create the loading graphic
        self.loadingGraphic = WebBrowser.WebpageLoadingGraphic(toolBarPanel)
        #Add all the components to the toolbar.
        toolBar.Add(backwardButton, 0)
        toolBar.Add(forwardButton, 0)
        toolBar.Add(self.adressBar, 1, wx.EXPAND)
        toolBar.Add(self.loadingGraphic.GetPanel(), 0, wx.ALIGN_CENTER_VERTICAL)
        toolBar.Add(goButton, 0)
        toolBarPanel.Layout()
        #Add the toolbar to the panel.
        vSizer.Add(toolBarPanel, 0, wx.EXPAND)
        
        '''Add the overlay for the info bar'''
        self.infobaroverlay = wx.Panel(self)
        self.infobaroverlay.SetBackgroundColour(wx.Colour(255,255,153))
        self.infobaroverlay.vSizer = vSizer
        vSizer.Add(self.infobaroverlay, 1, wx.EXPAND | wx.ALL, 1)
        
        self.infobaroverlay.COLOR_BACKGROUND = wx.Colour(255,255,153)
        self.infobaroverlay.COLOR_FOREGROUND = wx.Colour(50,50,50)
        self.infobaroverlay.COLOR_BACKGROUND_SEL = wx.Colour(255,255,230)
        self.infobaroverlay.COLOR_FOREGROUND_SEL = wx.Colour(0,0,0)
        
        self.SetBackgroundColour(wx.Colour(205,190,112))
        
        '''Create the webview'''
        self.webviewPanel = wx.Panel(self)
        wvPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.webviewPanel.SetSizer(wvPanelSizer)
        self.webview = wx.html2.WebView.New(self.webviewPanel)
        wvPanelSizer.Add(self.webview, 0, wx.EXPAND)
        self.webviewPanel.Layout()
        #Clear the blank page loaded on startup.        
        self.webview.ClearHistory()
        
        self.currentURL = ''
        
        vSizer.Add(self.webviewPanel, 2, wx.EXPAND) 
        
        '''Add all components'''
        self.SetSizer(vSizer)
        self.Layout()
        
        '''Add observerlist for checking load events'''
        self.loadlisteners = []
        
        '''Register the action on the event that a URL is being loaded and when finished loading'''
        self.Bind(wx.html2.EVT_WEB_VIEW_NAVIGATED, self.onURLNavigating, self.webview)
        self.Bind(wx.html2.EVT_WEB_VIEW_LOADED, self.onURLLoaded, self.webview)
        
        self.infobaroverlay.Bind(wx.EVT_ENTER_WINDOW, self.OnInfoBarMouseOver, self.infobaroverlay)
        self.infobaroverlay.Bind(wx.EVT_LEAVE_WINDOW, self.OnInfoBarMouseOut, self.infobaroverlay)

        '''Register typing event to prevent hindering the user while typing in a new address'''
        self.adressBar.Bind(wx.EVT_TEXT, self.UserChangeText, self.adressBar)
        self.__evtUserChangedText = Event()

        '''Do final GUI calls'''
        self.HideInfoBar()
        
        wx.CallAfter(self.webview.SetMinSize,(2000, -1))   #Fix initial expansion, 2.9.4.0 bug
        
        #Fix libtorrent bug with sockets
        self.__allowBrowsing = Event()
        self.__dhtFound = 0
        thread.start_new(self.MonitorLibtorrentMgr,())    
    
    def MonitorLibtorrentMgr(self):
        """When a socket is opened by the webview it interferes with
            the LibtorrentMgr class. This causes LibtorrentMgr to lock
            up Tribler entirely. Therefore we wait until it has initialized
            (dh_nodes > 10) before we allow browsing.
        """
        mngr = LibtorrentMgr.getInstance()
        while (True):
            self.__dhtFound = mngr.get_dht_nodes()
            if ( self.__dhtFound > 10 ):
                self.__allowBrowsing.set()
                break
    
    def ShowLibtorrentWorkingError(self):
        """If the user has to wait for libtorrent to start up,
            notify the user via the infobar.
        """
        completion = (float(self.__dhtFound)/11.0)*100.0
        errorText = " <b>Cannot browse to page, waiting for Libtorrent to set up (%.2f%%)... Try again later</b>" % completion
        errorLabel = wx.StaticText(self.infobaroverlay)
        errorLabel.SetLabelMarkup(errorText)
        self.SetInfoBarContents((errorLabel,))
        self.ShowInfoBar()
    
    def goBackward(self, event):
        if self.webview.CanGoBack():
            self.webview.GoBack()
        
    def goForward(self, event):
        if self.webview.CanGoForward():
            self.webview.GoForward()
    
    def loadURLFromAdressBar(self, event):
        '''Wait for the flag to be set to allow us to browse
            to websites (see MonitorLibtorrentMgr())and then
            Load an URL from the adressbar'''
        if not self.__allowBrowsing.wait(0.5):
            self.ShowLibtorrentWorkingError()
            return
        url = self.adressBar.GetValue()
        if not urlparse.urlparse(url).scheme:
            url = 'http://' + url
        self.webview.LoadURL(url)
    
    def AddLoadedListener(self, listener):
        """Loaded listeners must expose a webpageLoaded(event) method
        """
        self.loadlisteners.append(listener)
        
    def RemoveLoadedListener(self, listener):
        self.loadlisteners.remove(listener)
    
    def __UrlToPageSrc(self, url):
        try:
            req = urllib2.Request(url, headers={'User-Agent':"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"})
            opener = urllib2.build_opener()
            contents = opener.open(req)
            return contents.read()
        except urllib2.URLError, e:
            return ''   # URL unknown, probably about:blank
    
    def __notifyLoadedListeners(self, event):
        for listener in self.loadlisteners:
            try:
                listener.webpageLoaded(event, self.__UrlToPageSrc(event.GetURL()))
            except:
                #Anything can go wrong with custom listeners, not our problem
                print >> sys.stderr, "WebBrowser: An error occurred in LoadedListener " + str(listener)
                traceback.print_exc()
    
    def onURLNavigating(self, event):
        """Actions to be taken when an URL is navigated to"""
        mainUrl = self.webview.GetCurrentURL()
        #Only take action when navigating to a new page. This event is also thrown for loading resources.
        if self.currentURL != mainUrl:
            self.currentURL = mainUrl
            #Reset the event for the user changing the address bar text
            self.__evtUserChangedText.clear()
            #Update the GUI (hide the infobar)
            self.HideInfoBar()
            self.loadingGraphic.Animate()
            #Notify our listeners we are navigating to a new page
            navigatingNewPageEvent = WebBrowser.NavigatingNewPageEvent(mainUrl)
            thread.start_new(self.__notifyLoadedListeners, (navigatingNewPageEvent,))
    
    def UserChangeText(self, event):
        '''Callback for when a user changed the text in the url-bar'''
        self.__evtUserChangedText.set()
    
    def onURLLoaded(self, event):
        '''Actions to be taken when an URL is loaded.'''
        self.loadingGraphic.Freeze()
        if not self.__evtUserChangedText.isSet():
            #Update the adressbar to the 'real' website address
            #If the user isn't entering new data
            self.adressBar.SetValue(self.webview.GetCurrentURL())
    
    def OnInfoBarMouseOver(self, event):
        """When we roll over the InfoBar, set our background to be brighter
            Set the foreground if any of our children want to stick to our style
        """
        self.infobaroverlay.SetBackgroundColour(self.infobaroverlay.COLOR_BACKGROUND_SEL)
        self.infobaroverlay.SetForegroundColour(self.infobaroverlay.COLOR_FOREGROUND_SEL)
        
    def OnInfoBarMouseOut(self, event):
        """When we roll off the InfoBar, set our background to be darker
            Set the foreground if any of our children want to stick to our style
        """
        self.infobaroverlay.SetBackgroundColour(self.infobaroverlay.COLOR_BACKGROUND)
        self.infobaroverlay.SetForegroundColour(self.infobaroverlay.COLOR_FOREGROUND)
    
    def SetInfoBarContents(self, *orderedContents):
        wx.CallAfter(self.__SetInfoBarContents, *orderedContents)
    
    def __SetInfoBarContents(self, *orderedContents):
        """Add content to the infobar in left -> right ordering
            Expects a list of tuples of a wxObject and a set of wxFlags
            For example:
                textlabel = wx.StaticText(webbrowser.infobaroverlay)
                textlabel.SetLabelMarkup(" <b>I am bold text</b>")
                webbrowser.SetInfoBarContents((textlabel,wx.CENTER))
        """
        #Remove all previous children
        previousContent = self.infobaroverlay.GetSizer()
        if previousContent:
            windows = []
            for child in previousContent.GetChildren():
                windows.append(child.GetWindow())
            for window in windows:
                if window:
                    self.infobaroverlay.RemoveChild(window)
                    window.Destroy()
            self.infobaroverlay.Layout()
        self.infobaroverlay.ClearBackground()
        #Overwrite with new sizer and contents
        infobarSizer = wx.BoxSizer(wx.HORIZONTAL)
        width = 0
        for contentTuple in orderedContents:
            flags = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT if len(contentTuple)==1 else contentTuple[1]
            width += contentTuple[0].GetMaxWidth() if contentTuple[0].GetMaxWidth() != -1 else 0
            infobarSizer.Add(contentTuple[0], 0, flags)
        width = self.GetSize().width - width
        infobarSizer.Add((width,1))
        self.infobaroverlay.SetSizer(infobarSizer)
        infobarSizer.FitInside(self.infobaroverlay)
    
    def __fixInfobarHeight(self, height):
        """In wxPython 2.9.0 SetSizeHints does not function properly,
            we are only interested in fixing the height of the infobar
            and the webview here.
            Call this after laying out the vSizer of the main panel.
        """
        width, oHeight = self.infobaroverlay.GetSize()
        #Fix infobar
        self.infobaroverlay.SetSize((width, height))
        diffHeight = oHeight-height
        self.infobaroverlay.vSizer.SetItemMinSize(self.infobaroverlay, (width, height))
        self.infobaroverlay.vSizer.Fit(self.infobaroverlay)
        #Fix webview
        width, oHeight = self.webviewPanel.GetSize()
        self.infobaroverlay.vSizer.SetItemMinSize(self.webviewPanel, (width, oHeight + diffHeight))
        self.infobaroverlay.vSizer.Fit(self.webviewPanel)
        self.webviewPanel.GetSizer().SetItemMinSize(self.webview, (width, oHeight + diffHeight))
        self.webviewPanel.GetSizer().Fit(self.webview)
        #Finally, lay it out
        self.infobaroverlay.vSizer.Layout()
    
    def HideInfoBar(self):
        wx.CallAfter(self.__HideInfoBar)
    
    def __HideInfoBar(self):     
        """Hide the InfoBar immediately
        """ 
        self.infobaroverlay.SetSizeHints(-1,0,-1,0)
        self.infobaroverlay.vSizer.Layout()
        self.infobaroverlay.Hide()
        self.__fixInfobarHeight(0)
        self.Refresh()

    def ShowInfoBar(self, finalHeight=28.0):
        wx.CallAfter(self.__ShowInfoBar, finalHeight)

    def __ShowInfoBar(self, finalHeight=28.0):      
        """Animated InfoBar drop down.
            Will grow to a maximum of finalHeight if the sizer deems it appropriate
        """
        self.infobaroverlay.Show()
        self.infobaroverlay.SetSizeHints(-1, -1,-1, finalHeight)
        self.infobaroverlay.vSizer.Layout()
        self.infobaroverlay.Layout()
        self.__fixInfobarHeight(finalHeight)
        self.Refresh()
            
    class NavigatingNewPageEvent(object):
        
        def __init__(self, url):
            self.url = url
            
        def GetURL(self):
            return self.url
        
    class WebpageLoadingGraphic(Thread):
        """WebpageLoadingGraphic
            Thread for the animated loading graphic next to the address bar
            in the web browser.
        """
        
        __loading = None            #Event to be signaled when we are loading a page
        
        __frame = -1                #The animation frame we are on [0,7], 8 for disabled
        __bitmaps = None            #The image frames loaded in memory
        
        __backgroundBrush = None    #The background color
        __panel = None              #The actual panel
        
        __alive = None              #Thread life
        
        def __init__(self, parent):
            """Initialize our thread and forward the 'parent' to a wx.Panel
                we own.
            Args:
                parent (wxWindow) : parent object for panel 
            """
            #Initialize our drawable surface
            self.__panel = wx.Panel(parent)
            #Initialze ourselves as a thread
            Thread.__init__(self)
            
            #Set the panel size
            self.__panel.SetSize((26,26))
            self.__panel.SetMinSize((26,26))
            
            #Set up the loading event
            self.__loading = Event()
            #Start with the disabled image
            self.__frame = 8
            
            #Resolve the path for our images
            guiUtility = GUIUtility.getInstance()
            imgPath = os.path.join(guiUtility.utility.getPath(), 'Tribler', 'Main', 'vwxGUI', 'images', '')
            
            #Load all of the bitmaps into memory
            #Note that we do this because we switch images frequently
            #and constantly doing IO to retrieve images is not a good idea.
            self.__bitmaps = []
            for i in range(8):
                self.__bitmaps.append(wx.Bitmap(imgPath + 'loading_' + str(i) + '.png', wx.BITMAP_TYPE_PNG))
            self.__bitmaps.append(wx.Bitmap(imgPath + 'loading_greyed.png', wx.BITMAP_TYPE_PNG))
            
            #Set the background colour
            self.__backgroundBrush = wx.Brush(wx.Colour(255,255,255))
            
            #Register for the paint event
            self.__panel.Bind(wx.EVT_PAINT, self.Paint)
            
            #Set ourselves up for Frozen mode (disabled)
            self.Freeze()
            
            #Set threading info
            self.name = 'WebpageLoadingGraphicThread'
            self.daemon = True
            self.__alive = True
            
            #Finally, start the waiting loop
            self.start()
            
        def __del__(self):
            """When we are removed, signal the main loop in run() to end
            """
            self.__alive = False
            
        def SetBackgroundColour(self, colour):
            """Set the background colour
            
            Args:
                colour (wxColour) : colour for the background
            """
            self.__backgroundBrush = wx.Brush(colour)
            
        def GetPanel(self):
            """Return our drawable panel
            """
            return self.__panel
            
        def Animate(self):
            """Set animation mode.
                Signal this when loading a webpage
            """
            self.__loading.set()
            self.__panel.SetToolTipString("Loading webpage..")
            
        def Freeze(self):
            """Set frozen mode.
                Signal this when done loading a webpage
            """
            self.__loading.clear()
            self.__frame = 8
            self.__panel.Refresh()
            self.__panel.SetToolTipString("Done loading webpage")
            
        def run(self):
            """Loop through the animation.
                Note that we do not block until a webpages loads:
                this would mean we would never be able to detect
                when we are no longer alive and need to return.
                
                Called when the Thread starts.
            """
            while self.__alive:
                if not self.__loading.isSet():
                    if not self.__loading.wait(0.5):
                        continue 
                self.__IncrementFrame()
                time.sleep(0.05)
                
        def Paint(self, event):
            """Receive an EVT_PAINT from our paintable
            
            Args:
                event (wx.EVT_PAINT) : paint event object
            """
            if not self.__alive:
                return
            dc = wx.ClientDC(self.__panel)
            dc.SetBackground(self.__backgroundBrush)
            dc.Clear()
            image = self.__bitmaps[self.__frame]
            dc.DrawBitmap(image, 0, 0, True)
            
        def __IncrementFrame(self):
            """Increment the iterator for the (non-frozen) bitmaps,
                namely self.__frame.
                Then repaint our paintable.
            """
            self.__frame = (self.__frame + 1)%8
            self.__panel.Refresh()
        