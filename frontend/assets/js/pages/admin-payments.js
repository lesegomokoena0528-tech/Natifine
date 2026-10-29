/* Admin — Payments */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("admin");

  var tbody = NF.qs("#rows");
  var pager = NF.qs("#pager");
  var SIZE = 15;
  var payments = [];
  var state = { page: 1, query: "", status: "" };

  function filtered() {
    return payments.filter(function (p) {
      if (state.status && p.status !== state.status) return false;
      return true;
    });
  }

  function render() {
    var rows = filtered();
    var pages = Math.max(1, Math.ceil(rows.length / SIZE));
    if (state.page > pages) state.page = pages;
    var slice = rows.slice((state.page - 1) * SIZE, state.page * SIZE);
    if (!slice.length) {
      tbody.innerHTML = '<tr><td colspan="8">' + NF.emptyState("No payments", "No transactions match your filters.", "payment") + "</td></tr>";
      pager.innerHTML = "";
      return;
    }
    tbody.innerHTML = "";
    slice.forEach(function (p) {
      var tr = NF.el("tr");
      var receipt = p.status === "PAID" ? '<button class="btn btn-sm btn-secondary rcpt" type="button">Receipt</button>' : "";
      tr.innerHTML =
        '<td class="mono nowrap">' + NF.esc(p.payment_reference) + "</td>" +
        '<td class="mono nowrap">' + NF.esc(p.fine_number || "—") + "</td>" +
        "<td>" + NF.esc(NF.titleCase(p.gateway)) + "</td>" +
        "<td>" + NF.esc(NF.titleCase(p.payment_method)) + "</td>" +
        '<td class="nowrap"><strong>' + NF.money(p.amount) + "</strong></td>" +
        "<td>" + NF.statusBadge(p.status) + "</td>" +
        '<td class="nowrap">' + (p.paid_at ? NF.fmtDateTime(p.paid_at) : "—") + "</td>" +
        '<td class="actions">' + receipt + "</td>";
      var r = NF.qs(".rcpt", tr);
      if (r) r.addEventListener("click", function () { download(p); });
      tbody.appendChild(tr);
    });
    NF.renderPagination(pager, { page: state.page, pages: pages, total: rows.length, onPage: function (pg) { state.page = pg; render(); } });
  }

  function download(p) {
    NF.toast("Preparing receipt…", "info");
    Api.download("/api/v1/payments/" + p.payment_id + "/receipt", "NatiFine-Receipt-" + p.payment_reference + ".pdf")
      .then(function () { NF.toast("Receipt downloaded.", "success"); })
      .catch(function (err) { NF.toast(err.message, "error", "Receipt failed"); });
  }

  function loadStats() {
    Api.get("/api/v1/payments/statistics").then(function (res) {
      var d = res.data || {};
      NF.qs("#t-payments").textContent = d.payments != null ? d.payments : 0;
      NF.qs("#t-success").textContent = d.successful != null ? d.successful : 0;
      NF.qs("#t-pending").textContent = d.pending != null ? d.pending : 0;
      NF.qs("#t-failed").textContent = d.failed != null ? d.failed : 0;
      NF.qs("#t-refunds").textContent = d.refunds != null ? d.refunds : 0;
    }).catch(function () {});
  }

  function load() {
    tbody.innerHTML = '<tr><td colspan="8"><div class="spinner"></div></td></tr>';
    Api.get("/api/v1/payments/search", { query: { keyword: state.query } }).then(function (res) {
      payments = res.data || [];
      render();
    }).catch(function (err) {
      tbody.innerHTML = '<tr><td colspan="8">' + NF.emptyState("Could not load payments", err.message, "x") + "</td></tr>";
    });
  }

  NF.qs("#search").addEventListener("input", NF.debounce(function (e) { state.query = e.target.value.trim(); state.page = 1; load(); }, 300));
  NF.qs("#status").addEventListener("change", function (e) { state.status = e.target.value; state.page = 1; render(); });
  NF.qs("#refresh").addEventListener("click", function () { load(); loadStats(); });

  loadStats();
  load();
})();