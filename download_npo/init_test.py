# encoding:utf-8

import unittest
import download_npo


class Test_DownloadNPO(unittest.TestCase):
    def test_replace_vars(self):
        self.assertEqual(download_npo.replace_vars('/hello/{titel}', {'titel': 'world'}),
                         '/hello/world')
        self.assertEqual(download_npo.replace_vars('/hello/{titel}', {'titel': u'ωορλδ'}),
                         u'/hello/ωορλδ')

    def test_make_filename(self):
        cases = (
            (u'world', u'/tmp/world.mp4', {}),
            (u'ωορλδ', u'/tmp/ωορλδ.mp4', {}),
            (u'ωορλδ', u'/tmp/ωορλδ.mp4', {}),
        )
        for tc, expected, args in cases:
            path = download_npo.make_filename('/tmp', '{titel}', 'mp4', {'titel': tc}, **args)
            self.assertEqual(path, expected)


# Some more realistic integration tests.
class Test_Integration(unittest.TestCase):
    def test_make_filename(self):
        site = download_npo.sites.NPOPlayer()
        meta = site.meta('POW_03414349')
        self.assertEqual(meta.get('STATUS'), 'OK')

        path = download_npo.make_filename('/tmp', '{titel}', 'mp4', meta)
        self.assertEqual(path, u'/tmp/Gouden_Jaren_Indonesië.mp4')
