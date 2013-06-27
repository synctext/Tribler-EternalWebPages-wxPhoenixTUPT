"""This file contains the SortedTorrentList class."""

import difflib

class SortedTorrentList:
    """Class for sorting search results as they come in
    """
    
    __orderedList = None  # List of tuples of a torrentDef coupled to a rank
    __userDict = None  # Dictionary of named quality identifying words
    
    def __init__(self):
        self.__orderedList = []
        self.__userDict = {}
    
    def GetList(self):
        """Return the ordered list of torrent definitions based on quality rank.
        """
        out = []
        for torrentdef in self.__orderedList:
            out.append(torrentdef[0])
        return out
    
    def Insert(self, torrentDef, trust):
        """Insert a value into our ordered list of torrents.
        Args:
            torrentDef (TorrentDef) : torrentdef to be added to the list.
            trust (float) : trust in the plugin.
        """
        rank = self.__GetRank(torrentDef, trust)
        inserted = False
        for i in range(len(self.__orderedList)):
            if rank > self.__orderedList[i][1]:
                self.__orderedList.insert(i, (torrentDef, rank))
                inserted = True
                break
        if not inserted:
            self.__orderedList.append((torrentDef, rank))
    
    def SetUserDict(self, userDict):
        """Set a dictionary of terms deemed to signify quality in a 
            torrent (Like your favorite torrent release group)
        Args:
            userDict ({}) : dictionary containing favoring terms.
        """
        self.__userDict = userDict
    
    def __GetUserDict(self):
        """Returns a list of terms set by the user that signify some sort
            of quality (Like your favorite torrent release group).
        """
        return self.__userDict
    
    def __MatchesInDict(self, string, userDict):
        """For all of the values in 'userDict' we perform fuzzy matching
            to 'string'. We return the amount of matches we think we
            have.
        Args:
            string (str) : potential term to favor matching if it is in the dictionary.
            userDict {} : dictionary containing the favored keys.
        """
        lstring = string.lower()
        matchers = userDict.values()
        matches = 0.0
        for match in matchers:
            matcher = difflib.SequenceMatcher(None, str(match).lower(), lstring)
            matchrate = matcher.ratio()
            matches += matchrate
        return matches
    
    def __GetRank(self, torrentDef, trust):
        """Use a heuristic for determining a certain score for a torrent
            definition.
        Args:
            torrentDef (TorrentDef) : torrentdef that needs to be ranked.
            trust (float) : trust in the plugin. 
        """
        movieDict = torrentDef.GetMovieDescriptor().dictionary
        userDict = self.__GetUserDict()
        torrentName = torrentDef.GetTorrentName()
        
        potSpeed = torrentDef.GetSeeders() + 0.5 * torrentDef.GetLeechers()
        techWant = (self.__MatchesInDict(torrentName, movieDict) + 1) * (self.__MatchesInDict(torrentName, userDict) + 1)
        
        return trust * techWant * potSpeed
