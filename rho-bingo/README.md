# Rho Bingo — Family Day

- `rho-bingo-cards.pdf` — 5 różnych kart 4×4 i instrukcja „How to play”, każda w formacie
  A5, po dwie na arkuszu A4 (poziomo). Drukować w skali 100% („rzeczywisty rozmiar”),
  przeciąć wzdłuż przerywanej linii.
- `rho-bingo-host-script.pdf` — tekst do odczytania po angielsku (A4): zasady gry do
  przeczytania na początku i opowieść o Rho ze słowami z kart wyróżnionymi.
- `generate.py` — generuje oba pliki: `pip install reportlab pdfrw && python3 rho-bingo/generate.py`

Logo: `logo.pdf` (wektorowe, wstawiane bez utraty jakości). Kolory kart (CMYK) to
niebieski i zielony z logo — są na górze `generate.py` (`BLUE`, `GREEN`, …).

Karty: 40 słów z tekstu, każde na dokładnie 2 kartach, każde dwie karty mają 4 wspólne
słowa. Układ dobrany tak, żeby nikt nie miał linii w pierwszych ~40% tekstu, a karty
kończyły linię w różnych momentach (bez remisów).

## Gry na Family Day (`games.py`)

Każda gra to jedna strona A4 (pionowo), po polsku, z logo Rho.
`python3 rho-bingo/games.py` tworzy:

- `rho-gry-dzieci.pdf` — Misja Family Day (szukanie rzeczy w biurze), Wykreślanka
  (12 słów z opowieści o Rho), Kawowy labirynt, Mama lub tata w pracy (rysunek).
- `rho-gry-dorosli.pdf` — Quiz o Rho (12 pytań), Znajdź kogoś, kto… (zapoznawanie się),
  Rozszyfruj (12 słów z podpowiedziami), Sudoku (4 poziomy).

Odpowiedzi do quizu, Rozszyfruj i sudoku są wydrukowane do góry nogami na dole strony.

Font: Montserrat (Google Fonts, licencja SIL Open Font License).
