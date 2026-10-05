"""Rho Family Day — printable games, one A4 page each.

Generates:
  rho-gry-dzieci.pdf    Misja Family Day, Wykreślanka, Kawowy labirynt, Mama lub tata w pracy
  rho-gry-dorosli.pdf   Quiz o Rho, Znajdź kogoś, kto…, Rozszyfruj, Sudoku (in Polish)

Answers (quiz, unscramble, sudoku) are printed upside down at the bottom of the page.
Uses the fonts, colours and logo from generate.py.

    pip install reportlab pdfrw
    python3 rho-bingo/games.py
"""

import random
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from generate import BLUE, GREEN, HERE, LINE, MUTED, TINT, draw_logo, spaced, white, wrap

W, H = A4
M = 16 * mm            # content margin
CW = W - 2 * M         # content width


# --- Shared page parts ---------------------------------------------------------
def text_width(text, font, size, spacing=0):
    return pdfmetrics.stringWidth(text, font, size) + spacing * (len(text) - 1)


def header(c, title, subtitle, audience):
    """Frame, logo, Family Day label, title and subtitle. Returns the y where content starts."""
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.roundRect(8 * mm, 8 * mm, W - 16 * mm, H - 16 * mm, 5 * mm, stroke=1, fill=0)

    draw_logo(c, M, H - 16 * mm, 55 * mm, 14 * mm)
    pill_w, pill_h = 36 * mm, 7 * mm
    c.setFillColor(GREEN)
    c.roundRect(W - M - pill_w, H - 16 * mm - pill_h, pill_w, pill_h, pill_h / 2, stroke=0, fill=1)
    c.setFillColor(white)
    spaced(c, "FAMILY DAY", W - M - pill_w / 2, H - 16 * mm - pill_h + 2.3 * mm,
           "Montserrat-ExtraBold", 8.5, 1.3, align="center")
    c.setFillColor(MUTED)
    spaced(c, audience, W - M, H - 29 * mm, "Montserrat-SemiBold", 8, 1.4, align="right")

    size = 30
    while text_width(title, "Montserrat-ExtraBold", size, size / 12) > CW:
        size -= 1
    c.setFillColor(BLUE)
    spaced(c, title, W / 2, H - 50 * mm, "Montserrat-ExtraBold", size, size / 12, align="center")

    y = H - 58 * mm
    c.setFont("Montserrat-SemiBold", 10.5)
    for line in wrap(subtitle, "Montserrat-SemiBold", 10.5, 150 * mm):
        c.drawCentredString(W / 2, y, line)
        y -= 5.2 * mm
    return y - 4 * mm


def write_line(c, x, y, label, width, font_size=9.5):
    c.setFillColor(BLUE)
    c.setFont("Montserrat-SemiBold", font_size)
    c.drawString(x, y, label)
    start = x + pdfmetrics.stringWidth(label, "Montserrat-SemiBold", font_size) + 2 * mm
    c.setStrokeColor(LINE)
    c.setLineWidth(0.9)
    c.line(start, y - 1 * mm, x + width, y - 1 * mm)


def upside_down(c, cx, cy, draw):
    c.saveState()
    c.translate(cx, cy)
    c.rotate(180)
    draw()
    c.restoreState()


def answers_line(c, *lines, y=16 * mm):
    def draw():
        c.setFillColor(MUTED)
        c.setFont("Montserrat-SemiBold", 7.5)
        for i, text in enumerate(lines):
            c.drawCentredString(0, -i * 4 * mm, text)
    upside_down(c, W / 2, y, draw)


def checkbox(c, x, y, size):
    c.setFillColor(white)
    c.setStrokeColor(BLUE)
    c.setLineWidth(1.1)
    c.roundRect(x, y, size, size, size * 0.22, stroke=1, fill=1)


# --- Kids: Family Day Quest ----------------------------------------------------
QUEST = [
    "Znajdź coś zielonego, jak logo Rho",
    "Wypatrz logo Rho gdzieś w biurze",
    "Znajdź ekspres do kawy",
    "Znajdź roślinę",
    "Policz krzesła w sali spotkań",
    "Znajdź komputer z dwoma monitorami",
    "Znajdź coś okrągłego",
    "Znajdź coś na literę R",
    "Powiedz „cześć” komuś nowemu",
    "Zapytaj kogoś, czym się zajmuje",
    "Przybij piątkę komuś z zespołu mamy lub taty",
    "Znajdź okno z najładniejszym widokiem",
]


def draw_star(c, cx, cy, r_out, r_in):
    import math
    p = c.beginPath()
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi / 2 + i * math.pi / 5
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        p.moveTo(x, y) if i == 0 else p.lineTo(x, y)
    p.close()
    c.drawPath(p, stroke=1, fill=0)


def page_quest(c):
    y = header(c, "MISJA FAMILY DAY",
               "Zwiedź biuro z mamą lub tatą. Zaznacz każde pole, gdy coś znajdziesz!",
               "DLA DZIECI")
    gap = 4 * mm
    box_w, box_h = (CW - gap) / 2, 23 * mm
    rows = (len(QUEST) + 1) // 2
    for i, item in enumerate(QUEST):
        col, row = i // rows, i % rows
        x = M + col * (box_w + gap)
        top = y - row * (box_h + 3 * mm)
        c.setFillColor(TINT)
        c.roundRect(x, top - box_h, box_w, box_h, 3 * mm, stroke=0, fill=1)
        checkbox(c, x + 4 * mm, top - box_h / 2 - 3.5 * mm, 7 * mm)
        lines = wrap(item, "Montserrat-SemiBold", 10.5, box_w - 18 * mm)
        c.setFillColor(BLUE)
        c.setFont("Montserrat-SemiBold", 10.5)
        base = top - box_h / 2 + (len(lines) - 1) * 2.5 * mm - 1.4 * mm
        for k, line in enumerate(lines):
            c.drawString(x + 14 * mm, base - k * 5 * mm, line)

    bottom = y - rows * (box_h + 3 * mm)
    c.setStrokeColor(GREEN)
    c.setLineWidth(2)
    draw_star(c, M + 16 * mm, bottom - 20 * mm, 14 * mm, 6 * mm)
    c.setFillColor(GREEN)
    c.setFont("Montserrat-ExtraBold", 15)
    c.drawString(M + 36 * mm, bottom - 15 * mm, "Misja wykonana!")
    write_line(c, M + 36 * mm, bottom - 26 * mm, "Podpis kogoś z Rho:", CW - 36 * mm)
    write_line(c, M, 20 * mm, "Moje imię:", CW)


# --- Kids: Word Search ---------------------------------------------------------
SEARCH_WORDS = ["ZESPÓŁ", "KAWA", "NAUKA", "ZDROWIE", "POMYSŁY", "PRZYSZŁOŚĆ",
                "ENERGIA", "ZAUFANIE", "PASJA", "PACJENCI", "EKSPERCI", "BIURKO"]
SEARCH_SIZE = 12


def occurrences(grid, word):
    lines = ["".join(row) for row in grid] + ["".join(col) for col in zip(*grid)]
    return sum(len(re.findall(f"(?={word})", line)) for line in lines)


def build_word_search(seed=7):
    """Words go left-to-right or top-to-bottom only (easy for kids); each appears exactly once."""
    rng = random.Random(seed)
    n = SEARCH_SIZE
    while True:
        grid = [[None] * n for _ in range(n)]
        for word in sorted(SEARCH_WORDS, key=len, reverse=True):
            for _ in range(300):
                across = rng.random() < 0.5
                r = rng.randrange(n if across else n - len(word) + 1)
                k = rng.randrange(n - len(word) + 1 if across else n)
                cells = [(r, k + i) if across else (r + i, k) for i in range(len(word))]
                if all(grid[a][b] in (None, ch) for (a, b), ch in zip(cells, word)):
                    for (a, b), ch in zip(cells, word):
                        grid[a][b] = ch
                    break
            else:
                break
        else:
            filler = "AAĄBCĆDEEĘGHIIJKLŁMNŃOOÓPRSŚTUWYYZŹŻ"
            grid = [[ch or rng.choice(filler) for ch in row] for row in grid]
            if all(occurrences(grid, w) == 1 for w in SEARCH_WORDS):
                return grid


def page_word_search(c):
    y = header(c, "WYKREŚLANKA",
               "Znajdź 12 słów z opowieści o Rho. Biegną poziomo albo pionowo.",
               "DLA DZIECI")
    grid = build_word_search()
    cell = 12.4 * mm
    size = SEARCH_SIZE * cell
    gx, gy = (W - size) / 2, y - size - 2 * mm
    c.setFillColor(TINT)
    c.roundRect(gx - 3 * mm, gy - 3 * mm, size + 6 * mm, size + 6 * mm, 4 * mm, stroke=0, fill=1)
    c.setFillColor(BLUE)
    c.setFont("Montserrat-Bold", 16)
    for r, row in enumerate(grid):
        for k, ch in enumerate(row):
            c.drawCentredString(gx + (k + 0.5) * cell, gy + size - (r + 0.5) * cell - 5.6, ch)

    top = gy - 12 * mm
    cols = 4
    col_w = CW / cols
    for i, word in enumerate(SEARCH_WORDS):
        x = M + (i % cols) * col_w
        yy = top - (i // cols) * 9.5 * mm
        checkbox(c, x + 4 * mm, yy - 1.2 * mm, 4.6 * mm)
        c.setFillColor(BLUE)
        c.setFont("Montserrat-SemiBold", 10.5)
        c.drawString(x + 11 * mm, yy, word)
    write_line(c, M, 20 * mm, "Moje imię:", CW)


# --- Kids: maze ----------------------------------------------------------------
def build_maze(rows, cols, seed=11):
    rng = random.Random(seed)
    open_ = {(r, k): set() for r in range(rows) for k in range(cols)}
    steps = {"N": (-1, 0), "S": (1, 0), "W": (0, -1), "E": (0, 1)}
    back = {"N": "S", "S": "N", "W": "E", "E": "W"}
    stack, seen = [(0, 0)], {(0, 0)}
    while stack:
        r, k = stack[-1]
        options = [(d, (r + dr, k + dk)) for d, (dr, dk) in steps.items()
                   if (r + dr, k + dk) in open_ and (r + dr, k + dk) not in seen]
        if not options:
            stack.pop()
            continue
        d, nxt = rng.choice(options)
        open_[(r, k)].add(d)
        open_[nxt].add(back[d])
        seen.add(nxt)
        stack.append(nxt)
    return open_


def coffee_cup(c, x, y, s):
    c.setStrokeColor(BLUE)
    c.setLineWidth(s * 0.09)
    c.circle(x + s * 0.68, y + s * 0.36, s * 0.15, stroke=1, fill=0)
    c.setFillColor(BLUE)
    c.roundRect(x, y + s * 0.06, s * 0.7, s * 0.62, s * 0.1, stroke=0, fill=1)
    c.roundRect(x - s * 0.1, y, s * 0.9, s * 0.09, s * 0.045, stroke=0, fill=1)
    c.setStrokeColor(GREEN)
    c.setLineWidth(s * 0.06)
    c.setLineCap(1)
    for i in range(3):
        sx = x + s * (0.17 + i * 0.18)
        p = c.beginPath()
        p.moveTo(sx, y + s * 0.78)
        p.curveTo(sx - s * 0.08, y + s * 0.88, sx + s * 0.08, y + s * 0.96, sx, y + s * 1.06)
        c.drawPath(p, stroke=1, fill=0)


def team_icon(c, x, y, s):
    for i, colour in enumerate((GREEN, BLUE, GREEN)):
        px = x + i * s * 0.55
        c.setFillColor(colour)
        c.circle(px + s * 0.25, y + s * 0.72, s * 0.15, stroke=0, fill=1)
        c.roundRect(px, y, s * 0.5, s * 0.5, s * 0.2, stroke=0, fill=1)


def page_maze(c):
    y = header(c, "KAWOWY LABIRYNT",
               "Zaraz zaczyna się spotkanie! Pomóż kawie dotrzeć do zespołu.",
               "DLA DZIECI")
    rows, cols, cell = 13, 14, 11.4 * mm
    maze = build_maze(rows, cols)
    mw, mh = cols * cell, rows * cell
    mx, top = (W - mw) / 2, y - 20 * mm

    c.setStrokeColor(BLUE)
    c.setLineWidth(2.4)
    c.setLineCap(1)
    for r in range(rows):
        for k in range(cols):
            x0, y0 = mx + k * cell, top - (r + 1) * cell
            if r == 0 and k != 0:
                c.line(x0, y0 + cell, x0 + cell, y0 + cell)
            if k == 0:
                c.line(x0, y0, x0, y0 + cell)
            if "E" not in maze[(r, k)]:
                c.line(x0 + cell, y0, x0 + cell, y0 + cell)
            if "S" not in maze[(r, k)] and not (r == rows - 1 and k == cols - 1):
                c.line(x0, y0, x0 + cell, y0)

    coffee_cup(c, mx + cell * 0.18, top + 3 * mm, 11 * mm)
    c.setFillColor(GREEN)
    c.setFont("Montserrat-ExtraBold", 11)
    c.drawString(mx + cell + 8 * mm, top + 6 * mm, "START")
    team_icon(c, mx + mw - cell * 1.3, top - mh - 15 * mm, 11 * mm)
    c.drawRightString(mx + mw - cell * 1.6, top - mh - 9 * mm, "SPOTKANIE ZESPOŁU")
    write_line(c, M, 20 * mm, "Moje imię:", CW)


# --- Kids: drawing -------------------------------------------------------------
def page_drawing(c):
    y = header(c, "MAMA LUB TATA W PRACY",
               "Co robi Twoja mama lub Twój tata w Rho? Narysuj to w ramce!",
               "DLA DZIECI")
    frame_h = 150 * mm
    c.setStrokeColor(GREEN)
    c.setLineWidth(2)
    c.setDash(6, 4)
    c.roundRect(M, y - frame_h, CW, frame_h, 5 * mm, stroke=1, fill=0)
    c.setDash()
    yy = y - frame_h - 14 * mm
    for label in ("Moja mama / mój tata ma na imię", "W Rho moja mama / mój tata pomaga",
                  "Dziś najbardziej podobało mi się:", "Moje imię:"):
        write_line(c, M, yy, label, CW, font_size=10.5)
        yy -= 13 * mm


# --- Adults: quiz --------------------------------------------------------------
QUIZ = [
    ("Od jak dawna działa Rho?",
     ["Od około 10 lat", "Od około 25 lat", "Od ponad 40 lat"], 2),
    ("Co oznacza skrót „CRO”?",
     ["Clinical Review Office", "Contract Research Organization", "Central Research Operations"], 1),
    ("Jak Rho nazywa siłę połączeń między ludźmi, nauką i wspólnym celem?",
     ["Cohesion Effect", "Network Effect", "Butterfly Effect"], 0),
    ("Misja Rho to poprawa zdrowia, wydłużanie życia i podnoszenie…",
     ["pensji", "jakości życia", "liczby spotkań"], 1),
    ("Czym jest placebo?",
     ["Preparatem, który wygląda jak lek, ale nie ma substancji czynnej", "Najwyższą dawką leku",
      "Rodzajem badania krwi"], 0),
    ("Kto w badaniu podwójnie ślepym wie, jakie leczenie dostaje uczestnik?",
     ["Tylko uczestnicy", "Tylko lekarze", "Nikt z nich, aż do końca badania"], 2),
    ("W której fazie badań klinicznych lek zwykle testuje się na największej grupie pacjentów przed dopuszczeniem?",
     ["Faza I", "Faza II", "Faza III"], 2),
    ("„Randomizacja” oznacza, że uczestnicy…",
     ["trafiają do grup losowo", "są wybierani przez lekarza", "dostają losowe wynagrodzenie"], 0),
    ("Czym jest „świadoma zgoda”?",
     ["Akceptacją budżetu przez sponsora", "Zgodą na udział w badaniu po poznaniu wszystkich informacji",
      "Podpisem lekarza pod raportem końcowym"], 1),
    ("Która amerykańska agencja dopuszcza nowe leki do obrotu?",
     ["FDA", "NASA", "FBI"], 0),
    ("Mediana w statystyce to…",
     ["najczęstsza wartość", "średnia wszystkich wartości", "środkowa wartość po uporządkowaniu danych"], 2),
    ("Kto zamienia dane z badań klinicznych w odpowiedzi?",
     ["Architekci", "Biostatystycy", "Botanicy"], 1),
]


def page_quiz(c):
    y = header(c, "QUIZ O RHO",
               "Jak dobrze znasz Rho i świat badań klinicznych? "
               "Zakreśl jedną odpowiedź w każdym pytaniu.",
               "DLA DOROSŁYCH")
    gap = 8 * mm
    col_w = (CW - gap) / 2
    text_x = 9 * mm
    per_col = (len(QUIZ) + 1) // 2
    for i, (question, options, _) in enumerate(QUIZ):
        col = i // per_col
        if i % per_col == 0:
            yy = y
        x = M + col * (col_w + gap)
        c.setFillColor(GREEN)
        c.circle(x + 3.2 * mm, yy + 1.2 * mm, 3.2 * mm, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont("Montserrat-ExtraBold", 8.5)
        c.drawCentredString(x + 3.2 * mm, yy + 1.2 * mm - 3, str(i + 1))
        c.setFillColor(BLUE)
        c.setFont("Montserrat-Bold", 10)
        for line in wrap(question, "Montserrat-Bold", 10, col_w - text_x):
            c.drawString(x + text_x, yy, line)
            yy -= 4.6 * mm
        yy -= 0.8 * mm
        for letter, option in zip("ABC", options):
            c.setStrokeColor(BLUE)
            c.setLineWidth(0.9)
            c.circle(x + text_x + 2 * mm, yy + 1.1 * mm, 2 * mm, stroke=1, fill=0)
            c.setFillColor(BLUE)
            c.setFont("Montserrat-Bold", 7)
            c.drawCentredString(x + text_x + 2 * mm, yy + 1.1 * mm - 2.4, letter)
            c.setFont("Montserrat-Regular", 9.5)
            for line in wrap(option, "Montserrat-Regular", 9.5, col_w - text_x - 7 * mm):
                c.drawString(x + text_x + 6 * mm, yy, line)
                yy -= 4.4 * mm
            yy -= 0.6 * mm
        yy -= 5.5 * mm

    write_line(c, M, 31 * mm, "Imię:", CW * 0.62)
    write_line(c, M + CW * 0.7, 31 * mm, "Wynik:", CW * 0.3 - 9 * mm)
    c.setFont("Montserrat-SemiBold", 9.5)
    c.drawRightString(M + CW, 31 * mm, f"/ {len(QUIZ)}")
    answers_line(c, "ODPOWIEDZI:  " + "   ".join(f"{i} {'ABC'[a]}" for i, (_, _, a) in enumerate(QUIZ, 1)))


# --- Adults: Find Someone Who --------------------------------------------------
FIND = [
    "pracuje w Rho dłużej niż 5 lat",
    "dołączył(a) do Rho w tym roku",
    "pije herbatę, a nie kawę",
    "mówi w trzech lub więcej językach",
    "dotarł(a) tu dziś rowerem lub pieszo",
    "ma psa lub kota",
    "przebiegł(a) półmaraton (lub dłużej)",
    "urodził(a) się w innym kraju",
    "codziennie pracuje z danymi",
    "urodził(a) się w tym samym miesiącu co Ty",
    "gra na jakimś instrumencie",
    "był(a) w USA",
    "jest na Family Day pierwszy raz",
    "ma ukryty talent (zapytaj jaki!)",
    "piecze najlepsze ciasto w biurze",
    "w tym tygodniu pracował(a) z kimś z innego kraju",
]


def page_find(c):
    y = header(c, "ZNAJDŹ KOGOŚ, KTO…",
               "Poznajcie się! Znajdź osobę pasującą do każdego pola i wpisz jej imię. "
               "Każde pole to inna osoba. Wygrywa ten, kto pierwszy wypełni całą linię!",
               "DLA DOROSŁYCH")
    gap = 3 * mm
    cell_w = (CW - 3 * gap) / 4
    cell_h = 41 * mm
    for i, prompt in enumerate(FIND):
        r, k = divmod(i, 4)
        x = M + k * (cell_w + gap)
        top = y - r * (cell_h + gap)
        c.setFillColor(TINT)
        c.roundRect(x, top - cell_h, cell_w, cell_h, 3 * mm, stroke=0, fill=1)
        c.setFillColor(BLUE)
        c.setFont("Montserrat-Bold", 9.5)
        yy = top - 7 * mm
        for line in wrap("… " + prompt, "Montserrat-Bold", 9.5, cell_w - 6 * mm):
            c.drawString(x + 3 * mm, yy, line)
            yy -= 4.4 * mm
        c.setStrokeColor(LINE)
        c.setLineWidth(0.9)
        c.line(x + 3 * mm, top - cell_h + 7 * mm, x + cell_w - 3 * mm, top - cell_h + 7 * mm)
        c.setFillColor(MUTED)
        c.setFont("Montserrat-Regular", 6.5)
        c.drawString(x + 3 * mm, top - cell_h + 3.6 * mm, "Imię")
    write_line(c, M, 20 * mm, "Moje imię:", CW)


# --- Adults: Unscramble --------------------------------------------------------
UNSCRAMBLE = [
    ("PROTOKÓŁ", "Zasady, których trzyma się każde badanie"),
    ("OCHOTNIK", "Ktoś, kto sam zgłasza się do badania"),
    ("STATYSTYKA", "Zamienia liczby w odpowiedzi"),
    ("LEKARSTWO", "Pomaga wyzdrowieć"),
    ("DIAGNOZA", "Ustalenie, co komuś dolega"),
    ("MIKROSKOP", "Powiększa maleńkie rzeczy"),
    ("PROBÓWKA", "Szklane naczynko z laboratorium"),
    ("INNOWACJA", "Nowy pomysł wcielony w życie"),
    ("WSPÓŁPRACA", "Razem raźniej"),
    ("CIEKAWOŚĆ", "Od niej zaczyna się każde odkrycie"),
    ("CZĄSTECZKA", "Maleńka grupa atomów"),
    ("HIPOTEZA", "Pomysł, który sprawdzasz danymi"),
]


def scramble(word, rng):
    while True:
        letters = list(word)
        rng.shuffle(letters)
        mixed = "".join(letters)
        if mixed != word and sum(a == b for a, b in zip(mixed, word)) <= len(word) // 4:
            return mixed


def page_unscramble(c):
    y = header(c, "ROZSZYFRUJ",
               "Ułóż litery we właściwej kolejności. Podpowiedzi Ci pomogą!",
               "DLA DOROSŁYCH")
    rng = random.Random(3)
    gap = 8 * mm
    col_w = (CW - gap) / 2
    per_col = len(UNSCRAMBLE) // 2
    tile, tile_gap = 6.2 * mm, 1 * mm
    for i, (word, hint) in enumerate(UNSCRAMBLE):
        col, row = divmod(i, per_col)
        x = M + col * (col_w + gap)
        top = y - row * 30 * mm
        c.setFillColor(GREEN)
        c.circle(x + 3.2 * mm, top - tile / 2, 3.2 * mm, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont("Montserrat-ExtraBold", 8.5)
        c.drawCentredString(x + 3.2 * mm, top - tile / 2 - 3, str(i + 1))
        for k, ch in enumerate(scramble(word, rng)):
            tx = x + 9 * mm + k * (tile + tile_gap)
            c.setFillColor(TINT)
            c.roundRect(tx, top - tile, tile, tile, 1.2 * mm, stroke=0, fill=1)
            c.setFillColor(BLUE)
            c.setFont("Montserrat-Bold", 11)
            c.drawCentredString(tx + tile / 2, top - tile / 2 - 3.8, ch)
        c.setFillColor(MUTED)
        c.setFont("Montserrat-Regular", 8.5)
        c.drawString(x + 9 * mm, top - tile - 5 * mm, hint)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.9)
        c.line(x + 9 * mm, top - tile - 14 * mm, x + col_w, top - tile - 14 * mm)
    write_line(c, M, 31 * mm, "Imię:", CW)
    words = [f"{i}. {w}" for i, (w, _) in enumerate(UNSCRAMBLE, 1)]
    answers_line(c, "ODPOWIEDZI:  " + "  ·  ".join(words[:6]), "  ·  ".join(words[6:]), y=19 * mm)


# --- Adults: Sudoku ------------------------------------------------------------
def candidates(grid, i):
    r, k = divmod(i, 9)
    used = set(grid[r * 9:(r + 1) * 9]) | set(grid[k::9])
    br, bk = r // 3 * 3, k // 3 * 3
    used |= {grid[(br + a) * 9 + bk + b] for a in range(3) for b in range(3)}
    return [d for d in range(1, 10) if d not in used]


def solve(grid, limit=2, rng=None, found=None):
    """Counts solutions up to `limit`; with rng, fills the grid with a random solution."""
    found = found if found is not None else []
    empty = [i for i, v in enumerate(grid) if v == 0]
    if not empty:
        found.append(grid[:])
        return found
    i = min(empty, key=lambda j: len(candidates(grid, j)))
    options = candidates(grid, i)
    if rng:
        rng.shuffle(options)
    for d in options:
        grid[i] = d
        solve(grid, limit, rng, found)
        if len(found) >= limit:
            break
    grid[i] = 0
    return found


def make_sudoku(rng, clues):
    solution = solve([0] * 81, limit=1, rng=rng)[0]
    puzzle = solution[:]
    for i in rng.sample(range(81), 81):
        if sum(v != 0 for v in puzzle) <= clues:
            break
        keep, puzzle[i] = puzzle[i], 0
        if len(solve(puzzle[:])) != 1:
            puzzle[i] = keep
    return puzzle, solution


def draw_sudoku(c, x, top, cell, grid, font_size, shade_givens=True):
    size = 9 * cell
    c.setFillColor(white)
    c.rect(x, top - size, size, size, stroke=0, fill=1)
    for i, v in enumerate(grid):
        r, k = divmod(i, 9)
        if v:
            if shade_givens:
                c.setFillColor(TINT)
                c.rect(x + k * cell, top - (r + 1) * cell, cell, cell, stroke=0, fill=1)
            c.setFillColor(BLUE)
            c.setFont("Montserrat-Bold", font_size)
            c.drawCentredString(x + (k + 0.5) * cell, top - (r + 0.5) * cell - font_size * 0.36, str(v))
    for n in range(10):
        thick = n % 3 == 0
        c.setStrokeColor(BLUE if thick else LINE)
        c.setLineWidth((1.6 if thick else 0.6) * (cell / (8.4 * mm)))
        c.line(x + n * cell, top, x + n * cell, top - size)
        c.line(x, top - n * cell, x + size, top - n * cell)


def page_sudoku(c):
    y = header(c, "SUDOKU",
               "Wpisz cyfry od 1 do 9 tak, aby w każdym wierszu, kolumnie i kwadracie 3×3 "
               "każda pojawiła się dokładnie raz. Zacznij od łatwego!",
               "DLA DOROSŁYCH")
    rng = random.Random(2026)
    levels = [("ŁATWE", 40), ("ŚREDNIE", 34), ("TRUDNE", 29), ("EKSPERT", 25)]
    puzzles = [(label, *make_sudoku(rng, clues)) for label, clues in levels]
    cell = 8.4 * mm
    size = 9 * cell
    gap_x = CW - 2 * size
    for n, (label, puzzle, _) in enumerate(puzzles):
        x = M + (n % 2) * (size + gap_x)
        top = y - 6 * mm - (n // 2) * (size + 14 * mm)
        c.setFillColor(GREEN)
        spaced(c, label, x, top + 2.5 * mm, "Montserrat-ExtraBold", 9, 1.4)
        draw_sudoku(c, x, top, cell, puzzle, 13)
        print(f"sudoku {label}: {sum(v != 0 for v in puzzle)} clues")

    small = 3.5 * mm
    span = 4 * 9 * small + 3 * 6 * mm

    def draw_solutions():
        c.setFillColor(MUTED)
        c.setFont("Montserrat-SemiBold", 7)
        c.drawString(-span / 2, 9 * small + 2 * mm, "ROZWIĄZANIA")
        for n, (label, _, solution) in enumerate(puzzles):
            sx = -span / 2 + n * (9 * small + 6 * mm)
            c.setFillColor(MUTED)
            c.setFont("Montserrat-SemiBold", 6)
            c.drawRightString(sx + 9 * small, 9 * small + 2 * mm, label)
            draw_sudoku(c, sx, 9 * small, small, solution, 6.5, shade_givens=False)

    upside_down(c, W / 2, 14 * mm + 9 * small, draw_solutions)


def make_pdf(path, title, pages):
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle(title)
    c.setAuthor("Rho")
    for page in pages:
        page(c)
        c.showPage()
    c.save()


if __name__ == "__main__":
    make_pdf(HERE / "rho-gry-dzieci.pdf", "Rho Family Day — gry dla dzieci",
             [page_quest, page_word_search, page_maze, page_drawing])
    make_pdf(HERE / "rho-gry-dorosli.pdf", "Rho Family Day — gry dla dorosłych",
             [page_quiz, page_find, page_unscramble, page_sudoku])
    print("done")
