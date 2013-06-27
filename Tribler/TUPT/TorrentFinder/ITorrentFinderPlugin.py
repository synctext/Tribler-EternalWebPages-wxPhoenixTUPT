import urllib2

class ITorrentFinderPlugin(object):
	
	def GetTorrentDefsForMovie(self, movie):
		"""Receive a Movie object and return a list of matching IMovieTorrentDefs
		"""
		pass
	
class ITorrentFinderScreenScraperPlugin(object):
	
	def UrlToPageSrc(self, url):
		req = urllib2.Request(url, headers={'User-Agent':"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"})
		opener = urllib2.build_opener()
		return opener.open(req).read()
		