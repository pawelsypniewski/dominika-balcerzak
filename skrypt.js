// Jedyny skrypt strony. Trzymany w osobnym pliku, bo polityka bezpieczeństwa
// (Content-Security-Policy w <head>) nie pozwala na skrypty wpisane w HTML.

// Znacznik „działa JavaScript” — dopiero wtedy telefon zwija dłuższe teksty.
// Ustawiany od razu, zanim strona się narysuje, żeby nic nie mignęło.
document.documentElement.classList.add('js');

document.addEventListener('DOMContentLoaded', function () {
  // „Czytaj więcej” w sekcji O mnie (na telefonie)
  var sekcja = document.getElementById('o-mnie');
  var przycisk = sekcja.querySelector('.czytaj-wiecej');
  przycisk.addEventListener('click', function () {
    var otwarte = sekcja.classList.toggle('rozwiniete');
    przycisk.setAttribute('aria-expanded', otwarte);
    przycisk.textContent = otwarte ? 'Zwiń' : 'Czytaj więcej';
  });

  // Adres e-mail składany dopiero w przeglądarce. W kodzie strony nie ma
  // gotowego „nazwa@domena”, więc roboty zbierające adresy go nie znajdą.
  document.querySelectorAll('[data-email-nazwa]').forEach(function (el) {
    var nazwa = el.getAttribute('data-email-nazwa');
    var domena = el.getAttribute('data-email-domena');
    var link = document.createElement('a');
    link.href = 'mailto:' + nazwa + '@' + domena;
    link.append(nazwa + '@', document.createElement('wbr'), domena);
    el.replaceChildren(link);
  });
});
