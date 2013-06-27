"""THis file contains the KatPhMovieTorrrentFinderPlugin class."""

import urllib
import urllib2
import gzip
import StringIO
import xml.dom.minidom as minidom

from Tribler.TUPT.TorrentFinder.ITorrentFinderPlugin import ITorrentFinderScreenScraperPlugin, ITorrentFinderPlugin
from Tribler.TUPT.TorrentFinder.IMovieTorrentDef import IMovieTorrentDef

class KatPhMovieTorrentDef(IMovieTorrentDef):
    """IMovieTorrentdef for Katph."""

    def __init__(self, node):
        self.highdef = str(node.getElementsByTagName('category')[0].childNodes[0].nodeValue).find('Highres Movies') != -1
        self.seeders = int(node.getElementsByTagName('torrent:seeds')[0].childNodes[0].nodeValue)
        self.leechers = int(node.getElementsByTagName('torrent:peers')[0].childNodes[0].nodeValue)
        self.torrentname = str(node.getElementsByTagName('torrent:fileName')[0].childNodes[0].nodeValue)
        self.torrenturl = node.getElementsByTagName('enclosure')[0].getAttribute('url') 

    def GetTorrentProviderName(self):
        return 'kat.ph'
    

class KatPhTorrentFinderPlugin(ITorrentFinderPlugin, ITorrentFinderScreenScraperPlugin):
    """TorrentFinderplugin that can find plugins from KatPh."""

    def __DecompressRss(self, content):
        """Decrompress the RSS"""
        f = StringIO.StringIO()
        f.write(content)
        f.seek(0)
        return gzip.GzipFile(fileobj=f).read()

    def __ParseResultPage(self, url, movie, n=10):
        """Given a kat.ph rss result page, return the first 'n' results
            as IMovieTorrentDefs
        """
        page = self.__DecompressRss(self.UrlToPageSrc(url))
        dom = minidom.parseString(page)
            
        out = []
        
        for item in dom.getElementsByTagName('item'):
            torrentDef = KatPhMovieTorrentDef(item)
            torrentDef.moviedescriptor = movie
            out.append(torrentDef)
            if len(out) == n:
                break
        return out

    def __GetQueryForMovie(self, movieDict):
        """Return a search query given a movie dictionary
        """
        return urllib.quote(movieDict['title'] + " " + str(movieDict['releaseYear']))

    def GetTorrentDefsForMovie(self, movie):
        """Receive a Movie object and return a list of matching IMovieTorrentDefs
        """
        resultUrl = 'http://kat.ph/usearch/' + self.__GetQueryForMovie(movie.dictionary) + '/?rss=1&field=seeders&sorder=desc'
        return self.__ParseResultPage(resultUrl, movie)
