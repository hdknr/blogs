#!/usr/bin/env python3
"""Second-pass filter for the weekly lychee sweep.

The sweep runs on a shared GitHub Actions runner, so a congested run turns
transient stalls into a report full of links that are perfectly alive. #632 ran
for 15m and reported 112 timeouts; the week before it ran 6m and reported 9, on
a link set that had grown 4%. Re-running the exact 107 reported URLs through the
same lychee version and config from an ordinary network produced 0 timeouts.

So the report is only trustworthy after a second look: re-check the URLs the
first pass complained about, serially and with a longer timeout, and keep only
the ones that fail twice. A 404 fails both passes; a stall from a busy runner
does not.

Subcommands:
  extract <report> <urls-out>            first-pass report -> unique URL list
  filter  <report> <retry-report> <out>  keep only entries that failed twice

`filter` exits 0 when nothing survives (no issue should be opened) and 1 when
the rewritten report still has entries.
"""

import re
import sys
from pathlib import Path

# Entry lines look like:
#   [TIMEOUT] http://example.com/a (at 73:1700) | Request timed out
#   [404] http://example.com/b (at 12:340) | Rejected status code: 404 Not Found
# The tag is either a word or a bare status code, so it must accept digits: an
# [A-Z]-only pattern silently drops every 404/410, which is exactly the class of
# genuinely dead link this job exists to catch. #632 happened to contain only
# TIMEOUT/ERROR, but #607 the week before carried four 404s and four 302s.
ENTRY = re.compile(r"^\[([A-Z0-9]+)\]\s+(\S+)\s+\(at\s+[^)]+\)\s*\|\s*(.*)$")
# Input-file headers look like:
#   [_site/blogs/posts/2015/02/xxxx/index.html]:
SOURCE = re.compile(r"^\[(.+)\]:$")
# lychee's trailing one-line summary, e.g. "🔍 117395 Total (in 15m 10s ...)".
SUMMARY = re.compile(r"Total \(in ")


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
            yield source, kind, url, reason


def summary_line(path: Path) -> str:
    for raw in path.read_text(encoding="utf-8").splitlines():
        if SUMMARY.search(raw):
            return raw.strip()
    return ""


def cmd_extract(report: Path, out: Path) -> int:
    urls = []
    for _, _, url, _ in parse(report):
        if url not in urls:
            urls.append(url)
    out.write_text("".join(u + "\n" for u in urls), encoding="utf-8")
    print(f"first pass reported {len(urls)} unique URLs")
    return 0


def cmd_filter(report: Path, retry: Path, out: Path) -> int:
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

    still_failing = {url for _, _, url, _ in parse(retry)}
    kept = [e for e in entries if e[2] in still_failing]
    cleared = len(entries) - len(kept)

    print(f"first pass: {len(entries)} entries")
    print(f"second pass: {len(kept)} confirmed, {cleared} cleared as transient")

    if not kept:
        out.write_text("", encoding="utf-8")
        return 0

    # An entry can precede the first `[path]:` header, leaving source unset.
    # Give it a name rather than letting a None sort against the strings and
    # crash the whole step.
    by_source = {}
    for source, kind, url, reason in kept:
        by_source.setdefault(source or "(unattributed)", []).append((kind, url, reason))

    lines = [
        f"Confirmed by two passes: {len(kept)} of {len(entries)} reported links "
        f"failed again when re-checked with a longer timeout "
        f"({cleared} cleared as transient).",
        "",
    ]
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
    if len(args) == 3 and args[0] == "extract":
        return cmd_extract(Path(args[1]), Path(args[2]))
    if len(args) == 4 and args[0] == "filter":
        return cmd_filter(Path(args[1]), Path(args[2]), Path(args[3]))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
