import unittest

import vigenere

data = [
        {
            'P': 'The imitation game',
            'K': 'cipher',
            'C': 'VPTPQZVIIPSEIIBL'
        },
        {
            'P': 'The',
            'K': 'cipher',
            'C': 'VPT'
        }
    ]

class TestVigenere(unittest.TestCase):
    def test_enkripsi(self):
        for d in data:
            chiper_teks = vigenere.enkripsi(P=d['P'], K=d['K'])
            self.assertEqual(chiper_teks, d['C'])
    def test_dekripsi(self):
        for d in data:
            plain_teks = vigenere.dekripsi(C=d['C'], K=d['K'])
            self.assertEqual(plain_teks, d['P'].replace(' ', '').lower())

if __name__ == '__main__':
    unittest.main()
