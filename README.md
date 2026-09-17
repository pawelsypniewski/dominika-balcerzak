# lek. wet. Dominika Balcerzak — strona

Jednostronicowa wizytówka przeniesiona z projektu Claude Design
(„Dominika Balcerzak.dc.html”). Zwykły HTML + CSS + jeden mały skrypt.

- `index.html` — cała treść strony (po polsku)
- `en/index.html`, `en/privacy-policy.html` — wersja angielska (te same style, zdjęcia i skrypt przez `../`)
- `style.css` — wygląd (kolory na górze pliku, wersja na telefon na dole)
- `skrypt.js` — „Czytaj więcej” na telefonie i składanie adresu e-mail
- `zdjecia/` — zdjęcia; oryginały leżą w `Praca/Strona Internetowa dominika/gotowe/`
  - `portret.jpg` — 1200×1500 (4:5)
  - `pacjent-1-kot.jpg`, `pacjent-2-bernenczyk.jpg`, `pacjent-3-owczarek.jpg` — 1500×998 (3:2)
  - każde zdjęcie ma też lżejszą kopię `…-800.jpg` (800 px szerokości) — przeglądarka
    sama wybiera wersję pasującą do ekranu

Podmiana zdjęcia: nowy plik pod tą samą nazwą w `zdjecia/` **i nowa kopia 800 px**
(inaczej część ekranów pokaże stare zdjęcie):

    sips --resampleWidth 800 -s formatOptions 80 zdjecia/portret.jpg --out zdjecia/portret-800.jpg

## Typografia i odstępy

Cała strona korzysta z jednego systemu zapisanego na górze `style.css` (zmienne `--t-…`,
`--odstep-…`, `--kafel`). Każdy tekst ma jedną z 11 ról: nazwisko, tytuł, podtytuł, wstęp,
liczba, tytuł karty, tekst, tekst drobny, etykieta, przycisk/menu, podpis. Dodając nowy
element, przypisz mu rolę zamiast wpisywać nową wielkość. Wersja na telefon zmienia
tylko wartości zmiennych (blok `:root` w `@media (max-width: 720px)`).

## Wersja angielska

- Adres: `/en/`. Przełącznik **EN / PL** w nagłówku (obok „Umów się”) i link „English / Polski” w stopce
  prowadzą do tej samej strony w drugim języku.
- **Każda zmiana treści po polsku = ta sama zmiana w `en/`.** Nazwy klas i kotwic (`#o-mnie`, `#kiedy`…)
  są wspólne, więc wystarczy podmienić tekst.
- W `<head>` każdej strony są linki `hreflang` (pl / en / x-default) — przy zmianie domeny też do podmiany.
- Napis „Zwiń” / „Show less” skrypt wybiera według `<html lang>`.
- Do 900 px nagłówek ma dwa wiersze (logo + PL/EN + „Umów się”, pod spodem menu).

## Ekrany

Sprawdzone na: iPhone SE–16 Pro Max (pionowo i poziomo), iPad mini / Air / Pro 11 / Pro 13
(pionowo i poziomo), MacBook Air 13/15, MacBook Pro 14/16, laptopy 1280×720, 1366×768,
1536×864, monitory 1920×1080 i 2560×1440.

- do 720 px — wersja na telefon (pasek kontaktu na dole, zwijany życiorys)
- 721–900 px — iPad pionowo: sekcje jedna pod drugą
- 901–1279 px — iPad poziomo / małe laptopy: pierwszy ekran pół na pół
- od 1280 px — pełny układ z projektu
- kafelki dobierają kolumny do miejsca (4 / 2 / 1), nigdy 3 + 1
- na niskich ekranach nazwisko i odstępy się kurczą, żeby pierwszy ekran mieścił się w całości

## Bezpieczeństwo

- W `<head>` jest **Content-Security-Policy**: strona wczytuje tylko własne pliki.
  Skrypty wpisane w HTML, pliki z innych serwerów i formularze są blokowane.
  **Dodając coś z zewnątrz** (mapa Google, czcionka Google, licznik odwiedzin),
  trzeba dopisać ten adres do polityki — inaczej przeglądarka to po cichu zablokuje.
- JavaScript tylko w `skrypt.js`, nigdy w `<script>…</script>` ani `onclick=`.
- E-mail nie jest wpisany wprost — składa go `skrypt.js` z atrybutów
  `data-email-nazwa` / `data-email-domena` (ochrona przed robotami spamerów).
- Zdjęcia mają w metadanych autora i prawa autorskie (Paweł Sypniewski), bez GPS.

## Podgląd

    npm run serve

i otwórz http://localhost:8130/

## Podgląd linku i znaczek strony

- `zdjecia/podglad.jpg` — 1200×630, obrazek, który pokazuje się przy wklejeniu linku
  na Facebooka, Instagrama, WhatsAppa i Messengera. Składany z portretu i nazwiska.
- `favicon.svg` + `favicon-32.png` — znaczek w karcie przeglądarki.
- `apple-touch-icon.png` — 180×180, ikona po dodaniu strony do ekranu głównego iPhone'a.
- `404.html` — strona pokazywana pod nieistniejącym adresem.

**Po podpięciu własnej domeny trzeba podmienić adresy w czterech miejscach:**

1. `index.html` i `en/index.html` — `canonical`, `hreflang`, `og:url`, `og:image`
2. `polityka-prywatnosci.html` i `en/privacy-policy.html` — `canonical`, `hreflang`, `og:url`, `og:image`
3. `404.html` — wszystkie adresy `/dominika-balcerzak/...` zamienić na `/...`
4. plik `CNAME` w katalogu głównym (tworzy go GitHub przy ustawianiu domeny)

Podmiana obrazka podglądu: zmień `kafelek.html` w materiałach roboczych albo poproś
o nowy — musi mieć dokładnie 1200×630 px, inaczej Facebook przytnie go po swojemu.

## Do uzupełnienia

- lista publikacji (na razie trzy wiersze-zaślepki „20__”)
