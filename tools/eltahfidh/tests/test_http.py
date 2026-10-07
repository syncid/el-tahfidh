import unittest

from tools.eltahfidh.http import UrllibClient


class PacingTest(unittest.TestCase):
    def test_downloads_use_their_own_shorter_interval(self):
        clock, waits = [100.0], []
        client = UrllibClient("ua", 2.5, sleep=waits.append, now=lambda: clock[0], download_interval=0.5)
        client._pace()
        client._pace(client._download_interval)
        client._pace()
        self.assertEqual(waits, [0.5, 2.5])


if __name__ == "__main__":
    unittest.main()
