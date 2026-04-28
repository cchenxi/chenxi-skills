"""Test cases for rowkey-convert CLI tool."""

import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "rowkey-convert"


def run(input_str: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), input_str, *args],
        capture_output=True, text=True
    )


class TestForwardConversion(unittest.TestCase):
    """mixed → hex / escaped / bytes / annotated"""

    def test_all_non_printable(self):
        r = run(r"\x00\x01\xFF")
        self.assertEqual(r.returncode, 0)
        self.assertIn("0001FF", r.stdout)
        self.assertIn(r"\x00\x01\xFF", r.stdout)
        self.assertIn("[0, 1, 255]", r.stdout)
        self.assertIn("00 01 FF", r.stdout)
        self.assertIn(r"\x00\x01\xFF", r.stdout)  # mixed output

    def test_all_printable(self):
        r = run("hello")
        self.assertEqual(r.returncode, 0)
        self.assertIn("68656C6C6F", r.stdout)
        self.assertIn(r"\x68\x65\x6C\x6C\x6F", r.stdout)
        self.assertIn("[104, 101, 108, 108, 111]", r.stdout)

    def test_mixed(self):
        r = run(r"\x00\xFFhello\x01")
        self.assertEqual(r.returncode, 0)
        self.assertIn("00FF68656C6C6F01", r.stdout)
        self.assertIn(r"\x00\xFF\x68\x65\x6C\x6C\x6F\x01", r.stdout)
        self.assertIn("[0, 255, 104, 101, 108, 108, 111, 1]", r.stdout)
        self.assertIn(r"\x00\xFFhello\x01", r.stdout)  # mixed output

    def test_single_byte(self):
        r = run(r"\x41")
        self.assertEqual(r.returncode, 0)
        self.assertIn("41", r.stdout)


class TestReverseConversion(unittest.TestCase):
    """hex / bytes → mixed"""

    def test_hex_to_all(self):
        r = run("00FF68656C6C6F")
        self.assertEqual(r.returncode, 0)
        self.assertIn("00FF68656C6C6F", r.stdout)
        self.assertIn(r"\x00\xFFhello", r.stdout)

    def test_bytes_decimal_to_all(self):
        r = run("[0, 255, 104]")
        self.assertEqual(r.returncode, 0)
        self.assertIn("00FF68", r.stdout)
        self.assertIn(r"\x00\xFFh", r.stdout)

    def test_bytes_hex_prefix_to_all(self):
        r = run("[0x00, 0xFF, 0x68]")
        self.assertEqual(r.returncode, 0)
        self.assertIn("00FF68", r.stdout)
        self.assertIn(r"\x00\xFF\x68", r.stdout)


class TestFormatFlag(unittest.TestCase):
    """--format flag limits output"""

    def test_format_hex_only(self):
        r = run(r"\x00\xFFhello", "--format", "hex")
        self.assertEqual(r.returncode, 0)
        self.assertIn("00FF68656C6C6F", r.stdout)
        self.assertNotIn("Escaped", r.stdout)

    def test_format_escaped_only(self):
        r = run(r"\x00\xFFhello", "--format", "escaped")
        self.assertEqual(r.returncode, 0)
        self.assertIn(r"\x00\xFF\x68\x65\x6C\x6C\x6F", r.stdout)

    def test_format_bytes_only(self):
        r = run(r"\x00\xFFhello\x01", "--format", "bytes")
        self.assertEqual(r.returncode, 0)
        self.assertIn("[0, 255, 104, 101, 108, 108, 111, 1]", r.stdout)

    def test_format_mixed_only(self):
        r = run("00FF68656C6C6F", "--format", "mixed")
        self.assertEqual(r.returncode, 0)
        self.assertIn(r"\x00\xFFhello", r.stdout)

    def test_format_annotated_only(self):
        r = run(r"\x00\xFFhello", "--format", "annotated")
        self.assertEqual(r.returncode, 0)
        self.assertIn("00 FF 68 65 6C 6C 6F", r.stdout)
        self.assertIn(" .   .   h   e   l   l   o", r.stdout)
        self.assertNotIn("Escaped", r.stdout)


class TestErrorHandling(unittest.TestCase):
    """Invalid inputs produce clean errors"""

    def test_empty_input(self):
        r = run("")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Error:", r.stderr)

    def test_garbage_input(self):
        r = run("not_a_valid_input!!!")
        self.assertEqual(r.returncode, 0)  # treated as mixed
        # Should output the ASCII bytes of the garbage string
        self.assertIn("6E6F745F", r.stdout)


if __name__ == "__main__":
    unittest.main()
