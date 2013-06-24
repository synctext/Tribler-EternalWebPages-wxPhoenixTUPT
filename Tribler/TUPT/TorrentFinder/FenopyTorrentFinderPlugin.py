import urllib
import urllib2

from bs4 import BeautifulSoup

from Tribler.TUPT.TorrentFinder.ITorrentFinderPlugin import ITorrentFinderScreenScraperPlugin
from Tribler.TUPT.TorrentFinder.IMovieTorrentDef import IMovieTorrentDef
from Tribler.TUPT.Movie import Movie

class FenopyMovieTorrentDef(IMovieTorrentDef):
    """TorrentFinder plugin that can find plugins on Fenopy."""
    
    def __SearchSeeder(self, tag):
        return tag.has_key('class') and 'se' in tag['class']
    
    def __SearchLeecher(self, tag):
        return tag.has_key('class') and 'le' in tag['class']
    
    def __ExtractMagnet(self, str):
        index = str.find('magnet')
        eindex = str.find('"',index)
        return str[index:eindex]
    
    def __init__(self, tag):
        self.seeders = int(tag.find(self.__SearchSeeder).string)
        self.leechers = int(tag.find(self.__SearchLeecher).string)
        self.torrentname = str(tag.td.a['title'])
        self.torrenturl = self.__ExtractMagnet(str(tag))
        self.highdef = self.torrentname.find("1080p") != -1

    def GetTorrentProviderName(self):
        return 'Fenopy'

class FenopyTorrentFinderPlugin(ITorrentFinderScreenScraperPlugin):

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
    
    def __GetQueryForMovie(self, dict):
        """Return a search query given a movie dictionary
        """
        return urllib.quote(dict['title'].replace(" ", "+") + "+" + str(dict['releaseYear']))
    
    def GetTorrentDefsForMovie(self, movie):
        """Receive a Movie object and return a list of matching IMovieTorrentDefs
        """
        #Construct the results page
        resultUrl = "http://www.fenopyproxy.com/search/" + self.__GetQueryForMovie(movie.dictionary) + ".html?order=2&quality=0&cat=3"
        return self.__GetTorrentDefs(self.UrlToPageSrc(resultUrl), movie)