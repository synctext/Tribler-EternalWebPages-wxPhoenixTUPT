"""This file contains the FenopyMovieTorrentPlugin class."""

import urllib
import urllib2

from bs4 import BeautifulSoup

from Tribler.TUPT.TorrentFinder.ITorrentFinderPlugin import ITorrentFinderPlugin
from Tribler.TUPT.TorrentFinder.IMovieTorrentDef import IMovieTorrentDef

class FenopyMovieTorrentDef(IMovieTorrentDef):
    """TorrentFinder plugin that can find plugins on Fenopy."""
    
    def __SearchSeeder(self, tag):
        """Search the seeders."""
        return tag.has_key('class') and 'se' in tag['class']
    
    def __SearchLeecher(self, tag):
        """Search the leechers."""
        return tag.has_key('class') and 'le' in tag['class']
    
    def __ExtractMagnet(self, source):
        """Extract the magnet link to the torrent."""
        index = source.find('magnet')
        eindex = source.find('"', index)
        return source[index:eindex]
    
    def __init__(self, tag):
        self.seeders = int(tag.find(self.__SearchSeeder).string)
        self.leechers = int(tag.find(self.__SearchLeecher).string)
        self.torrentname = str(tag.td.a['title'])
        self.torrenturl = self.__ExtractMagnet(str(tag))
        self.highdef = self.torrentname.find("1080p") != -1

    def GetTorrentProviderName(self):
        return 'Fenopy'

class TriblerTorrentFinderPlugin(ITorrentFinderPlugin):
    """TorrentFinder plugin to search within Tribler. Will only work within a running Tribler instance."""

    def __GetTorrentDefs(self, src, movie):
        """Split our soup into search results
        """
        soup = BeautifulSoup(src)
        resTable = soup.find(id="search_table")
        out = []
        for tr in resTable.find_all("tr"):
            if str(tr).find('magnet') != -1:
                torrentDef = FenopyMovieTorrentDef(tr)
                torrentDef.moviedescriptor = movie
                out.append(torrentDef)
                if len(out) == 10:
                    break
        return out
    
    def __UrlToPageSrc(self, url):
        """Retrieve the HTML source."""
        req = urllib2.Request(url, headers={'User-Agent':"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"})
        opener = urllib2.build_opener()
        contents = opener.open(req)
        return contents.read()
    
    def __GetQueryForMovie(self, movieDict):
        """Return a search query given a movie dictionary
        """
        return urllib.quote(movieDict['title'].replace(" ", "+") + "+" + str(movieDict['releaseYear']))
    
    def GetTorrentDefsForMovie(self, movie):
        """Receive a Movie object and return a list of matching IMovieTorrentDefs
        """
        # Construct the results page
        resultUrl = "http://www.fenopyproxy.com/search/" + self.__GetQueryForMovie(movie.dictionary) + ".html?order=2&quality=0&cat=3"
        return self.__GetTorrentDefs(self.__UrlToPageSrc(resultUrl), movie)
