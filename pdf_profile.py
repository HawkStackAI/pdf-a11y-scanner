#!/usr/bin/env python3
"""Structural accessibility profile of a PDF, using pypdf only.

Reports the machine-checkable facts that decide most of a PDF/UA and
WCAG document triage: page count, text layer presence, tagged status
(MarkInfo/Marked plus a structure tree root), document language,
metadata title and whether the viewer is told to display it, AcroForm
field count and how many fields carry an accessible name (/TU), and
the PDF/UA identifier (pdfuaid:part in XMP metadata) if present.

This is a triage profile, not a conformance verdict. Full PDF/UA
validation runs through veraPDF (see verapdf_check.py).
"""
import json
import sys

from pypdf import PdfReader


def profile(path):
    r = PdfReader(path)
    root = r.trailer["/Root"]
    out = {"file": path, "pages": len(r.pages)}

    meta = r.metadata
    out["title_metadata"] = (meta.title if meta else None) or None

    markinfo = root.get("/MarkInfo")
    marked = bool(markinfo and markinfo.get("/Marked"))
    out["marked"] = marked
    out["has_struct_tree"] = "/StructTreeRoot" in root
    out["tagged"] = bool(marked and out["has_struct_tree"])
    lang = root.get("/Lang")
    out["lang"] = str(lang) if lang else None

    viewer = root.get("/ViewerPreferences")
    out["display_doc_title"] = bool(viewer and viewer.get("/DisplayDocTitle"))

    # Text layer: total extractable characters across pages.
    chars = 0
    images = 0
    for p in r.pages:
        try:
            chars += len(p.extract_text() or "")
        except Exception:
            pass
        try:
            res = p.get("/Resources")
            if res and "/XObject" in res:
                for obj in res["/XObject"].values():
                    o = obj.get_object()
                    if o.get("/Subtype") == "/Image":
                        images += 1
        except Exception:
            pass
    out["extractable_chars"] = chars
    out["image_xobjects"] = images
    out["image_only_pages_likely"] = bool(chars < 20 * max(1, out["pages"]) and images > 0)

    # AcroForm fields and accessible names.
    fields = r.get_fields() or {}
    out["form_fields"] = len(fields)
    named = 0
    for f in fields.values():
        if f.get("/TU"):
            named += 1
    out["form_fields_with_accessible_name"] = named

    # PDF/UA identifier lives in XMP metadata (pdfuaid:part).
    out["pdfuaid_part"] = None
    try:
        xmp = r.xmp_metadata
        if xmp is not None:
            raw = xmp.stream.get_data() if hasattr(xmp, "stream") else b""
            if b"pdfuaid:part" in raw:
                out["pdfuaid_part"] = "present"
    except Exception:
        pass
    try:
        with open(path, "rb") as fh:
            head = fh.read(2_000_000)
        if b"pdfuaid:part" in head and out["pdfuaid_part"] is None:
            out["pdfuaid_part"] = "present"
    except Exception:
        pass

    return out


if __name__ == "__main__":
    results = [profile(p) for p in sys.argv[1:]]
    print(json.dumps(results, indent=2))
