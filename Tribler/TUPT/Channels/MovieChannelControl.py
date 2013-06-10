import time

from Tribler.Main.vwxGUI.GuiUtility import GUIUtility

class MovieChannelControl(object):
    """Controller for channels specifically for TUPT
        retrieved movies.
        
        Every movie will go in its corresponding channel
        based on the release year.
    """
    
    __channelManager = None
    __single = None
    
    def __init__(self, initLater = False):
        if not initLater:
            self.initAuto()
            
    def getInstance(*args, **kw):
        if MovieChannelControl.__single is None:
            MovieChannelControl(*args, **kw)
        return MovieChannelControl.__single
    getInstance = staticmethod(getInstance)

    def hasInstance():
        return MovieChannelControl.__single != None
        hasInstance = staticmethod(hasInstance)

    def delInstance():
        MovieChannelControl.__single = None
    delInstance = staticmethod(delInstance)
    
    def initAuto(self):
        self.__channelManager = GUIUtility.getInstance().channelsearch_manager
        MovieChannelControl.__single = self
        
    def initWithChannelSearchManager(self, manager):
        self.__channelManager = manager
        MovieChannelControl.__single = self
    
    def GetChannelNameForYear(self, year):
        """Return the pretty name for a channel of a certain year
        """
        return "Movies of " + str(year)
    
    def GetChannelDescriptionForYear(self, year):
        return "Auto-generated TUPT channel for movies of the year " + str(year)

    def GetChannelIDForYear(self, year):
        """Given a year, search for the channel id we want to put
            our torrents in.
            If needed, create our own channel
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
        elif totalHits == 1:
            #In the perfect world our channel already exists
            #and is the only one of its kind
            return hits.values()[0].id
        else:
            #We found multiple channels that resemble our
            #requested channel. Select the right one.
            return self.__FindRightChannel(hits.values(), year)
        
    def RemoveChannelByYear(self, year):
        """Given a year, remove our local database entry for it
        """
        name = self.GetChannelNameForYear(year)
        desc = self.GetChannelDescriptionForYear(year)
        self.__channelManager.removeChannelByNameDesc(name, desc)
        
    def RemoveChannelById(self, channelId):
        """Given a channel id, remove our local database entry for it
        """
        self.__channelManager.removeChannelById(channelId)
        
    def GetKnownTUPTChannels(self):
        """Return all TUPT channels we can find in our database
        """
        emptyName = self.GetChannelNameForYear("")
        return self.__channelManager.findChannelsWithNameLike(emptyName)
        
    def GetKnownYears(self):
        """Return all TUPT channel years we can find in our database
        """
        out = []
        emptyName = self.GetChannelNameForYear("")
        for channel in self.__channelManager.findChannelsWithNameLike(emptyName):
            value = int(channel.name[len(emptyName):])
            out.append(value)
        return out
    
    def __GetMyChannel(self, name, description):
        """Get our own channel
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
        """
        self.__channelManager.createChannel(name, description)
        channelId = self.__GetMyChannel(name, description)
        self.__channelManager.setChannelGenerated(channelId, True) #This is not the user's personal channel
        return channelId
    
    def __FilterChannels(self, channels, **requestedPropertyMap):
        """Filter channels by property and requested value.
            Check GUIDBTuples.Channel(Helper) for available properties.
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
    
    def GetChannelObjectFromID(self, channelID):
        return self.__channelManager.getChannel(channelID)
    
    def UpVoteChannel(self, channelID):
        """Upvote a channel by favoriting it"""
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
        self.__channelManager.removeTorrent(self.GetChannelObjectFromID(channelID), torrentDef.infohash)
        
    def RenameChannelTorrent(self, channelID, torrentDef, name):
        """Rename a torrent in a channel and notify the channel community of the changes"""
        self.__channelManager.modifyTorrentName(channelID, torrentDef, name)