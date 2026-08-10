(function () {
  var btn = document.getElementById('themeBtn');
  var html = document.documentElement;
  var saved = localStorage.getItem('autobrain-theme');
  if (saved === 'light') html.dataset.theme = 'light';
  if (btn) {
    btn.textContent = html.dataset.theme === 'light' ? '☀️' : '🌙';
    btn.addEventListener('click', function () {
      var next = html.dataset.theme === 'light' ? 'dark' : 'light';
      html.dataset.theme = next;
      localStorage.setItem('autobrain-theme', next);
      btn.textContent = next === 'light' ? '☀️' : '🌙';
    });
  }
  var hb = document.getElementById('hamburger');
  var navList = document.querySelector('nav ul');
  if (hb && navList) {
    hb.addEventListener('click', function () {
      navList.classList.toggle('open');
    });
    navList.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') navList.classList.remove('open');
    });
  }
  var moreBtn = document.getElementById('moreBtn');
  var moreMenu = document.querySelector('.nav-more');
  if (moreBtn && moreMenu) {
    moreBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = moreMenu.classList.toggle('open');
      moreBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function (e) {
      if (!moreMenu.contains(e.target)) {
        moreMenu.classList.remove('open');
        moreBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }
})();
