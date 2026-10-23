from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "real-time-commerce-streaming-pipeline-explanation.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverX", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=21, leading=26, alignment=TA_CENTER, textColor=colors.HexColor("#15324B"), spaceAfter=12))
styles.add(ParagraphStyle(name="H1X", parent=styles["Heading1"], fontSize=14, leading=18, textColor=colors.HexColor("#15324B"), spaceBefore=9, spaceAfter=5))
styles.add(ParagraphStyle(name="H2X", parent=styles["Heading2"], fontSize=11, leading=14, textColor=colors.HexColor("#1F5A7A"), spaceBefore=7, spaceAfter=4))
styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontSize=9, leading=12, spaceAfter=5))
styles.add(ParagraphStyle(name="CodeX", fontName="Courier", fontSize=7.2, leading=9, backColor=colors.HexColor("#F2F5F7"), borderPadding=6, spaceBefore=4, spaceAfter=7))
story = [
    Spacer(1, 2*cm),
    Paragraph("REAL-TIME COMMERCE<br/>STREAMING PIPELINE", styles["CoverX"]),
    Paragraph("Project Explanation & Data Engineering Portfolio Guide", styles["BodyText"]),
    Spacer(1, 0.5*cm),
    Paragraph('<link href="https://github.com/shubham05jaiswal-coder/realtime-commerce-streaming-pipeline" color="#176B87">GitHub Repository</link>', styles["BodyX"]),
    PageBreak()
]
source = (ROOT / "docs" / "project-explanation.md").read_text(encoding="utf-8")
in_code = False
code_lines = []
for line in source.splitlines():
    if line.startswith("```"):
        if not in_code:
            in_code = True
            code_lines = []
        else:
            story.append(Preformatted("\n".join(code_lines), styles["CodeX"]))
            in_code = False
        continue
    if in_code:
        code_lines.append(line)
        continue
    if not line.strip():
        story.append(Spacer(1, 3))
        continue
    if line.startswith("# "):
        story.append(Paragraph(line[2:], styles["H1X"]))
    elif line.startswith("## "):
        story.append(Paragraph(line[3:], styles["H2X"]))
    elif line.startswith("- "):
        story.append(Paragraph("&#8226; " + line[2:], styles["BodyX"]))
    elif re.match(r"^\d+\. ", line):
        story.append(Paragraph(line, styles["BodyX"]))
    else:
        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", safe)
        safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
        story.append(Paragraph(safe, styles["BodyX"]))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D6E0E6"))
    canvas.line(1.7*cm, 1.15*cm, A4[0]-1.7*cm, 1.15*cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#526779"))
    canvas.drawString(1.7*cm, 0.75*cm, "Real-Time Commerce Streaming Pipeline | Project Guide")
    canvas.drawRightString(A4[0]-1.7*cm, 0.75*cm, f"Page {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=1.7*cm, leftMargin=1.7*cm, topMargin=1.6*cm, bottomMargin=1.5*cm, title="Real-Time Commerce Streaming Pipeline - Project Explanation", author="Shubham Jaiswal")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(f"Generated {OUT}")
