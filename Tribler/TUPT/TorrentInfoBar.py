import wx

import Tribler.TUPT.TUPTControl

from Tribler.Main.vwxGUI.webbrowser import WebBrowser
        
class TorrentInfoBar():
    '''Class that willl create and show the found movies'''
    
    HDCHOICE = "HD    Quality"
    SDCHOICE = "SD    Quality"
    
    __webview = None
    __tuptControl = None
    __comboBox = None
    __comboboxMovieTorrent = None
    __comboboxMovieTorrentMap = None
    __movieTorrentIterator = None
    
    
    def __init__(self, webview, __tuptControl, movieTorrentIterator):
        self.__webview = webview
        self.__tuptControl = __tuptControl
        self.__movieTorrentIterator = movieTorrentIterator
        self.Update()
    
    def Update(self, movie = None):    
        #Get all the movies with torrents
        validMovieIndices = []
        for i in range(self.__movieTorrentIterator.GetSize()):
            if self.__movieTorrentIterator.GetMovie(i).HasTorrent():
                validMovieIndices.append(i)
        #Set movie infobar information
        if len(validMovieIndices)>0:               
           self.ShowMovieState(validMovieIndices)
        else:
            self.ShowParsingState()
            
        self.__webview.ShowInfoBar()   
    
    def ShowParsingState(self):
        """Show parsing state."""
            # Create parseLabel
        parseText = " <b>Parsing website.... </b>"
        parseLabel = wx.StaticText(self.__webview.infobaroverlay)
        parseLabel.SetLabelMarkup(parseText)
        self.__webview.SetInfoBarContents((parseLabel,))
            
    def ShowMovieState(self, validMovieIndices):
        """Show movie state"""
         # movieLabel
        movieText = " <b>The following movie was found: </b>"
        if len(validMovieIndices) > 1:
            movieText = " <b>The following movies were found: </b>"
        movieLabel = wx.StaticText(self.__webview.infobaroverlay)
        movieLabel.SetLabelMarkup(movieText)
            
        # ComboboxMovieTorrent
        self.__comboboxMovieTorrent = self.__CreateStdComboCtrl(200, self.MovieSelectionUpdated)
        for i in validMovieIndices:
            self.__comboboxMovieTorrent.Append(self.__movieTorrentIterator.GetMovie(i).movie.dictionary['title'])
            self.__comboboxMovieTorrent.SetValue(self.__movieTorrentIterator.GetMovie(validMovieIndices[0]).movie.dictionary['title']) 
            
        #Register mapping of valid indices
        self.__comboboxMovieTorrentMap = validMovieIndices
            
        # QualityLabel
        qualityText = "<b>. Do you want to watch this movie in:</b>"
        qualityLabel = wx.StaticText(self.__webview.infobaroverlay)
        qualityLabel.SetLabelMarkup(qualityText)
        qualityLabel.SetSizeHints(-1,-1,220,-1)
        
        #Create the quality selection.
        self.__comboBox = self.__CreateStdComboCtrl()
        movieTorrent = self.__movieTorrentIterator.GetMovie(validMovieIndices[0])
        if movieTorrent.HasHDTorrent():
            self.__comboBox.Append(self.HDCHOICE)
            #Set default value to HD Quality.
            self.__comboBox.SetValue(self.HDCHOICE)  
        if movieTorrent.HasSDTorrent():
            self.__comboBox.Append(self.SDCHOICE)
        #Set default value to SD quality if no HD quality    
        if not movieTorrent.HasHDTorrent():
            self.__comboBox.SetValue(self.SDCHOICE)
                   
        #Create play button.
        button = wx.Button(self.__webview.infobaroverlay)
        button.SetLabel("Play!")
        button.SetBackgroundColour(self.__webview.infobaroverlay.COLOR_BACKGROUND_SEL)
        button.SetSizeHints(-1,-1,150,-1)
        
        #Register action.
        self.__webview.Bind(wx.EVT_BUTTON, self.playButtonPressed, button)
        
        #Add all elements to the infobar.
        self.__webview.SetInfoBarContents((movieLabel,), (self.__comboboxMovieTorrent,), (qualityLabel,), (self.__comboBox,), (button,))
    
    def playButtonPressed(self, event):
        """Callback for when the user wants to play the movie.
        """
        #Get selected movie
        rawMovieSelection = self.__comboboxMovieTorrent.GetSelection()
        movieSelection = self.__comboboxMovieTorrentMap[rawMovieSelection]
        #Get selection and the corresponding calls.
        qualitySelection = self.__comboBox.GetValue()
        if qualitySelection == self.HDCHOICE:
            self.__tuptControl.DownloadHDMovie(movieSelection)
        else:
            self.__tuptControl.DownloadSDMovie(movieSelection)

    def RemoveHDQuality(self):
        """Remove SDQuality from the choices."""
        self.__RemoveComboBoxtem(self.HDCHOICE)          

    def RemoveSDQuality(self):
        """Remove SDQuality from the choices."""
        self.__RemoveComboBoxtem(self.SDCHOICE)
      
    def __RemoveComboBoxtem(self, item):
        #Find index of item.
        index =  self.__comboBox.FindString(item)
        #Remove item.
        self.__comboBox.Delete(index)
        #Check if a item exists
        if self.__comboBox.IsEmpty():        
            #Remove infobar
            self.__webview.HideInfoBar()
        else:        
            #Set selection to 0
            self.__comboBox.SetSelection(0)
    
    def MovieSelectionUpdated(self, event):
        #Get selected movie
        rawMovieSelection = self.__comboboxMovieTorrent.GetSelection()
        movieSelection = self.__comboboxMovieTorrentMap[rawMovieSelection]
        #Remove old available definitions
        self.__RemoveComboBoxtem(self.SDCHOICE)
        self.__RemoveComboBoxtem(self.HDCHOICE)
        #We changed our movie selection, update the available definitions
        movieTorrent = movieTorrentIterator.GetMovie(movieSelection)
        if movieTorrent.HasHDTorrent():
            self.__comboBox.Append(self.HDCHOICE)
            #Set default value to HD Quality.
            self.__comboBox.SetValue(self.HDCHOICE)  
        if movieTorrent.HasSDTorrent():
            self.__comboBox.Append(self.SDCHOICE)
        #Set default value to SD quality if no HD quality    
        if not movieTorrent.HasHDTorrent():
            self.__comboBox.SetValue(self.SDCHOICE)
        self.__webview.infobaroverlay.Refresh()
            
    def __CreateStdComboCtrl(self, width = 150, callback = None):
        """Create a dropdown control set (comboBox and popupCtrl) in our theme
        """
        comboBox = wx.ComboBox(self.__webview.infobaroverlay)
        comboBox.SetSizeHints(-1,-1,width,-1)
        comboBox.SetEditable(False)
        
        comboBox.SetBackgroundColour(self.__webview.infobaroverlay.COLOR_BACKGROUND_SEL)
        comboBox.SetForegroundColour(self.__webview.infobaroverlay.COLOR_FOREGROUND)
        
        if callback is not None:
            self.__webview.Bind(wx.EVT_CHOICE, callback, comboBox) 

        return comboBox  