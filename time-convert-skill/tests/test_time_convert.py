"""Test cases for time-convert CLI tool."""

import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "time-convert"


def run(input_str: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), input_str, *args],
        capture_output=True, text=True
    )


class TestForwardConversion(unittest.TestCase):
    """Time string → all formats"""

    def test_datetime_to_all(self):
        r = run("2026-04-26 21:00:00")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertIn("69EE0C50", r.stdout)
        self.assertIn(r"\x69\xEE\x0C\x50", r.stdout)
        self.assertIn("[105, 238, 12, 80]", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)

    def test_iso_with_offset(self):
        r = run("2026-04-26T21:00:00+08:00")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertIn("69EE0C50", r.stdout)

    def test_date_only(self):
        r = run("2026-04-26")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777132800", r.stdout)
        self.assertIn("2026-04-26 00:00:00 +0800", r.stdout)

    def test_slash_format(self):
        r = run("2026/04/26 21:00:00")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)

    def test_compact_format(self):
        r = run("20260426210000")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)


class TestReverseConversion(unittest.TestCase):
    """Hex / escaped / bytes / timestamp → time"""

    def test_hex_to_all(self):
        r = run("69EE0C50")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)

    def test_hex_lowercase(self):
        r = run("69ee0c50")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)

    def test_escaped_to_all(self):
        r = run(r"\x69\xEE\x0C\x50")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)

    def test_bytes_array_to_all(self):
        r = run("[105, 238, 12, 80]")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)

    def test_timestamp_to_all(self):
        r = run("1777208400")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)


class TestTimezone(unittest.TestCase):
    """Timezone handling"""

    def test_utc_plus_1(self):
        r = run("2026-04-26 14:00:00", "--tz", "UTC+1")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-04-26 14:00:00 +0100", r.stdout)

    def test_utc_plus_0(self):
        r = run("2026-04-26 13:00:00", "--tz", "UTC+0")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-04-26 13:00:00 +0000", r.stdout)

    def test_iana_timezone(self):
        r = run("2026-04-26 09:00:00", "--tz", "America/New_York")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-04-26 09:00:00 -0400", r.stdout)

    def test_short_offset(self):
        r = run("2026-04-26 21:00:00", "--tz", "+9")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-04-26 21:00:00 +0900", r.stdout)


class TestFormatFilter(unittest.TestCase):
    """--format flag"""

    def test_format_escaped_only(self):
        r = run("2026-04-26 21:00:00", "-f", "escaped")
        self.assertEqual(r.returncode, 0)
        self.assertIn(r"\x69\xEE\x0C\x50", r.stdout)
        self.assertNotIn("[Timestamp]", r.stdout)

    def test_format_hex_only(self):
        r = run("2026-04-26 21:00:00", "-f", "hex")
        self.assertEqual(r.returncode, 0)
        self.assertIn("69EE0C50", r.stdout)
        self.assertNotIn("[Timestamp]", r.stdout)

    def test_format_time_only(self):
        r = run("69EE0C50", "-f", "time")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)
        self.assertNotIn("[Hex]", r.stdout)

    def test_format_timestamp_only(self):
        r = run("69EE0C50", "-f", "timestamp")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertNotIn("[Hex]", r.stdout)

    def test_format_bytes_only(self):
        r = run("69EE0C50", "-f", "bytes")
        self.assertEqual(r.returncode, 0)
        self.assertIn("[105, 238, 12, 80]", r.stdout)

    def test_format_java_only(self):
        r = run("69EE0C50", "-f", "java")
        self.assertEqual(r.returncode, 0)
        self.assertIn("[105, -18, 12, 80]", r.stdout)


class TestExtractMode(unittest.TestCase):
    """--extract flag"""

    def test_extract_escaped_sequences(self):
        r = run(r"prefix_\x69\xEE\x0C\x50_data_\x67\x89\xAB\xCD", "-e")
        self.assertEqual(r.returncode, 0)
        self.assertIn(r"\x69\xEE\x0C\x50", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)
        self.assertIn(r"\x67\x89\xAB\xCD", r.stdout)
        self.assertIn("2025-01-17 09:01:01 +0800", r.stdout)

    def test_extract_plain_hex(self):
        r = run("prefix_69EE0C50_data", "-e")
        self.assertEqual(r.returncode, 0)
        self.assertIn(r"\x69\xEE\x0C\x50", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)

    def test_extract_no_match(self):
        r = run("no timestamp here", "-e")
        self.assertEqual(r.returncode, 0)
        self.assertIn("未在输入中找到时间戳候选", r.stdout)


class TestBatchMode(unittest.TestCase):
    """--batch flag"""

    def test_batch_mixed_formats(self):
        r = run(
            "2026-04-26 21:00:00\n69EE0C50",
            "--batch", "--format", "all"
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("--- [1] (time) ---", r.stdout)
        self.assertIn("--- [2] (hex) ---", r.stdout)
        self.assertIn("1777208400", r.stdout)

    def test_batch_pipe_friendly(self):
        r = run(
            "2026-04-26 21:00:00\n69EE0C50",
            "--batch", "--format", "hex"
        )
        self.assertEqual(r.returncode, 0)
        lines = r.stdout.strip().split("\n")
        self.assertEqual(len(lines), 2)
        self.assertIn("69EE0C50", lines)

    def test_batch_blank_lines_skipped(self):
        r = run(
            "2026-04-26 21:00:00\n\n\n69EE0C50",
            "--batch", "--format", "hex"
        )
        self.assertEqual(r.returncode, 0)
        lines = r.stdout.strip().split("\n")
        self.assertEqual(len(lines), 2)

    def test_batch_error_continues(self):
        r = run(
            "2026-04-26 21:00:00\nnot_a_time_string\n69EE0C50",
            "--batch", "--format", "hex"
        )
        self.assertIn("Warning: line 2:", r.stderr)
        lines = r.stdout.strip().split("\n")
        self.assertEqual(len(lines), 2)

    def test_batch_all_fail_exit_code_one(self):
        r = run("not_a_time_string", "--batch", "--format", "hex")
        self.assertNotEqual(r.returncode, 0)

    def test_batch_partial_success_exit_code_zero(self):
        r = run(
            "2026-04-26 21:00:00\nbad_input",
            "--batch", "--format", "hex"
        )
        self.assertEqual(r.returncode, 0)

    def test_batch_with_extract(self):
        r = run(
            r"prefix_\x69\xEE\x0C\x50\nother_\x67\x89\xAB\xCD",
            "--batch", "--extract"
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)
        self.assertIn("2025-01-17 09:01:01 +0800", r.stdout)

    def test_batch_stdin(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "-", "--batch", "--format", "hex"],
            input="2026-04-26 21:00:00\n69EE0C50",
            capture_output=True, text=True
        )
        self.assertEqual(r.returncode, 0)
        lines = r.stdout.strip().split("\n")
        self.assertEqual(len(lines), 2)


class TestEdgeCases(unittest.TestCase):
    """Edge cases"""

    def test_empty_input_error(self):
        r = run("")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Error:", r.stderr)

    def test_java_output_signed_bytes(self):
        r = run("69EE0C50", "-f", "java")
        self.assertEqual(r.returncode, 0)
        self.assertIn("[105, -18, 12, 80]", r.stdout)


if __name__ == "__main__":
    unittest.main()
