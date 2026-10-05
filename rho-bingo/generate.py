"""Rho Bingo — Family Day.

Generates:
  rho-bingo-cards.pdf        5 different 4x4 cards + a "How to play" sheet, each A5,
                             two per A4 sheet (cut in half)
  rho-bingo-host-script.pdf  A4 text to read aloud (English) with the bingo words highlighted

Logo: rho-bingo/logo.pdf (vector, embedded as is) or logo.png / logo.jpg.
Without one a plain "Rho" wordmark is drawn in its place.

    pip install reportlab pdfrw
    python3 rho-bingo/generate.py
"""

import random
import re
from itertools import permutations
from pathlib import Path

from pdfrw import PdfReader as PdfrwReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from reportlab.lib.colors import CMYKColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, A5, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

HERE = Path(__file__).resolve().parent

# --- Colours: CMYK, the blue and green are taken from the Rho logo ---------------
BLUE = CMYKColor(0.94, 0.71, 0.21, 0.05)
GREEN = CMYKColor(0.60, 0.05, 0.95, 0)
TINT = CMYKColor(0.08, 0.03, 0, 0)          # cell background
GREEN_TINT = CMYKColor(0.14, 0, 0.26, 0)    # highlighter in the host script
LINE = CMYKColor(0.22, 0.12, 0.02, 0)
MUTED = CMYKColor(0.40, 0.28, 0.15, 0.30)

# --- Fonts ---------------------------------------------------------------------
for name in ("Regular", "SemiBold", "Bold", "ExtraBold"):
    pdfmetrics.registerFont(TTFont(f"Montserrat-{name}", HERE / "fonts" / f"Montserrat-{name}.ttf"))
pdfmetrics.registerFontFamily(
    "Montserrat", normal="Montserrat-Regular", bold="Montserrat-Bold",
    italic="Montserrat-Regular", boldItalic="Montserrat-Bold",
)

# --- Text read aloud by the host -----------------------------------------------
INTRO = [
    "Welcome to Rho Bingo!",
    "In a moment you will hear a short story about our company. "
    "Each of you has received a bingo card with different words.",
    "Here's how to play: each time you hear a word from your card, cross it out. As soon as "
    "you have four crossed-out words in a line \u2013 across, down or diagonally \u2013 shout "
    "\u201cBINGO!\u201d and raise your card so we can check it.",
]

SCRIPT = [
    "Rho's story began over 40 years ago. Since then, the company has helped advance "
    "clinical research, supported science and worked with experts all over the world. "
    "You could say that Rho grew up together with modern medicine.",

    "At Rho, we believe the best things come from collaboration. That's why every day "
    "specialists, researchers, statisticians, programmers and many others come together "
    "here to solve challenges as a team. Sometimes at a desk, sometimes in an online meeting, "
    "and sometimes over a good cup of coffee.",

    "Our mission is to improve health, extend lives and raise people's quality of life. "
    "It sounds serious, but that is exactly why we value creativity, innovation and "
    "a positive attitude. Because the best ideas often appear when someone dares to look "
    "at a problem from a completely different angle.",

    "As a company, we focus on honesty, trust and relationships. We value people who think "
    "independently, but who can also work as a team.",

    "Growth is very important to us. We learn new things, gain experience and we are not "
    "afraid of change. Flexibility matters, because the world keeps racing forward. Luckily, "
    "we have people full of energy, passion and commitment, who can find their way even in "
    "the most surprising situations.",

    "Our work helps clients, researchers and, above all, patients. It is for them that new "
    "solutions and therapies are created. Every project is another step towards a better future.",

    "So what makes Rho unique? According to the company, it is the so-called Cohesion Effect: "
    "the power of connections between people, science and a shared purpose. We could simply "
    "say: great people doing important things together.",

    "That's why, regardless of role, department or location, we are all one team. And today's "
    "Family Day is a perfect opportunity to meet the people we work with every day, and to show "
    "our loved ones where we spend a big part of our time.",

    "Thank you for being here with us today! And remember: if you complete a line while "
    "listening, shout “BINGO!” out loud.",
]

# Every word below appears in SCRIPT (checked at start-up).
WORDS = [
    "40 Years", "Clinical Research", "Science", "Experts", "Medicine",
    "Collaboration", "Specialists", "Researchers", "Statisticians", "Programmers",
    "Challenges", "Desk", "Online Meeting", "Coffee", "Mission",
    "Health", "Quality of Life", "Creativity", "Innovation", "Positive Attitude",
    "Ideas", "Honesty", "Trust", "Relationships", "Team",
    "Growth", "Experience", "Change", "Flexibility", "Energy",
    "Passion", "Commitment", "Clients", "Patients", "Therapies",
    "Solutions", "Future", "Cohesion Effect", "Great People", "Family Day",
]

N_CARDS = 5
SIZE = 4
LINES = (
    [[(r, c) for c in range(SIZE)] for r in range(SIZE)]
    + [[(r, c) for r in range(SIZE)] for c in range(SIZE)]
    + [[(i, i) for i in range(SIZE)], [(i, SIZE - 1 - i) for i in range(SIZE)]]
)


def word_pattern(word):
    return re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)


def first_mentions():
    """Position of each word's first mention, as a fraction (0..1) of the read-aloud text."""
    text = " ".join(SCRIPT)
    out = {}
    for w in WORDS:
        m = word_pattern(w).search(text)
        if not m:
            raise SystemExit(f"'{w}' does not appear in the script")
        out[w] = m.start() / len(text)
    return out


def first_line_at(grid, when):
    return min(max(when[grid[r][c]] for r, c in line) for line in LINES)


# Where in the story (0..1) each card should get its first full line: nobody wins in the
# first half, and the cards win one after another rather than all at once.
TARGETS = (0.50, 0.57, 0.65, 0.71, 0.80)


def build_cards():
    """5 cards x 16 words from 40: every word is on exactly 2 cards and any two cards share
    exactly 4 words (each of the 10 card pairs gets its own 4 words). The grid layouts are
    then picked so the cards' first full lines land as close to TARGETS as possible."""
    when = first_mentions()
    pairs = [(a, b) for a in range(N_CARDS) for b in range(a + 1, N_CARDS)]
    best_error, best = None, None
    for seed in range(200):
        rng = random.Random(seed)
        words = WORDS[:]
        rng.shuffle(words)
        cards = [[] for _ in range(N_CARDS)]
        for i, (a, b) in enumerate(pairs):
            for w in words[i * 4:(i + 1) * 4]:
                cards[a].append(w)
                cards[b].append(w)
        layouts = []  # per card: first-line moment -> grid
        for card in cards:
            found = {}
            for _ in range(400):
                rng.shuffle(card)
                grid = [card[r * SIZE:(r + 1) * SIZE] for r in range(SIZE)]
                found.setdefault(first_line_at(grid, when), grid)
            layouts.append(found)
        for order in permutations(range(N_CARDS)):
            picks = {i: min(layouts[i], key=lambda t: abs(t - target))
                     for i, target in zip(order, TARGETS)}
            moments = sorted(picks.values())
            if min(b - a for a, b in zip(moments, moments[1:])) < 0.03:
                continue  # two cards would shout BINGO at the same word
            error = sum(abs(picks[i] - target) for i, target in zip(order, TARGETS))
            if best_error is None or error < best_error:
                best_error, best = error, [layouts[i][picks[i]] for i in range(N_CARDS)]
    return best, when


# --- Drawing helpers -----------------------------------------------------------
def logo_file():
    for name in ("logo.pdf", "logo.png", "logo.jpg", "logo.jpeg"):
        if (HERE / name).exists():
            return HERE / name
    return None


def draw_logo(c, x, y_top, max_w, max_h):
    path = logo_file()
    if path and path.suffix == ".pdf":
        form = pagexobj(PdfrwReader(str(path)).pages[0])
        x0, y0, x1, y1 = (float(v) for v in form.BBox)
        scale = min(max_w / (x1 - x0), max_h / (y1 - y0))
        c.saveState()
        c.translate(x - x0 * scale, y_top - (y1 - y0) * scale - y0 * scale)
        c.scale(scale, scale)
        c.doForm(makerl(c, form))
        c.restoreState()
        return
    if path:
        img = ImageReader(str(path))
        iw, ih = img.getSize()
        scale = min(max_w / iw, max_h / ih)
        w, h = iw * scale, ih * scale
        c.drawImage(img, x, y_top - h, w, h, mask="auto")
        return
    c.setFillColor(BLUE)
    c.setFont("Montserrat-ExtraBold", max_h / mm * 2.2)
    c.drawString(x, y_top - max_h * 0.82, "Rho")


def spaced(c, text, x, y, font, size, spacing, align="left"):
    width = sum(pdfmetrics.stringWidth(ch, font, size) for ch in text) + spacing * (len(text) - 1)
    if align == "right":
        x -= width
    elif align == "center":
        x -= width / 2
    c.setFont(font, size)
    for ch in text:
        c.drawString(x, y, ch)
        x += pdfmetrics.stringWidth(ch, font, size) + spacing
    return width


def wrap(word, font, size, max_w):
    lines, current = [], ""
    for part in word.split():
        trial = f"{current} {part}".strip()
        if current and pdfmetrics.stringWidth(trial, font, size) > max_w:
            lines.append(current)
            current = part
        else:
            current = trial
    lines.append(current)
    return lines


def fits(size, font, max_w):
    return all(
        pdfmetrics.stringWidth(line, font, size) <= max_w and len(wrap(w, font, size, max_w)) <= 2
        for w in WORDS for line in wrap(w, font, size, max_w)
    )


# --- Card ----------------------------------------------------------------------
CELL = 30 * mm
CELL_PAD = 2 * mm
CELL_FONT = "Montserrat-Bold"
# largest size at which every word fits its cell in at most two lines
CELL_SIZE_PT = next(s for s in (11, 10.5, 10, 9.5, 9, 8.5, 8)
                    if fits(s, CELL_FONT, CELL - 2 * CELL_PAD))


def draw_header(c, W, H, title, title_size, tag=None):
    """Frame, logo, Family Day label and title shared by the cards and the rules sheet."""
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.roundRect(6 * mm, 6 * mm, W - 12 * mm, H - 12 * mm, 4 * mm, stroke=1, fill=0)

    left, right = 13 * mm, W - 13 * mm
    draw_logo(c, left, H - 13 * mm, 48 * mm, 12 * mm)

    pill_w, pill_h = 32 * mm, 6.2 * mm
    c.setFillColor(GREEN)
    c.roundRect(right - pill_w, H - 13 * mm - pill_h, pill_w, pill_h, pill_h / 2, stroke=0, fill=1)
    c.setFillColor(white)
    spaced(c, "FAMILY DAY", right - pill_w / 2, H - 13 * mm - pill_h + 2.05 * mm,
           "Montserrat-ExtraBold", 7.5, 1.2, align="center")
    if tag:
        c.setFillColor(MUTED)
        spaced(c, tag, right, H - 25 * mm, "Montserrat-SemiBold", 7, 1.2, align="right")

    c.setFillColor(BLUE)
    spaced(c, title, W / 2, H - 40 * mm, "Montserrat-ExtraBold", title_size, title_size / 10,
           align="center")
    parts = [("Listen", BLUE), ("  \u2022  ", GREEN), ("Mark", BLUE), ("  \u2022  ", GREEN),
             ("Shout BINGO!", BLUE)]
    c.setFont("Montserrat-SemiBold", 9)
    x = W / 2 - sum(pdfmetrics.stringWidth(t, "Montserrat-SemiBold", 9) for t, _ in parts) / 2
    for text, colour in parts:
        c.setFillColor(colour)
        c.drawString(x, H - 47 * mm, text)
        x += pdfmetrics.stringWidth(text, "Montserrat-SemiBold", 9)


def draw_card(c, ox, oy, number, grid, cell_size=CELL):
    W, H = A5
    c.saveState()
    c.translate(ox, oy)
    draw_header(c, W, H, "BINGO", 40, tag=f"CARD {number:02d}")

    # grid
    gap = 2.4 * mm
    grid_w = SIZE * cell_size + (SIZE - 1) * gap
    gx = (W - grid_w) / 2
    gy_top = H - 52 * mm
    pad = CELL_PAD
    for r in range(SIZE):
        for col in range(SIZE):
            x = gx + col * (cell_size + gap)
            y = gy_top - (r + 1) * cell_size - r * gap
            c.setFillColor(TINT)
            c.roundRect(x, y, cell_size, cell_size, 2.6 * mm, stroke=0, fill=1)
            lines = wrap(grid[r][col], CELL_FONT, CELL_SIZE_PT, cell_size - 2 * pad)
            leading = CELL_SIZE_PT * 1.18
            block = leading * (len(lines) - 1)
            base = y + cell_size / 2 + block / 2 - CELL_SIZE_PT * 0.35
            c.setFillColor(BLUE)
            c.setFont(CELL_FONT, CELL_SIZE_PT)
            for i, line in enumerate(lines):
                c.drawCentredString(x + cell_size / 2, base - i * leading, line)

    # footer: name line + rules
    grid_bottom = gy_top - SIZE * cell_size - (SIZE - 1) * gap
    y = grid_bottom - 9 * mm
    c.setFillColor(BLUE)
    c.setFont("Montserrat-SemiBold", 8.5)
    c.drawString(gx, y, "Name:")
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.line(gx + 11 * mm, y - 0.8 * mm, gx + grid_w, y - 0.8 * mm)

    c.setFillColor(MUTED)
    c.setFont("Montserrat-Regular", 7.2)
    c.drawCentredString(W / 2, y - 7 * mm,
                        "Cross out every word you hear in the story about Rho.")
    c.drawCentredString(W / 2, y - 10.6 * mm,
                        "Complete a full row, column or diagonal and shout “BINGO!”")
    c.restoreState()


RULES = [
    ("Grab a pen", "Write your name on your card. Every card is different."),
    ("Listen", "The host reads a short story about Rho."),
    ("Cross out your words", "Each time you hear a word from your card, cross it out."),
    ("Make a line", "Cross out 4 words in a line: across, down or diagonally."),
    ("Shout BINGO!", "Shout it out loud and raise your card. The host checks it, "
                     "and the first correct card wins!"),
]

MINI_CELL, MINI_GAP = 5 * mm, 1 * mm


def draw_mini_grid(c, x, y, line):
    """Small 4x4 grid with one winning line filled in; (x, y) is the bottom-left corner."""
    cell, gap = MINI_CELL, MINI_GAP
    for r in range(SIZE):
        for col in range(SIZE):
            c.setFillColor(GREEN if (r, col) in line else TINT)
            c.roundRect(x + col * (cell + gap), y + (SIZE - 1 - r) * (cell + gap),
                        cell, cell, 0.8 * mm, stroke=0, fill=1)
    return SIZE * cell + (SIZE - 1) * gap


def draw_rules(c, ox, oy):
    W, H = A5
    c.saveState()
    c.translate(ox, oy)
    draw_header(c, W, H, "HOW TO PLAY", 26)

    left, right = 15 * mm, W - 15 * mm
    text_x = left + 11 * mm
    y = H - 62 * mm
    for i, (title, text) in enumerate(RULES, 1):
        r = 3.6 * mm
        c.setFillColor(GREEN)
        c.circle(left + r, y + 1.2 * mm, r, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont("Montserrat-ExtraBold", 10)
        c.drawCentredString(left + r, y + 1.2 * mm - 3.5, str(i))
        c.setFillColor(BLUE)
        c.setFont("Montserrat-Bold", 11)
        c.drawString(text_x, y, title)
        c.setFont("Montserrat-Regular", 8.8)
        for line in wrap(text, "Montserrat-Regular", 8.8, right - text_x):
            y -= 4.6 * mm
            c.drawString(text_x, y, line)
        y -= 10.5 * mm

    # winning lines
    c.setFillColor(MUTED)
    spaced(c, "WINNING LINES", W / 2, y, "Montserrat-Bold", 7.5, 1.2, align="center")
    examples = [("Across", LINES[1]), ("Down", LINES[SIZE + 2]), ("Diagonal", LINES[2 * SIZE])]
    size = SIZE * MINI_CELL + (SIZE - 1) * MINI_GAP
    step = (right - left - size) / (len(examples) - 1)
    for k, (label, line) in enumerate(examples):
        x = left + k * step
        draw_mini_grid(c, x, y - 5 * mm - size, line)
        c.setFillColor(BLUE)
        c.setFont("Montserrat-SemiBold", 8.5)
        c.drawCentredString(x + size / 2, y - 10 * mm - size, label)

    c.setFillColor(GREEN)
    c.setFont("Montserrat-Bold", 10)
    c.drawCentredString(W / 2, 13 * mm, "Good luck and have fun!")
    c.restoreState()


def draw_cut_line(c, x, height):
    c.saveState()
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.5)
    c.setDash(3, 3)
    c.line(x, 4 * mm, x, height - 4 * mm)
    c.restoreState()


def make_cards_pdf(grids, path):
    page_w, page_h = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=(page_w, page_h))
    c.setTitle("Rho Bingo — Family Day cards")
    c.setAuthor("Rho")
    a5_w = A5[0]
    halves = [lambda c, x, i=i, g=g: draw_card(c, x, 0, i, g) for i, g in enumerate(grids, 1)]
    halves.append(lambda c, x: draw_rules(c, x, 0))  # fills the free half of the last sheet
    for start in range(0, len(halves), 2):
        for slot, draw in enumerate(halves[start:start + 2]):
            draw(c, slot * a5_w)
        draw_cut_line(c, a5_w, page_h)
        c.showPage()
    c.save()


# --- Host script ---------------------------------------------------------------
def make_host_pdf(path):
    W, H = A4
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle("Rho Bingo — host script")
    c.setAuthor("Rho")
    left, right = 22 * mm, W - 22 * mm

    draw_logo(c, left, H - 15 * mm, 50 * mm, 12 * mm)
    c.setFillColor(GREEN)
    spaced(c, "FAMILY DAY  ·  RHO BINGO", right, H - 22 * mm,
           "Montserrat-Bold", 8, 1.4, align="right")
    c.setFillColor(BLUE)
    c.setFont("Montserrat-ExtraBold", 22)
    c.drawString(left, H - 40 * mm, "Host script")
    c.setFillColor(MUTED)
    c.setFont("Montserrat-Regular", 9)
    c.drawString(left, H - 46.5 * mm,
                 "Read the text slowly. The words on the bingo cards are highlighted.")

    pattern = re.compile(
        r"\b(" + "|".join(re.escape(w) for w in sorted(WORDS, key=len, reverse=True)) + r")\b",
        re.IGNORECASE,
    )
    marker = "cmyk({},{},{},{})".format(*GREEN_TINT.cmyk())

    def highlight(text):
        return pattern.sub(
            lambda m: f'<font name="Montserrat-Bold" backColor="{marker}">{m.group(0)}</font>', text)

    body = ParagraphStyle("body", fontName="Montserrat-Regular", fontSize=10.5, leading=14.6,
                          textColor=BLUE, alignment=TA_LEFT, spaceAfter=5.5)
    intro = ParagraphStyle("intro", parent=body, fontName="Montserrat-SemiBold")
    label = ParagraphStyle("label", parent=body, fontName="Montserrat-Bold", fontSize=8,
                           textColor=MUTED, spaceAfter=3)

    y = H - 54 * mm
    width = right - left

    def put(p, space=None):
        nonlocal y
        _, h = p.wrap(width, H)
        p.drawOn(c, left, y - h)
        y -= h + (space if space is not None else p.style.spaceAfter)

    put(Paragraph("BEFORE THE STORY", label))
    for t in INTRO:
        put(Paragraph(t, intro))
    y -= 3 * mm
    put(Paragraph("THE STORY", label))
    for t in SCRIPT:
        put(Paragraph(highlight(t), body))

    c.setFillColor(MUTED)
    c.setFont("Montserrat-Regular", 7.5)
    c.drawString(left, 14 * mm,
                 "Checking a BINGO: all 4 words in the line must already have been read out "
                 "(highlighted above).")
    c.showPage()
    c.save()


if __name__ == "__main__":
    grids, when = build_cards()
    make_cards_pdf(grids, HERE / "rho-bingo-cards.pdf")
    make_host_pdf(HERE / "rho-bingo-host-script.pdf")

    print(f"cell font size: {CELL_SIZE_PT} pt, logo: {logo_file() or 'placeholder wordmark'}")
    for i, g in enumerate(grids, 1):
        print(f"card {i}: first line after {first_line_at(g, when):.0%} of the story")
        for row in g:
            print("   " + " | ".join(f"{w:<17}" for w in row))
