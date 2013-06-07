from Tribler.Test.TUPT.TUPTStubs import PluginManagerStub
from Tribler.Test.TUPT.TUPTStubs import PluginStub

from Tribler.TUPT.TorrentFinder.IMovieTorrentDef import IMovieTorrentDef

import time

class TorrentFinderPluginManagerStub(PluginManagerStub):
        
    def __init__(self, loopTorrentFinder = False, delaySlowTorrentFinder = 0, changedResult = False):
        
        self.torrentFinderPlugins = [TorrentFinderPluginStub(returnOnlyHD = not changedResult), slowTorrentFinder(delaySlowTorrentFinder)]
        if loopTorrentFinder:
            self.torrentFinderPlugins.append(LoopingTorrentFinderPlugin())
            
    def GetPluginDescriptorsForCategory(self, category):
        if category == 'TorrentFinder':
            return self.torrentFinderPlugins
        return []
    
    def GetPluginFolder(self):
        return "NaN"
    
class TorrentFinderPluginStub(PluginStub):
    
    name = 'TestTorrentFinder'
    
    def __init__(self, returnOnlyHD = False):
       PluginStub.__init__(self)
       self.returnOnlyHD = returnOnlyHD
        
    def GetTorrentDefsForMovie(self, movie):
        return [TorrentDefStub(True, movie), TorrentDefStub(self.returnOnlyHD, movie)]

class LoopingTorrentFinderPlugin(TorrentFinderPluginStub):
    """A test TorrentFinderPlugin that will loop for ever when trying to find torrents."""
    
    def GetTorrentDefsForMovie(self, movie):
        while(True):
            time.sleep(100)

class slowTorrentFinder(TorrentFinderPluginStub):
    
    def __init__(self, delay):
        TorrentFinderPluginStub.__init__(self)
        self.__delay = delay
    
    def GetTorrentDefsForMovie(self, movie):
        time.sleep(self.__delay)
        return [TorrentDefStub(True, movie), TorrentDefStub(False, movie)]
    
class TorrentDefStub(IMovieTorrentDef):

    seeders = 5          # Set in init
    leechers = 5         # Set in init
    highdef = None          # Set in init
    torrentname = 'Test'      # Set in init
    torrenturl = 'Test'       # Set in init
    movieDescriptor = None
    
    def __init__(self, highdef, movieDescriptor):
        self.highdef = highdef   
        self.movieDescriptor = movieDescriptor
    
    def GetSeeders(self):
        return self.seeders
    
    def GetLeechers(self):
        return self.leechers
    
    def IsHighDef(self):
        return self.highdef
    
    def GetMovieDescriptor(self):
        return self.movieDescriptor
    def GetTorrentName(self):
        return self.torrentname
    
    def GetTorrentURL(self):
        return self.torrenturl
    
    def GetTorrentProviderName(self):
        return 'kat.ph'