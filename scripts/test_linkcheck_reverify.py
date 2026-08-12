#!/usr/bin/env python3
"""Tests for linkcheck_reverify.

Run with `python3 scripts/test_linkcheck_reverify.py`. No test runner needed --
this ships alongside a CI workflow, so it stays dependency-free.

Two cases carry most of the weight:

- A genuinely dead link is tagged with a bare status code, `[404]`, not a word.
  An `[A-Z]+` pattern misses those, and because a stall in the same report still
  parsed, the filter used to report "nothing confirmed" and open no issue at
  all -- silently losing the exact links this job exists to find.
- A congested runner stalls on a hundred live links at once. Those must be
  suppressed, but any 404 or expired certificate in the same report must still
  be reported: a busy runner cannot invent a server's answer.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "linkcheck_reverify.py"

HEALTHY = """Issues found in 2 inputs. Find details below.

[_site/blogs/posts/2020/01/alpha/index.html]:
[404] https://example.com/removed-page (at 12:340) | Rejected status code: 404 Not Found
[TIMEOUT] https://example.com/slow-host (at 12:900) | Request timed out

[_site/blogs/posts/2020/02/beta/index.html]:
[410] https://example.com/gone-page (at 8:100) | Rejected status code: 410 Gone
[ERROR] https://example.com/bad-cert (at 9:120) | SSL certificate expired

\U0001f50d 100 Total (in 5m 0s 0ms) \U0001f517 50 Unique ✅ 46 OK \U0001f6ab 3 Errors ⏳ 1 Timeouts
"""

# The dead links still fail on re-check; the stall cleared.
HEALTHY_RETRY = """Issues found in 1 input. Find details below.

[retry-urls.txt]:
[404] https://example.com/removed-page (at 1:1) | Rejected status code: 404 Not Found
[410] https://example.com/gone-page (at 3:1) | Rejected status code: 410 Gone
[ERROR] https://example.com/bad-cert (at 4:1) | SSL certificate expired

\U0001f50d 4 Total (in 30s) \U0001f517 4 Unique ✅ 1 OK \U0001f6ab 3 Errors
"""

ALL_CLEARED = "\U0001f50d 4 Total (in 30s) \U0001f517 4 Unique ✅ 4 OK \U0001f6ab 0 Errors\n"


def degraded_report(stalls=40):
    """A report dominated by stalls, with one real death mixed in."""
    lines = ["Issues found in 1 input. Find details below.", ""]
    lines.append("[_site/blogs/posts/2020/01/alpha/index.html]:")
    for i in range(stalls):
        lines.append(
            f"[TIMEOUT] https://stalled-{i}.example.com/page (at {i}:1) | Request timed out"
        )
    # lychee reuses an earlier verdict for a URL it already saw. This one echoes
    # a stall, so it is a stall too -- not a hard failure.
    lines.append(
        "[ERROR] https://stalled-0.example.com/page (at 900:1) | Error (cached)"
    )
    lines.append("[ERROR] https://example.com/bad-cert (at 901:1) | SSL certificate expired")
    lines.append("")
    lines.append("\U0001f50d 100 Total (in 20m 0s 0ms) \U0001f517 50 Unique ✅ 9 OK")
    return "\n".join(lines) + "\n"


DEGRADED_RETRY = """Issues found in 1 input. Find details below.

[retry-urls.txt]:
[ERROR] https://example.com/bad-cert (at 1:1) | SSL certificate expired

\U0001f50d 1 Total (in 2s) \U0001f517 1 Unique ✅ 0 OK \U0001f6ab 1 Errors
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
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)

        healthy = d / "healthy.md"
        healthy.write_text(HEALTHY, encoding="utf-8")
        retry = d / "retry.md"
        retry.write_text(HEALTHY_RETRY, encoding="utf-8")

        print("plan re-checks everything when the run looks healthy")
        urls, state = d / "urls.txt", d / "state.json"
        code, _ = run("plan", str(healthy), str(urls), str(state))
        check("exit code", code, 0)
        listed = urls.read_text(encoding="utf-8").split()
        check("url count", len(listed), 4)
        check("the 404 is re-checked", "https://example.com/removed-page" in listed, True)
        check("the 410 is re-checked", "https://example.com/gone-page" in listed, True)
        check("not flagged degraded", json.loads(state.read_text())["degraded"], False)

        print("report keeps what failed twice and drops the stall")
        out = d / "confirmed.md"
        code, stdout = run("report", str(healthy), str(retry), str(state), str(out))
        check("exit code signals 'open an issue'", code, 1)
        check("counts", "opening an issue about 3 of 4 entries" in stdout, True)
        body = out.read_text(encoding="utf-8")
        check("the 404 survives", "removed-page" in body, True)
        check("the 410 survives", "gone-page" in body, True)
        check("the stall is dropped", "slow-host" not in body, True)
        check(
            "source posts are preserved",
            "posts/2020/01/alpha" in body and "posts/2020/02/beta" in body,
            True,
        )

        print("report opens nothing when the second pass clears everything")
        cleared = d / "cleared.md"
        cleared.write_text(ALL_CLEARED, encoding="utf-8")
        out2 = d / "confirmed2.md"
        code, _ = run("report", str(healthy), str(cleared), str(state), str(out2))
        check("exit code signals 'no issue'", code, 0)
        check("report is empty", out2.read_text(encoding="utf-8"), "")

        print("a congested run suppresses stalls but keeps the real death")
        deg = d / "degraded.md"
        deg.write_text(degraded_report(), encoding="utf-8")
        durls, dstate = d / "durls.txt", d / "dstate.json"
        code, stdout = run("plan", str(deg), str(durls), str(dstate))
        check("exit code", code, 0)
        check("flagged degraded", json.loads(dstate.read_text())["degraded"], True)
        dlisted = durls.read_text(encoding="utf-8").split()
        check("only the hard failure is re-checked", dlisted, ["https://example.com/bad-cert"])
        check(
            "the cached echo counts as a stall",
            json.loads(dstate.read_text())["stalls"],
            41,
        )

        dretry = d / "dretry.md"
        dretry.write_text(DEGRADED_RETRY, encoding="utf-8")
        out3 = d / "confirmed3.md"
        code, stdout = run("report", str(deg), str(dretry), str(dstate), str(out3))
        check("exit code signals 'open an issue'", code, 1)
        check("stalls suppressed", "41 suppressed" in stdout, True)
        body3 = out3.read_text(encoding="utf-8")
        check("the real death is reported", "bad-cert" in body3, True)
        check("no stall leaks into the issue", "stalled-" not in body3, True)
        check("the suppression is explained", "stalled on 41 link(s)" in body3, True)

        print("report falls back to the raw report when it cannot be parsed")
        junk = d / "junk.md"
        junk.write_text("lychee exploded before checking anything\n", encoding="utf-8")
        out4 = d / "confirmed4.md"
        code, _ = run("report", str(junk), str(retry), str(state), str(out4))
        check("exit code signals 'open an issue'", code, 1)
        check("raw report passed through", "exploded" in out4.read_text(encoding="utf-8"), True)

        print("report falls back when the second pass never ran")
        out5 = d / "confirmed5.md"
        code, _ = run("report", str(healthy), str(d / "missing.md"), str(state), str(out5))
        check("exit code signals 'open an issue'", code, 1)
        check(
            "raw report passed through",
            "removed-page" in out5.read_text(encoding="utf-8"),
            True,
        )

        # An entry before the first `[path]:` header has no source. Sorting a
        # None against the other sources used to raise TypeError, which the
        # workflow could only read as "the filter exited 1" -- the same signal
        # as a real report, so it would try to open an issue from a file that
        # was never written.
        print("report handles an entry with no source header")
        headerless = d / "headerless.md"
        headerless.write_text(
            "[404] https://example.com/orphan (at 1:1) | Rejected status code: 404\n"
            "\n"
            "[_site/blogs/posts/2020/01/alpha/index.html]:\n"
            "[404] https://example.com/removed-page (at 12:340) | Rejected status code: 404\n",
            encoding="utf-8",
        )
        hurls, hstate = d / "hurls.txt", d / "hstate.json"
        run("plan", str(headerless), str(hurls), str(hstate))
        hretry = d / "hretry.md"
        hretry.write_text(
            "[retry-urls.txt]:\n"
            "[404] https://example.com/orphan (at 1:1) | Rejected status code: 404\n"
            "[404] https://example.com/removed-page (at 2:1) | Rejected status code: 404\n",
            encoding="utf-8",
        )
        out6 = d / "confirmed6.md"
        code, _ = run("report", str(headerless), str(hretry), str(hstate), str(out6))
        check("exit code signals 'open an issue'", code, 1)
        body6 = out6.read_text(encoding="utf-8")
        check("the attributed link survives", "removed-page" in body6, True)
        check("the orphan is labelled", "(unattributed)" in body6, True)

    if failures:
        print(f"\n{len(failures)} check(s) failed")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
