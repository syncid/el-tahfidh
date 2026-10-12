(function () {
  'use strict';

  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');
  if (!toggle || !nav) return;

  function updateNavHeight() {
    if (!nav.classList.contains('is-open')) return;
    var top = nav.getBoundingClientRect().top;
    if (top >= 0 && top < window.innerHeight) {
      nav.style.maxHeight = 'calc(100dvh - ' + top + 'px)';
    }
  }

  function setOpen(open) {
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Tutup menu' : 'Buka menu');
    nav.classList.toggle('is-open', open);
    if (open) {
      updateNavHeight();
    } else {
      nav.style.maxHeight = '';
    }
  }

  toggle.addEventListener('click', function () {
    setOpen(toggle.getAttribute('aria-expanded') !== 'true');
  });

  // Tutup menu mobile setelah memilih tautan.
  nav.addEventListener('click', function (e) {
    if (e.target.closest('a[href]')) setOpen(false);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      if (nav.classList.contains('is-open')) {
        setOpen(false);
        toggle.focus();
      }
    }
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 1100) {
      setOpen(false);
    } else if (nav.classList.contains('is-open')) {
      updateNavHeight();
    }
  });

  window.addEventListener('scroll', function () {
    if (nav.classList.contains('is-open')) {
      updateNavHeight();
    }
  }, { passive: true });
})();
