#!/usr/bin/env python3
"""Extract (( ... )) placeholders from a markdown/MDX document.

Why this exists: when a document has several diagram placeholders scattered
across long prose, it's easy to miss one or to lose track of which heading each
belongs under. This script lists every placeholder with its line range and the
nearest preceding heading, so the authoring pass can address each one
deliberately and verify none were left behind.

Usage:
    python3 find_placeholders.py <path-to-md-or-mdx>

Output: one block per placeholder (JSON list on stdout), e.g.
    [
      {
        "index": 1,
        "start_line": 23,
        "end_line": 23,
        "heading": "# 2. 모델 폭발적 증가",
        "text": "before -> after 를 보여주는 각각의 도메인 모델 설계도"
      },
      ...
    ]
"""
import json
import re
import sys


def find_placeholders(text):
    lines = text.splitlines()

    # Track the nearest preceding markdown heading for each character offset.
    # Build a list of (line_index, heading_text).
    heading_re = re.compile(r"^\s{0,3}(#{1,6})\s+(.*\S)\s*$")
    headings = []  # (line_no_1based, full_heading_line)
    for i, line in enumerate(lines):
        if heading_re.match(line):
            headings.append((i + 1, line.strip()))

    def heading_for(line_no):
        current = None
        for ln, h in headings:
            if ln <= line_no:
                current = h
            else:
                break
        return current

    # Match (( ... )) spans, possibly multi-line. Non-greedy, DOTALL so a
    # placeholder can wrap several lines (e.g. a 성과/한계 block).
    #
    # The negative lookbehind (?<![\w.]) keeps us from matching code: a human
    # writes a placeholder after whitespace/newline (`... ((설계도))`), whereas
    # JS double-parens always follow an identifier or dot — `.map((o) => ...)`,
    # `fn((x))`. Without this, re-running on an already-enriched file would flag
    # the inserted React components' own `.map((...))` as leftover placeholders.
    span_re = re.compile(r"(?<![\w.])\(\((.*?)\)\)", re.DOTALL)

    results = []
    for m in span_re.finditer(text):
        inner = m.group(1).strip()
        # Belt-and-suspenders: real placeholders are prose, never arrow funcs.
        if "=>" in inner:
            continue
        start_line = text.count("\n", 0, m.start()) + 1
        end_line = text.count("\n", 0, m.end()) + 1
        results.append(
            {
                "index": len(results) + 1,
                "start_line": start_line,
                "end_line": end_line,
                "heading": heading_for(start_line),
                "text": inner,
            }
        )
    return results


def main():
    if len(sys.argv) != 2:
        print("usage: find_placeholders.py <path-to-md-or-mdx>", file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    results = find_placeholders(text)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n# {len(results)} placeholder(s) found", file=sys.stderr)


if __name__ == "__main__":
    main()
