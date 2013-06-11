class IParserPlugin(object):
    """Interface of the parser plugin that can parse websites looking for movies using the html source"""
    
    def ParseWebSite(self, url, html):
        """Parse a website and return a list of movies.
        Args:
            html (str): HTML source of the IMDB website.
        Returns a sequence of the parsed movies ([movie (Movie),])
        """
        pass
        """Parses websites looking for movies
        Args:
            html (str): HTML source of the IMDB website.
        Returns a sequence of the parsed movies ([movie (Movie),])"""
        
    def GetParseableSites(self):
        """Returns a list of parsable urls"""
        return []