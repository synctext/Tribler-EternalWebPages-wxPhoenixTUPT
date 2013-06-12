import unittest
import os

from yapsy.IPlugin import IPlugin

from Tribler.PluginManager.PluginManager import PluginManager

from plugintypes import TestPluginInterface
from plugintypes import TestPluginInterface1
from plugintypes import TestPluginInterface2

class TestPluginManager(unittest.TestCase):
    '''Test class to test PluginManager'''

    def thisFolder(self):
        return os.path.dirname(__file__)

    def test_LoadPlugin(self):
        '''Test loading and interacting with a plugin'''
        #Arrange
        manager = PluginManager()
        manager.OverwritePluginsFolder(self.thisFolder())
        manager.RegisterCategory("TestPlugin1", IPlugin)
        manager.LoadPlugins()
        #Act
        plugins = manager.GetPluginsForCategory("TestPlugin1")
        #Assert  
        self.assertEquals(len(plugins), 1)   
        self.assertEquals(plugins[0].identifier, "UNIT_TEST_1_TESTPLUGIN") 
        self.assertEquals(plugins[0].repeat(266324), 266324) 

    def test_GetAllPlugins(self):
        '''Test identifying plugin by interface'''
        #Arrange
        manager = PluginManager()
        manager.OverwritePluginsFolder(self.thisFolder())
        manager.RegisterCategory("TestPlugin2", TestPluginInterface)
        manager.LoadPlugins()
        #Act
        plugins = manager.GetAllPluginDescriptors()
        #Assert  
        self.assertEquals(len(plugins), 2) 
        
    def test_DiscernPlugins(self):
        '''Test identifying plugin by interface'''
        #Arrange
        manager = PluginManager()
        manager.OverwritePluginsFolder(self.thisFolder())
        manager.RegisterCategory("TestPlugin2", TestPluginInterface1)
        manager.LoadPlugins()
        #Act
        plugins = manager.GetPluginsForCategory("TestPlugin2")
        #Assert  
        self.assertEquals(len(plugins), 1)
        self.assertEquals(plugins[0].identifier, "UNIT_TEST_2_TESTPLUGIN1")
        
           
if __name__ == '__main__':
    unittest.main()
    
    