#!/usr/bin/env python3
"""Test cases for time-convert — validates forward and reverse conversion scenarios."""

import subprocess
import sys

SCRIPT = './time-convert'
PASS = 0
FAIL = 0


def run(args: str) -> str:
    """Run time-convert with given arguments and return stdout."""
    cmd = f'python3 {SCRIPT} {args}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def check(name: str, args: str, expected_lines: list[str]):
    """Assert that output contains all expected lines."""
    global PASS, FAIL
    output = run(args)
    missing = [line for line in expected_lines if line not in output]
    if missing:
        print(f'FAIL  [{name}]')
        for m in missing:
            print(f'      预期包含: {m}')
        print(f'      实际输出:\n{output}')
        FAIL += 1
    else:
        print(f'PASS  [{name}]')
        PASS += 1


# ---------- forward conversion ----------

def test_forward_basic():
    check(
        '正向: 时间字符串 → 全格式',
        "'2026-04-26 21:00:00'",
        [
            '[Timestamp]     1777208400',
            '[Hex]     69EE0C50',
            '[Escaped]     \\x69\\xEE\\x0C\\x50',
            '[Bytes]     [105, 238, 12, 80]',
            '[Time]     2026-04-26 21:00:00 +0800',
        ],
    )


def test_forward_iso():
    check(
        '正向: ISO 8601 带时区偏移',
        "'2026-04-26T21:00:00+08:00'",
        [
            '[Timestamp]     1777208400',
            '[Hex]     69EE0C50',
        ],
    )


def test_forward_date_only():
    check(
        '正向: 仅日期',
        "'2026-04-26'",
        [
            '[Timestamp]     1777132800',
            '[Time]     2026-04-26 00:00:00 +0800',
        ],
    )


# ---------- reverse conversion ----------

def test_reverse_hex():
    check(
        '反向: Hex → 时间',
        "'69EE0C50'",
        [
            '[Timestamp]     1777208400',
            '[Time]     2026-04-26 21:00:00 +0800',
        ],
    )


def test_reverse_escaped():
    check(
        '反向: Escaped → 时间',
        r"'\x69\xEE\x0C\x50'",
        [
            '[Timestamp]     1777208400',
            '[Time]     2026-04-26 21:00:00 +0800',
        ],
    )


def test_reverse_bytes():
    check(
        '反向: Bytes 数组 → 时间',
        "'[105, 238, 12, 80]'",
        [
            '[Timestamp]     1777208400',
            '[Time]     2026-04-26 21:00:00 +0800',
        ],
    )


def test_reverse_timestamp():
    check(
        '反向: 时间戳 → 时间',
        "'1777208400'",
        [
            '[Timestamp]     1777208400',
            '[Time]     2026-04-26 21:00:00 +0800',
        ],
    )


# ---------- timezone ----------

def test_timezone_utc1():
    check(
        '时区: UTC+1',
        "'2026-04-26 14:00:00' --tz UTC+1",
        [
            '[Time]     2026-04-26 14:00:00 +0100',
        ],
    )


def test_timezone_utc0():
    check(
        '时区: UTC+0',
        "'2026-04-26 13:00:00' --tz UTC+0",
        [
            '[Time]     2026-04-26 13:00:00 +0000',
        ],
    )


def test_timezone_iana():
    check(
        '时区: America/New_York',
        "'2026-04-26 09:00:00' --tz America/New_York",
        [
            '[Time]     2026-04-26 09:00:00 -0400',
        ],
    )


# ---------- format filter ----------

def test_format_filter():
    check(
        '格式筛选: -f escaped',
        "'2026-04-26 21:00:00' -f escaped",
        [
            '\\x69\\xEE\\x0C\\x50',
        ],
    )


def test_format_hex_only():
    check(
        '格式筛选: -f hex',
        "'2026-04-26 21:00:00' -f hex",
        [
            '[Hex]     69EE0C50',
        ],
    )


def test_format_time_only():
    check(
        '格式筛选: -f time',
        "'69EE0C50' -f time",
        [
            '[Time]     2026-04-26 21:00:00 +0800',
        ],
    )


# ---------- extract ----------

def test_extract_escaped():
    check(
        '提取: 混合文本中的 \\xHH 序列',
        r"'prefix_\x69\xEE\x0C\x50_data_\x67\x89\xAB\xCD' -e",
        [
            r'\x69\xEE\x0C\x50',
            '2026-04-26 21:00:00 +0800',
            r'\x67\x89\xAB\xCD',
            '2025-01-17 09:01:01 +0800',
        ],
    )


def test_extract_plain_hex():
    check(
        '提取: 混合文本中的纯 hex 序列',
        "'prefix_69EE0C50_data' -e",
        [
            r'\x69\xEE\x0C\x50',
            '2026-04-26 21:00:00 +0800',
        ],
    )


# ---------- edge cases ----------

def test_slash_format():
    check(
        '格式: yyyy/MM/dd',
        "'2026/04/26 21:00:00'",
        [
            '[Timestamp]     1777208400',
        ],
    )


def test_compact_format():
    check(
        '格式: yyyyMMddHHmmss',
        "'20260426210000'",
        [
            '[Timestamp]     1777208400',
        ],
    )


def test_hex_lowercase():
    check(
        '格式: 小写 hex 输入',
        "'69ee0c50'",
        [
            '[Timestamp]     1777208400',
        ],
    )


# ---------- runner ----------

if __name__ == '__main__':
    test_forward_basic()
    test_forward_iso()
    test_forward_date_only()
    test_reverse_hex()
    test_reverse_escaped()
    test_reverse_bytes()
    test_reverse_timestamp()
    test_timezone_utc1()
    test_timezone_utc0()
    test_timezone_iana()
    test_format_filter()
    test_format_hex_only()
    test_format_time_only()
    test_extract_escaped()
    test_extract_plain_hex()
    test_slash_format()
    test_compact_format()
    test_hex_lowercase()

    total = PASS + FAIL
    print(f'\n{"="*40}')
    print(f'结果: {PASS}/{total} 通过')
    if FAIL > 0:
        print(f'       {FAIL} 失败')
        sys.exit(1)
    else:
        print('       全部通过')
