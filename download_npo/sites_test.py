import unittest
import download_npo.sites


class Test_NPOPlayer(unittest.TestCase):
    def test_find_video(self):
        site = download_npo.sites.NPOPlayer()
        req, player_id, extension = site.find_video('POW_03414349')
        self.assertEqual(player_id, 'POW_03414349')
        self.assertEqual(extension, 'mp4')

    def test_meta(self):
        site = download_npo.sites.NPOPlayer()
        meta = site.meta('POW_03414349')
        self.assertEqual(meta.get('STATUS'), 'OK')

    def test_list(self):
        site = download_npo.sites.NPOPlayer()
        l = site.list('VPWON_1247337', 1)
        self.assertTrue(len(l) > 1)
        self.assertTrue(len(l[0]) == 3)
        self.assertTrue(l[0][0] in l[0][1])
