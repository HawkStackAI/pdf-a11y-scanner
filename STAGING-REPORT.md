# Staging Report: Public PDF Accessibility Scanner

Prepared 2026-11-20 under the public layer plan approved 2026-11-10
and the publish approval given 2026-11-20. This folder is staging
only. No repository has been created and nothing has been pushed.

## Source of the scanner

The scanner comes from the internal accessibility tooling at
~/workspace/gov-contracting/accessibility/tools/, which supports
the gov-a11y-scan skill. Internally that folder holds two halves:

1. A PDF checker: pdf_profile.py (structural profile, pypdf only)
   and verapdf_check.py (veraPDF PDF/UA-1 validation wrapper).
2. Web page prospect scanning: axe-core runners (run_axe.mjs,
   run_axe_slow.mjs, scan_pages.py) used to scan government
   prospect websites for outreach.

The public version is the PDF checker half only, which matches the
approved plan: a free tool a prime contractor or agency can run on
its own PDFs to see whether they pass accessibility checks.

Honest note on what exists: internally this is a skill description
plus a tools folder, not a packaged product. The two Python modules
are genuinely runnable and are in daily internal use, and they are
what is staged here. A thin command line wrapper
(pdf_a11y_scan.py) was written for the public version so an outside
user gets one command and a plain language report instead of raw
JSON from two separate scripts.

## What the public version includes

- pdf_profile.py, copied verbatim from the internal original. It
  separated cleanly: no internal paths, no configuration, pypdf is
  its only dependency.
- verapdf_check.py, adapted in exactly one place: how the veraPDF
  program is located. The internal version resolved a vendored
  runtime folder and fell back to an install path inside an
  internal benchmark directory. The public version resolves the
  VERAPDF_BIN environment variable, then a `verapdf` launcher on
  PATH, and fails with a clear install message otherwise. The
  validation call and the report parsing are unchanged.
- pdf_a11y_scan.py, new thin wrapper: runs the profile, turns the
  facts into plain language findings, runs veraPDF when present,
  prints a per file report, supports a --json mode, and returns
  exit code 0 or 1 for use in scripts and build pipelines.
- requirements.txt (pypdf only).
- README.md for document owners and web teams, including one short
  paragraph noting HawkStack offers remediation as a service. No
  prices appear anywhere.
- LICENSE (MIT).

## What it excludes, deliberately

- The production remediation pipeline. None of its code is in this
  folder. The scanner only checks; it fixes nothing.
- The web page prospect scanning half (axe runners and page
  scanner), the outreach playbook, snapshot reports, and every
  prospect or client name connected with them.
- The vendored runtime (a Java runtime and a veraPDF install,
  roughly 500 MB of third party binaries). Public users install
  veraPDF themselves; the README explains how.
- All internal paths, bid references, pricing, and opportunity
  material. None was present in the two source modules except the
  one internal fallback path in verapdf_check.py, removed as
  described above.

## Scrub results

Every staged text file was scanned for: credential and token
patterns (key and token keywords, AWS and GitHub token shapes,
private key headers), personal identifiers (names, email
addresses), internal absolute paths, the day job employer name,
RELTO and RELTOLock mentions, pricing figures, and bid portal
references. Result: zero hits across all staged files. A first
scan flagged compiled Python cache files created by the run test
inside the staging folder (they embed source paths); the cache
folder was deleted and the rescan is clean. Em dash and en dash
scan: none present.

Rule 1 check: nothing in the staged files connects RELTO or
HawkStack to the day job employer; the employer is never named.
The only organization named is HawkStack AI LLC (LICENSE and one
README paragraph), plus the public website hawkstackllc.com.

## Run test

Tested 2026-11-20 with Python 3.12 and pypdf 7.0.1, using
synthetic QA harness documents and one HawkStack document. No
client documents were used.

- qa-harness/inputs/access.pdf (synthetic untagged document):
  3 structural findings, veraPDF FAIL with 43 failed checks,
  exit code 1. The 43 count matches the recorded internal QA
  harness baseline for this same file, which cross-checks the
  public build against the internal one.
- qa-harness/inputs/form.pdf (synthetic form): 4 structural
  findings including 8 of 8 form fields with no accessible name,
  veraPDF FAIL with 42 failed checks, exit code 1.
- delivery-proof/output/capability-statement_remediated.pdf
  (HawkStack's own remediated document): zero structural
  findings, veraPDF PASS with zero failed checks, exit code 0.
- Profile only mode (veraPDF deliberately unavailable): the
  structural report prints, the validation layer reports itself
  skipped, and the result still fails on structural findings.
  No crash, no silent pass.

## License choice

MIT, copyright HawkStack AI LLC. Reasoning: the org's existing
public repository (HawkStackAI/skills) already ships MIT under the
same holder, so the public layer stays consistent; MIT is the
lowest friction license for the small agencies and prime
contractor teams this tool is meant to reach; and the scanner is a
thin checker that invokes veraPDF as an external program rather
than embedding technology where a patent grant would matter, so
Apache 2.0's extra machinery buys little here. veraPDF itself is
a separate open source project, is not bundled, and keeps its own
license.

## Open items for the publisher

1. Create the repository under the HawkStackAI org and push this
   folder. Suggested name: pdf-a11y-scanner. Not done here.
2. Decide whether STAGING-REPORT.md itself should be published or
   removed at push time. It references internal folder paths by
   design, as the staging record. Recommendation: remove it from
   the pushed tree and keep it in the internal workspace.
3. The internal tools folder remains the working copy. Any future
   fix should be ported to the public tree deliberately, never by
   automatic sync, so internal material cannot leak into the
   public repo.
4. Possible later additions, not needed for launch: a small
   tagged sample PDF so users can see a passing result, and a
   packaged download bundling veraPDF for nontechnical users.
