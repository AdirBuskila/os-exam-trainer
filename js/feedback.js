/* feedback.js — "found a mistake / a new exam is missing? email me" links.
   Same idea as the other study apps, but the strings live in the i18n dictionaries (foot.feedback,
   report.link, mail.*) so both the English and the Hebrew UI get their own text.
   The mail address is never written out in HTML or as one string: it is assembled here at runtime,
   and a link only gets its mailto href when it is rendered.

   Public API (window.Feedback):
     mountFooter()      (re)fill <div id="feedbackLine"> in the footer (also on every languagechange)
     reportRow(q)       '<div class="reportrow"><a class="reportlink" href="mailto:…">…</a></div>' for one question
                        q = {id, exam, text}  (text = plain question text; only its first ~80 chars are used) */
(function (root, doc) {
'use strict';

function addr() { return ['adirbu98', 'gmail.com'].join('@'); }
function T(key, params) { return (root.I18N ? root.I18N.t(key, params) : key); }
function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;'); }
function mailto(subject, body) {
  return 'mailto:' + addr() + '?subject=' + encodeURIComponent(subject) + (body ? '&body=' + encodeURIComponent(body) : '');
}
function snippet(s) {
  var t = String(s == null ? '' : s).replace(/\s+/g, ' ').trim();
  return t.length > 80 ? t.slice(0, 80) + '…' : t;
}
function title() { return T('app.title'); }

function reportHref(q) {
  var p = { title: title(), id: q.id, exam: q.exam || '', snippet: snippet(q.text) };
  return mailto(T('mail.reportSubject', p), T('mail.reportBody', p));
}
function reportRow(q) {
  return '<div class="reportrow"><a class="reportlink" href="' + esc(reportHref(q)) + '" rel="noopener">' +
         esc(T('report.link')) + '</a></div>';
}
function mountFooter() {
  var box = doc.getElementById('feedbackLine');
  if (!box) return;
  box.textContent = '';
  var a = doc.createElement('a');
  a.className = 'feedback-link';
  a.href = mailto(T('mail.footerSubject', { title: title() }));
  a.textContent = T('foot.feedback');
  box.appendChild(a);
  var c = doc.createElement('a');
  c.className = 'coffee-link';
  c.href = 'https://buymeacoffee.com/adirbuskila';
  c.target = '_blank';
  c.rel = 'noopener';
  c.textContent = T('foot.coffee');
  box.appendChild(c);
}

root.Feedback = { mountFooter: mountFooter, reportRow: reportRow, reportHref: reportHref };
mountFooter();   // the script sits at the end of <body>: the footer already exists
if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', mountFooter);
if (root.addEventListener) root.addEventListener('languagechange', mountFooter);

})(typeof window !== 'undefined' ? window : globalThis,
   typeof document !== 'undefined' ? document : { getElementById: function () { return null; }, readyState: 'complete' });
