import time

from Tribler.Main.vwxGUI.GuiUtility import GUIUtility

class MovieChannelControl(object):
    """Controller for channels specifically for TUPT
        retrieved movies.
        
        Every movie will go in its corresponding channel
        based on the release year.
        
        Depends on: GUIUtility
    """
    
    __channelManager = None
    __single = None
    
    def __init__(self, initLater = False):
        if not initLater:
            self.initAuto()
            
    def getInstance(*args, **kw):
        """Get the Singleton instance of MovieChannelControl:
           Args:
               
           Returns singleton instance of MovieChannelControl (MovieChannelControl)
        """
        if MovieChannelControl.__single is None:
            MovieChannelControl(*args, **kw)
        return MovieChannelControl.__single
    getInstance = staticmethod(getInstance)

    def hasInstance():
        """ Check if a instance exists
        
            Returns True if a MovieChannelControl exists (bool)
        """
        return MovieChannelControl.__single != None
    hasInstance = staticmethod(hasInstance)

    @staticmethod
    def delInstance():
        """ Delete the singleton instance of MovieChannelControl"""
        MovieChannelControl.__single = None
    
    def initAuto(self):
        """Create a singleton instance of MovieChannelControl"""
        self.__channelManager = GUIUtility.getInstance().channelsearch_manager
        MovieChannelControl.__single = self
        
    def initWithChannelSearchManager(self, manager):
        """Create a singleton instance and set the channelManager.
        Args:
            manager (ChannelManager): The channelmanager object to be used with this MovieChannelControl.
        """
        self.__channelManager = manager
        MovieChannelControl.__single = self
    
    def GetChannelNameForYear(self, year):
        """Get description for a channel of a certain year
        Args:
            year (int): The year of which the channel name needs to be retrieved.
        Returns the channel name (str)
        """
        return "Movies of " + str(year)
    
    def GetChannelDescriptionForYear(self, year):
        """Get the description for a channel of a certain year
        Args:
            year (int): The year of the channel that the description of needs to be retrieved.
        Returns the channel description (str)
        """
        return "Auto-generated TUPT channel for movies of the year " + str(year)

    def GetChannelIDForYear(self, year):
        """Given a year, search for the channel id we want to put our torrents in. If needed, create our own channel
        Args:
             year (int): The year of which the channel id has to be retrieved.
        Returns channelID (int)
        """
        #Search for the correct channel in dispersy
        channelName = self.GetChannelNameForYear(year)
        self.__channelManager.setSearchKeywords([channelName])
        #Throw away the new hits, we don't care
        totalHits, _, hits = self.__channelManager.getChannelHits() 
        #Check which channel we need
        if totalHits == 0:
            #No existing channels found for our year,
            #Create a new channel
            return self.__CreateChannel(channelName, self.GetChannelDescriptionForYear(year))
        else:
            #We found multiple channels that resemble our
            #requested channel. Select the right one.
            return self.__FindRightChannel(hits.values(), year)
        
    def RemoveChannelByYear(self, year):
        """Given a year, remove our local database entry for it
        Args:
           year (int): The year of the channel that needs to be removed.
        """
        name = self.GetChannelNameForYear(year)
        desc = self.GetChannelDescriptionForYear(year)
        self.__channelManager.removeChannelByNameDesc(name, desc)
        
    def RemoveChannelById(self, channelId):
        """Given a channel id, remove our local database entry for it
        Args:
            id (int): The id of the channel that needs to be removed.
        """
        self.__channelManager.removeChannelById(channelId)
        
    def GetKnownTUPTChannels(self):
        """Return all TUPT channels we can find in our database
        
        Returns a sequence of all known TUPT channels ([channels])
        """
        emptyName = self.GetChannelNameForYear("")
        return self.__channelManager.findChannelsWithNameLike(emptyName)
        
    def GetKnownYears(self):
        """Return all TUPT channel years we can find in our database
        
        Returns a sequence of all years that have a known TUPT channels [year]
        """
        out = []
        emptyName = self.GetChannelNameForYear("")
        for channel in self.__channelManager.findChannelsWithNameLike(emptyName):
            value = int(channel.name[len(emptyName):])
            out.append(value)
        return out
    
    def GetMyChannel(self, name, description):
        """Get our own channel
        Args:
            name (str)        = Name of the channel.
            description (str) = Description of the channel
        Returns channelID (int)
        """
        hasChannel, hits = self.__channelManager.getAllMyChannels()
        for channel in hits:
            if channel.name == name and channel.description == description:
                return channel.id
        return None
            
    def __CreateChannel(self, name, description):
        """Create a channel with a certain name and return its id 
            Precondition for calling this method is that there exists no
            search results for channels with the name 'name', otherwise
            we will return the wrong channel id.
        Args:
            name (str)        : Name of the channel.
            description (str) : Description of the channel
        Returns channelID (int)    
        """
        self.__channelManager.createChannel(name, description)
        channelId = self.GetMyChannel(name, description)
        self.__channelManager.setChannelGenerated(channelId, True) #This is not the user's personal channel
        return channelId
    
    def __FilterChannels(self, channels, **requestedPropertyMap):
        """Filter channels by property and requested value.
            Check GUIDBTuples.Channel(Helper) for available properties.
        Args:
            channels [channels])     : list of channels that needs to be filtered.
            **requestedPropertyMap   : map of properties that the channel needs to have.
        Returns a filtered list ([channels])
        """
        out = []
        for channel in channels:
            satisfies = True
            for property in requestedPropertyMap:
                if getattr(channel, property) != requestedPropertyMap[property]:
                    satisfies = False
                    break
            if satisfies:
                out.append(channel)
        return out
        
    def __FindRightChannel(self, channels, year):
        """Tribler has found multiple channels that resemble the channel
            we want to insert our torrents in. Find the best match.
        Args:
            channels [channels]) : list of channels that needs to be filtered.: 
            year (int)           : The year of the channel that needs to be found.
        Returns channel with the best match (Channel)
        """
        channelName = self.GetChannelNameForYear(year)
        channelDescription = self.GetChannelDescriptionForYear(year)
        filtered = self.__FilterChannels(channels,
                                         name = channelName,
                                         description = channelDescription)
        results = len(filtered)
        #Check which channel we need
        if results == 0:
            #None of the returned results were actual TUPT channels
            return self.__CreateChannel(channelName, channelDescription)
        elif results == 1:
            #We managed to filter out the correct channel
            return filtered[0].id
        else:
            #We encountered duplicate channels. Select the most popular
            #(based on the number of torrents it owns)
            best = -1
            channelID = -1
            for channel in filtered:
                if channel.nr_torrents > best:
                    channelID = channel.id
            return channelID
    
    def MergeChannelInto(myChannel, channelID):
        """Add all torrents in one of the users channels (myChannel) to another
            channel (channelID)
            
        Args:
            myChannel (int): id of the users channel.    
            channelID (int): id of the channel to be merged into.
        """
        torrents = self.__channelManager.getTorrentsFromChannel(myChannel)
        if torrents:
            for torrent in torrents:
                torrentDef = torrent.ds.get_download().get_def()
                infohash = torrent.infohash
                otherTorrent = self.ChannelGetTorrentFromName(channelID, torrent.name)
                if not otherTorrent:
                    #Other channel does not have our torrent
                    #or anything like it, insert it
                    self.AddTorrentToChannel(channelID, torrentDef)
                elif otherTorrent.infohash != infohash:
                    #Other channel already has a torrent like ours
                    #Pick the best one to insert
                    self.ResolveTorrentConflict(channelID, torrentDef, otherTorrent.infohash)
    
    def GetChannelObjectFromID(self, channelID):
        """Return channel for the channel ID
        Args:
            id (int): id of the channel.
        Returns channel corresponding to the ID."""
        return self.__channelManager.getChannel(channelID)
    
    def UpVoteChannel(self, channelID):
        """Upvote a channel by favoriting it
         Args:
            id (int): id of the channel to be upvoted"""
        self.__channelManager.favorite(channelID)
        
    def AddTorrentToChannel(self, channelID, torrentDef):
        """Returns True if we were successful in adding the torrent to the channel.
            Returns False otherwise.
        """
        return self.__channelManager.createTorrentFromDef(channelID, torrentDef)
    
    def ChannelHasTorrent(self, channelID, torrentDef):
        """Returns True if a channel already owns this torrent definition.
            Returns False otherwise.
        """
        return self.GetChannelObjectFromID(channelID).getTorrent(torrentDef.infohash) is not None
    
    def ChannelGetTorrentFromName(self, channelID, name):
        """Returns a torrent from a name, if it exits. Otherwise
            returns None.
        """
        return self.__channelManager.getTorrentFromName(self.GetChannelObjectFromID(channelID), name)

    def RemoveTorrentFromChannel(self, channelID, torrentDef):
        """Remove the torrent from the channel.
        Args:
            channelID (int) : the channelid of the channel that the torrent needs to be removed from.
            torrentDef (Core.TorrentDef) : torrent that needs to be removed.
        """
        self.__channelManager.removeTorrent(self.GetChannelObjectFromID(channelID), torrentDef.infohash)
    
    def RemoveTorrentFromChannelByInfoHash(self, channelID, infohash):
        """Remove the torrent from the channel.
        Args:
            channelID (int) : the channelid of the channel that the torrent needs to be removed from.
            infohash (Core.TorrentDef.infohash) : infohash of torrent that needs to be removed.
        """
        self.__channelManager.removeTorrent(self.GetChannelObjectFromID(channelID), infohash)
        
    def RenameChannelTorrent(self, channelID, torrentDef, name):
        """Rename a torrent in a channel and notify the channel community of the changes.
         Args:
            channelID (int) : the channel id of the channel that the torrent needs to be renamed in.
            torrentDef (Core.TorrentDef) : torrent that needs to be renamed.
            name (str) : Name the torrents needs to be renamed to."""
        self.__channelManager.modifyTorrentName(channelID, torrentDef, name)
        
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
            self.RemoveTorrentFromChannelByInfoHash(otherInfoHash)
            self.AddTorrentToChannel(channelId, torrentDef)