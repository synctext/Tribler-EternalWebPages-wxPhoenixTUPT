from threading import Event

from Tribler.Core.Session import Session
from Tribler.Core.TorrentDef import TorrentDef
from Tribler.Core.exceptions import DuplicateDownloadException

from Tribler.Main.vwxGUI.SearchGridManager import LibraryManager
from Tribler.Main.vwxGUI.SearchGridManager import TorrentManager
from Tribler.Main.Utility.GuiDBTuples import CollectedTorrent, Torrent
from Tribler.Main.vwxGUI.GuiUtility import GUIUtility
from Tribler.Main.globals import DefaultDownloadStartupConfig

from Tribler.PluginManager.PluginManager import PluginManager

from Tribler.TUPT.TorrentInfoBar import TorrentInfoBar

from Tribler.TUPT.Channels.MovieInserter import MovieInserter

from Tribler.TUPT.Matcher.IMatcherPlugin import IMatcherPlugin
from Tribler.TUPT.Matcher.MatcherControl import MatcherControl

from Tribler.TUPT.Parser.IParserPlugin import IParserPlugin
from Tribler.TUPT.Parser.ParserControl import ParserControl

from Tribler.TUPT.TorrentFinder.ITorrentFinderPlugin import ITorrentFinderPlugin
from Tribler.TUPT.TorrentFinder.TorrentFinderControl import TorrentFinderControl


class TUPTControl:
    '''Class that controls the flow for parsing, matching and finding movies'''
    
    __infoBar = None
    __torrentFinder = None
    __movieTorrentIterator = None
    __callbackTDEvent = Event()
    __callbackTorrentdef = None
    
    def __init__(self, pluginManager = PluginManager()):
        self.pluginmanager = pluginManager
        self.parserControl = ParserControl(pluginManager)
        self.matcherControl = MatcherControl(pluginManager)
        self.__movieTorrentIterator = MovieTorrentIterator()
        
        #Setup the plugins.
        self.pluginmanager.RegisterCategory("Matcher", IMatcherPlugin)
        self.pluginmanager.RegisterCategory("Parser", IParserPlugin)
        self.pluginmanager.RegisterCategory("TorrentFinder", ITorrentFinderPlugin)
        self.pluginmanager.LoadPlugins()
        
    def CoupleGUI(self, gui):
        webview = gui.frame.webbrowser
        webview.AddLoadedListener(self)
        self.webview = webview
        self.mainFrame = gui.frame
        
    def webpageLoaded(self, event, html):
        """Callback for when a webpage was loaded
            We can now start feeding our parser controller.
        """
        print "DEBUG: TUPT started."
        #Parse the Website
        if self.parserControl.HasParser(event.GetURL()):
            movies, trust = self.parserControl.ParseWebsite(event.GetURL(), html)
            #Check if there a movies on the website.
            if movies is not None:
                self.__movieTorrentIterator = MovieTorrentIterator()
                self.__infoBar = TorrentInfoBar(self.webview, self, self.__movieTorrentIterator)
                for movie in movies:     
                    #Correct movie information
                    if trust == 1:
                        #If we fully trust the parser, skip correction
                        movie = movie
                    else:
                        movie = self.matcherControl.CorrectMovie(movie)
                    #Find torrents corresponding to the movie.
                    self.__torrentFinder = TorrentFinderControl(self.pluginmanager, movie, self.UpdateInforBar)
                    self.__torrentFinder.start()                    
                    movieTorrent = MovieTorrent(movie, self.__torrentFinder)                    
                    self.__movieTorrentIterator.append(movieTorrent)                    
    
    def UpdateInforBar(self, movie):
        print "DEBUG: Updating infobar."
        self.__infoBar.Update(movie)
    
    def DownloadHDMovie(self, n = 0):
        """Start downloading the selected movie in HD quality"""
        #Download the torrent.
        if self.__movieTorrentIterator.HasHDTorrent(n):
            self.__DownloadURL(self.__movieTorrentIterator.GetNextHDTorrent(n).GetTorrentURL(), 
                               self.__movieTorrentIterator.GetMovie(n).movie,
                               True)
        #Update the infobar. This has to be done regardless of if a torrent was added or not.
        if not self.__movieTorrentIterator.HasSDTorrent(n):
            self.__infoBar.RemoveSDQuality()

    def DownloadSDMovie(self, n = 0):
        """Start downliading the selected movie in SD quality"""
        #Check if a torrent exists.
        if self.__movieTorrentIterator.HasSDTorrent(n):
            self.__DownloadURL(self.__movieTorrentIterator.GetNextSDTorrent(n).GetTorrentURL(), 
                               self.__movieTorrentIterator.GetMovie(n).movie,
                               False)
        #Update the infobar. This has to be done regardless of if a torrent was added or not.
        if not self.__movieTorrentIterator.HasSDTorrent(n):
            self.__infoBar.RemoveSDQuality()
    
    def __DownloadURL(self, url, movie, isHD):
        """Download the URL using Tribler and start playing.
        """
        #Start downloading the torrent.
        torrentDef = None
        if url.startswith('http://'):            
            torrentDef  = TorrentDef.load_from_url(url)
        elif url.startswith('magnet:?'):
            TorrentDef.retrieve_from_magnet(url, self.__MagnetCallback)
            self.__callbackTDEvent.wait()
            torrentDef = self.__callbackTorrentdef
            self.__callbackTorrentdef = None
            self.__callbackTDEvent.clear()

        session = Session.get_instance()
        #Check if a torrent is already added.        
        downloadState = self.__FindDownloadStateByInfoHash(torrentDef.infohash)   
        if downloadState == None:
            #Add the torrent if is not already added
            downloadState = session.start_download(torrentDef).network_get_state(None, False, sessioncalling=True)
            #Update the channel
            channelInserter = MovieInserter()
            channelInserter.InsertThreaded(torrentDef, movie, isHD)
         
        libraryManager = LibraryManager.getInstance()
        libraryManager.PlayDownloadState(downloadState)      
        
    def __MagnetCallback(self, torrentdef):
        self.__callbackTorrentdef = torrentdef
        self.__callbackTDEvent.set()    
 
    def __FindDownloadStateByInfoHash(self, infohash):
        downloadStateList = LibraryManager.getInstance().dslist  
        for dls in downloadStateList:
            if dls.download.tdef.infohash == infohash:
                return dls
        return None
    
class MovieTorrentIterator:
    """Class that can hold movies and a HD torrentlist and a SD torrentlist"""
    
    __movies = None
    
    def __init__(self):
        self.__movies = []
    
    def append(self, movieTorrent):
        self.__movies.append(movieTorrent)
        
    def GetSize(self):
        return len(self.__movies)
        
    def HasHDTorrent(self, n):
        return self.__movies[n].HasHDTorrent()
    
    def HasSDTorrent(self, n):
        return self.__movies[n].HasSDTorrent()
    
    def HasTorrent(self, n):
        return self.__movies[n].HasTorrent()
    
    def GetMovie(self,n):
        return self.__movies[n]
    
    def GetNextHDTorrent(self, n):
        return self.__movies[n].GetNextHDTorrent()
    
    def GetNextSDTorrent(self, n):
        return self.__movies[n].GetNextSDTorrent()
        
        
class MovieTorrent:
    """ Class that contains a movie and the corresponding HD and SD torrentlists."""
    
    def __init__(self, movie, torrentFinder):
        self.movie = movie
        self.torrentFinder = torrentFinder
    
    def HasHDTorrent(self):
        return len(self.torrentFinder.GetHDTorrentList()) > 0    
    
    def HasSDTorrent(self):
        return len(self.torrentFinder.GetSDTorrentList()) > 0
    
    def HasTorrent(self):
        return self.HasHDTorrent() or self.HasSDTorrent()
    
    def GetNextHDTorrent(self):  
        return self.torrentFinder.GetHDTorrentList().pop(0)
    
    def GetNextSDTorrent(self):  
        return self.torrentFinder.GetSDTorrentList().pop(0)
   