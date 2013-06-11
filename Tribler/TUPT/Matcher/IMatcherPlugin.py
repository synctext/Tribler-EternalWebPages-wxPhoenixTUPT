class IMatcherPlugin(object):
    
    def MatchMovie(self, movie):
        '''Receive a Movie class and find our closest
            matching movie.
        Args:
            movie (Movie): movie that needs to be matched.
        '''
        pass
    
    def GetMovieAttributes(self):
        '''Get all attributes found for a movie.
            Called after MatchMovie()
        '''
        pass
    
    def GetAttribute(self, attribute):
        '''Returns the value of a certain movie attribute
            returned by GetMovieAttributes()
            
            For example:
                me.GetAttribute('title') == 'BBC Docu 5'
        Args:
            attribute (str) : key value of the attribute that needs to be retrieved.
        Returns the value of the attribute.
        '''
        pass