/* Visitor counters for alarmsong.com. One file for both, so changing a counter
   means changing one line instead of six pages.

   Google Analytics 4 — property "AlarmSong", stream alarmsong.com.
   Yandex Metrica — counter 113013793, session replay deliberately off.

   Both set cookies. Before the site goes public in the EU it needs a consent
   banner in front of this file; until then the site has no real visitors. */

(function () {
  var GA = 'G-C6TS1B9SZR';
  var YM = 113013793;

  /* Google */
  var tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA;
  document.head.appendChild(tag);
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag('js', new Date());
  gtag('config', GA);

  /* Yandex */
  (function (m, e, t, r, i, k, a) {
    m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments); };
    m[i].l = 1 * new Date();
    for (var j = 0; j < document.scripts.length; j++) {
      if (document.scripts[j].src === r) { return; }
    }
    k = e.createElement(t);
    a = e.getElementsByTagName(t)[0];
    k.async = 1;
    k.src = r;
    a.parentNode.insertBefore(k, a);
  })(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js?id=' + YM, 'ym');

  window.ym(YM, 'init', {
    ssr: true,
    clickmap: true,
    accurateTrackBounce: true,
    trackLinks: true,
    webvisor: false
  });
})();
