#!/usr/bin/env python3
"""Run veraPDF PDF/UA-1 validation on PDFs and print a compact summary.

veraPDF is an external tool and is not bundled with this project.
Install it from https://verapdf.org (it needs a Java 17 or newer
runtime), then either put the `verapdf` launcher on your PATH or set
the VERAPDF_BIN environment variable to the launcher's full path.

Output: one JSON object per file with the compliance status and the
failed check counts grouped by PDF/UA clause.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile


def resolve_verapdf():
    env_bin = os.environ.get("VERAPDF_BIN")
    if env_bin:
        return env_bin
    return shutil.which("verapdf")


VERAPDF = resolve_verapdf()


def check(path):
    if not VERAPDF:
        raise RuntimeError(
            "veraPDF not found. Install veraPDF, put it on PATH, or set "
            "VERAPDF_BIN to the veraPDF launcher path."
        )
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        out_path = tf.name
    try:
        proc = subprocess.run(
            [VERAPDF, "--flavour", "ua1", "--format", "json", "-r", path],
            capture_output=True, text=True, timeout=600,
        )
        raw = proc.stdout
        start = raw.find("{")
        data = json.loads(raw[start:])
        report = data["report"]
        job = report["jobs"][0]
        result = job["validationResult"]
        if isinstance(result, list):
            result = result[0]
        details = result.get("details", {})
        failed = {}
        for rule in details.get("ruleSummaries", []):
            if rule.get("ruleStatus") == "FAILED":
                failed[rule["clause"]] = rule.get("failedChecks", 0)
        return {
            "file": path,
            "compliant": details.get("failedRules", 1) == 0 and details.get("failedChecks", 1) == 0,
            "failed_rules": details.get("failedRules"),
            "failed_checks_total": details.get("failedChecks", sum(failed.values())),
            "failed_clauses": failed,
        }
    finally:
        os.unlink(out_path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(json.dumps(check(p)))
