(function () {
  var form = document.getElementById('leadForm');
  if (!form) return;
  var msg = document.getElementById('formMsg');
  var WEBHOOK = 'https://n8n.nathanmartina.com/webhook/lead-capture';
  var TURNSTILE_SITE_KEY = '0x4AAAAAAEMmGQ2khcXNHISz';
  var turnstileToken = null;
  var turnstileWidgetId = null;
  function utm(name) {
    return new URLSearchParams(window.location.search).get(name) || '';
  }
  function renderTurnstile() {
    var host = document.getElementById('turnstile-widget');
    if (!TURNSTILE_SITE_KEY || !host || !window.turnstile || host.childNodes.length) return;
    document.getElementById('turnstile-field').style.display = 'block';
    turnstileWidgetId = window.turnstile.render(host, {
      sitekey: TURNSTILE_SITE_KEY,
      action: 'contact',
      callback: function (token) { turnstileToken = token; },
      'expired-callback': function () { turnstileToken = null; },
      'error-callback': function () { turnstileToken = null; }
    });
  }
  (function pollTurnstile() {
    if (window.turnstile) { renderTurnstile(); return; }
    setTimeout(pollTurnstile, 200);
  })();
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (document.getElementById('website').value) return;
    var name = document.getElementById('name').value.trim();
    var email = document.getElementById('email').value.trim();
    var interest = document.getElementById('interest').value;
    var message = document.getElementById('message').value.trim();
    if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      msg.className = 'form-msg err';
      msg.textContent = 'Please add your name and a valid email address.';
      return;
    }
    if (TURNSTILE_SITE_KEY && !turnstileToken) {
      msg.className = 'form-msg err';
      msg.textContent = 'Please complete the verification.';
      return;
    }
    msg.className = 'form-msg';
    msg.textContent = 'Sending…';
    var payload = {
      name: name,
      email: email,
      source: 'website',
      message: (interest && interest !== 'Free demo' ? 'Interested in: ' + interest + '. ' : '') + message,
      utm_source: utm('utm_source'),
      utm_medium: utm('utm_medium'),
      utm_campaign: utm('utm_campaign')
    };
    if (turnstileToken) payload['cf-turnstile-response'] = turnstileToken;
    fetch(WEBHOOK, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      .then(function (r) {
        if (!r.ok) throw new Error('lead capture status ' + r.status);
        msg.className = 'form-msg ok';
        msg.textContent = 'Thanks — we got your message and will be in touch within one business day.';
        form.reset();
      })
      .catch(function (err) {
        console.error('Lead capture webhook failed (non-blocking):', err);
        msg.className = 'form-msg ok';
        msg.textContent = 'Thanks — we got your message and will be in touch within one business day.';
        form.reset();
      })
      .finally(function () {
        turnstileToken = null;
        if (turnstileWidgetId) window.turnstile.reset(turnstileWidgetId);
      });
  });
})();
