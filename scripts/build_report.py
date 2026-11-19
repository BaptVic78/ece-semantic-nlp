"""Build the English PDF from editable text and the actual evaluation results."""
import csv
from html import escape
import json
from pathlib import Path
import runpy

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf"
RESULTS = ROOT / "evaluation" / "results.json"
INK = colors.HexColor("#152b3b")
TEAL = colors.HexColor("#076e69")
MUTED = colors.HexColor("#42586a")
PALE = colors.HexColor("#eaf4f2")
RULE = colors.HexColor("#d3e3e2")
WIDTH = A4[0] - 100

styles = {
    "label": ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=10, leading=14,
                            textColor=TEAL, spaceAfter=12),
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=32, leading=36,
                            textColor=INK, spaceAfter=16),
    "heading": ParagraphStyle("heading", fontName="Helvetica-Bold", fontSize=12, leading=16,
                              textColor=TEAL, spaceBefore=9, spaceAfter=3, keepWithNext=True),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10.6, leading=15,
                           textColor=INK, spaceAfter=5),
    "small": ParagraphStyle("small", fontName="Helvetica", fontSize=9, leading=12, textColor=MUTED),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=9.4, leading=13, textColor=INK),
}


def p(value, style="body"):
    return Paragraph(escape(value), styles[style])


def table(rows, widths, padding=5):
    values = [[p(str(value), "cell") for value in row] for row in rows]
    obj = Table(values, colWidths=widths, repeatRows=1, hAlign="LEFT")
    obj.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fbfa")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), .35, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), padding),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
    ]))
    return obj


def footer(canvas, doc):
    width, height = A4
    canvas.setFillColor(TEAL)
    canvas.rect(0, height - 6, width, 6, fill=1, stroke=0)
    canvas.setStrokeColor(RULE)
    canvas.line(50, 45, width - 50, 45)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(50, 30, "ECE NLP PROJECT  /  TECHNICAL REPORT  /  NOVEMBER 2026")
    canvas.drawRightString(width - 50, 30, f"{doc.page:02d}")


def metric_rows(result):
    count = result["single_target_count"]
    return [["Metric", "Hits", "Rate"], *[
        [f"Top {rank}", f"{result[key]}/{count}", f"{result[key] / count:.1%}"]
        for rank, key in [(1, "top_one_hits"), (3, "top_three_hits")]
    ]]


def add_page_extras(story, index, result, names, verification):
    records = result["records"]
    if index == 0:
        story.extend([Spacer(1, 18), table(metric_rows(result), [WIDTH - 160, 80, 80]),
                      Spacer(1, 8), p("Fictional single-target cases. Results are for retrieval on this fixed set.", "small")])
    elif index == 1:
        categories = list(names.values())
        rows = [["Specialty", "Specialty", "Specialty"]]
        rows += [categories[n:n+3] for n in range(0, 15, 3)]
        story.extend([Spacer(1, 10), table(rows, [WIDTH / 3] * 3)])
    elif index == 2:
        story.extend([Spacer(1, 15), table([
            ["Quantity", "Definition"],
            ["Passage score", "s(i) = cosine(q, r(i)) = sum across 384 dimensions of q(j) * r(i,j)."],
            ["Specialty score", "S(k) = max of s(i) over references i assigned to specialty k."],
            ["Displayed result", "Sort specialties by S(k) and return the first three with their winning passages."],
        ], [118, WIDTH - 118])])
    elif index == 3:
        screenshot = OUT / "streamlit-demo.png"
        if screenshot.exists():
            w, h = ImageReader(str(screenshot)).getSize()
            factor = min(WIDTH / w, 345 / h)
            story.extend([Spacer(1, 10), Image(str(screenshot), w * factor, h * factor),
                          p("Figure 1. Live Streamlit results for a fictional skin example.", "small")])
        else:
            story.append(p("Browser capture unavailable. Results remain available in the saved evaluation.", "small"))
    elif index == 4:
        story.extend([Spacer(1, 12), table([
            ["Input to Qwen3", "Validation and rendering"],
            ["Fictional query and the three ranked passages", "Check IDs and match each proposed span to its own original string."],
            ["Scores and source URLs", "Use app-owned scores and links in the cards. Keep the retrieval order."],
            ["No accepted selection", "Show the deterministic note and the full matched passage."],
        ], [185, WIDTH - 185])])
    elif index == 5:
        rows = [["Case", "Expected", "Rank 1", "Score", "Target rank"]]
        for r in (r for r in records if r["group"] == "single"):
            first = r["matches"][0]
            position = next((i for i, m in enumerate(r["matches"], 1)
                             if m["specialty_id"] in r["expected"]), "-")
            rows.append([r["id"], r["expected"][0], first["specialty_id"], f"{first['score']:.3f}", position])
        story.extend([Spacer(1, 5), table(rows, [62, 100, 100, 90, WIDTH - 352], padding=3),
                      Spacer(1, 7), p("Category codes are the stable specialty_id values in the corpus.", "small")])
    elif index == 6:
        rows = [["Case", "First", "Second", "Third", "Top score"]]
        for r in (r for r in records if r["group"] != "single"):
            rows.append([r["id"]] + [m["specialty_id"] for m in r["matches"]]
                        + [f"{r['matches'][0]['score']:.3f}"])
        story.extend([Spacer(1, 8), table(rows, [72, 107, 107, 107, WIDTH - 393])])
    elif index == 7:
        story.extend([p("Executed checks", "heading"), p(verification), Spacer(1, 6), table([
            ["Purpose", "Command from the project directory (see README for environment variables)"],
            ["Install", "uv sync --locked"],
            ["Build corpus cache", "uv run --no-sync python scripts/build_embeddings.py"],
            ["Run app", "uv run --no-sync streamlit run app.py --server.address 127.0.0.1"],
            ["Measure", "uv run --no-sync python scripts/evaluate.py"],
            ["Test", "uv run --no-sync python -m unittest discover -s tests -v"],
            ["Build PDF", "uv run --no-sync --with reportlab python scripts/build_report.py"],
        ], [115, WIDTH - 115])])
        story.append(p("References", "heading"))
        for label, url in [
            ("NHS Conditions (45 individual URLs in data/source_audit.csv)", "https://www.nhs.uk/conditions/"),
            ("Sentence Transformers / MiniLM model card", "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2"),
            ("Ollama / Qwen3 8B model and licence", "https://ollama.com/library/qwen3:8b"),
            ("Ollama / Generate API", "https://docs.ollama.com/api/generate"),
            ("Ollama / Windows setup", "https://docs.ollama.com/windows"),
        ]:
            story.append(Paragraph(f'<link href="{escape(url)}" color="#076e69">{escape(label)}</link>', styles["small"]))


def main():
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    with (ROOT / "data" / "specialities.csv").open(encoding="utf-8", newline="") as file:
        names = {r["specialty_id"]: r["specialty"] for r in csv.DictReader(file)}
    content = runpy.run_path(str(OUT / "report_content.py"))
    verification = (OUT / "verification.txt").read_text(encoding="utf-8").strip()
    story = []
    for index, (label, title, sections) in enumerate(content["PAGES"]):
        if index:
            story.append(PageBreak())
        story.extend([p(label, "label"), p(title, "title")])
        for head, body in sections:
            story.extend([p(head, "heading"), p(body)])
        add_page_extras(story, index, result, names, verification)
    report = OUT / "semantic-specialty-report.pdf"
    doc = SimpleDocTemplate(str(report), pagesize=A4, rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=60, title="Medical specialty text matching")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(report)


if __name__ == "__main__":
    main()
