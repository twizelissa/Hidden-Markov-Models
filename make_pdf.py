"""
Convert Report_Final.md to a professional PDF using ReportLab.
Figures are embedded from the figures/ directory.
"""

import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.units import inch
from PIL import Image as PILImage

PAGE_W, PAGE_H = A4
MARGIN = 1.5 * cm
CONTENT_W = PAGE_W - 2 * MARGIN

# ── Style setup ─────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_style(name, parent='Normal', **kwargs):
    s = ParagraphStyle(name, parent=styles[parent], **kwargs)
    return s

title_style = make_style('ReportTitle', 'Title',
    fontSize=15, textColor=colors.HexColor('#1a1a2e'),
    spaceAfter=2, alignment=TA_CENTER, fontName='Helvetica-Bold')

subtitle_style = make_style('Subtitle', 'Normal',
    fontSize=9, textColor=colors.HexColor('#555555'),
    spaceAfter=6, alignment=TA_CENTER)

h1_style = make_style('H1', 'Heading1',
    fontSize=11, textColor=colors.HexColor('#1a1a2e'),
    spaceBefore=8, spaceAfter=2, fontName='Helvetica-Bold',
    borderPad=1)

h2_style = make_style('H2', 'Heading2',
    fontSize=10, textColor=colors.HexColor('#2e4057'),
    spaceBefore=6, spaceAfter=2, fontName='Helvetica-Bold')

h3_style = make_style('H3', 'Heading3',
    fontSize=9.5, textColor=colors.HexColor('#2e4057'),
    spaceBefore=5, spaceAfter=1, fontName='Helvetica-BoldOblique')

body_style = make_style('Body', 'Normal',
    fontSize=8.5, leading=12, spaceAfter=4, alignment=TA_JUSTIFY)

caption_style = make_style('Caption', 'Normal',
    fontSize=8.5, textColor=colors.HexColor('#444444'),
    alignment=TA_CENTER, spaceAfter=8, fontName='Helvetica-Oblique')

code_style = make_style('Code', 'Code',
    fontSize=8, fontName='Courier', backColor=colors.HexColor('#f5f5f5'),
    spaceAfter=4, spaceBefore=2, leading=11)

bullet_style = make_style('Bullet', 'Normal',
    fontSize=8.5, leading=12, spaceAfter=2,
    leftIndent=14, bulletIndent=0)

table_header_style = make_style('TableHeader', 'Normal',
    fontSize=9, fontName='Helvetica-Bold',
    textColor=colors.white, alignment=TA_CENTER)

table_body_style = make_style('TableBody', 'Normal',
    fontSize=8.5, leading=12, alignment=TA_LEFT)

eq_style = make_style('Equation', 'Normal',
    fontSize=9, fontName='Courier', alignment=TA_CENTER,
    spaceAfter=6, spaceBefore=4, textColor=colors.HexColor('#1a1a2e'))

# ── Table style ──────────────────────────────────────────────────────────────
TABLE_STYLE = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
    ('FONTSIZE', (0, 1), (-1, -1), 7.5),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
    ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
    ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 2),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ('ROWBACKGROUNDS', (0, 0), (-1, 0), [colors.HexColor('#1a1a2e')]),
])

def make_table(rows):
    col_count = max(len(r) for r in rows)
    col_w = CONTENT_W / col_count
    col_widths = [col_w] * col_count
    cells = [[Paragraph(str(c), table_body_style) for c in row] for row in rows]
    cells[0] = [Paragraph(str(c), table_header_style) for c in rows[0]]
    t = Table(cells, colWidths=col_widths, repeatRows=1)
    t.setStyle(TABLE_STYLE)
    return t

def embed_image(path, caption=None, max_h_override=None):
    if not os.path.exists(path):
        return []
    pil = PILImage.open(path)
    w, h = pil.size
    max_w = CONTENT_W
    max_h = max_h_override if max_h_override else 6.0 * cm
    ratio = min(max_w / w, max_h / h)
    disp_w = w * ratio
    disp_h = h * ratio
    items = [
        Spacer(1, 2),
        Image(path, width=disp_w, height=disp_h),
    ]
    if caption:
        items.append(Paragraph(caption, caption_style))
    items.append(Spacer(1, 2))
    return items


def embed_image_pair(path1, path2, caption1=None, caption2=None):
    """Render two images side by side in a two-column table."""
    items = []
    col_w = (CONTENT_W - 0.3 * cm) / 2
    max_h = 4.5 * cm

    def scale(p):
        if not os.path.exists(p):
            return None, 0, 0
        pil = PILImage.open(p)
        w, h = pil.size
        ratio = min(col_w / w, max_h / h)
        return p, w * ratio, h * ratio

    p1, w1, h1 = scale(path1)
    p2, w2, h2 = scale(path2)
    disp_h = max(h1, h2)

    row = []
    for p, w, cap in [(p1, w1, caption1), (p2, w2, caption2)]:
        cell = []
        if p:
            cell.append(Image(p, width=w, height=disp_h))
        if cap:
            cell.append(Paragraph(cap, caption_style))
        row.append(cell)

    t = Table([row], colWidths=[col_w, col_w])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    items.append(Spacer(1, 2))
    items.append(t)
    items.append(Spacer(1, 2))
    return items

# ── Parse markdown ────────────────────────────────────────────────────────────
def inline_fmt(text):
    """Convert inline markdown bold/italic/code to ReportLab XML."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'`(.+?)`', r'<font name="Courier" size="8.5" color="#c0392b">\1</font>', text)
    text = re.sub(r'\$\$?.+?\$\$?', lambda m: (
        '<font name="Courier" color="#1a1a2e">' + m.group(0).strip('$') + '</font>'
    ), text)
    # convert markdown links to clickable ReportLab hyperlinks
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)',
                  r'<a href="\2" color="#0563C1"><u>\1</u></a>', text)
    return text

def parse_md(md_path):
    with open(md_path, encoding='utf-8') as f:
        lines = f.readlines()

    story = []
    i = 0
    in_table = False
    table_rows = []
    pending_figs = []   # list of (path, caption)

    def flush_figs():
        nonlocal pending_figs
        if not pending_figs:
            return
        if len(pending_figs) == 1:
            path, cap = pending_figs[0]
            # transition matrix (2x2 grid) and Viterbi (4-subplot) need taller slot
            mh = 7.0 * cm if 'cell_22' in path else 5.0 * cm
            story.extend(embed_image(path, cap, max_h_override=mh))
        elif len(pending_figs) == 2:
            (p1, c1), (p2, c2) = pending_figs
            story.extend(embed_image_pair(p1, p2, c1, c2))
        else:
            for path, cap in pending_figs:
                story.extend(embed_image(path, cap))
        pending_figs = []

    # group figure pairs: figures 1+2 side-by-side, 5+6 side-by-side
    fig_pair_keys = {
        'cell_09.png': 'cell_09_3.png',   # Fig1 pairs with Fig2
        'cell_34.png': 'cell_38.png',      # Fig6 pairs with confusion matrix (cell_38)
    }

    while i < len(lines):
        line = lines[i].rstrip('\n')

        # --- figure image embed ---
        img_match = re.match(r'!\[([^\]]*)\]\(([^\)]+)\)', line.strip())
        if img_match:
            pending_figs.append([img_match.group(2), None])   # path, caption TBD
            i += 1
            continue

        # --- figure caption (the **Figure N.** line after an image) ---
        if pending_figs and pending_figs[-1][1] is None and line.strip().startswith('**Figure'):
            pending_figs[-1][1] = inline_fmt(line.strip())
            # peek: if next non-blank line is another image, keep accumulating
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            next_line = lines[j].strip() if j < len(lines) else ''
            if not re.match(r'!\[', next_line):
                flush_figs()
            i += 1
            continue

        # flush any pending figures before processing other content
        if pending_figs and line.strip() and not re.match(r'!\[', line.strip()):
            flush_figs()

        # --- horizontal rule ---
        if re.match(r'^---+$', line.strip()):
            story.append(HRFlowable(width='100%', thickness=0.5,
                                     color=colors.HexColor('#cccccc'),
                                     spaceAfter=4, spaceBefore=4))
            i += 1
            continue

        # --- headings ---
        h_match = re.match(r'^(#{1,4})\s+(.+)$', line)
        if h_match:
            level = len(h_match.group(1))
            text = inline_fmt(h_match.group(2))
            if level == 1:
                story.append(Paragraph(text, h1_style))
            elif level == 2:
                story.append(Paragraph(text, h2_style))
            else:
                story.append(Paragraph(text, h3_style))
            i += 1
            continue

        # --- table ---
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            # skip separator rows like |---|---|
            if not all(re.match(r'^[-: ]+$', c) for c in cells):
                table_rows.append(cells)
            i += 1
            continue
        else:
            if in_table and table_rows:
                story.append(make_table(table_rows))
                story.append(Spacer(1, 4))
                in_table = False
                table_rows = []

        # --- fenced code blocks ---
        if line.strip().startswith('```'):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i].rstrip('\n'))
                i += 1
            story.append(Paragraph('<br/>'.join(code_lines), code_style))
            i += 1
            continue

        # --- equations ($$...$$) spanning lines ---
        if line.strip().startswith('$$'):
            eq = line.strip().strip('$')
            if not eq:
                i += 1
                eq_lines = []
                while i < len(lines) and '$$' not in lines[i]:
                    eq_lines.append(lines[i].rstrip('\n').strip())
                    i += 1
                eq = ' '.join(eq_lines)
            story.append(Paragraph(eq, eq_style))
            i += 1
            continue

        # --- bullet / numbered lists ---
        bullet_match = re.match(r'^(\s*)([-*]|\d+\.)\s+(.+)$', line)
        if bullet_match:
            text = inline_fmt(bullet_match.group(3))
            indent = len(bullet_match.group(1))
            style = ParagraphStyle('BulletN', parent=bullet_style,
                                   leftIndent=14 + indent * 10)
            story.append(Paragraph('&#x2022; ' + text, style))
            i += 1
            continue

        # --- blank line ---
        if not line.strip():
            story.append(Spacer(1, 4))
            i += 1
            continue

        # --- normal paragraph ---
        text = inline_fmt(line.strip())
        if text:
            story.append(Paragraph(text, body_style))
        i += 1

    # flush trailing table / figures
    if in_table and table_rows:
        story.append(make_table(table_rows))
    flush_figs()

    return story

# ── Build PDF ─────────────────────────────────────────────────────────────────
def build_pdf(md_path, out_path):
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.2*cm, bottomMargin=1.2*cm,
        title='HMM Activity Recognition Report',
        author='Elissa Twizeyimana & Uwingabire Caline',
    )

    story = parse_md(md_path)
    doc.build(story)
    print('PDF saved to:', out_path)

if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base)
    build_pdf('Report_Final.md', 'Report_Final.pdf')
