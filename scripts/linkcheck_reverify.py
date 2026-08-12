#!/usr/bin/env python3
"""Turn a raw lychee sweep report into one worth opening an issue about.

The weekly sweep runs on a shared GitHub Actions runner, and when that runner's
network is congested the report fills up with links that are perfectly alive.
Measured across sweeps, the stall count tracks the wall clock, not the health of
the web:

    #543 11m31s / 87    #561 11m59s / 87    #574 7m19s / 19
    #607  6m07s /  9    #632 15m10s / 112

Re-running #632's exact 107 reported URLs through the same lychee and config
from an ordinary network produced 0 timeouts.

Retrying does not fix this. A run on this branch stalled for 22 minutes and a
second pass over the same URLs, on the same runner, confirmed 102 of 103 — the
congestion outlasted both passes. What that run did show is which signals
survive congestion:

    100 [TIMEOUT]  all alive, all noise
      1 [ERROR]    monotalk.xyz, certificate genuinely expired
      1 [ERROR]    "Error (cached)", echoing a timeout of the same URL

A 404 or an expired certificate is a server's answer, and a congested runner
does not invent one. Only stalls are artifacts. So the report is split by that
line: hard failures are always trustworthy and always reported, while stalls are
reported only when the run as a whole looks healthy, and re-checked even then.
When too many links stall at once the run is treated as degraded and the stalls
are dropped with a note — a host that is genuinely gone still fails next week,
and the repo already only excludes hosts reported by three consecutive sweeps.

Subcommands:
  plan   <report> <urls-out> <state-out>            what to re-check, and why
  report <report> <retry> <state> <out>             the issue body

`report` exits 0 when there is nothing to open an issue about and 1 when there
is, so the workflow can branch on it.
"""

import json
import re
import sys
from pathlib import Path

# Above this many stalls in one sweep, the runner -- not the web -- is the most
# likely explanation. Healthy sweeps have produced 0-19; degraded ones 87-112.
STALL_LIMIT = 30

# Entry lines look like:
#   [TIMEOUT] http://example.com/a (at 73:1700) | Request timed out
#   [404] http://example.com/b (at 12:340) | Rejected status code: 404 Not Found
# The tag is either a word or a bare status code, so it must accept digits: an
# [A-Z]-only pattern silently drops every 404/410, which is exactly the class of
# genuinely dead link this job exists to catch.
ENTRY = re.compile(r"^\[([A-Z0-9]+)\]\s+(\S+)\s+\(at\s+[^)]+\)\s*\|\s*(.*)$")
# Input-file headers look like:
#   [_site/blogs/posts/2015/02/xxxx/index.html]:
SOURCE = re.compile(r"^\[(.+)\]:$")
# lychee's trailing one-line summary, e.g. "🔍 117395 Total (in 15m 10s ...)".
SUMMARY = re.compile(r"Total \(in ")

UNATTRIBUTED = "(unattributed)"


def parse(path: Path):
    """Yield (source, kind, url, reason) for each entry in a lychee report."""
    source = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        m = SOURCE.match(line)
        if m:
            source = m.group(1)
            continue
        m = ENTRY.match(line)
        if m:
            kind, url, reason = m.groups()
            yield source or UNATTRIBUTED, kind, url, reason


def summary_line(path: Path) -> str:
    for raw in path.read_text(encoding="utf-8").splitlines():
        if SUMMARY.search(raw):
            return raw.strip()
    return ""


def is_stall(kind: str, reason: str, stalled_urls: set, url: str) -> bool:
    """Is this entry an artifact of the request never completing?

    TIMEOUT is the obvious case. "Error (cached)" is lychee reusing an earlier
    verdict for a URL it already checked, so it inherits whatever that verdict
    was -- a stall if the same URL stalled elsewhere in the report, a real
    failure otherwise.
    """
    if kind == "TIMEOUT":
        return True
    if reason.strip().lower().startswith("error (cached)"):
        return url in stalled_urls
    return False


def split(entries):
    """Split entries into (stalls, hard failures)."""
    stalled_urls = {url for _, kind, url, _ in entries if kind == "TIMEOUT"}
    stalls, hard = [], []
    for source, kind, url, reason in entries:
        target = stalls if is_stall(kind, reason, stalled_urls, url) else hard
        target.append((source, kind, url, reason))
    return stalls, hard


def cmd_plan(report: Path, urls_out: Path, state_out: Path) -> int:
    entries = list(parse(report))
    stalls, hard = split(entries)
    degraded = len(stalls) > STALL_LIMIT

    # On a degraded run there is no point paying for a second pass over the
    # stalls: the congestion that produced them is still there. Re-check the
    # hard failures only, which is fast and still catches a cached artifact or
    # a one-off blip.
    recheck = hard if degraded else entries
    urls = []
    for _, _, url, _ in recheck:
        if url not in urls:
            urls.append(url)

    urls_out.write_text("".join(u + "\n" for u in urls), encoding="utf-8")
    state_out.write_text(
        json.dumps(
            {
                "degraded": degraded,
                "stalls": len(stalls),
                "hard": len(hard),
                "limit": STALL_LIMIT,
            }
        ),
        encoding="utf-8",
    )

    print(f"first pass: {len(entries)} entries ({len(stalls)} stalls, {len(hard)} hard)")
    if degraded:
        print(f"run looks degraded (>{STALL_LIMIT} stalls); re-checking hard failures only")
    print(f"re-checking {len(urls)} URLs")
    return 0


def cmd_report(report: Path, retry: Path, state_path: Path, out: Path) -> int:
    entries = list(parse(report))
    if not entries:
        # Nothing parseable: the first pass failed for some reason other than a
        # dead link (lychee crash, bad config). Keep the raw report so the
        # failure is still surfaced rather than silently swallowed.
        out.write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
        print("could not parse the first-pass report; passing it through as-is")
        return 1

    if not retry.exists():
        # lychee writes its --output file even when every link passes, so a
        # missing one means the second pass never ran. Without a verdict, fall
        # back to reporting the first pass rather than clearing it.
        out.write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"{retry} is missing; the second pass did not run")
        return 1

    state = json.loads(state_path.read_text(encoding="utf-8"))
    degraded = state["degraded"]
    stalls, hard = split(entries)
    still_failing = {url for _, _, url, _ in parse(retry)}

    kept_hard = [e for e in hard if e[2] in still_failing]
    kept_stalls = [] if degraded else [e for e in stalls if e[2] in still_failing]
    kept = kept_hard + kept_stalls
    cleared = (len(hard) - len(kept_hard)) + (0 if degraded else len(stalls) - len(kept_stalls))

    print(f"hard failures: {len(kept_hard)} of {len(hard)} confirmed")
    if degraded:
        print(f"stalls: {len(stalls)} suppressed (run degraded)")
    else:
        print(f"stalls: {len(kept_stalls)} of {len(stalls)} confirmed")
    print(f"opening an issue about {len(kept)} of {len(entries)} entries")

    if not kept:
        out.write_text("", encoding="utf-8")
        return 0

    if degraded:
        head = (
            f"{len(kept)} link(s) failed for a reason a busy runner cannot "
            f"invent (404, expired certificate, refused connection) and failed "
            f"again on re-check.\n\n"
            f"This sweep also stalled on {len(stalls)} link(s). That is above the "
            f"{state['limit']} that separates a healthy sweep from a congested "
            f"one, so those are almost certainly the runner rather than the web "
            f"and have been left out. They will be reported next week if they "
            f"are real."
        )
    else:
        head = (
            f"Confirmed by two passes: {len(kept)} of {len(entries)} reported "
            f"link(s) failed again on re-check "
            f"({cleared} cleared as transient)."
        )

    by_source = {}
    for source, kind, url, reason in kept:
        by_source.setdefault(source, []).append((kind, url, reason))

    lines = [head, ""]
    for source in sorted(by_source):
        lines.append(f"[{source}]:")
        for kind, url, reason in by_source[source]:
            lines.append(f"[{kind}] {url} | {reason}")
        lines.append("")

    first = summary_line(report)
    if first:
        lines.append(f"First pass: {first}")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 1


def main() -> int:
    args = sys.argv[1:]
    if len(args) == 4 and args[0] == "plan":
        return cmd_plan(Path(args[1]), Path(args[2]), Path(args[3]))
    if len(args) == 5 and args[0] == "report":
        return cmd_report(Path(args[1]), Path(args[2]), Path(args[3]), Path(args[4]))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
