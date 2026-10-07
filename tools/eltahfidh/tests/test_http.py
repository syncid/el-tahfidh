import unittest

from tools.eltahfidh.http import UrllibClient, safe_url


class PacingTest(unittest.TestCase):
    def test_downloads_use_their_own_shorter_interval(self):
        clock, waits = [100.0], []
        client = UrllibClient("ua", 2.5, sleep=waits.append, now=lambda: clock[0], download_interval=0.5)
        client._pace()
        client._pace(client._download_interval)
        client._pace()
        self.assertEqual(waits, [0.5, 2.5])


class SafeUrlTest(unittest.TestCase):
    def test_non_ascii_is_encoded_and_valid_url_untouched(self):
        self.assertEqual(safe_url("https://x.id/a/\U0001f389-Bogor-\u2013-9.jpg?a=1&b=2"),
                         "https://x.id/a/%F0%9F%8E%89-Bogor-%E2%80%93-9.jpg?a=1&b=2")
        self.assertEqual(safe_url("https://x.id/a%20b.jpg"), "https://x.id/a%20b.jpg")


if __name__ == "__main__":
    unittest.main()
