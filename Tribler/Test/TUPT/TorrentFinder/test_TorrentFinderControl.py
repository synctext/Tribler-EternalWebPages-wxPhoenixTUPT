import unittest

from Tribler.Test.TUPT.TorrentFinder.TorrentFinderStubs import TorrentFinderPluginManagerStub
from Tribler.Test.TUPT.TorrentFinder.TorrentFinderStubs import TorrentDefStub

from Tribler.TUPT.TorrentFinder.TorrentFinderControl import TorrentFinderControl
from Tribler.TUPT.Movie import Movie

import time

class TestTorrentFinderControl(unittest.TestCase):
    '''Test class to test TorrentFinderControl'''
    
    def setUp(self, ):
        """Setup before testing"""
        #Arrange
        self.__movie = Movie()
        self.__movie.dictionary['title'] = 'TestMovie'
        self.__pluginmanager = TorrentFinderPluginManagerStub()
        self.__torrentFinderControl = TorrentFinderControl(self.__pluginmanager, self.__movie, self.callback)
        self.__timesCallbacked = 0       
    
    def test_HasHDTorrent_HasNoTorrent(self):
        #Act
        result = self.__torrentFinderControl.HasHDTorrent()
        #Assert
        self.assertFalse(result)
        
    def test_HasHDTorrent_HasTorrent(self):
        #Arrange
        self.__torrentFinderControl.FindTorrents()
        #Act
        result = self.__torrentFinderControl.HasHDTorrent()
        #Assert
        self.assertTrue(result)
        
    def test_HasSDTorrent_HasNoTorrent(self):
        #Act
        result = self.__torrentFinderControl.HasSDTorrent()
        #Assert
        self.assertFalse(result)
        
    def test_HasSDTorrent_HasTorrent(self):
        #Arrange
        self.__torrentFinderControl.FindTorrents()
        #Act
        result = self.__torrentFinderControl.HasSDTorrent()
        #Assert
        self.assertTrue(result)
     
    def test_FindTorrent_GetResults(self):
        #Act
        self.__torrentFinderControl.FindTorrents()
        #Assert
        self.assertTrue(len(self.__torrentFinderControl.GetHDTorrentList()) > 0)
        self.assertTrue(len(self.__torrentFinderControl.GetSDTorrentList()) > 0)
        
    def test_ProcessTorrentDef_addHDDefinition(self):
         """Test processing a HD TorrentDef."""
         torrentDef =  TorrentDefStub(True, self.__movie)
         #Act
         self.__torrentFinderControl.ProcessTorrentDef(torrentDef, 0.5)
         #Assert
         self.assertTrue(len(self.__torrentFinderControl.GetHDTorrentList()) > 0)
         self.assertEqual(0, len(self.__torrentFinderControl.GetSDTorrentList()))
         
    def test_ProcessTorrentDef_addSDDefinition(self):
         """Test processing a SD TorrentDef."""
         torrentDef =  TorrentDefStub(False, self.__movie)
         #Act
         self.__torrentFinderControl.ProcessTorrentDef(torrentDef, 0.5)
         #Assert
         self.assertTrue(len(self.__torrentFinderControl.GetSDTorrentList()) > 0)
         self.assertEqual(0, len(self.__torrentFinderControl.GetHDTorrentList()))
    
    def test_AsynchronosCallback_CallbackCalled(self):
        """Test if the callback is called on results"""
        self.__torrentFinderControl.start()
        #Assert
        self.__torrentFinderControl.join()
        self.assertTrue(self.__timesCallbacked)

    def test_FindTorrent_CallBack_OnlyCalledOnChange_NoChange(self):
        """Test if the callback is only called on a change in results."""
        #Act
        self.__torrentFinderControl.start()
        self.__torrentFinderControl.join()
        #Assert
        self.assertTrue(1, self.__timesCallbacked)
        
    def test_FindTorrent_CallBack_OnlyCalledOnChange_Change(self):
        """Test if the callback is only called on a change in results."""
        #Arrange
        self.__torrentFinderControl = TorrentFinderControl(TorrentFinderPluginManagerStub(changedResult = True), self.__movie, self.callback)
        #Act
        self.__torrentFinderControl.start()
        self.__torrentFinderControl.join()
        #Assert
        self.assertEqual(2, self.__timesCallbacked)
    
    def callback(self):
        self.__timesCallbacked += 2  
    
if __name__ == '__main__':
    unittest.main()
    