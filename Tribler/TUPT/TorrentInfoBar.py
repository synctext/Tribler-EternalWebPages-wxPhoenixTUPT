"""This file contains the TorrentInfoBar class."""

import wx

class TorrentInfoBar():
    '''Class that willl create and show the found movies
    
    Depends on: WX, TUPTControl, WebBrowser
    '''
    
    HDCHOICE = "HD    Quality"
    SDCHOICE = "SD    Quality"
    
    __webview = None
    __tuptControl = None
    __comboboxMovieTorrentMap = None
    __movieTorrentIterator = None
    
    
    def __init__(self, webview, tuptControl, movieTorrentIterator):
        self.__webview = webview
        self.__tuptControl = tuptControl
        self.__movieTorrentIterator = movieTorrentIterator
    
    def Update(self):
        """Update the state using the movieTorrentIterator."""    
        # Get all the movies with torrents
        validMovieIndices = self.__GetValidMovieIndices()
        # Set movie infobar information
        if self.__movieTorrentIterator.HasMovie():
            if len(validMovieIndices) > 0:               
                wx.CallAfter(self.ShowMovieState, validMovieIndices)
            else:
                wx.CallAfter(self.ShowParsingState)
        else:          
            wx.CallAfter(self.ShowNoResultFoundState)
    
    def CheckForResults(self):
        """Check a final time if there are results """
        validMovieIndices = self.__GetValidMovieIndices()
        if self.__movieTorrentIterator.HasMovie():
            if len(validMovieIndices) > 0:               
                wx.CallAfter(self.ShowMovieState, validMovieIndices)
            else:
                wx.CallAfter(self.ShowNoTorrentFoundState)
        else:          
            wx.CallAfter(self.ShowNoResultFoundState)
    
    def __GetValidMovieIndices(self):
        """Get all movies that have a valid torrent
        Returns list of valid movies ([MovieTorrent,])"""
        validMovieIndices = []
        for i in range(self.__movieTorrentIterator.GetSize()):
            if self.__movieTorrentIterator.GetMovie(i).HasTorrent():
                validMovieIndices.append(i)
        return validMovieIndices
    
    def ShowNoTorrentFoundState(self):
        """Show no torrent found state."""
        # Create noResultFoundText.
        noTorrentFoundText = " <b>No torrents found </b>"
        noTorrentFoundLabel = wx.StaticText(self.__webview.infobaroverlay)
        noTorrentFoundLabel.SetLabelMarkup(noTorrentFoundText)
        self.__webview.SetInfoBarContents((noTorrentFoundLabel,))
    
    def ShowNoResultFoundState(self):
        """Show no results found state."""
        # Create noResultFoundText.
        noResultFoundText = " <b>No results found </b>"
        noResultFoundLabel = wx.StaticText(self.__webview.infobaroverlay)
        noResultFoundLabel.SetLabelMarkup(noResultFoundText)
        self.__webview.SetInfoBarContents((noResultFoundLabel,))    
    
    def ShowParsingState(self):
        """Show parsing state."""
            # Create parseLabel
        parseText = " <b>Parsing website.... </b>"
        parseLabel = wx.StaticText(self.__webview.infobaroverlay)
        parseLabel.SetLabelMarkup(parseText)
        self.__webview.SetInfoBarContents((parseLabel,))
            
    def ShowMovieState(self, validMovieIndices):
        """Show movie state
        Args:
            validMovieIndices ([movieTorrentDef,]) : list of movies with torrents."""
        # Register mapping of valid indices
        self.__comboboxMovieTorrentMap = validMovieIndices
          
        #Produce elements  
        movieLabel = self.__ProduceMovieLabel()
        comboboxMovieTorrent = self.__ProduceComboboxMovieTorrent()
        qualityLabel = self.__ProduceQualityLabel()
        comboBox = self.__ProduceQualitySelectionBox()
        button = self.__ProducePlayButton()

        #Add all elements to the infobar.
        self.__webview.SetInfoBarContents((movieLabel,), (comboboxMovieTorrent,), (qualityLabel,), (comboBox,), (button,))     
    
    def playButtonPressed(self, event):# Event always given. pylint: disable=W0613
        """Callback for when the user wants to play the movie.
        """
        # Get selected movie
        rawMovieSelection = self.__rawMovieSelection
        movieSelection = self.__comboboxMovieTorrentMap[rawMovieSelection]
        # Get selection and the corresponding calls.
        qualitySelection = self.__qualitySelection
        if qualitySelection == self.HDCHOICE:
            self.__tuptControl.DownloadHDMovie(movieSelection)
        else:
            self.__tuptControl.DownloadSDMovie(movieSelection)
    
    def QualitySelectionUpdated(self, event):
        self.__qualitySelection = event.GetEventObject().GetValue()
    
    def MovieSelectionUpdated(self, event):# Event always given. pylint: disable=W0613
        """Update the selection of quality when the movie selection has changed"""
        self.__rawMovieSelection = event.GetEventObject().GetCurrentSelection()
        self.Update()
            
    def __CreateStdComboCtrl(self, width=150, callback=None):
        """Create a dropdown control set (comboBox and popupCtrl) in our theme
        """
        comboBox = wx.ComboBox(self.__webview.infobaroverlay)
        comboBox.SetSizeHints(-1, -1, width, -1)
        comboBox.SetEditable(False)
        
        comboBox.SetBackgroundColour(self.__webview.infobaroverlay.COLOR_BACKGROUND_SEL)
        comboBox.SetForegroundColour(self.__webview.infobaroverlay.COLOR_FOREGROUND)
        
        if callback is not None:
            self.__webview.Bind(wx.EVT_COMBOBOX, callback, comboBox) 

        return comboBox  
    
    def __ProduceMovieLabel(self):
        movieText = " <b>The following movie was found: </b>"
        if len(self.__comboboxMovieTorrentMap) > 1:
            movieText = " <b>The following movies were found: </b>"
        movieLabel = wx.StaticText(self.__webview.infobaroverlay)
        movieLabel.SetLabelMarkup(movieText)
        return movieLabel
    
    def __ProduceComboboxMovieTorrent(self):
        comboboxMovieTorrent = self.__CreateStdComboCtrl(200, self.MovieSelectionUpdated)
        for i in self.__comboboxMovieTorrentMap:
            comboboxMovieTorrent.Append(self.__movieTorrentIterator.GetMovie(i).movie.dictionary['title'])
        comboboxMovieTorrent.SetValue(self.__movieTorrentIterator.GetMovie(self.__comboboxMovieTorrentMap[0]).movie.dictionary['title']) 
        self.__rawMovieSelection = 0
        return comboboxMovieTorrent
        
    def __ProduceQualityLabel(self):
        qualityText = "<b>. Do you want to watch this movie in:</b>"
        qualityLabel = wx.StaticText(self.__webview.infobaroverlay)
        qualityLabel.SetLabelMarkup(qualityText)
        qualityLabel.SetSizeHints(-1, -1, 220, -1)
        return qualityLabel
    
    def __ProduceQualitySelectionBox(self):
        comboBox = self.__CreateStdComboCtrl(callback=self.QualitySelectionUpdated)
        movieTorrent = self.__movieTorrentIterator.GetMovie(self.__comboboxMovieTorrentMap[0])
        if movieTorrent.HasHDTorrent():
            comboBox.Append(self.HDCHOICE)
            # Set default value to HD Quality.
            comboBox.SetValue(self.HDCHOICE)  
        if movieTorrent.HasSDTorrent():
            comboBox.Append(self.SDCHOICE)
        # Set default value to SD quality if no HD quality  
        self.__qualitySelection = self.HDCHOICE
        if not movieTorrent.HasHDTorrent():
            comboBox.SetValue(self.SDCHOICE)
            self.__qualitySelection = self.SDCHOICE
            
        return comboBox
    
    def __ProducePlayButton(self):
        button = wx.Button(self.__webview.infobaroverlay)
        button.SetLabel("Play!")
        button.SetBackgroundColour(self.__webview.infobaroverlay.COLOR_BACKGROUND_SEL)
        button.SetSizeHints(-1, -1, 150, -1)
        
        self.__webview.Bind(wx.EVT_BUTTON, self.playButtonPressed, button)
        
        return button
        
        