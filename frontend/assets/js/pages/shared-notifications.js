/* Shared — Notifications (citizen / officer / admin) */
(function () {
  "use strict";
  var NF = window.NF;
  if (!Guard.requireAuth()) return;
  var list = NF.qs("#list");
  var items = [];

  function render() {
    if (!items.length) {
      list.innerHTML = NF.emptyState("No notifications", "You're all caught up.", "bell");
      return;
    }
    list.innerHTML = "";
    items.forEach(function (n) {
      var unread = !n.read_date;
      var card = NF.el("div", { class: "card notif" + (unread ? " unread" : "") });
      card.innerHTML =
        "<div class='card-body'>" +
        "<div class='flex items-center gap-12'>" +
        "<span class='avatar avatar-sm'>" + NF.icon(n.type === "FINE_DUE" || n.type === "OVERDUE_FINE" ? "fines" : "bell", "ico") + "</span>" +
        "<div class='flex-1'><div class='flex items-center gap-8'><strong>" + NF.esc(n.title) + "</strong>" +
        (unread ? "<span class='badge badge-info'>New</span>" : "") + "</div>" +
        "<div class='small text-muted'>" + NF.esc(NF.relTime(n.created_at)) + " · " + NF.esc(NF.titleCase(n.channel)) + "</div></div>" +
        NF.statusBadge(n.status) +
        "</div>" +
        "<p class='text-soft mt-12 mb-0'>" + NF.esc(n.message) + "</p>" +
        "<div class='small text-muted mt-8'>Type: " + NF.esc(NF.titleCase(n.type)) + (n.sent_date ? " · Sent " + NF.fmtDateTime(n.sent_date) : "") + "</div>" +
        "</div>";
      card.addEventListener("click", function () { markRead(n, card); });
      list.appendChild(card);
    });
  }

  function markRead(n, card) {
    if (n.read_date) return;
    Api.put("/api/notifications/" + n.notification_id + "/read", {}).then(function () {
      n.read_date = new Date().toISOString();
      card.classList.remove("unread");
      var badge = NF.qs(".badge-info", card);
      if (badge) badge.remove();
    }).catch(function () { /* silent */ });
  }

  Api.get("/api/notifications/me").then(function (res) { items = res.data || []; render(); })
    .catch(function (err) {
      list.innerHTML = NF.emptyState("Could not load notifications", err.message, "x");
    });
})();
