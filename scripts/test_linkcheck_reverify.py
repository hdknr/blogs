#!/usr/bin/env python3
"""Tests for linkcheck_reverify.

Run with `python3 scripts/test_linkcheck_reverify.py`. No test runner needed --
this ships alongside a CI workflow, so it stays dependency-free.

The case that matters most is a genuinely dead link (lychee tags those with a
bare status code, `[404]`, not a word) sharing a report with a link that merely
stalled. The first version of the parser matched `[A-Z]+` only, so every 404
was invisible: the dead link never reached the second pass, the stall cleared,
and the workflow opened no issue at all.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "linkcheck_reverify.py"

FIRST_PASS = """Issues found in 2 inputs. Find details below.

[_site/blogs/posts/2020/01/alpha/index.html]:
[404] https://example.com/removed-page (at 12:340) | Rejected status code: 404 Not Found
[TIMEOUT] https://example.com/slow-host (at 12:900) | Request timed out

[_site/blogs/posts/2020/02/beta/index.html]:
[410] https://example.com/gone-page (at 8:100) | Rejected status code: 410 Gone
[ERROR] https://example.com/bad-cert (at 9:120) | SSL certificate expired

\U0001f50d 100 Total (in 5m 0s 0ms) \U0001f517 50 Unique ✅ 46 OK \U0001f6ab 3 Errors ⏳ 1 Timeouts
"""

# The second pass only still-fails for the genuinely dead ones; the stall cleared.
SECOND_PASS = """Issues found in 1 input. Find details below.

[retry-urls.txt]:
[404] https://example.com/removed-page (at 1:1) | Rejected status code: 404 Not Found
[410] https://example.com/gone-page (at 3:1) | Rejected status code: 410 Gone
[ERROR] https://example.com/bad-cert (at 4:1) | SSL certificate expired

\U0001f50d 4 Total (in 30s) \U0001f517 4 Unique ✅ 1 OK \U0001f6ab 3 Errors
"""

ALL_CLEARED = """\U0001f50d 4 Total (in 30s) \U0001f517 4 Unique ✅ 4 OK \U0001f6ab 0 Errors
"""

failures = []


def check(label, actual, expected):
    if actual == expected:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}: expected {expected!r}, got {actual!r}")
        failures.append(label)


def run(*args):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True
    )
    return proc.returncode, proc.stdout


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        first = d / "report.md"
        first.write_text(FIRST_PASS, encoding="utf-8")

        print("extract picks up status-code tags as well as word tags")
        urls = d / "urls.txt"
        code, _ = run("extract", str(first), str(urls))
        check("exit code", code, 0)
        extracted = urls.read_text(encoding="utf-8").split()
        check("url count", len(extracted), 4)
        check(
            "the 404 is extracted",
            "https://example.com/removed-page" in extracted,
            True,
        )
        check("the 410 is extracted", "https://example.com/gone-page" in extracted, True)

        print("filter keeps links that failed twice and drops the stall")
        second = d / "retry.md"
        second.write_text(SECOND_PASS, encoding="utf-8")
        out = d / "confirmed.md"
        code, stdout = run("filter", str(first), str(second), str(out))
        check("exit code signals 'open an issue'", code, 1)
        check("counts", "3 confirmed, 1 cleared as transient" in stdout, True)
        body = out.read_text(encoding="utf-8")
        check("the 404 survives", "https://example.com/removed-page" in body, True)
        check("the 410 survives", "https://example.com/gone-page" in body, True)
        check("the stall is dropped", "slow-host" not in body, True)
        check(
            "source posts are preserved",
            "posts/2020/01/alpha" in body and "posts/2020/02/beta" in body,
            True,
        )

        print("filter opens nothing when the second pass clears everything")
        cleared = d / "cleared.md"
        cleared.write_text(ALL_CLEARED, encoding="utf-8")
        out2 = d / "confirmed2.md"
        code, _ = run("filter", str(first), str(cleared), str(out2))
        check("exit code signals 'no issue'", code, 0)
        check("report is empty", out2.read_text(encoding="utf-8"), "")

        print("filter falls back to the raw report when it cannot be parsed")
        junk = d / "junk.md"
        junk.write_text("lychee exploded before checking anything\n", encoding="utf-8")
        out3 = d / "confirmed3.md"
        code, _ = run("filter", str(junk), str(second), str(out3))
        check("exit code signals 'open an issue'", code, 1)
        check("raw report passed through", "exploded" in out3.read_text(encoding="utf-8"), True)

        print("filter falls back when the second pass never ran")
        out4 = d / "confirmed4.md"
        code, _ = run("filter", str(first), str(d / "missing.md"), str(out4))
        check("exit code signals 'open an issue'", code, 1)
        check(
            "raw report passed through",
            "removed-page" in out4.read_text(encoding="utf-8"),
            True,
        )

    if failures:
        print(f"\n{len(failures)} check(s) failed")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
