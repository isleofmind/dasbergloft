/* Das Bergloft – kleine Helfer ohne Framework: Galerie, Anfrageformular, Belegungskalender */
(function () {
  "use strict";
  var MAIL = "simone@alpenglueck-apartments.at", SUBJECT = "Anfrage Das Bergloft", PHONE = "4368110613284";

  document.querySelectorAll("footer").forEach(function (f) {
    var last = f.querySelector("p.text-secondary\\/50");
    if (last && /© \d{4}/.test(last.textContent)) last.textContent = "© " + new Date().getFullYear() + " Das Bergloft";
  });

  /* ---------- Galerie-Lightbox ---------- */
  var lb = document.getElementById("lightbox");
  var thumbs = Array.prototype.slice.call(document.querySelectorAll("#galerie button[aria-label]"));
  if (lb && thumbs.length) {
    var img = lb.querySelector("img"), cap = lb.querySelector("figcaption"), idx = 0, lastFocus = null;
    var full = function (b) {
      var i = b.querySelector("img"), m = (i.getAttribute("srcset") || "").match(/(\S+)\s+2000w/);
      return m ? m[1] : i.src;
    };
    var show = function (n) {
      idx = (n + thumbs.length) % thumbs.length;
      var t = thumbs[idx].querySelector("img");
      img.src = full(thumbs[idx]); img.alt = t.alt; cap.textContent = t.alt + " (" + (idx + 1) + "/" + thumbs.length + ")";
      [idx + 1, idx - 1].forEach(function (k) { new Image().src = full(thumbs[(k + thumbs.length) % thumbs.length]); });
    };
    var open = function (n) { lastFocus = document.activeElement; show(n); lb.hidden = false; document.body.style.overflow = "hidden"; lb.querySelector(".lb-close").focus(); };
    var close = function () { lb.hidden = true; document.body.style.overflow = ""; if (lastFocus) lastFocus.focus(); };
    thumbs.forEach(function (b, n) { b.addEventListener("click", function () { open(n); }); });
    lb.addEventListener("click", function (e) {
      var a = e.target.getAttribute("data-lb");
      if (a === "close" || e.target === lb) close(); else if (a === "prev") show(idx - 1); else if (a === "next") show(idx + 1);
    });
    document.addEventListener("keydown", function (e) {
      if (lb.hidden) return;
      if (e.key === "Escape") close(); else if (e.key === "ArrowLeft") show(idx - 1); else if (e.key === "ArrowRight") show(idx + 1);
    });
    var x0 = null;
    lb.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) show(idx + (dx < 0 ? 1 : -1));
    });
  }

  /* ---------- Anfrageformular ---------- */
  var form = document.getElementById("anfrage-form"), btns = document.getElementById("anfrage-buttons");
  if (form && btns) {
    var v = function (id) { return form.elements[id].value.trim(); };
    var de = function (d) { if (!d) return "-"; var p = d.split("-"); return p[2] + "." + p[1] + "." + p[0]; };
    var text = function () {
      return ["Hallo Simone,", "", "ich interessiere mich für eine Buchung im Das Bergloft.", "",
        "Name: " + (v("name") || "-"), "E-Mail: " + (v("email") || "-"),
        "Anreise: " + de(v("arrival")), "Abreise: " + de(v("departure")),
        "Anzahl Gäste: " + (v("guests") || "-"), "",
        v("message") || "Bitte sendet mir Verfügbarkeiten und Preise zu.", "", "Viele Grüße", v("name")].join("\n");
    };
    var q = function (o) { return Object.keys(o).map(function (k) { return k + "=" + encodeURIComponent(o[k]); }).join("&"); };
    var links = {
      whatsapp: function (t) { return "https://wa.me/" + PHONE + "?" + q({ text: t }); },
      mail: function (t) { return "mailto:" + MAIL + "?" + q({ subject: SUBJECT, body: t }); },
      gmail: function (t) { return "https://mail.google.com/mail/?" + q({ view: "cm", fs: 1, to: MAIL, su: SUBJECT, body: t }); },
      outlook: function (t) { return "https://outlook.live.com/mail/0/deeplink/compose?" + q({ to: MAIL, subject: SUBJECT, body: t }); }
    };
    var update = function () {
      var t = text();
      form.querySelectorAll("a[data-send]").forEach(function (a) { a.href = links[a.getAttribute("data-send")](t); });
    };
    var today = new Date().toISOString().slice(0, 10);
    form.elements.arrival.min = today; form.elements.departure.min = today;
    form.elements.arrival.addEventListener("change", function () {
      form.elements.departure.min = this.value || today;
      if (form.elements.departure.value && form.elements.departure.value <= this.value) form.elements.departure.value = "";
    });
    form.addEventListener("input", update); form.addEventListener("change", update); update();
    form.addEventListener("submit", function (e) { e.preventDefault(); });
    form.addEventListener("click", function (e) {
      var el = e.target.closest("[data-send]"); if (!el) return;
      var kind = el.getAttribute("data-send");
      if (kind === "cancel") { form.hidden = true; btns.hidden = false; return; }
      if (!form.reportValidity()) { e.preventDefault(); return; }
      update();
      if (kind === "copy") {
        var full = "An: " + MAIL + "\nBetreff: " + SUBJECT + "\n\n" + text();
        (navigator.clipboard ? navigator.clipboard.writeText(full) : Promise.reject()).then(function () {
          el.textContent = "Anfrage kopiert"; setTimeout(function () { el.textContent = "Anfrage kopieren"; }, 2500);
        }, function () { window.prompt("Anfrage kopieren:", full); });
      }
    });
    document.querySelectorAll("[data-open-form]").forEach(function (b) {
      b.addEventListener("click", function () {
        btns.hidden = true; form.hidden = false;
        form.scrollIntoView({ behavior: "smooth", block: "start" });
        setTimeout(function () { form.elements.name.focus({ preventScroll: true }); }, 400);
      });
    });
  }

  /* ---------- Belegungskalender (Xentra) passt seine Höhe an ---------- */
  var cal = document.getElementById("xentra-calendar-widget");
  if (cal) window.addEventListener("message", function (e) {
    if (e.origin !== "https://app.myxentra.com") return;
    var d = e.data;
    if (d && d.type === "xentra-widget-resize" && typeof d.height === "number") cal.style.height = d.height + "px";
  });
})();
