import thread

from Tribler.Core.TorrentDef import TorrentDef
from Tribler.Main.vwxGUI.GuiUtility import GUIUtility

from MovieChannelControl import MovieChannelControl

class MovieInserter(object):
    """This class can insert movies into channels.
    
    Depends on: TorrentDef, GuiUtility, MovieChannelcontrol
    """
    
    __channelController = None
    
    def __init__(self):
        self.__channelController = MovieChannelControl.getInstance()
        
    def PrettyMovieName(self, movie, isHD):
        """Create a pretty torrent name for a movie definition
            Uses movie title, movie release year and wether it is HD or not
            
            Ex.
            "[HD] The Matrix (1999)" For high-definition version
            "The Matrix (1999)" For unkown/lower-definition version
            
            Args:
                movie (Movie) : movie of which a nicer name needs to be made.
                isHD (bool): boolean value of the movie isHD or not.
        Returns the pretty name for the movie (str).
        """
        title = movie.dictionary['title']
        releaseYear = '(' + str(movie.dictionary['releaseYear']) + ')'
        hd = "[HD] " if isHD else ""
        return hd + title + " " + releaseYear
        
    def AddTorrentToChannel(self, channelId, torrentDef, name):
        """Add a torrent to the local database and notify the Dispersy community
            #of the change.
        Args:
            channelID (int) : ID of the channel the torrent has to be inserted in.
            torrentDef (Core.TorrentDef) : definition of the torrent that has to be inserted.
            name (str) : name of the torrent.
        """
        self.__channelController.AddTorrentToChannel(channelId, torrentDef)
        self.__channelController.RenameChannelTorrent(channelId, torrentDef, name)
        
        #Update the front-end to show the standardized name
        gui = GUIUtility.getInstance()
        mngr = gui.frame.librarylist.GetManager()
        mngr.refresh()
        
    def ResolveTorrentConflict(self, channelId, torrentDef, otherInfoHash):
        """We have found a different 'best' torrent than the channel.
            Try to find out which of the torrents is actually the best
            and update accordingly.
           
            We base ourselves on the amount of seeds to determine the 
            support for a torrent.
            
        Args:
            channelID (int) : ID of the channel the torrent may be inserted in.
            torrentDef (Core.TorrentDef) : definition of the torrent that wants to be inserted.
            otherInfoHash (Core.TorrentDef.infohash) : infohash of the conflicting torrent already available.
        """
        gui = GUIUtility.getInstance()
        mngr = gui.torrentsearch_manager.torrent_db
        
        ourSeeds = mngr.getTorrent(torrentDef.infohash)
        theirSeeds = mngr.getTorrent(otherInfoHash)
        
        if ourSeeds > theirSeeds:
            #Our torrent has more support than the
            #torrent already on the channel.
            #Move our torrent into the channel.
            #Note that both the Remove and Add calls are networked through dispersy correctly
            self.__channelController.RemoveTorrentFromChannelByInfoHash(otherInfoHash)
            self.__channelController.AddTorrentToChannel(channelId, torrentDef)
        
    def Insert(self, torrentDef, movie, isHD):
        """Put a movie in a channel given a certain torrentDef
        Args:
            torrentDef (Core.TorrentDef) : definition of the torrent that has to be inserted.
            movie (Movie) : movie of which a torrent needs to be inserted.
            isHD (bool): boolean value of the movie isHD or not.
        """
        #Get the pretty name for this torrent
        # Keeps the channel clean.
        name = self.PrettyMovieName(movie, isHD)

        year = movie.dictionary['releaseYear']
        
        channelId = self.__channelController.GetChannelIDForYear(year)
        
        #Whether or not we add our torrent to this channel,
        #it was determined to be the right channel. So upvote it.
        self.__channelController.UpVoteChannel(channelId)
        
        if not self.__channelController.ChannelHasTorrent(channelId, torrentDef):
            duplicateInfoHash = self.__channelController.ChannelGetTorrentFromName(channelId, name)
            if not duplicateInfoHash:
                #If the torrent is not already in the channel
                #Add it to the local database and notify the Dispersy community
                #of the change.
                self.AddTorrentToChannel(channelId, torrentDef, name)
            else:
                #There is already a definition of our torrent in this channel.
                #Try to find out which one is the best.
                self.ResolveTorrentConflict(channelId, torrentDef, duplicateInfoHash)
            
    def InsertThreaded(self, torrentDef, movie, isHD):
        """Put a movie in a threaded way in a channel given a certain torrentDef
        Args:
            torrentDef (Core.TorrentDef) : definition of the torrent that has to be inserted.
            movie (Movie) : movie of which a torrent needs to be inserted.
            isHD (bool): boolean value of the movie isHD or not.
        """
        thread.start_new(self.Insert, (torrentDef, movie, isHD))