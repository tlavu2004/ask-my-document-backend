# scripts/make_sample_pdf.py
import os
import platform
import urllib.request
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, ListFlowable, ListItem
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ====== FONT SETUP ======
FONTS_DIR = Path(__file__).parent.parent / "fonts"
FONTS_DIR.mkdir(parents=True, exist_ok=True)
FONT_NAME = "CustomFont"

def get_font_path():
    system = platform.system()
    if system == "Windows":
        # Use Arial if available
        arial_path = r"C:\Windows\Fonts\arial.ttf"
        if os.path.exists(arial_path):
            return arial_path
        
    # Default: DejaVuSans from fonts/ folder
    dejavu_path = FONTS_DIR / "DejaVuSans.ttf"
    if not dejavu_path.exists():
        print("Downloading DejaVuSans.ttf...")
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        urllib.request.urlretrieve(url, dejavu_path)
    return str(dejavu_path)

FONT_PATH = get_font_path()
pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))

# ====== CREATE CUSTOM STYLES ======
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    name="Title",
    fontName=FONT_NAME,
    parent=styles["Heading1"],
    alignment=TA_CENTER,
    fontSize=18,
    leading=22,
)
h2_style = ParagraphStyle(
    name="Heading2",
    fontName=FONT_NAME,
    parent=styles["Heading2"],
    alignment=TA_LEFT,
    fontSize=14,
    leading=18,
)
body_style = ParagraphStyle(
    name="Body",
    fontName=FONT_NAME,
    parent=styles["BodyText"],
    fontSize=11,
    leading=15,
)

def make_pdf(output_path: Path):
    """Make a sample PDF for testing."""
    
    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    story = []

    story.append(Paragraph("Sample PDF for Tests — Ask My Document", title_style))
    story.append(Spacer(1, 12))

    intro = (
        "This document is created to test PDF text extraction. "
        "It contains multiple paragraphs, lists, a small table, and multilingual content "
        "including Vietnamese characters."
    )
    story.append(Paragraph(intro, body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Mục tiêu kiểm thử", h2_style))
    story.append(Spacer(1, 6))

    vn_paragraph = (
        "Tài liệu này dùng để kiểm tra chức năng trích xuất văn bản từ file PDF. "
        "Nội dung bao gồm nhiều đoạn văn, danh sách, và một bảng nhỏ. "
        "Các đoạn tiếng Việt có dấu: âm, ươ, ứ, ệ, ồ, ẵ — để chắc chắn parser xử lý Unicode tốt."
    )
    story.append(Paragraph(vn_paragraph, body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Notes: The module should extract sentences, preserve punctuation, and detect numbers such as 2025, 3.14, "
        "and phone-like patterns (e.g., +84-123-456-789).", body_style))
    story.append(Spacer(1, 10))

    bullets = [
        Paragraph("First bullet: Python is a programming language.", body_style),
        Paragraph("Second bullet: FastAPI is used for APIs.", body_style),
        Paragraph("Third bullet: FAISS and embeddings for retrieval.", body_style),
    ]
    story.append(Paragraph("Key points:", h2_style))
    story.append(Spacer(1, 6))
    story.append(ListFlowable([ListItem(x) for x in bullets], bulletType='bullet'))
    story.append(Spacer(1, 12))

    num_items = [
        Paragraph("Step 1: Upload the document.", body_style),
        Paragraph("Step 2: Extract and chunk the text.", body_style),
        Paragraph("Step 3: Build FAISS index and store metadata.", body_style),
    ]
    story.append(Paragraph("Workflow:", h2_style))
    story.append(Spacer(1, 6))
    story.append(ListFlowable([ListItem(x) for x in num_items], bulletType='1'))
    story.append(Spacer(1, 12))

    table_data = [
        ["Name", "Description", "Qty"],
        ["Sample doc", "A short text sample", "1"],
        ["Test cases", "Unit + Integration", "5"],
    ]
    table = Table(table_data, colWidths=[120, 250, 60])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (2, 1), (2, -1), "CENTER"),
    ]))
    story.append(Paragraph("Summary table:", h2_style))
    story.append(Spacer(1, 6))
    story.append(table)
    story.append(Spacer(1, 20))

    story.append(Paragraph(
        "End of document. Special characters: © ® — ©2025. "
        "Multilingual snippet: Xin chào, thế giới! — Cảm ơn bạn.",
        body_style))

    doc.build(story)
    return output_path

if __name__ == "__main__":
    OUT_DIR = Path("tests/resources")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH = OUT_DIR / "sample.pdf"
    make_pdf(OUT_PATH)
    print(f"Created sample PDF at: {OUT_PATH} (Font: {FONT_PATH})")
