"""
prepare_docs.py - one-time step that turns the office's Word/PDF files into
clean Markdown that DocuBot can index.

What it does
- Reads each source file listed in SOURCES (docx, pdf, or already-clean md).
- Numbered rules become their own sections ("Customer Service #9"), so one
  rule = one retrievable chunk with a citable name.
- Applies the cleanup rules agreed with the office (drop supervisor-only
  content, fix the document list, drop one contradictory EIC line).
- Writes knowledge_base/*.md and knowledge_base/manifest.json (year, tier, audience,
  language per document) and prints a report, including a scan for
  SSN/EIN-shaped text so sensitive numbers never reach the index.

Usage
    python prepare_docs.py --src "<folder with the office files>" \
                           --extra "<folder with transcribed .md files>" \
                           --out knowledge_base

Original files are only read, never changed.
"""

import argparse
import json
import os
import re
import shutil
import sys
import zipfile
from xml.etree import ElementTree as ET

import docx  # python-docx
import pdfplumber

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{%s}" % W_NS

# ---------------------------------------------------------------------------
# What goes into the index. One entry per source file.
# keys: file, kind (docx|pdf|md), id (output name), title, year, tier,
#       audience, language, type
# optional: drop_items [(group, number)], drop_lines [regex],
#           replace_lines [(old, new)], drop_sections [heading text],
#           pdf_headings [..]
# ---------------------------------------------------------------------------
SOURCES = [
    # ---- Tier 1: core ----
    dict(file="2026 office manual.docx", kind="docx", id="office_manual_2026",
         title="Office Manual 2026", year=2026, tier=1, audience="PT",
         language="en", type="rule",
         drop_items=[("Tax & Software", 27)]),          # addressed to supervisors
    dict(file="Tax  Season Preparer Manual.docx", kind="docx",
         id="preparer_manual_2025", title="Tax Season Preparer Manual",
         year=2025, tier=1, audience="PT", language="en", type="rule",
         # Office decision: for single filers the second EIC line stands
         # ("has either proof ... = claim EIC"); the contradictory first line
         # ("do not have both ... = don't claim") is dropped.
         drop_lines=[r"^File as single; do not have both proof of income and expense"]),
    dict(file="2026 service fee cover page (transcribed).md", kind="md",
         id="fee_cover_page_2026", title="2026 Service Fee Cover Page",
         year=2026, tier=1, audience="PT", language="en", type="fee"),

    # ---- Tier 2: workflow and policy ----
    dict(file="Walk client handle steps.docx", kind="docx",
         id="walk_in_steps_2026", title="Steps and Conversations: Walk-in Clients",
         year=2026, tier=2, audience="PT", language="en", type="workflow"),
    dict(file="document list.docx", kind="docx", id="document_list_2026",
         title="Useful Documents in the 2026 Folder", year=2026, tier=2,
         audience="PT", language="en", type="navigation",
         # PTs must never be pointed to supervisor-only material.
         replace_lines=[("Supervisor manual & Preparer manual (Protocol)",
                         "Preparer manual (Protocol)")],
         drop_lines=[r"^Supervisor additional training manual"]),
    dict(file="Minimum Fee Letter for over 200K.docx", kind="docx",
         id="minimum_fee_letter_2025", title="Minimum Fee Letter (income over $200K)",
         year=2025, tier=2, audience="PT", language="en+zh", type="fee",
         insert_headings=[("Introducing Our New Minimum Fee Structure", "Minimum Fee Letter (English)"),
                          ("关于新增年度收入最低服务费结构的通知", "Minimum Fee Letter (Chinese)")]),

    # ---- Tier 3: reference tables and short notes ----
    dict(file="IRS standard deduction 2025 (official source).md", kind="md",
         id="irs_standard_deduction_2025", title="IRS Standard Deduction 2025",
         year=2025, tier=3, audience="PT", language="en", type="reference"),
    dict(file="IRA income limits 2025 (transcribed).md", kind="md",
         id="ira_limits_2025", title="IRA Income Limits 2025",
         year=2025, tier=3, audience="PT", language="en", type="reference"),
    dict(file="Essential Plan eligibility 2025 (transcribed).md", kind="md",
         id="essential_plan_2025", title="Essential Plan Eligibility 2025",
         year=2025, tier=3, audience="PT", language="en", type="reference"),
    dict(file="NYS bank routing numbers and school district codes (transcribed).md",
         kind="md", id="routing_school_codes_2024",
         title="NYS Bank Routing Numbers and School District Codes",
         year=2024, tier=3, audience="PT", language="en", type="reference"),
    dict(file="Medicaid & Obama Care Income Level 2026.pdf", kind="pdf",
         id="medicaid_aca_2026", title="Medicaid and ACA Income Levels (Coverage Year 2026)",
         year=2026, tier=3, audience="PT", language="en", type="reference",
         pdf_headings=[
             "2025 Federal Poverty Guidelines (Coverage Year 2026)",
             "Expected Premium Contribution (Coverage Year 2026)",
             "Employer-Sponsored Insurance Affordability Threshold (Coverage Year 2026)",
             "Out-Of-Pocket Maximum (Coverage Year 2026)",
             "Affordability Exemption Threshold (Coverage Year 2026)",
             "Tax Filing Thresholds (Tax Year 2025)",
             "Repayment Limits on APTC (Tax Year 2025)",
             "2024 Federal Poverty Guidelines (Coverage Year 2025)",
         ]),
    dict(file="New York IT214 ack.docx", kind="docx", id="it214_rent_ack_2023",
         title="New York IT-214 Rent Acknowledgment", year=2023, tier=3,
         audience="PT", language="en+zh", type="reference"),
    dict(file="Property Tax Credit Lookup.docx", kind="docx",
         id="property_tax_lookup_2023", title="Property Tax Credit Lookup",
         year=2023, tier=3, audience="PT", language="en", type="reference"),
    dict(file="Our service is not 100_ audit protected.docx", kind="docx",
         id="audit_protection_2026", title="Why Our Service Is Not 100% Audit Protected",
         year=2026, tier=3, audience="PT", language="en", type="policy"),

    # ---- Tier 4: client conversation scripts ----
    dict(file="Personal Tax Return Conversation.docx", kind="docx",
         id="script_personal_return_2026", title="Conversation Script: Personal Tax Return Call",
         year=2026, tier=4, audience="PT", language="en", type="script"),
    dict(file="Technical Question Conversation.docx", kind="docx",
         id="script_technical_question_2026", title="Conversation Script: Technical Questions",
         year=2026, tier=4, audience="PT", language="en", type="script"),
]

# Files deliberately NOT indexed (documented so the choice is visible).
EXCLUDED = {
    "Supervisoer additonal trainning.docx": "supervisor-only training (PTs must not see it)",
    "Drawing conversation.docx": "marketing prize-drawing script, not a PT question",
    "Quick Reference Guide.pdf": "2021 Drake keyboard shortcuts, possible later feature",
    "NYC care 2025.pdf": "Chinese two-column PDF; text extracts out of order. Needs a manual translation first",
    "NYS bank routing number & school district.pdf": "replaced by transcribed .md",
    "IRA income limits 2025.docx": "replaced by transcribed .md (tables were images)",
    "Essential Plan for 2025.png": "replaced by transcribed .md",
}

SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
EIN_RE = re.compile(r"\b\d{2}-\d{7}\b")


# ---------------------------------------------------------------------------
# docx -> markdown
# ---------------------------------------------------------------------------
def _numbering_formats(document):
    """Map numId -> {ilvl: numFmt} so we can tell numbered lists from bullets."""
    fmts = {}
    try:
        numbering = document.part.numbering_part.element
    except Exception:
        return fmts
    abstract = {}
    for an in numbering.findall(W + "abstractNum"):
        aid = an.get(W + "abstractNumId")
        levels = {}
        for lvl in an.findall(W + "lvl"):
            nf = lvl.find(W + "numFmt")
            levels[int(lvl.get(W + "ilvl"))] = nf.get(W + "val") if nf is not None else "decimal"
        abstract[aid] = levels
    for num in numbering.findall(W + "num"):
        nid = num.get(W + "numId")
        aid = num.find(W + "abstractNumId").get(W + "val")
        fmts[nid] = abstract.get(aid, {})
    return fmts


def _para_numpr(p):
    pPr = p._p.pPr
    if pPr is None or pPr.numPr is None:
        return None
    numId = pPr.numPr.numId.val if pPr.numPr.numId is not None else None
    ilvl = pPr.numPr.ilvl.val if pPr.numPr.ilvl is not None else 0
    return (str(numId), int(ilvl)) if numId is not None else None


def _all_bold(p):
    runs = [r for r in p.runs if r.text.strip()]
    return bool(runs) and all(bool(r.bold) for r in runs)


def _clean(text):
    text = text.replace(" ", " ").replace("\t", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    return text.strip()


def _table_to_md(table):
    rows = []
    for row in table.rows:
        cells = []
        for c in row.cells:
            cells.append(_clean(c.text).replace("\n", " ").replace("|", "/"))
        rows.append(cells)
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def docx_to_md(path, cfg):
    document = docx.Document(path)
    fmts = _numbering_formats(document)
    counters = {}
    drop_items = set(cfg.get("drop_items", []))
    drop_lines = [re.compile(r, re.I) for r in cfg.get("drop_lines", [])]
    replace_lines = cfg.get("replace_lines", [])

    out = ["# %s" % cfg["title"], ""]
    group = None           # current "## " group heading text
    dropping = False       # True while skipping the body of a dropped item
    stats = {"dropped_items": [], "dropped_lines": [], "replaced": 0}

    body = document.element.body
    para_map = {p._p: p for p in document.paragraphs}
    table_map = {t._tbl: t for t in document.tables}

    for el in body.iterchildren():
        if el in table_map:
            out += [_table_to_md(table_map[el]), ""]
            dropping = False
            continue
        if el not in para_map:
            continue
        p = para_map[el]
        text = _clean(p.text)
        if not text:
            continue

        for old, new in replace_lines:
            if old in text:
                text = text.replace(old, new)
                stats["replaced"] += 1
        if any(rx.search(text) for rx in drop_lines):
            stats["dropped_lines"].append(text[:80])
            continue

        for starts, heading in cfg.get("insert_headings", []):
            if text.startswith(starts):
                group = heading
                out += ["", "## " + heading, ""]
                dropping = False

        np_ = _para_numpr(p)
        style = (p.style.name or "") if p.style is not None else ""

        # explicit Word headings
        m = re.match(r"Heading (\d)", style)
        if m:
            group = text.rstrip(":")
            out += ["## " + group, ""]
            dropping = False
            continue

        if np_ is None:
            # a bold, short, non-list paragraph is a group heading
            if _all_bold(p) and len(text) <= 90:
                group = text.rstrip(":")
                out += ["## " + group, ""]
                dropping = False
            else:
                if not dropping:
                    out += [text, ""]
            continue

        numId, ilvl = np_
        fmt = fmts.get(numId, {}).get(ilvl, "decimal")
        # maintain counters
        key = (numId, ilvl)
        counters[key] = counters.get(key, 0) + 1
        for (n, l) in list(counters):
            if n == numId and l > ilvl:
                counters[(n, l)] = 0

        if fmt == "bullet":
            if not dropping:
                out.append("%s- %s" % ("  " * ilvl, text))
            continue

        # numbered item
        n = counters[key]
        if ilvl == 0:
            label = "%s #%d" % (group, n) if group else "Item %d" % n
            if (group, n) in drop_items:
                dropping = True
                stats["dropped_items"].append("%s #%d" % (group, n))
                continue
            dropping = False
            out += ["", "### " + label, text, ""]
        else:
            if not dropping:
                out.append("%s%d. %s" % ("  " * ilvl, n, text))

    # tidy: collapse blank runs, make sure bullets are surrounded by blank lines
    md = "\n".join(out)
    md = re.sub(r"(?<!\n)\n(#{2,3} )", r"\n\n\1", md)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    md = drop_empty_sections(md)
    md = re.sub(r"(?m)^([^-#\s].*)\n(- )", r"\1\n\n\2", md)
    return md, stats


def drop_empty_sections(md):
    """Remove '## Heading' lines that have no text before the next heading."""
    lines = md.splitlines()
    keep = []
    for i, ln in enumerate(lines):
        if re.match(r"^##\s+\S", ln):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines) or re.match(r"^#{1,6}\s+\S", lines[j]):
                continue
        keep.append(ln)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(keep)).strip() + "\n"


# ---------------------------------------------------------------------------
# pdf -> markdown (text PDFs with known section titles)
# ---------------------------------------------------------------------------
def pdf_to_md(path, cfg):
    pages = []
    with pdfplumber.open(path) as pdf:
        for pg in pdf.pages:
            pages.append(pg.extract_text() or "")
    lines = "\n".join(pages).splitlines()
    headings = cfg.get("pdf_headings", [])
    out = ["# %s" % cfg["title"], ""]
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("Page ") and "out of" in s:
            continue
        if s in ("REFERENCE", "CHART"):
            continue
        if s.startswith("#"):          # a literal '#' would look like a Markdown heading
            s = "Number" + s[1:]
        if s in headings:
            out += ["", "## " + s, ""]
        else:
            out.append(s)
    md = "\n".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return md, {"dropped_items": [], "dropped_lines": [], "replaced": 0}


def md_passthrough(path, cfg):
    text = open(path, encoding="utf8").read()
    return text.strip() + "\n", {"dropped_items": [], "dropped_lines": [], "replaced": 0}


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="folder with the office .docx/.pdf files")
    ap.add_argument("--extra", help="folder with transcribed/official .md files")
    ap.add_argument("--out", default="knowledge_base", help="output folder (default knowledge_base)")
    args = ap.parse_args()

    if os.path.isdir(args.out):
        for f in os.listdir(args.out):
            if f.endswith(".md") or f == "manifest.json":
                os.remove(os.path.join(args.out, f))
    os.makedirs(args.out, exist_ok=True)

    manifest, problems = [], []
    for cfg in SOURCES:
        folder = args.extra if cfg["kind"] == "md" and args.extra else args.src
        path = os.path.join(folder, cfg["file"])
        if not os.path.exists(path):
            # md files may live in either folder
            alt = os.path.join(args.src, cfg["file"])
            path = alt if os.path.exists(alt) else path
        if not os.path.exists(path):
            problems.append("MISSING source: %s" % cfg["file"])
            continue
        try:
            conv = {"docx": docx_to_md, "pdf": pdf_to_md, "md": md_passthrough}[cfg["kind"]]
            md, stats = conv(path, cfg)
        except Exception as exc:  # keep going, report at the end
            problems.append("FAILED %s: %s: %s" % (cfg["file"], type(exc).__name__, exc))
            continue

        out_name = cfg["id"] + ".md"
        with open(os.path.join(args.out, out_name), "w", encoding="utf8") as f:
            f.write(md)

        sections = len(re.findall(r"^#{2,3} ", md, re.M))
        ssn = SSN_RE.findall(md)
        ein = EIN_RE.findall(md)
        if ssn or ein:
            problems.append("%s contains SSN/EIN-shaped text: %s" % (out_name, ssn + ein))
        manifest.append({
            "doc": out_name, "title": cfg["title"], "year": cfg["year"],
            "tier": cfg["tier"], "audience": cfg["audience"],
            "language": cfg["language"], "type": cfg["type"],
            "source_file": cfg["file"], "sections": sections,
        })
        print("%-34s sections=%-3d dropped_items=%s dropped_lines=%d replaced=%d"
              % (out_name, sections, stats["dropped_items"] or "-",
                 len(stats["dropped_lines"]), stats["replaced"]))

    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf8") as f:
        json.dump({"documents": manifest, "excluded": EXCLUDED}, f, indent=2, ensure_ascii=False)

    print("\nWrote %d documents to %s/" % (len(manifest), args.out))
    print("Excluded on purpose:")
    for k, v in EXCLUDED.items():
        print("  - %s: %s" % (k, v))
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  !", p)
        sys.exit(1)
    print("\nNo problems found.")


if __name__ == "__main__":
    main()
