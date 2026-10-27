"""Generate a public Boosthub Staking v2 PDF with release-local evidence links.

This is a PUBLICATION task, not a new audit.
- Copy no files from the private Audit-Controller repository.
- Do not fabricate or reconstruct a source ZIP.
- Preserve the already-published audited PDF's conclusions and issue pages.
- Only link to the seven selected release-local supporting documents.
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen, Request
import hashlib
import io
import base64
import json

import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor

ROOT = Path(__file__).resolve().parents[2]
FOLDER = "Boosthub Staking v2 - Linked Public Release"
DEST = ROOT / FOLDER
PDF_NAME = "CurveYield_Boosthub_Staking_v2_Linked_Security_Audit.pdf"
DEST.mkdir(parents=True, exist_ok=True)

# The prior audit PDF is already public. We do not use private controller content.
SOURCE_URL = "https://api.github.com/repos/CurveYield2/Audits/git/blobs/2f396f05e07d575f9ee02358b236c20856f91091"
EXPECTED_SHA256 = "088e8d6700678442a47265b9cc1457ee824a1347efdf66da57c70c8355901adf"

ROWS = [
    ("Audit scope", "Exactly which source contracts and interfaces were reviewed.", "Audit_Scope.json"),
    ("Findings and remediation", "Seven validated Low findings and their final dispositions.", "Findings_and_Remediation.json"),
    ("Methodology and analysis", "Consolidated methodological review and technical assessment.", "Methodology_and_Analysis.json"),
    ("Evidence index", "This release's aggregated evidence and provenance references.", "Evidence_Index.json"),
    ("Execution results", "Structured reproduction and verification observations.", "Execution_Results.json"),
    ("Medusa fuzz results", "Recorded Medusa fuzzing execution outcome.", "Medusa_Fuzz_Results.json"),
    ("Native fuzz results", "Recorded native fuzzing execution outcome.", "Native_Fuzz_Results.json"),
]
BASE_URL = "https://github.com/CurveYield-Security/Audits/blob/main/" + quote(FOLDER) + "/"
for title, description, filename in ROWS:
    assert (DEST / filename).is_file(), f"Selected public evidence missing: {filename}"

req = Request(SOURCE_URL, headers={"User-Agent": "CurveYield-Audit-Publication/1.0", "Accept": "application/vnd.github+json"})
with urlopen(req, timeout=90) as response:
    public_blob = json.load(response)
assert public_blob.get("encoding") == "base64", "Unexpected GitHub blob encoding"
original = base64.b64decode(public_blob["content"])
assert hashlib.sha256(original).hexdigest() == EXPECTED_SHA256, "Public baseline report SHA-256 mismatch"

W, H = A4
NAVY = HexColor("#071F36")
TEAL = HexColor("#12877E")
SUB = HexColor("#49647B")
PALE = HexColor("#EAF6F3")
LIGHT = HexColor("#F4F8FA")
BORDER = HexColor("#D9E5E9")
WHITE = HexColor("#FFFFFF")

buffer = io.BytesIO()
c = canvas.Canvas(buffer, pagesize=A4, pageCompression=1)
c.setFillColor(NAVY)
c.rect(0, H - 24, W, 24, stroke=0, fill=1)
c.setFillColor(WHITE)
c.setFont("Helvetica-Bold", 8)
c.drawString(34, H - 16, "CURVEYIELD SECURITY  /  BOOSTHUB STAKING V2")
c.setFillColor(NAVY)
c.setFont("Helvetica-Bold", 19)
c.drawString(34, H - 67, "AUDIT EVIDENCE LIBRARY")
c.setFont("Helvetica", 10)
c.setFillColor(SUB)
c.drawString(34, H - 88, "Seven curated public evidence documents for this security audit.")
c.drawString(34, H - 104, "Every link opens a file in this PDF's own public release folder.")

c.setFillColor(PALE)
c.roundRect(34, H - 151, W - 68, 31, 7, fill=1, stroke=0)
c.setFillColor(TEAL)
c.setFont("Helvetica-Bold", 9)
c.drawString(46, H - 138, "7 SELECTED PUBLIC REFERENCES")
c.setFillColor(SUB)
c.setFont("Helvetica", 8)
c.drawRightString(W - 46, H - 138, "Source ZIP: not published")

for i, (title, desc, filename) in enumerate(ROWS):
    top = H - 164 - i * 78
    bottom = top - 70
    c.setFillColor(LIGHT if i % 2 == 0 else WHITE)
    c.setStrokeColor(BORDER)
    c.roundRect(34, bottom, W - 68, 70, 7, fill=1, stroke=1)
    c.setFillColor(TEAL)
    c.roundRect(46, bottom + 19, 34, 33, 6, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(63, bottom + 31, f"{i + 1:02}")
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11.0)
    c.drawString(93, bottom + 47, title)
    c.setFillColor(SUB)
    c.setFont("Helvetica", 8.3)
    c.drawString(93, bottom + 29, desc)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 8.4)
    c.drawString(93, bottom + 12, "OPEN PUBLIC DOCUMENT")
    c.linkURL(BASE_URL + quote(filename), (34, bottom, W - 34, top), relative=0, thickness=0)

c.setFillColor(SUB)
c.setFont("Helvetica", 7.7)
c.drawString(34, 58, "Source archive omitted: no original initialization ZIP has been selected for public release.")
c.drawString(34, 43, "These are supporting records, not a separate security review or new audit verdict.")
c.showPage()
c.save()

out = DEST / PDF_NAME
with fitz.open(stream=original, filetype="pdf") as document, fitz.open(stream=buffer.getvalue(), filetype="pdf") as insert:
    # The public release must have no unapproved outbound evidence links.
    for page in document:
        for link in list(page.get_links()):
            if link.get("kind") == fitz.LINK_URI:
                page.delete_link(link)
    source_text = "".join(page.get_text() for page in document)
    assert "github.com/curveyield3/Audit-Controller" not in source_text, "Private controller URL present in published report text"
    document.insert_pdf(insert, links=1)
    document.set_metadata({
        "title": "CurveYield Boosthub Staking v2 Security Audit - Linked Public Release",
        "author": "CurveYield Security",
        "subject": "Previously completed audit with seven curated public evidence links"
    })
    document.save(out, garbage=4, deflate=True)

with fitz.open(out) as report:
    links = [link["uri"] for page in report for link in page.get_links() if link.get("kind") == fitz.LINK_URI]
    expected = [BASE_URL + quote(row[2]) for row in ROWS]
    assert len(links) == 7 and set(links) == set(expected), (links, expected)
    assert len(report) >= 2
    print(f"Created {out} | {len(report)} pages | 7 public release-local links | no source ZIP")
