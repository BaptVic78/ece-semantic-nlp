"""Render the current report from its editable prose and saved measurements."""
import csv
from hashlib import sha256
from html import escape
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle

from report_content import SECTIONS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MARGIN = 53
WIDTH = A4[0] - MARGIN * 2
INK = colors.HexColor("#251e37")
MUTED = colors.HexColor("#524b65")
ACCENT = colors.HexColor("#5938a2")
TINT = colors.HexColor("#f1edf9")
LINE = colors.HexColor("#ded7eb")

STYLES = {
    "label": ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=10, leading=14,
                            textColor=ACCENT, spaceAfter=10),
    "title": ParagraphStyle("title", fontName="Times-Bold", fontSize=33, leading=37,
                            textColor=INK, spaceAfter=15),
    "lead": ParagraphStyle("lead", fontName="Times-Italic", fontSize=15, leading=20,
                           textColor=MUTED, spaceAfter=17),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=11, leading=16,
                           textColor=INK, spaceAfter=12),
    "caption": ParagraphStyle("caption", fontName="Helvetica", fontSize=9, leading=13,
                              textColor=MUTED, spaceBefore=6, spaceAfter=10),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=9.7, leading=13, textColor=INK),
    "column": ParagraphStyle("column", fontName="Helvetica-Bold", fontSize=9.3, leading=13, textColor=INK),
    "subhead": ParagraphStyle("subhead", fontName="Helvetica-Bold", fontSize=12, leading=16,
                              textColor=ACCENT, spaceAfter=6, spaceBefore=9, keepWithNext=True),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=8.8, leading=13, textColor=INK),
}


def para(text, style="body"):
    return Paragraph(escape(text), STYLES[style])


def grid(rows, widths):
    cells = [[para(str(v), "column" if i == 0 else "cell") for v in row] for i, row in enumerate(rows)]
    table = Table(cells, colWidths=widths, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TINT),
        ("LINEBELOW", (0, 0), (-1, -1), .4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def frame(canvas, doc):
    w, h = A4
    canvas.setFillColor(ACCENT)
    canvas.rect(0, h - 5, w, 5, fill=1, stroke=0)
    canvas.setStrokeColor(LINE)
    canvas.line(MARGIN, 46, w - MARGIN, 46)
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, 30, "ECE NLP Project  /  Medical Specialty Finder")
    canvas.drawRightString(w - MARGIN, 30, str(doc.page))


def comparison_table(data):
    header = ["Cases", "Passages", "Top one", "Top three"]
    rows = [header]
    for key, name in (("original", "Original test"), ("new", "New test")):
        for size in ("45", "210"):
            summary = data["evaluations"][key]["summary"][size]
            n = summary["single_count"]
            values = [summary[k] for k in ("top_one", "top_three")]
            rows.append([name, size, *(f"{v}/{n} ({v/n:.1%})" for v in values)])
    return grid(rows, [140, 80, 130, WIDTH - 350])


def case_table(data):
    rows = [["Case", "Expected specialty", "Rank with 45", "Rank with 210"]]
    for group, case_id, label in (
        ("original", "S04", "Cardiology"),
        ("original", "S12", "Endocrinology"),
        ("new", "N18", "Orthopedics"),
        ("new", "N12", "Gastroenterology"),
    ):
        case = next(r for r in data["evaluations"][group]["records"] if r["id"] == case_id)
        ranks = [str(next((i for i, m in enumerate(case["rankings"][size], 1)
                           if m["specialty_id"] in case["expected"]), "Outside top 3"))
                 for size in ("45", "210")]
        rows.append([case_id, label, *ranks])
    return grid(rows, [65, 155, 130, WIDTH - 350])


def screenshot():
    asset = HERE / "streamlit-demo.png"
    w, h = ImageReader(str(asset)).getSize()
    scale = min(WIDTH / w, 374 / h)
    return Image(str(asset), w * scale, h * scale)


def reproduce():
    command = Preformatted(
        "$env:HF_HOME = Join-Path (Get-Location) '.hf-cache'\n"
        "uv sync --locked\n"
        "uv run --no-sync python scripts/build_embeddings.py\n"
        "uv run --no-sync streamlit run app.py\n"
        "uv run --no-sync python scripts/compare_corpora.py",
        STYLES["code"],
    )
    box = Table([[command]], colWidths=[WIDTH], hAlign="LEFT")
    box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TINT),
                              ("TOPPADDING", (0, 0), (-1, -1), 9),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                              ("LEFTPADDING", (0, 0), (-1, -1), 12)]))
    references = [
        ("[1] NHS. Conditions A to Z.", "https://www.nhs.uk/conditions/"),
        ("[2] Sentence Transformers. all-MiniLM-L6-v2 model card.",
         "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2"),
        ("[3] Ollama. Qwen3 8B model and licence.", "https://ollama.com/library/qwen3:8b"),
        ("[4] Ollama. Generate API.", "https://docs.ollama.com/api/generate"),
    ]
    return [
        para("PowerShell, from the project directory", "subhead"),
        box,
        para("Run the last command in a separate terminal or after stopping Streamlit. Set HF_HOME in each new terminal. Once the model is cached, setting HF_HUB_OFFLINE to '1' avoids network access for MiniLM.", "caption"),
        para("Project files", "subhead"),
        para("The two corpora are in data/. The input cases and corpus_comparison.json are in evaluation/. For the original 45-reference run, see the baseline instructions in README.md."),
        para("References", "subhead"),
        *[Paragraph(f'<link href="{escape(url)}" color="#5938a2">{escape(label)}</link>', STYLES["caption"])
          for label, url in references],
    ]


def main():
    data = json.loads((ROOT / "evaluation" / "corpus_comparison.json").read_text(encoding="utf-8"))
    for mapping, fingerprints in (
        ({"45": "data/specialities.csv", "210": "data/specialities_210.csv"}, data["corpus_sha256"]),
        ({"original": "evaluation/cases.csv", "new": "evaluation/comparison_cases.csv"}, data["case_set_sha256"]),
    ):
        for name, path in mapping.items():
            if sha256((ROOT / path).read_bytes()).hexdigest() != fingerprints[name]:
                raise ValueError(f"Saved evaluation does not match {path}. Rerun compare_corpora.py.")
    with (ROOT / "data" / "specialities_210.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    story = []
    for i, section in enumerate(SECTIONS):
        if i:
            story.append(PageBreak())
        story.extend([para(section["label"], "label"), para(section["title"], "title")])
        if "lead" in section:
            story.append(para(section["lead"], "lead"))
        story.extend(para(text) for text in section["paragraphs"])
        if i == 0:
            story.extend([para("Corpus at a glance", "subhead"), grid([
                ["Reference descriptions", "Specialties", "Descriptions per specialty", "Source URLs"],
                [len(rows), len({r["specialty_id"] for r in rows}), 14, len({r["source_url"] for r in rows})],
            ], [115, 84, 166, WIDTH - 365])])
        elif i == 1:
            story.extend([para("Scoring in two steps", "subhead"), grid([
                ["Step", "Calculation"],
                ["Passage", "s(i) = q dot r(i), where q and r(i) have unit length."],
                ["Specialty", "S(k) = max s(i) over passages i assigned to specialty k."],
            ], [115, WIDTH - 115])])
        elif i == 2:
            story.extend([screenshot(), para("Figure 1. Current Streamlit results for the cough, fever and vomiting query, shown with the standard explanation.", "caption")])
        elif i == 3:
            story.extend([comparison_table(data), Spacer(1, 14)])
        elif i == 4:
            story.extend([para("Selected changes in target rank", "subhead"), case_table(data)])
        elif i == 5:
            story.extend(reproduce())
        story.extend(para(text) for text in section.get("after", []))
    output = HERE / "semantic-specialty-report.pdf"
    document = SimpleDocTemplate(str(output), pagesize=A4, title="Medical Specialty Finder",
                                 leftMargin=MARGIN, rightMargin=MARGIN, topMargin=56, bottomMargin=61)
    document.build(story, onFirstPage=frame, onLaterPages=frame)
    print(output)


if __name__ == "__main__":
    main()
