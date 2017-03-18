import unittest
import download_npo.sites


class Test_NPOPlayer(unittest.TestCase):
    def test_find_video(self):
        site = download_npo.sites.NPOPlayer()
        req, player_id, extension = site.find_video('POW_03414349')
        self.assertEqual(player_id, 'POW_03414349')
        self.assertEqual(extension, 'mp4')
