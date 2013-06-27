"""File contains the ParserControl class."""
import sys
import urlparse

from Tribler.TUPT.Movie import Movie

class ParserControl():
    """Class that determines if it has a plugin that can parse a particulair website or try a general parser.
    
    Depends on Sys, URLParse, Movie
    """
    
    __pluginManager = None
    
    def __init__(self, pluginManager):
        self.__pluginManager = pluginManager

    def HasParser(self, url):   
        """ Check if a parser exists.
        Args:
            url (str) : url that needs to be parsed.
        Returns True if the url an be parsed. (bool)"""
        plugin, _ , _ = self.__FindPlugin(url)
        return plugin is not None
    
    def ParseWebsite(self, url, html):
        """Parse a website using the best parser
        Args:
            url (str) : url that needs to be parsed.
            html (str): HTML source of the website.
        Returns a sequence of the parsed movies and the trust of the parser used. ([movie (Movie),]), trust(float)  """
        # Determine parser
        plugin, trust, name = self.__FindPlugin(url)
        # Check if we can parse the site
        if plugin:        
             # Defensivly execute the plugin.
            result = None
            try:
                result = plugin.ParseWebSite(url, html)
            except Exception:# Defensive programming pylint: disable=W0703
                print "Unexpected error in plugin ", name , "." , sys.exc_info()
            # Return the result
            if result != None:
                for movie in result:
                    if not isinstance(movie, Movie):
                        # Should return a Movie object.
                        raise IllegalParseResultException('Parser returned a result not of Type Movie.')
            return result, trust
        else:
            raise NoParserFoundException('No parser found for:' + url + '. Use HasParser before using ParseWebsite.')
        return None, None
    
    def __FindPlugin(self, url):
        """Find a parser that will be able to parse the website.
        Args:
            url (str) : url that needs to be parsed.
        Returns plugin, trust of the plugin and name of the plugin. (plugin (IParserPlugin, trust (float), name (str))"""
        url = urlparse.urlparse(url).netloc    
    
         # Determine parser
        plugins = self.__pluginManager.GetPluginDescriptorsForCategory('Parser')
        plugin = None
        trust = -1
        name = None
        for plugin_info in plugins:
            # Check if you want to use this plugin. This is based on a higher trust and if the plugin can parse the website.
            if self.__GetPluginTrust(plugin_info) > trust and url in plugin_info.plugin_object.GetParseableSites():
                plugin = plugin_info.plugin_object
                trust = self.__GetPluginTrust(plugin_info)
                name = plugin_info.name
        return plugin, trust, name

    def __GetPluginTrust(self, plugin_info):
        """ Get the plugin trust
        Args:
            plugin_info (IPlugin) : plugin of which the trust needs to retrieved.
        Returns the trust of the plugin (float)"""
        trust = 0.5
        try:
            trust = plugin_info.details.getfloat("Core", "Trust")
        except Exception:# Defensive programming pylint: disable=W0703
            print sys.exc_info()
            trust = 0.5  # Not a valid float
        return trust

class NoParserFoundException(Exception):
    """Exception that should be thrown when no parser was found on for page."""
    
    def __init__(self, value):
        super(NoParserFoundException, self).__init__(value)
        self.value = value
        
    def __str__(self):
        return repr(self.value)
    
class IllegalParseResultException(Exception):
    """Exception that should be thrown when no parser was found on for page."""
    
    def __init__(self, value):
        super(IllegalParseResultException, self).__init__(value)
        self.value = value
        
    def __str__(self):
        return repr(self.value)
        
        
