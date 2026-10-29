/* Admin — Dashboard */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("admin");

  Api.get("/api/admin/dashboard").then(function (res) {
    var d = res.data || {};
    NF.qs("#s-users").textContent = d.users != null ? d.users : 0;
    NF.qs("#s-officers").textContent = d.officers != null ? d.officers : 0;
    NF.qs("#s-vehicles").textContent = d.vehicles != null ? d.vehicles : 0;
    NF.qs("#s-revenue").textContent = NF.money(d.revenue || 0);
    NF.qs("#s-payments").textContent = d.payments != null ? d.payments : 0;
    NF.qs("#s-overdue").textContent = d.overdue_fines != null ? d.overdue_fines : 0;
    NF.qs("#s-unpaid").textContent = d.unpaid_fines != null ? d.unpaid_fines : 0;

    NF.qs("#k-fines").textContent = d.fines != null ? d.fines : 0;
    NF.qs("#k-paid").textContent = d.paid_fines != null ? d.paid_fines : 0;
    NF.qs("#k-unpaid").textContent = d.unpaid_fines != null ? d.unpaid_fines : 0;
    NF.qs("#k-disputes").textContent = d.disputes != null ? d.disputes : 0;
    NF.qs("#k-notifications").textContent = d.notifications != null ? d.notifications : 0;

    chart([
      { label: "Total", value: d.fines || 0, cls: "" },
      { label: "Paid", value: d.paid_fines || 0, cls: "accent" },
      { label: "Unpaid", value: d.unpaid_fines || 0, cls: "" },
      { label: "Overdue", value: d.overdue_fines || 0, cls: "" },
      { label: "Disputes", value: d.disputes || 0, cls: "" }
    ]);
  }).catch(function (err) {
    NF.toast(err.message, "error", "Dashboard");
  });

  function chart(items) {
    var box = NF.qs("#fine-chart");
    var max = Math.max.apply(null, items.map(function (i) { return i.value; }).concat([1]));
    box.innerHTML = "";
    items.forEach(function (it) {
      var col = NF.el("div", { class: "bar-col" });
      var pct = Math.round((it.value / max) * 100);
      col.innerHTML =
        "<div class='small fw-600'>" + it.value + "</div>" +
        "<div class='bar " + it.cls + "' style='height:" + Math.max(pct, 3) + "%'></div>" +
        "<div class='bar-label'>" + NF.esc(it.label) + "</div>";
      box.appendChild(col);
    });
  }
})();