/* ==========================================================================
   NatiFine SA — shared UI helpers, app shell, guards
   Exposes: window.NF  (helpers), window.NFShell (portal shell), window.Guard
   ========================================================================== */

(function () {
  "use strict";

  /* ----------------------------------------------------------------- utils */
  function qs(sel, root) { return (root || document).querySelector(sel); }
  function qsa(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v === null || v === undefined || v === false) return;
        if (k === "class") node.className = v;
        else if (k === "html") node.innerHTML = v;
        else if (k === "text") node.textContent = v;
        else if (k.indexOf("on") === 0 && typeof v === "function") node.addEventListener(k.slice(2), v);
        else if (k === "dataset") Object.keys(v).forEach(function (d) { node.dataset[d] = v[d]; });
        else node.setAttribute(k, v);
      });
    }
    if (children !== undefined && children !== null) {
      (Array.isArray(children) ? children : [children]).forEach(function (c) {
        if (c === null || c === undefined || c === false) return;
        node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
      });
    }
    return node;
  }

  function esc(s) {
    if (s === null || s === undefined) return "";
    return String(s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  var zar = new Intl.NumberFormat("en-ZA", { style: "currency", currency: "ZAR", minimumFractionDigits: 2 });

  function money(n) {
    var num = Number(n);
    if (isNaN(num)) return "R 0.00";
    return zar.format(num).replace("ZAR", "R").replace(/\u00a0/g, " ");
  }

  function parseDate(v) {
    if (!v) return null;
    var d = new Date(v);
    return isNaN(d.getTime()) ? null : d;
  }

  function fmtDate(v) {
    var d = parseDate(v);
    if (!d) return "—";
    return d.toLocaleDateString("en-ZA", { day: "2-digit", month: "short", year: "numeric" });
  }

  function fmtDateTime(v) {
    var d = parseDate(v);
    if (!d) return "—";
    return d.toLocaleDateString("en-ZA", { day: "2-digit", month: "short", year: "numeric" }) + ", " +
      d.toLocaleTimeString("en-ZA", { hour: "2-digit", minute: "2-digit" });
  }

  function relTime(v) {
    var d = parseDate(v);
    if (!d) return "—";
    var diff = Date.now() - d.getTime();
    var mins = Math.round(diff / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return mins + "m ago";
    var hrs = Math.round(mins / 60);
    if (hrs < 24) return hrs + "h ago";
    var days = Math.round(hrs / 24);
    if (days < 30) return days + "d ago";
    return fmtDate(v);
  }

  function titleCase(s) {
    if (!s) return "";
    return String(s).toLowerCase().replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  function initials(name) {
    if (!name) return "?";
    return name.trim().split(/\s+/).slice(0, 2).map(function (p) { return p[0]; }).join("").toUpperCase();
  }

  function statusBadge(status) {
    var key = String(status || "").toLowerCase();
    return '<span class="badge badge-' + esc(key) + '">' + esc(titleCase(status)) + "</span>";
  }

  function param(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  function isOverdue(fine) {
    if (!fine) return false;
    var open = ["ISSUED", "DISPUTED", "UNDER_REVIEW"].indexOf(fine.status) >= 0;
    var due = parseDate(fine.due_date);
    return open && due && due.getTime() < Date.now();
  }

  function debounce(fn, wait) {
    var t;
    return function () {
      var args = arguments, ctx = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(ctx, args); }, wait || 300);
    };
  }

  /* ----------------------------------------------------------------- toasts */
  function toastStack() {
    var s = qs("#nf-toasts");
    if (!s) { s = el("div", { id: "nf-toasts", class: "toast-stack" }); document.body.appendChild(s); }
    return s;
  }

  function toast(message, type, title) {
    var stack = toastStack();
    var node = el("div", { class: "toast " + (type || "info") });
    node.innerHTML =
      '<div class="flex-1">' +
      (title ? '<div class="t-title">' + esc(title) + "</div>" : "") +
      '<div class="t-msg">' + esc(message) + "</div>" +
      "</div>" +
      '<button class="t-close" aria-label="Dismiss">&times;</button>';
    qs(".t-close", node).addEventListener("click", function () { node.remove(); });
    stack.appendChild(node);
    setTimeout(function () { node.style.opacity = "0"; node.style.transition = "opacity .3s"; setTimeout(function () { node.remove(); }, 320); }, type === "error" ? 6000 : 4200);
    return node;
  }

  /* ---------------------------------------------------------------- modal */
  function openModal(opts) {
    opts = opts || {};
    var overlay = el("div", { class: "modal-overlay" });
    var modal = el("div", { class: "modal" + (opts.size === "lg" ? " modal-lg" : "") });
    var header = el("div", { class: "modal-header" });
    header.appendChild(el("h3", { text: opts.title || "" }));
    var closeBtn = el("button", { class: "icon-btn", html: icon("x"), "aria-label": "Close" });
    header.appendChild(closeBtn);
    var body = el("div", { class: "modal-body" });
    if (typeof opts.content === "string") body.innerHTML = opts.content;
    else if (opts.content) body.appendChild(opts.content);
    modal.appendChild(header);
    modal.appendChild(body);

    var footer = null;
    if (opts.actions && opts.actions.length) {
      footer = el("div", { class: "modal-footer" });
      opts.actions.forEach(function (a) {
        var b = el("button", { class: "btn " + (a.class || "btn-secondary"), text: a.label });
        b.addEventListener("click", function () { a.onClick && a.onClick(close, b); });
        footer.appendChild(b);
      });
      modal.appendChild(footer);
    }
    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    function close() { overlay.remove(); document.removeEventListener("keydown", onKey); }
    function onKey(e) { if (e.key === "Escape") close(); }
    closeBtn.addEventListener("click", close);
    overlay.addEventListener("mousedown", function (e) { if (e.target === overlay) close(); });
    document.addEventListener("keydown", onKey);
    return { close: close, body: body, overlay: overlay, footer: footer };
  }

  function confirmDialog(opts) {
    return new Promise(function (resolve) {
      var m = openModal({
        title: opts.title || "Please confirm",
        content: '<p style="margin:0;color:var(--text-soft)">' + esc(opts.message || "") + "</p>",
        actions: [
          { label: opts.cancelLabel || "Cancel", class: "btn-secondary", onClick: function (close) { close(); resolve(false); } },
          { label: opts.confirmLabel || "Confirm", class: opts.danger ? "btn-danger" : "btn", onClick: function (close) { close(); resolve(true); } }
        ]
      });
      m.overlay.addEventListener("mousedown", function (e) { if (e.target === m.overlay) resolve(false); });
    });
  }

  /* ----------------------------------------------------------------- icons */
  var ICONS = {
    dashboard: '<path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>',
    fines: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h6"/>',
    payment: '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',
    payments: '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',
    dispute: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    disputes: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    bell: '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
    notifications: '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
    user: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    vehicle: '<path d="M5 17H3v-5l2-5h14l2 5v5h-2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M5 17h14"/>',
    vehicles: '<path d="M5 17H3v-5l2-5h14l2 5v5h-2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M5 17h14"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    audit: '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    chart: '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
    logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>',
    download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    x: '<path d="M18 6 6 18M6 6l12 12"/>',
    menu: '<path d="M3 12h18M3 6h18M3 18h18"/>',
    eye: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/>',
    settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    officers: '<path d="M12 2 4 5v6c0 5 3.4 8.5 8 11 4.6-2.5 8-6 8-11V5l-8-3z"/><path d="m9 12 2 2 4-4"/>',
    refund: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',
    broadcast: '<path d="m3 11 18-8v18l-18-8z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>',
    eyeOff: '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><path d="M1 1l22 22"/>'
  };

  function icon(name, cls) {
    var path = ICONS[name] || "";
    return '<svg class="' + (cls || "ico") + '" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + path + "</svg>";
  }

  /* ----------------------------------------------------------------- guard */
  var Guard = {
    requireAuth: function () {
      if (!Session.isLoggedIn()) {
        window.location.href = "/pages/login.html?next=" + encodeURIComponent(window.location.pathname);
        return false;
      }
      return true;
    },
    requireRole: function (role) {
      if (!Guard.requireAuth()) return false;
      var r = Session.role();
      if (role && r !== role) {
        window.location.href = "/pages/" + (r || "login") + "/dashboard.html";
        return false;
      }
      return true;
    }
  };

  /* ------------------------------------------------------------------ shell */
  var NAV = {
    citizen: [
      { key: "dashboard", label: "Dashboard", href: "/pages/citizen/dashboard.html", icon: "dashboard" },
      { key: "fines", label: "My Fines", href: "/pages/citizen/fines.html", icon: "fines" },
      { key: "payments", label: "Payments", href: "/pages/citizen/payments.html", icon: "payment" },
      { key: "disputes", label: "Disputes", href: "/pages/citizen/disputes.html", icon: "dispute" },
      { key: "vehicles", label: "My Vehicles", href: "/pages/citizen/vehicles.html", icon: "vehicle" },
      { key: "notifications", label: "Notifications", href: "/pages/citizen/notifications.html", icon: "bell" },
      { key: "profile", label: "Profile", href: "/pages/citizen/profile.html", icon: "user" }
    ],
    officer: [
      { key: "dashboard", label: "Dashboard", href: "/pages/officer/dashboard.html", icon: "dashboard" },
      { key: "fines", label: "Traffic Fines", href: "/pages/officer/fines.html", icon: "fines" },
      { key: "issue-fine", label: "Issue Fine", href: "/pages/officer/issue-fine.html", icon: "plus" },
      { key: "disputes", label: "Disputes", href: "/pages/officer/disputes.html", icon: "dispute" },
      { key: "vehicles", label: "Vehicles", href: "/pages/officer/vehicles.html", icon: "vehicle" },
      { key: "notifications", label: "Notifications", href: "/pages/officer/notifications.html", icon: "bell" },
      { key: "profile", label: "Profile", href: "/pages/officer/profile.html", icon: "user" }
    ],
    admin: [
      { key: "dashboard", label: "Dashboard", href: "/pages/admin/dashboard.html", icon: "dashboard" },
      { key: "users", label: "Users", href: "/pages/admin/users.html", icon: "users" },
      { key: "officers", label: "Officers", href: "/pages/admin/officers.html", icon: "officers" },
      { key: "vehicles", label: "Vehicles", href: "/pages/admin/vehicles.html", icon: "vehicle" },
      { key: "fines", label: "Traffic Fines", href: "/pages/admin/fines.html", icon: "fines" },
      { key: "payments", label: "Payments", href: "/pages/admin/payments.html", icon: "payment" },
      { key: "refunds", label: "Refunds", href: "/pages/admin/refunds.html", icon: "refund" },
      { key: "disputes", label: "Disputes", href: "/pages/admin/disputes.html", icon: "dispute" },
      { key: "notifications", label: "Notifications", href: "/pages/admin/notifications.html", icon: "bell" },
      { key: "broadcast", label: "Broadcast", href: "/pages/admin/broadcast.html", icon: "broadcast" },
      { key: "audit", label: "Audit Log", href: "/pages/admin/audit.html", icon: "audit" },
      { key: "reports", label: "Reports", href: "/pages/admin/reports.html", icon: "chart" },
      { key: "profile", label: "Profile", href: "/pages/admin/profile.html", icon: "user" }
    ]
  };

  var NFShell = {
    nav: NAV,
    mount: function (config) {
      config = config || {};
      var role = config.role || Session.role();
      if (!Guard.requireAuth()) return;
      var user = Session.user() || {};
      var items = NAV[role] || [];

      /* sidebar */
      var sidebar = qs("#sidebar");
      if (sidebar) {
        var brand = el("div", { class: "sidebar-brand" });
        brand.innerHTML = '<a class="brand" href="/pages/' + role + '/dashboard.html"><span class="brand-mark">NF</span><span>NatiFine<small>' + esc(titleCase(role)) + " Portal</small></span></a>";
        var nav = el("nav", { class: "sidebar-nav" });
        items.forEach(function (it) {
          var a = el("a", { class: "sidebar-link" + (it.key === config.active ? " active" : ""), href: it.href });
          a.innerHTML = icon(it.icon) + "<span>" + esc(it.label) + "</span>";
          nav.appendChild(a);
        });
        var foot = el("div", { class: "sidebar-foot" });
        foot.innerHTML = "NatiFine SA &middot; Academic Prototype<br>Simulated payment & notification services";
        sidebar.innerHTML = "";
        sidebar.appendChild(brand);
        sidebar.appendChild(nav);
        sidebar.appendChild(foot);
      }

      /* topbar */
      var topbar = qs("#topbar");
      if (topbar) {
        var hamburger = el("button", { class: "icon-btn hamburger", html: icon("menu"), "aria-label": "Menu" });
        var titleWrap = el("div", {});
        titleWrap.innerHTML = '<div class="topbar-title">' + esc(config.title || "") + "</div>" +
          (config.subtitle ? '<div class="topbar-sub">' + esc(config.subtitle) + "</div>" : "");
        var spacer = el("div", { class: "topbar-spacer" });

        var bell = el("a", { class: "icon-btn", href: "/pages/" + role + "/notifications.html", html: icon("bell"), id: "nf-bell", "aria-label": "Notifications" });
        var userWrap = el("div", { class: "user-menu" });
        var userBtn = el("button", { class: "user-menu-btn" });
        userBtn.innerHTML = '<span class="avatar">' + esc(initials(user.full_name)) + "</span>" +
          '<span class="who hide-sm"><strong>' + esc(user.full_name || "Account") + "</strong><span>" + esc(titleCase(user.role || role)) + "</span></span>";
        var dd = el("div", { class: "dropdown hidden" });
        dd.innerHTML =
          '<a href="/pages/' + role + '/profile.html">' + icon("user", "ico") + "<span>My Profile</span></a>" +
          '<div class="sep"></div>' +
          '<button type="button" class="danger" id="nf-logout">' + icon("logout", "ico") + "<span>Sign out</span></button>";
        userWrap.appendChild(userBtn);
        userWrap.appendChild(dd);

        topbar.innerHTML = "";
        topbar.appendChild(hamburger);
        topbar.appendChild(titleWrap);
        topbar.appendChild(spacer);
        topbar.appendChild(bell);
        topbar.appendChild(userWrap);

        hamburger.addEventListener("click", function () { toggleSidebar(); });
        userBtn.addEventListener("click", function (e) { e.stopPropagation(); dd.classList.toggle("hidden"); });
        document.addEventListener("click", function () { dd.classList.add("hidden"); });
        dd.addEventListener("click", function (e) { e.stopPropagation(); });
        qs("#nf-logout", dd).addEventListener("click", function () {
          Api.logout();
          window.location.href = "/pages/login.html";
        });

        /* unread notification dot */
        Api.get("/api/notifications/me").then(function (res) {
          var list = res.data || [];
          var unread = list.filter(function (n) { return !n.read_date; }).length;
          if (unread > 0) {
            var dot = el("span", { class: "dot" });
            bell.appendChild(dot);
          }
        }).catch(function () { /* silent */ });
      }

      /* scrim */
      var scrim = qs("#scrim");
      if (scrim) scrim.addEventListener("click", function () { toggleSidebar(false); });

      function toggleSidebar(force) {
        var sb = qs("#sidebar");
        var sc = qs("#scrim");
        if (!sb) return;
        var open = force === undefined ? !sb.classList.contains("open") : force;
        sb.classList.toggle("open", open);
        if (sc) sc.classList.toggle("hidden", !open);
      }
      NFShell.toggleSidebar = toggleSidebar;
    }
  };

  /* ------------------------------------------------------------ pagination */
  function renderPagination(container, opts) {
    container.innerHTML = "";
    var page = opts.page || 1;
    var pages = Math.max(opts.pages || 1, 1);
    var info = el("div", { class: "text-muted small" });
    info.textContent = "Page " + page + " of " + pages + (opts.total != null ? " · " + opts.total + " records" : "");
    var pager = el("div", { class: "pager" });
    function btn(label, target, disabled, active) {
      var b = el("button", { class: "page-btn" + (active ? " is-active" : ""), type: "button" });
      b.innerHTML = label;
      b.disabled = !!disabled;
      if (!disabled && !active) b.addEventListener("click", function () { opts.onPage(target); });
      return b;
    }
    pager.appendChild(btn("&lsaquo;", page - 1, page <= 1));
    var start = Math.max(1, page - 2), end = Math.min(pages, start + 4);
    start = Math.max(1, end - 4);
    if (start > 1) pager.appendChild(btn("1", 1, false, page === 1)).appendChild(el("span", { class: "text-muted", text: "…" }));
    for (var i = start; i <= end; i++) pager.appendChild(btn(String(i), i, false, i === page));
    if (end < pages) { pager.appendChild(el("span", { class: "text-muted", text: "…" })); pager.appendChild(btn(String(pages), pages, false, page === pages)); }
    pager.appendChild(btn("&rsaquo;", page + 1, page >= pages));
    container.appendChild(info);
    container.appendChild(pager);
  }

  /* ------------------------------------------------------------- empty state */
  function emptyState(title, message, iconName) {
    return '<div class="empty"><div class="ico">' + icon(iconName || "search", "ico") + "</div><h3>" + esc(title) +
      "</h3><p>" + esc(message || "") + "</p></div>";
  }

  function skeletonRows(n, cols) {
    var out = "";
    for (var i = 0; i < (n || 5); i++) {
      out += "<tr>";
      for (var c = 0; c < (cols || 5); c++) out += '<td><div class="skeleton skeleton-row" style="width:' + (50 + Math.random() * 40) + '%"></div></td>';
      out += "</tr>";
    }
    return out;
  }

  function formErrors(form, errors) {
    qsa(".field-error", form).forEach(function (n) { n.textContent = ""; });
    qsa(".is-invalid", form).forEach(function (n) { n.classList.remove("is-invalid"); });
    if (!errors) return;
    Object.keys(errors).forEach(function (field) {
      var input = qs("[name='" + field + "']", form);
      var msg = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
      if (input) {
        input.classList.add("is-invalid");
        var target = qs("[data-error-for='" + field + "']", form) || input.parentNode.querySelector(".field-error");
        if (target) target.textContent = msg;
      }
    });
  }

  function setLoading(btn, loading, loadingText) {
    if (!btn) return;
    if (loading) {
      btn.dataset._label = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<span class="btn-spinner"></span> ' + (loadingText || "Please wait…");
    } else {
      btn.disabled = false;
      if (btn.dataset._label) btn.innerHTML = btn.dataset._label;
    }
  }

  window.NF = {
    qs: qs, qsa: qsa, el: el, esc: esc, icon: icon, icons: ICONS,
    money: money, fmtDate: fmtDate, fmtDateTime: fmtDateTime, relTime: relTime,
    titleCase: titleCase, initials: initials, statusBadge: statusBadge, isOverdue: isOverdue,
    param: param, debounce: debounce, toast: toast, modal: openModal, confirm: confirmDialog,
    renderPagination: renderPagination, emptyState: emptyState, skeletonRows: skeletonRows,
    formErrors: formErrors, setLoading: setLoading
  };
  window.NFShell = NFShell;
  window.Guard = Guard;
})();
