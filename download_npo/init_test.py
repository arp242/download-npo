# encoding:utf-8

import locale
import unittest
import download_npo


class Test_DownloadNPO(unittest.TestCase):
    def test_replace_vars(self):
        self.assertEqual(download_npo.replace_vars('/hello/a-{titel}', {'titel': 'world'}),
                         '/hello/a-world')

        if locale.getpreferredencoding() != 'UTF-8':
            expected = u'/hello/a-'
        else:
            expected = u'/hello/a-ωορλδ'
        self.assertEqual(download_npo.replace_vars('/hello/a-{titel}', {'titel': u'ωορλδ'}),
                         expected)

    def test_make_filename(self):
        cases = (
            (u'world', u'/tmp/a-world.mp4', u'/tmp/a-world.mp4', {}),
            (u'ωορλδ', u'/tmp/a-ωορλδ.mp4', u'/tmp/a-.mp4', {}),
            (u'ωορλδ', u'/tmp/a-ωορλδ.mp4', u'/tmp/a-.mp4', {}),
        )
        for tc, expected, expected2, args in cases:
            path = download_npo.make_filename('/tmp', 'a-{titel}', 'mp4', {'titel': tc}, **args)
            if locale.getpreferredencoding() != 'UTF-8':
                expected = expected2
            self.assertEqual(path, expected)


# Some more realistic integration tests.
class Test_Integration(unittest.TestCase):
    def test_make_filename(self):
        site = download_npo.sites.NPOPlayer()
        meta = site.meta('POW_03414349')
        self.assertEqual(meta.get('STATUS'), 'OK')

        path = download_npo.make_filename('/tmp', '{titel}', 'mp4', meta)
        if locale.getpreferredencoding() != 'UTF-8':
            self.assertEqual(path, u'/tmp/Gouden_Jaren_Indonesie.mp4')
        else:
            self.assertEqual(path, u'/tmp/Gouden_Jaren_Indonesië.mp4')
