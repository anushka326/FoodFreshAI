"""Render the judge-facing HTML project document to a styled PDF.

Requires ReportLab and lxml. The HTML remains the editable source of truth.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

from lxml import html
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table,
    TableStyle, KeepTogether,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "FoodFresh_AI_Judge_Project_Document.html"
OUTPUT = ROOT / "docs" / "FoodFresh_AI_Judge_Project_Document.pdf"
GREEN = colors.HexColor("#176b3a")
LIME = colors.HexColor("#8ecf54")
PALE = colors.HexColor("#f1f7f2")
LINE = colors.HexColor("#d8e3db")
INK = colors.HexColor("#1d2922")
MUTED = colors.HexColor("#59685e")
WIDTH, HEIGHT = A4

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=35, leading=40, textColor=GREEN, alignment=TA_CENTER, spaceAfter=8*mm))
styles.add(ParagraphStyle("Motto", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=17, leading=23, textColor=GREEN, alignment=TA_CENTER, spaceAfter=6*mm))
styles.add(ParagraphStyle("CoverSub", parent=styles["Normal"], fontSize=12, leading=18, textColor=MUTED, alignment=TA_CENTER, spaceAfter=8*mm))
styles.add(ParagraphStyle("Chapter", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=GREEN, spaceBefore=2*mm, spaceAfter=5*mm, keepWithNext=True))
styles.add(ParagraphStyle("Subhead", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=GREEN, spaceBefore=4*mm, spaceAfter=2*mm, keepWithNext=True))
styles.add(ParagraphStyle("SubSub", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=GREEN, spaceBefore=3*mm, spaceAfter=1.5*mm, keepWithNext=True))
styles.add(ParagraphStyle("BodyDoc", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.1, leading=13.2, textColor=INK, alignment=TA_LEFT, spaceAfter=2.4*mm, splitLongWords=1))
styles.add(ParagraphStyle("SmallDoc", parent=styles["BodyDoc"], fontSize=7.6, leading=10, textColor=MUTED, spaceAfter=2*mm))
styles.add(ParagraphStyle("TableDoc", parent=styles["BodyDoc"], fontSize=7.1, leading=9.1, spaceAfter=0, textColor=INK))
styles.add(ParagraphStyle("TableHeadDoc", parent=styles["TableDoc"], fontName="Helvetica-Bold", textColor=GREEN))
styles.add(ParagraphStyle("QuoteDoc", parent=styles["BodyDoc"], backColor=PALE, borderColor=LIME, borderWidth=0, borderPadding=7, leftIndent=5, rightIndent=5, spaceBefore=2*mm, spaceAfter=3*mm))
styles.add(ParagraphStyle("TOCDoc", parent=styles["BodyDoc"], fontSize=10, leading=15, textColor=GREEN))
styles.add(ParagraphStyle("CenterDoc", parent=styles["BodyDoc"], alignment=TA_CENTER, textColor=GREEN))


def inline(node) -> str:
    if node is None:
        return ""
    parts = [safe_text(node.text or "")]
    for child in node:
        tag = str(child.tag).lower() if isinstance(child.tag, str) else ""
        value = inline(child)
        if tag in ("strong", "b"):
            value = f"<b>{value}</b>"
        elif tag in ("em", "i"):
            value = f"<i>{value}</i>"
        elif tag == "code":
            value = f'<font name="Courier" size="8">{value}</font>'
        elif tag == "a":
            href = escape(child.get("href", ""), quote=True)
            value = f'<link href="{href}" color="#176b3a">{value}</link>' if href else value
        elif tag == "br":
            value += "<br/>"
        parts.append(value)
        parts.append(safe_text(child.tail or ""))
    return "".join(parts)


def safe_text(text: str) -> str:
    text = (text.replace("→", " » ").replace("↓", " v ").replace("↔", " <-> ")
            .replace("×", " x ").replace("≤", "<=").replace("≥", ">=")
            .replace("Δ", "delta").replace("’", "'").replace("‘", "'")
            .replace("—", "-").replace("–", "-").replace("…", "..."))
    return escape(text)


def para(node, style="BodyDoc"):
    text = inline(node).strip()
    if not text:
        return None
    return Paragraph(text, styles[style])


def list_flow(node, ordered=False):
    items = []
    for index, li in enumerate(node.findall("li"), 1):
        label = f"{index}." if ordered else "•"
        content = inline(li).strip()
        items.append(Paragraph(f'<font color="#176b3a"><b>{label}</b></font>&nbsp;&nbsp;{content}', styles["BodyDoc"]))
    return items


def table_flow(node):
    rows = []
    for tr in node.xpath(".//tr"):
        cells = []
        for cell in tr.xpath("./th|./td"):
            cells.append(Paragraph(inline(cell).strip(), styles["TableHeadDoc" if cell.tag.lower() == "th" else "TableDoc"]))
        if cells:
            rows.append(cells)
    if not rows:
        return None
    ncols = max(len(row) for row in rows)
    col_widths = [ (WIDTH - 34*mm) / ncols ] * ncols
    for row in rows:
        row.extend([Paragraph("", styles["TableDoc"])] * (ncols - len(row)))
    tbl = Table(rows, colWidths=col_widths, repeatRows=1, hAlign="LEFT", splitByRow=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f2e9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), GREEN),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfdfb")]),
    ]))
    return tbl


def flow_diagram(node):
    labels = []
    for child in node.xpath(".//span"):
        text = " ".join("".join(child.itertext()).split())
        if text:
            labels.append(text)
    if not labels:
        return None
    cells = []
    for index, label in enumerate(labels):
        is_arrow = label in {"→", "↓", "+", "↔"}
        label = {"→": "»", "↓": "v", "↔": "<->"}.get(label, label)
        cells.append(Paragraph(label if is_arrow else escape(safe_text(label)), styles["CenterDoc" if is_arrow else "TableDoc"]))
        widths = [0.17 if cell.getPlainText().strip() in {"»", "+", "<->"} else 1 for cell in cells]
    total = sum(widths)
    col_widths = [(WIDTH-42*mm)*w/total for w in widths]
    tbl = Table([cells], colWidths=col_widths, hAlign="LEFT")
    tbl.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), PALE), ("BOX", (0,0), (-1,-1), 0.5, LINE), ("INNERGRID", (0,0), (-1,-1), 0.4, LINE), ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
    return tbl


def children_flow(node):
    out = []
    for child in node:
        tag = str(child.tag).lower() if isinstance(child.tag, str) else ""
        result = None
        if tag == "h1":
            result = para(child, "Chapter")
        elif tag == "h2":
            result = para(child, "Subhead")
        elif tag == "h3":
            result = para(child, "SubSub")
        elif tag == "p":
            result = para(child, "SmallDoc" if "small" in child.get("class", "") else "BodyDoc")
        elif tag in ("ul", "ol"):
            out.extend(list_flow(child, tag == "ol"))
        elif tag == "table":
            result = table_flow(child)
        elif tag == "div" and "flow" in child.get("class", ""):
            result = flow_diagram(child)
        elif tag == "div" and "vision" in child.get("class", ""):
            result = Paragraph("<b>" + inline(child).strip() + "</b>", styles["CenterDoc"])
        elif tag == "div" and ("callout" in child.get("class", "") or "end" in child.get("class", "")):
            result = Paragraph(inline(child).strip(), styles["QuoteDoc"])
        elif tag in ("div", "section"):
            out.extend(children_flow(child))
        if result is not None:
            out.append(result)
            if tag in ("table", "div"):
                out.append(Spacer(1, 2.5*mm))
    return out


def paint_page(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(17*mm, HEIGHT-12*mm, WIDTH-17*mm, HEIGHT-12*mm)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.setFillColor(GREEN)
    canvas.drawString(17*mm, HEIGHT-9.5*mm, "FOODFRESH AI")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(17*mm, 10*mm, "Know Your Food. Save Your Food. Waste Less.")
    canvas.drawRightString(WIDTH-17*mm, 10*mm, f"{doc.page}")
    canvas.restoreState()


def main():
    tree = html.parse(str(SOURCE))
    body = tree.find("body")
    sections = body.findall("section")
    story = []
    # Cover: restrained typography; the SVG artwork remains in the editable HTML source.
    story += [Spacer(1, 42*mm), Paragraph("PROJECT DOCUMENT", ParagraphStyle("Eyebrow", parent=styles["CoverSub"], fontName="Helvetica-Bold", fontSize=11, textColor=GREEN, spaceAfter=5*mm)), Paragraph("FoodFresh AI", styles["CoverTitle"]), Paragraph("Know Your Food. Save Your Food. Waste Less.", styles["Motto"]), Spacer(1, 8*mm), Paragraph("An AI-assisted food management prototype connecting visual food analysis with pantry decisions.", styles["CoverSub"]), Spacer(1, 26*mm), Paragraph("JUDGE-FACING TECHNICAL AND SOCIAL-IMPACT OVERVIEW", ParagraphStyle("CoverMeta", parent=styles["SmallDoc"], alignment=TA_CENTER, fontName="Helvetica-Bold", fontSize=9, textColor=MUTED)), Spacer(1, 2*mm), Paragraph("Project state reviewed 30 September 2026", ParagraphStyle("CoverDate", parent=styles["SmallDoc"], alignment=TA_CENTER)), PageBreak()]
    toc = next((s for s in sections if "toc" in s.get("class", "")), None)
    if toc is not None:
        story.append(Paragraph("Contents", styles["Chapter"]))
        entries = toc.xpath(".//li")
        for i, entry in enumerate(entries):
            story.append(Paragraph(f"{i+1:02d}.&nbsp;&nbsp;{escape(' '.join(''.join(entry.itertext()).split()))}", styles["TOCDoc"]))
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph("Implementation status, research candidates and limitations are labeled separately. Project test scores refer to the named local test split; external model-card scores are identified as external.", styles["SmallDoc"]))
        story.append(PageBreak())
    first = True
    for section in sections:
        classes = section.get("class", "")
        if "cover" in classes or "toc" in classes:
            continue
        if not first:
            story.append(PageBreak())
        first = False
        story.extend(children_flow(section))
    doc = BaseDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=17*mm, rightMargin=17*mm, topMargin=18*mm, bottomMargin=17*mm, title="FoodFresh AI — Judge-Facing Project Document", author="FoodFresh AI Project")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main", topPadding=1*mm, bottomPadding=1*mm)
    doc.addPageTemplates([PageTemplate(id="project", frames=frame, onPage=paint_page)])
    doc.build(story)
    print(f"Created {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
