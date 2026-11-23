# PDF Accessibility Scanner

A small, free checker that tells you whether your PDF documents can
actually be read by everyone, including people using screen readers
and other assistive technology.

If you publish PDFs on a website, send them to customers, or post
them for a public agency, this tool gives you a straight answer in
seconds: what is broken, in plain language, before a reader or a
compliance review finds it first.

## What it checks

The scanner runs two layers of checks on each PDF.

**Structural profile** (always runs, needs only Python and pypdf):

- Tagged structure. An untagged PDF has no reading order, so a
  screen reader reads content in whatever order it happens to be
  stored, and headings, lists, and tables are not announced.
- Document language. Without it, screen readers may pronounce the
  text using the wrong language.
- Title metadata, and whether the viewer is set to display the
  title instead of the file name.
- Text layer. Image only pages (scans with no real text) are
  invisible to screen readers and to search.
- Form fields. Every field needs an accessible name, or a screen
  reader cannot say what the field is asking for.
- PDF/UA identifier in the document metadata.

**Full PDF/UA-1 validation** (runs when veraPDF is installed):
the complete machine checkable rule set of PDF/UA-1, the
international standard for accessible PDFs, reported as failed
checks grouped by clause.

## What a failure means

A failure is a real barrier, not a style nit. An untagged agenda
packet cannot be navigated by a blind resident. An image only form
cannot be filled in with assistive technology. A field with no
accessible name is a blank question. Public agencies in the United
States have legal duties here under the ADA Title II rule, which
points to WCAG 2.1 AA for web content including posted documents,
and Section 508 applies the same expectations to federal material.
Whatever your obligations, a failing document is one some of your
readers simply cannot use.

Two honest limits. First, automation cannot check everything:
meaningful reading order judgment, alt text quality, and color
contrast in context still need human review. Second, a clean
structural profile alone is triage, not proof. Only the veraPDF
layer speaks to PDF/UA-1 conformance, and even a full pass is a
machine verdict, not a certification.

## How to run it

You need Python 3.10 or newer.

```bash
pip install -r requirements.txt
python3 pdf_a11y_scan.py your-document.pdf
```

Scan several documents at once, or get machine readable output:

```bash
python3 pdf_a11y_scan.py budget.pdf agenda.pdf form.pdf
python3 pdf_a11y_scan.py --json your-document.pdf
```

The exit code is 0 when every check that ran passed, and 1 when
any check failed, so the scanner drops into a script or a build
pipeline as-is.

For the full PDF/UA-1 validation layer, install veraPDF from
https://verapdf.org (free and open source; it needs a Java 17 or
newer runtime). Put the `verapdf` launcher on your PATH, or point
the scanner at it:

```bash
export VERAPDF_BIN=/path/to/verapdf
python3 pdf_a11y_scan.py your-document.pdf
```

Without veraPDF the scanner still runs the structural profile and
tells you the validation layer was skipped.

## Fixing what it finds

Most findings are fixed in the source document: export tagged PDFs
from Word, InDesign, or your publishing tool, set the document
language and title, run OCR on scans, and give every form field a
proper label or tooltip. Documents that were born as untagged scans
usually need full remediation: OCR, structure tagging, reading
order repair, and validation.

HawkStack builds and runs document production systems, and
accessibility remediation of PDFs and document backlogs is one of
the services we sell. If your scan comes back with more failures
than your team has time to fix, that is the work we do. Find us at
hawkstackllc.com.

## License

MIT. See LICENSE. veraPDF is a separate open source project with
its own license and is not included here.
