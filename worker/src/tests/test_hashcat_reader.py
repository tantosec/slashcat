import unittest
import asyncio
from hashcat_reader import HashcatReader


class TestHashcatReader(unittest.IsolatedAsyncioTestCase):
    async def test_reading(self):
        stream = asyncio.StreamReader()
        stream.feed_data(b"Hello\nThere\n")
        stream.feed_eof()

        hr = HashcatReader(stream)

        self.assertEqual(await hr.try_read_nonjson(), "Hello")
        self.assertEqual(await hr.try_read_nonjson(), "There")

    async def test_filtering(self):
        stream = asyncio.StreamReader()
        stream.feed_data(b'Hello\n{"a":"b"}\n{"c":"d"}\nThere\n{"e":"f"}\n')
        stream.feed_eof()

        hr = HashcatReader(stream)

        self.assertEqual(await hr.try_read_json(), '{"a":"b"}')
        self.assertEqual(await hr.try_read_nonjson(), "Hello")
        self.assertEqual(await hr.try_read_nonjson(), "There")
        self.assertEqual(await hr.try_read_nonjson(), None)
        self.assertEqual(await hr.try_read_json(), '{"c":"d"}')
        self.assertEqual(await hr.try_read_json(), '{"e":"f"}')
        self.assertEqual(await hr.try_read_json(), None)

    async def test_clear(self):
        stream = asyncio.StreamReader()
        stream.feed_data(b"Hello\nA\nB\nC\n")

        hr = HashcatReader(stream)

        self.assertEqual(await hr.try_read_nonjson(), "Hello")
        await hr.clear()

        self.assertEqual(await hr.try_read_nonjson(), None)

        stream.feed_data(b"D\nE\n")

        self.assertEqual(await hr.try_read_nonjson(), "D")

    async def test_forcing(self):
        stream = asyncio.StreamReader()
        stream.feed_data(b"Hello\nA\nB\nC\n")

        hr = HashcatReader(stream)

        self.assertEqual(await hr.try_read_nonjson(), "Hello")
        hr.stop_unforced_reads()
        await hr.clear()  # Shouldn't work
        self.assertEqual(await hr.try_read_nonjson(), None)
        self.assertEqual(await hr.try_read_nonjson(force=True), "A")
        hr.allow_unforced_reads()
        self.assertEqual(await hr.try_read_nonjson(), "B")

    async def test_read_remaining(self):
        stream = asyncio.StreamReader()
        stream.feed_data(b"Hello\n{}\nA\nB\nC\n")

        hr = HashcatReader(stream)

        self.assertEqual(await hr.try_read_nonjson(), "Hello")
        self.assertEqual(await hr.read_remaining(), "{}\nA\nB\nC")


if __name__ == "__main__":
    unittest.main()
