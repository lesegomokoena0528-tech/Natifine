/* Officer — Dashboard */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("officer");

  Api.get("/api/v1/fines/statistics").then(function (res) {
    var d = res.data || {};
    NF.qs("#s-total").textContent = d.total != null ? d.total : 0;
    NF.qs("#s-unpaid").textContent = d.unpaid != null ? d.unpaid : 0;
    NF.qs("#s-paid").textContent = d.paid != null ? d.paid : 0;
    NF.qs("#s-revenue").textContent = NF.money(d.revenue || 0);
  }).catch(function (err) { NF.toast(err.message, "error", "Statistics"); });

  var recent = NF.qs("#recent");
  Api.get("/api/v1/fines", { query: { page: 1, size: 6 } }).then(function (res) {
    var items = (res.data && res.data.items) || [];
    if (!items.length) {
      recent.innerHTML = '<tr><td colspan="5">' + NF.emptyState("No fines yet", "Issue the first fine to get started.", "fines") + "</td></tr>";
      return;
    }
    recent.innerHTML = "";
    items.forEach(function (f) {
      var tr = NF.el("tr", { class: "row-link" });
      tr.innerHTML =
        '<td class="mono nowrap">' + NF.esc(f.fine_number) + "</td>" +
        "<td>" + NF.esc(f.offence) + "</td>" +
        '<td class="nowrap">' + NF.esc(f.registration_number) + "</td>" +
        '<td class="nowrap"><strong>' + NF.money(f.amount) + "</strong></td>" +
        "<td>" + NF.statusBadge(f.status) + "</td>";
      tr.addEventListener("click", function () {
        window.location.href = "/pages/officer/fines.html?id=" + f.fine_id;
      });
      recent.appendChild(tr);
    });
  }).catch(function (err) {
    recent.innerHTML = '<tr><td colspan="5">' + NF.emptyState("Could not load fines", err.message, "x") + "</td></tr>";
  });

  var disputesBox = NF.qs("#disputes");
  Api.get("/api/v1/disputes/pending").then(function (res) {
    var list = res.data || [];
    if (!list.length) {
      disputesBox.innerHTML = NF.emptyState("Nothing to review", "No disputes are awaiting your review.", "check");
      return;
    }
    disputesBox.innerHTML = "";
    list.forEach(function (d) {
      var row = NF.el("div", { class: "flex items-center gap-12", style: "padding:12px 0;border-bottom:1px solid var(--border)" });
      row.innerHTML =
        "<span class='avatar avatar-sm'>" + NF.icon("dispute", "ico") + "</span>" +
        "<div class='flex-1'><strong>" + NF.esc(d.fine_number || ("Dispute #" + d.dispute_id)) + "</strong>" +
        "<div class='small text-muted'>" + NF.esc(d.citizen_name || "Citizen") + "</div></div>" +
        '<a class="btn btn-sm btn-secondary" href="/pages/officer/disputes.html?id=' + d.dispute_id + '">Review</a>';
      disputesBox.appendChild(row);
    });
  }).catch(function (err) {
    disputesBox.innerHTML = NF.emptyState("Could not load disputes", err.message, "x");
  });
})();