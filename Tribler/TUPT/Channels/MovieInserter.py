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

        #If we have our own version of this channel and it is not
        #the best channel, merge our channel into the other channel.
        myChannel = self.__channelController.GetMyChannel(self.__channelController.GetChannelNameForYear(year), 
                                        self.__channelController.GetChannelDescriptionForYear(year))
        if myChannel and myChannel != channelId:
            #Merge our entire channel into the other channel
            self.__channelController.MergeChannelInto(myChannel, channelId)
        elif not self.__channelController.ChannelHasTorrent(channelId, torrentDef):
            #Merge the single torrent into the other channel
            duplicateInfoHash = self.__channelController.ChannelGetTorrentFromName(channelId, name)
            if not duplicateInfoHash:
                #If the torrent is not already in the channel
                #Add it to the local database and notify the Dispersy community
                #of the change.
                self.AddTorrentToChannel(channelId, torrentDef, name)
            else:
                #There is already a definition of our torrent in this channel.
                #Try to find out which one is the best.
                self.__channelController.ResolveTorrentConflict(channelId, torrentDef, duplicateInfoHash.infohash)
            
    def InsertThreaded(self, torrentDef, movie, isHD):
        """Put a movie in a threaded way in a channel given a certain torrentDef
        Args:
            torrentDef (Core.TorrentDef) : definition of the torrent that has to be inserted.
            movie (Movie) : movie of which a torrent needs to be inserted.
            isHD (bool): boolean value of the movie isHD or not.
        """
        thread.start_new(self.Insert, (torrentDef, movie, isHD))