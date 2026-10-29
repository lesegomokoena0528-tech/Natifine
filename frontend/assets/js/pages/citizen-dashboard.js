/* Citizen dashboard */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("citizen");

  function renderVehicles(vehicles) {
    var box = NF.qs("#vehicles");
    if (!vehicles || !vehicles.length) {
      box.innerHTML = NF.emptyState("No vehicles yet", "Add a vehicle to start receiving fines.", "vehicle");
      return;
    }
    box.innerHTML = "";
    vehicles.forEach(function (v) {
      var row = NF.el("div", { class: "flex items-center gap-12" });
      row.style.padding = "12px 0";
      row.style.borderBottom = "1px solid var(--border)";
      row.innerHTML =
        '<span class="avatar avatar-sm">' + NF.esc(NF.initials(v.make)) + "</span>" +
        "<div class='flex-1'><strong>" + NF.esc(v.registration_number) + "</strong>" +
        "<div class='small text-muted'>" + NF.esc(v.make + " " + v.model + " · " + v.year) + "</div></div>" +
        '<span class="badge badge-' + NF.esc(String(v.status).toLowerCase()) + '">' + NF.esc(NF.titleCase(v.status)) + "</span>";
      box.appendChild(row);
    });
  }

  Api.get("/api/citizen/dashboard").then(function (res) {
    var d = res.data;
    var user = d.user || {};
    var s = d.summary || {};

    NF.qs("#welcome").textContent = "Welcome, " + (user.first_name || "motorist");
    NF.qs("#welcome-sub").textContent = d.message || "Here is a summary of your traffic fines and account.";

    NF.qs("#s-total").textContent = s.total_fines != null ? s.total_fines : 0;
    NF.qs("#s-unpaid").textContent = s.unpaid_fines != null ? s.unpaid_fines : 0;
    NF.qs("#s-out").textContent = NF.money(s.outstanding_amount || 0);
    NF.qs("#s-paid").textContent = NF.money(s.paid_amount || 0);

    renderVehicles(d.vehicles || []);

    var fines = d.recent_fines || [];
    var body = NF.qs("#recent-fines");
    if (!fines.length) {
      body.innerHTML = '<tr><td colspan="5">' + NF.emptyState("No fines", "You have no traffic fines on record.", "check") + "</td></tr>";
      return;
    }
    body.innerHTML = "";
    fines.forEach(function (f) {
      var overdue = NF.isOverdue(f);
      var tr = NF.el("tr", { class: "row-link" });
      tr.innerHTML =
        '<td class="mono nowrap">' + NF.esc(f.fine_number) + "</td>" +
        "<td>" + NF.esc(f.offence) + "</td>" +
        '<td class="nowrap"><strong>' + NF.money(f.amount) + "</strong></td>" +
        '<td class="nowrap">' + NF.fmtDate(f.due_date) + (overdue ? ' <span class="badge badge-overdue">Overdue</span>' : "") + "</td>" +
        "<td>" + NF.statusBadge(f.status) + "</td>";
      tr.addEventListener("click", function () {
        window.location.href = "/pages/citizen/fines.html?id=" + f.fine_id;
      });
      body.appendChild(tr);
    });
  }).catch(function (err) {
    NF.toast(err.message, "error", "Could not load dashboard");
  });
})();
