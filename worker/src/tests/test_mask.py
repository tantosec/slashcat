import unittest
from mask import split_mask, InvalidMaskError, parse_maskfile_from_str


class TestSplitMask(unittest.TestCase):
    def test_split_mask(self):
        self.assertEqual(split_mask("abc"), ["a", "b", "c"])
        self.assertEqual(
            split_mask("?l?u?d?h?H?s?a?b?1?2?3?4"),
            ["?l", "?u", "?d", "?h", "?H", "?s", "?a", "?b", "?1", "?2", "?3", "?4"],
        )
        self.assertEqual(split_mask("???l"), ["??", "?l"])

    def test_invalid_mask(self):
        self.assertRaises(InvalidMaskError, lambda: split_mask("asd?"))


class TestMaskfiles(unittest.TestCase):
    def test_simple(self):
        parsed = parse_maskfile_from_str("hi\ntest")
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0].mask, "hi")
        self.assertEqual(parsed[0].custom_charsets, [])
        self.assertEqual(parsed[1].mask, "test")
        self.assertEqual(parsed[1].custom_charsets, [])

    def test_complex(self):
        parsed = parse_maskfile_from_str("?l?u,cool?1\n?u?s,?l?d,?1?2")
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0].mask, "cool?1")
        self.assertEqual(parsed[0].custom_charsets, ["?l?u"])
        self.assertEqual(parsed[1].mask, "?1?2")
        self.assertEqual(parsed[1].custom_charsets, ["?u?s", "?l?d"])

    def test_comments(self):
        parsed = parse_maskfile_from_str("#comment\n\ncool\n\n#comment2\n\n")
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].mask, "cool")
        self.assertEqual(parsed[0].custom_charsets, [])

    def test_escaping(self):
        parsed = parse_maskfile_from_str("a\\,b,c\\,d\\\\")
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].mask, "c\\,d\\\\")
        self.assertEqual(parsed[0].custom_charsets, ["a\\,b"])

    def test_invalid(self):
        self.assertRaises(InvalidMaskError, lambda: parse_maskfile_from_str("asd?"))


if __name__ == "__main__":
    unittest.main()
