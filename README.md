# lek. wet. Dominika Balcerzak — strona

Jednostronicowa wizytówka przeniesiona z projektu Claude Design
(„Dominika Balcerzak.dc.html”). Zwykły HTML + CSS + jeden mały skrypt.

- `index.html` — cała treść strony
- `style.css` — wygląd (kolory na górze pliku, wersja na telefon na dole)
- `skrypt.js` — „Czytaj więcej” na telefonie i składanie adresu e-mail
- `zdjecia/` — zdjęcia; oryginały leżą w `Praca/Strona Internetowa dominika/gotowe/`
  - `portret.jpg` — 1200×1500 (4:5)
  - `pacjent-1-kot.jpg`, `pacjent-2-bernenczyk.jpg`, `pacjent-3-owczarek.jpg` — 1500×998 (3:2)

Podmiana zdjęcia: nowy plik pod tą samą nazwą w `zdjecia/` i odświeżenie strony.

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

## Do uzupełnienia

- lista publikacji (na razie trzy wiersze-zaślepki „20__”)
