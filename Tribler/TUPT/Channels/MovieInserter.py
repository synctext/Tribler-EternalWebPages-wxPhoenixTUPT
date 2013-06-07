import thread

from Tribler.Core.TorrentDef import TorrentDef

from MovieChannelControl import MovieChannelControl

class MovieInserter(object):
    
    __channelController = None
    
    def __init__(self):
        self.__channelController = MovieChannelControl.getInstance()
        
    def PrettyMovieName(self, movie, isHD):
        """Create a pretty torrent name for a movie definition
            Uses movie title, movie release year and wether it is HD or not
            
            Ex.
            "[HD] The Matrix (1999)" For high-definition version
            "The Matrix (1999)" For unkown/lower-definition version
        """
        title = movie.dictionary['title']
        releaseYear = '(' + str(movie.dictionary['releaseYear']) + ')'
        hd = "[HD] " if isHD else ""
        return hd + title + " " + releaseYear
        
    def Insert(self, torrentDef, movie, isHD):
        """Put a movie in a channel given a certain torrentDef
        """
        #Get the pretty name for this torrent
        # Keeps the channel clean.
        name = self.PrettyMovieName(movie, isHD)

        year = movie.dictionary['releaseYear']
        
        channelId = self.__channelController.GetChannelIDForYear(year)
        
        if not self.__channelController.ChannelHasTorrent(channelId, torrentDef):
            self.__channelController.AddTorrentToChannel(channelId, torrentDef)
            
    def InsertThreaded(self, torrentDef, movie, isHD):
        """Same as Insert(), but threaded
        """
        thread.start_new(self.Insert, (torrentDef, movie, isHD))