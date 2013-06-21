import urllib
import urllib2

from imdb.parser.http.topBottomParser import DOMHTMLTop250Parser

from Tribler.TUPT.Movie import Movie
from Tribler.TUPT.Matcher.IMatcherPlugin import IMatcherPlugin

class IMDbMatcherPlugin(IMatcherPlugin):
    """Query IMDb using the IMDbPY library.
        Searches for a movie by title and year (if available) and
        sets the self.result variable to the closest result to be
        found for the input.
        
        Call MatchMovie() before GetMovieAttributes() and GetAttribute()
        
        Depends on imdbpy, Movie, IMatcherplugin, urllib, urllib2
    """

    result = None
    __items = {}

    def __init__(self):
        self.__items = {'title' : ('title', IMDbMatcherPlugin.__ParseNothing), 'year' : ('releaseYear', IMDbMatcherPlugin.__ParseNothing),
                        'director' : ('director', IMDbMatcherPlugin.__ParseDirector), 'cast' : ('cast', IMDbMatcherPlugin.__ParseDirector)}
        self.result = None
    
    def __GetPageSrc(self, url):
        """Return the source of a certain url using a fake header.
        Args:
            url (str): url of the source that needs to be retrieved.
        """
        req = urllib2.Request(url, headers={'User-Agent':"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"})
        opener = urllib2.build_opener()
        return opener.open(req).read()
    
    def __MakeQuery(self, movie):
        """Create a query url for IMDb.
        Args:
            movie (Movie): movie that needs to be queried.
        Returns url of the query (str)"""
        title = movie.dictionary['title'] if 'title' in movie.dictionary else None
        year = movie.dictionary['releaseYear'] if 'releaseYear' in movie.dictionary else None
        titleSubquery = "title=" + urllib.quote(str(title)) if title else None
        yearSubquery = "release_date=" + urllib.quote(str(year)) if year else None
        subquery = '&'.join(value for value in [titleSubquery, yearSubquery] if value is not None)
        return "http://www.imdb.com/search/title?" + subquery
    
    def MatchMovie(self, movie):
        """Search IMDb for the best match to a movie.
        Args:
            movie (Movie): movie that needs to be found.
        Returns url of the movie details page (str)"""
        url = self.__MakeQuery(movie)
        html = self.__GetPageSrc(url)

        searchPageParser = DOMHTMLTop250Parser()
        results = searchPageParser.parse(html)['data']
        if results:
            #If we have results
            #They come in the format of a list of tuples like:
            #(imdbID, movieDictionary)
            #We want the first (/best) result, hence [0]
            #We want to convert the dictionary to a movie, hence [1] 
            self.result = self.__ParseMovie(results[0][1])
        else:
            self.result = {}
    
    def __ParseMovie(self, imdbMovie):
        """Converts a movie from an imdbpy movie to our own Movie class
        Args:
            imdbMovie (imdbMovie) : movies parsed in the imdbpy format
        Returns the parsed movie in Movie format"""
        movie = {}
        for key in self.__items:
            #If the metadata exists add it to the result.
            if imdbMovie.has_key(key):
                #Call on the found result the corresponding parse function and store this on the proper moviekey in movies.
                movie[self.__items[key][0]] = self.__items[key][1](imdbMovie[key])
        #Assert we have the minimum requirements posed by the Movie object
        if ((movie.has_key('title')) or
            (movie.has_key('releaseYear'))):
            return movie
        return None
    
    @staticmethod
    def __ParseNothing(input):
        """ Call this function if no extra parsing is necessary"""
        return input
    
    @staticmethod
    def __ParseDirector(input):
        """Converts the format of director of the IMDb parser to our format."""
        result =[]
        for person in input:
            result.append(person['name'])
        return result
    
    def GetMovieAttributes(self):
        '''Get all attributes found for a movie.
            Called after MatchMovie()
        '''
        return self.result.keys()

    def GetAttribute(self, attribute):
        '''Returns the value of a certain movie attribute
            returned by GetMovieAttributes()
            
            For example:
                me.GetAttribute('title') == 'BBC Docu 5'
        Args:
            attribute (str) : key value of the attribute that needs to be retrieved.
        Returns the value of the attribute.
        '''
        return self.result[attribute]