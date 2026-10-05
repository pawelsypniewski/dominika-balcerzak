# Rho Bingo — Family Day

- `rho-bingo-cards.pdf` — 5 różnych kart 4×4, każda w formacie A5, po dwie na arkuszu A4
  (poziomo). Drukować w skali 100% („rzeczywisty rozmiar”), przeciąć wzdłuż przerywanej linii.
- `rho-bingo-host-script.pdf` — tekst do odczytania po angielsku (A4), słowa z kart wyróżnione.
- `generate.py` — generuje oba pliki: `pip install reportlab pdfrw && python3 rho-bingo/generate.py`

Logo: `logo.pdf` (wektorowe, wstawiane bez utraty jakości). Kolory kart (CMYK) to
niebieski i zielony z logo — są na górze `generate.py` (`BLUE`, `GREEN`, …).

Karty: 40 słów z tekstu, każde na dokładnie 2 kartach, każde dwie karty mają 4 wspólne
słowa. Układ dobrany tak, żeby nikt nie miał linii w pierwszych ~40% tekstu, a karty
kończyły linię w różnych momentach (bez remisów).

Font: Montserrat (Google Fonts, licencja SIL Open Font License).
