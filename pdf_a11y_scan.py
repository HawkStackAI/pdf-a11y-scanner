#!/usr/bin/env python3
"""Check PDFs for the accessibility problems that lock readers out.

For each PDF this tool prints a short plain language report covering
two layers of checks:

1. A structural profile (pdf_profile.py, needs only pypdf): tagged
   structure, document language, title metadata and whether the
   viewer shows it, text layer versus image only pages, form field
   accessible names, and the PDF/UA identifier.
2. Full PDF/UA-1 validation through veraPDF (verapdf_check.py), when
   veraPDF is installed. Without veraPDF this layer is skipped and
   the report says so. A clean profile alone is triage, not proof of
   conformance.

Exit code: 0 when no check that ran found a failure, 1 when any did,
2 on a usage error.

Usage:
    python3 pdf_a11y_scan.py FILE.pdf [FILE2.pdf ...]
    python3 pdf_a11y_scan.py --json FILE.pdf
"""
import json
import sys

from pdf_profile import profile
import verapdf_check


def profile_findings(p):
    findings = []
    if not p["tagged"]:
        findings.append(
            "Not tagged. There is no structure tree, so screen readers "
            "get no reading order and headings, lists, and tables are "
            "not announced as what they are."
        )
    if not p["lang"]:
        findings.append(
            "No document language set. Screen readers may pronounce "
            "the text with the wrong language rules."
        )
    if not p["title_metadata"]:
        findings.append(
            "No title in the document metadata. Assistive technology "
            "and search results fall back to the file name."
        )
    elif not p["display_doc_title"]:
        findings.append(
            "The viewer is not set to display the document title, so "
            "the title bar shows the file name instead of the title."
        )
    if p["image_only_pages_likely"]:
        findings.append(
            "Pages look image only, with little or no extractable "
            "text. The content is invisible to screen readers and "
            "search until OCR and tagging are applied."
        )
    unnamed = p["form_fields"] - p["form_fields_with_accessible_name"]
    if unnamed > 0:
        findings.append(
            "%d of %d form fields have no accessible name, so a "
            "screen reader cannot say what the field is for."
            % (unnamed, p["form_fields"])
        )
    return findings


def scan(path, as_json):
    p = profile(path)
    findings = profile_findings(p)
    vera = None
    if verapdf_check.VERAPDF:
        vera = verapdf_check.check(path)
    failed = bool(findings) or (vera is not None and not vera["compliant"])
    if as_json:
        print(json.dumps({
            "file": path,
            "profile": p,
            "findings": findings,
            "verapdf": vera,
            "verapdf_skipped": vera is None,
            "result": "fail" if failed else "pass",
        }, indent=2))
        return failed
    print("=" * 70)
    print(path)
    print("Pages: %d" % p["pages"])
    if findings:
        print("Structural findings (%d):" % len(findings))
        for f in findings:
            print("  - " + f)
    else:
        print("Structural findings: none.")
    if vera is None:
        print("PDF/UA-1 validation: skipped (veraPDF not installed).")
        print("  A clean structural profile is triage only. Install")
        print("  veraPDF for a full PDF/UA-1 validation result.")
    elif vera["compliant"]:
        print("PDF/UA-1 validation (veraPDF): PASS, zero failed checks.")
    else:
        print("PDF/UA-1 validation (veraPDF): FAIL, %s failed checks."
              % vera["failed_checks_total"])
        for clause, count in sorted(vera["failed_clauses"].items()):
            print("  - Clause %s: %s failed checks" % (clause, count))
    print("Result: " + ("FAIL" if failed else "PASS"))
    return failed


def main(argv):
    as_json = "--json" in argv
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print(__doc__)
        return 2
    any_failed = False
    for path in files:
        if scan(path, as_json):
            any_failed = True
    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
