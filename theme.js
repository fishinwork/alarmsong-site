/* Which theme the page wears. Light by default — that is the site's own look.
   The choice is this browser's alone: it never leaves the machine and nothing
   is stored about who made it. Loaded in <head> so the page never flashes. */
(function () {
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem('theme'); } catch (e) {}
  root.setAttribute('data-theme', saved || 'light');

  function paint() {
    var now = root.getAttribute('data-theme');
    document.querySelectorAll('.themes button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.theme === now));
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    /* Every switch on the page, not just the first one: the page may carry
       one in the bar and another somewhere below, and a second silent switch
       is worse than none. */
    document.querySelectorAll('.themes').forEach(function (box) {
      box.addEventListener('click', function (e) {
        var b = e.target.closest('button');
        if (!b) return;
        root.setAttribute('data-theme', b.dataset.theme);
        try { localStorage.setItem('theme', b.dataset.theme); } catch (err) {}
        paint();
      });
    });
    paint();
  });
})();
