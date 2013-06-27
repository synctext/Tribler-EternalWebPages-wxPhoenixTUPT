class IMovieTorrentDef(object):
    
    seeders = None          # Set in init
    leechers = None         # Set in init
    highdef = None          # Set in init
    moviedescriptor = None  # Set externally
    torrentname = None      # Set in init
    torrenturl = None       # Set in init
    
    def GetSeeders(self):
        """Return the amount of seeders for the torrent
        """
        return self.seeders
    
    def GetLeechers(self):
        """Return the amount of leechers for the torrent
        """
        return self.leechers
    
    def IsHighDef(self):
        """Return True if a movie is High Definition
        """
        return self.highdef
    
    def GetMovieDescriptor(self):
        """Returns a Movie object that describes the movie (the search
            query)
        """
        return self.moviedescriptor
    
    def GetTorrentName(self):
        """Returns the name of the torrent.
            For example: '[BBC-FANSUB]birddocumentar.yv2.05Xbittorent.comX.torrent'
        """
        return self.torrentname
    
    def GetTorrentURL(self):
        """Returns the torrent URL location, if we wish to download it
        """
        return self.torrenturl
    
    def GetTorrentProviderName(self):
        """Returns the name of the torrent's provider
            For example: Official BitTorrent Site or Torrentz.eu
        """
        pass
    