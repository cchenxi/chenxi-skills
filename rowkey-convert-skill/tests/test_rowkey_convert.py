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
        r = run(r"\x00\x01\xFF", "--format", "all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("0001FF", r.stdout)
        self.assertIn(r"\x00\x01\xFF", r.stdout)
        self.assertIn("[0, 1, 255]", r.stdout)
        self.assertIn("00 01 FF", r.stdout)
        self.assertIn(r"\x00\x01\xFF", r.stdout)  # mixed output

    def test_all_printable(self):
        r = run("hello", "--format", "all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("68656C6C6F", r.stdout)
        self.assertIn(r"\x68\x65\x6C\x6C\x6F", r.stdout)
        self.assertIn("[104, 101, 108, 108, 111]", r.stdout)

    def test_mixed(self):
        r = run(r"\x00\xFFhello\x01", "--format", "all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("00FF68656C6C6F01", r.stdout)
        self.assertIn(r"\x00\xFF\x68\x65\x6C\x6C\x6F\x01", r.stdout)
        self.assertIn("[0, 255, 104, 101, 108, 108, 111, 1]", r.stdout)
        self.assertIn(r"\x00\xFFhello\x01", r.stdout)  # mixed output

    def test_single_byte(self):
        r = run(r"\x41", "--format", "all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("41", r.stdout)


class TestReverseConversion(unittest.TestCase):
    """hex / bytes → mixed"""

    def test_hex_to_all(self):
        r = run("00FF68656C6C6F", "--format", "all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("00FF68656C6C6F", r.stdout)
        self.assertIn(r"\x00\xFFhello", r.stdout)

    def test_bytes_decimal_to_all(self):
        r = run("[0, 255, 104]", "--format", "all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("00FF68", r.stdout)
        self.assertIn(r"\x00\xFFh", r.stdout)

    def test_bytes_hex_prefix_to_all(self):
        r = run("[0x00, 0xFF, 0x68]", "--format", "all")
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

    def test_format_java_only(self):
        r = run(r"\x00\xFFhello\x80", "--format", "java")
        self.assertEqual(r.returncode, 0)
        self.assertIn("[0, -1, 104, 101, 108, 108, 111, -128]", r.stdout)

    def test_default_is_all(self):
        """Without --format, default output is all formats"""
        r = run(r"\x00\xFFhello")
        self.assertEqual(r.returncode, 0)
        self.assertIn("[Hex]", r.stdout)
        self.assertIn("[Java]", r.stdout)
        self.assertIn(r"\x00\xFFhello", r.stdout)


class TestErrorHandling(unittest.TestCase):
    """Invalid inputs produce clean errors"""

    def test_empty_bytes_array(self):
        r = run("[]")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Error:", r.stderr)


class TestRoundTrip(unittest.TestCase):
    """Round-trip consistency"""

    def test_non_printable_roundtrip(self):
        """All non-printable bytes: mixed → hex → mixed should match"""
        r1 = run(r"\x00\x01\xFF\xFE", "--format", "hex")
        hex_val = r1.stdout.strip().split('\n')[-1]  # last line is the hex value
        r2 = run(hex_val, "--format", "mixed")
        self.assertIn(r"\x00\x01\xFF\xFE", r2.stdout)

    def test_printable_roundtrip(self):
        """All printable: hello → hex → mixed should match"""
        r1 = run("hello", "--format", "hex")
        hex_val = r1.stdout.strip().split('\n')[-1]
        r2 = run(hex_val, "--format", "mixed")
        self.assertIn("hello", r2.stdout)

    def test_mixed_roundtrip(self):
        """Mixed printable/non-printable: mixed → hex → mixed should match"""
        original = r"\x00\xFFhello\x01"
        r1 = run(original, "--format", "hex")
        hex_val = r1.stdout.strip().split('\n')[-1]
        r2 = run(hex_val, "--format", "mixed")
        self.assertIn(original, r2.stdout)


class TestBytesArrayEdgeCases(unittest.TestCase):
    """Edge cases for bytes array input"""

    def test_mixed_hex_prefix(self):
        """Bytes array with mixed decimal and 0x prefix: [0x00, 255, 0xFF]"""
        r = run("[0x00, 255, 0xFF]", "--format", "all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("00FFFF", r.stdout)
        self.assertIn("[0, 255, 255]", r.stdout)


class TestUnicodeInput(unittest.TestCase):
    """Unicode / non-ASCII input handling"""

    def test_utf8_chinese_in_mixed(self):
        """中 (U+4E2D) → UTF-8 bytes 0xE4 0xB8 0xAD → \xE4\xB8\xAD in mixed"""
        r = run(r"\xE4\xB8\xAD", "--format", "mixed")
        self.assertEqual(r.returncode, 0)
        self.assertIn(r"\xE4\xB8\xAD", r.stdout)


class TestAnnotatedReverse(unittest.TestCase):
    """Annotated format as input (reverse conversion)"""

    def test_annotated_to_all(self):
        annotated = "00 FF 68 65\n .   .   h   e"
        r = run(annotated, "--format", "all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("00FF6865", r.stdout)
        self.assertIn(r"\x00\xFFhe", r.stdout)


class TestExtractMode(unittest.TestCase):
    """--extract flag"""

    def test_extract_from_log_line(self):
        r = run(r"prefix_\x00\xFF_suffix", "--extract", "--format", "all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("rowkey at offset 7", r.stdout)
        self.assertIn(r"\x00\xFF", r.stdout)

    def test_extract_no_match(self):
        r = run("no rowkey here", "--extract")
        self.assertEqual(r.returncode, 0)
        self.assertIn("No rowkey candidates found", r.stdout)


class TestMaxLength(unittest.TestCase):
    """--max-length flag"""

    def test_within_limit(self):
        r = run(r"\x00\xFFhello", "--max-length", "10", "--format", "all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("00FF68656C6C6F", r.stdout)

    def test_exceeds_limit(self):
        r = run(r"\x00\xFFhello", "--max-length", "2")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("exceeds --max-length", r.stderr)


class TestInvalidHexError(unittest.TestCase):
    r"""Better error message for invalid \xHH"""

    def test_invalid_hex_escape(self):
        r = run(r"\xGG\x00")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Invalid hex escape", r.stderr)


if __name__ == "__main__":
    unittest.main()
