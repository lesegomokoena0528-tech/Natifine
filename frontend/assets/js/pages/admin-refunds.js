/* Admin — Refunds */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("admin");

  var tbody = NF.qs("#rows");
  var pager = NF.qs("#pager");
  var SIZE = 12;
  var refunds = [];
  var state = { page: 1, query: "", status: "" };

  function filtered() {
    var q = state.query.toLowerCase();
    return refunds.filter(function (r) {
      if (state.status && r.status !== state.status) return false;
      if (!q) return true;
      return [r.refund_reference, r.payment_reference, r.fine_number, r.user_name, r.user_email, r.reason]
        .some(function (v) { return v && String(v).toLowerCase().indexOf(q) >= 0; });
    });
  }

  function render() {
    var rows = filtered();
    var pages = Math.max(1, Math.ceil(rows.length / SIZE));
    if (state.page > pages) state.page = pages;
    var slice = rows.slice((state.page - 1) * SIZE, state.page * SIZE);

    if (!slice.length) {
      tbody.innerHTML = '<tr><td colspan="8">' + NF.emptyState("No refunds found", "No refund requests match your filters.", "refund") + "</td></tr>";
      pager.innerHTML = "";
      return;
    }
    tbody.innerHTML = "";
    slice.forEach(function (r) {
      var tr = NF.el("tr", { class: "row-link" });
      var actions = '<button class="btn btn-sm btn-secondary view" type="button">View</button>';
      if (r.status === "PENDING") {
        actions += ' <button class="btn btn-sm approve" type="button">Approve</button>';
        actions += ' <button class="btn btn-sm btn-secondary reject" type="button">Reject</button>';
      }
      tr.innerHTML =
        '<td class="mono nowrap">' + NF.esc(r.refund_reference || "—") + "</td>" +
        '<td class="mono nowrap">' + NF.esc(r.payment_reference || "—") + "</td>" +
        '<td class="nowrap">' + NF.esc(r.fine_number || "—") + "</td>" +
        "<td>" + NF.esc(r.user_name || "—") + (r.user_email ? '<div class="text-muted small">' + NF.esc(r.user_email) + "</div>" : "") + "</td>" +
        '<td class="nowrap"><strong>' + NF.money(r.amount) + "</strong></td>" +
        "<td>" + NF.statusBadge(r.status) + "</td>" +
        '<td class="nowrap">' + NF.fmtDateTime(r.created_at) + "</td>" +
        '<td class="actions">' + actions + "</td>";
      NF.qs(".view", tr).addEventListener("click", function (e) { e.stopPropagation(); detail(r); });
      var ab = NF.qs(".approve", tr);
      if (ab) ab.addEventListener("click", function (e) { e.stopPropagation(); approve(r); });
      var rb = NF.qs(".reject", tr);
      if (rb) rb.addEventListener("click", function (e) { e.stopPropagation(); reject(r); });
      tr.addEventListener("click", function () { detail(r); });
      tbody.appendChild(tr);
    });
    NF.renderPagination(pager, { page: state.page, pages: pages, total: rows.length, onPage: function (p) { state.page = p; render(); } });
  }

  function renderStats() {
    var pending = refunds.filter(function (r) { return r.status === "PENDING"; }).length;
    var completed = refunds.filter(function (r) { return r.status === "COMPLETED"; }).length;
    var value = refunds.reduce(function (sum, r) { return r.status === "COMPLETED" ? sum + Number(r.amount || 0) : sum; }, 0);
    NF.qs("#t-total").textContent = refunds.length;
    NF.qs("#t-pending").textContent = pending;
    NF.qs("#t-completed").textContent = completed;
    NF.qs("#t-amount").textContent = NF.money(value);
  }

  function detail(r) {
    var html = "<dl class='kv'>" +
      "<dt>Refund reference</dt><dd class='mono'>" + NF.esc(r.refund_reference || "—") + "</dd>" +
      "<dt>Payment reference</dt><dd class='mono'>" + NF.esc(r.payment_reference || "—") + "</dd>" +
      "<dt>Fine number</dt><dd>" + NF.esc(r.fine_number || "—") + "</dd>" +
      "<dt>Applicant</dt><dd>" + NF.esc(r.user_name || "—") + (r.user_email ? " &middot; " + NF.esc(r.user_email) : "") + "</dd>" +
      "<dt>Amount</dt><dd><strong>" + NF.money(r.amount) + "</strong></dd>" +
      "<dt>Status</dt><dd>" + NF.statusBadge(r.status) + "</dd>" +
      "<dt>Requested</dt><dd>" + NF.fmtDateTime(r.created_at) + "</dd>" +
      "<dt>Approved</dt><dd>" + (r.approved_date ? NF.fmtDateTime(r.approved_date) : "—") + "</dd>" +
      (r.admin_note ? "<dt>Decision note</dt><dd>" + NF.esc(r.admin_note) + "</dd>" : "") +
      "</dl>" +
      "<p class='mt-16'><strong>Reason:</strong> " + NF.esc(r.reason || "—") + "</p>";
    var actions = [{ label: "Close", class: "btn-secondary", onClick: function (c) { c(); } }];
    if (r.status === "PENDING") {
      actions.unshift({ label: "Reject refund", class: "btn-secondary", onClick: function (c) { c(); reject(r); } });
      actions.unshift({ label: "Approve refund", class: "btn", onClick: function (c) { c(); approve(r); } });
    }
    NF.modal({ title: "Refund " + (r.refund_reference || ""), size: "lg", content: html, actions: actions });
  }

  function approve(r) {
    NF.confirm({
      title: "Approve refund",
      message: "Approve the refund of " + NF.money(r.amount) + " for " + (r.user_name || "this citizen") + "? The payment will be marked refunded and the fine re-issued.",
      confirmLabel: "Approve refund"
    }).then(function (ok) {
      if (!ok) return;
      Api.patch("/api/v1/payments/refunds/" + r.refund_id + "/approve", {}).then(function () {
        NF.toast("Refund approved.", "success");
        load();
      }).catch(function (err) {
        NF.toast(err.message, "error", "Approval failed");
      });
    });
  }

  function reject(r) {
    var html =
      "<p>Reject the refund of <strong>" + NF.money(r.amount) + "</strong> for " +
      NF.esc(r.user_name || "this citizen") + "?</p>" +
      "<p class='text-muted small'>The payment and fine will stay unchanged.</p>" +
      "<div class='form-group mt-16'><label for='reject-reason'>Reason (optional)</label>" +
      "<textarea class='textarea' id='reject-reason' maxlength='500' placeholder='Optional note explaining the decision…'></textarea></div>";

    NF.modal({
      title: "Reject refund",
      size: "lg",
      content: html,
      actions: [
        { label: "Cancel", class: "btn-secondary", onClick: function (c) { c(); } },
        { label: "Reject refund", class: "btn", onClick: function (c, btn) { submit(c, btn); } }
      ]
    });

    function submit(close, btn) {
      var reason = NF.qs("#reject-reason").value.trim();
      NF.setLoading(btn, true, "Rejecting…");
      Api.patch("/api/v1/payments/refunds/" + r.refund_id + "/reject", reason ? { reason: reason } : {}).then(function () {
        close();
        NF.toast("Refund rejected.", "success");
        load();
      }).catch(function (err) {
        NF.setLoading(btn, false);
        NF.toast(err.message, "error", "Rejection failed");
      });
    }
  }

  function load() {
    tbody.innerHTML = '<tr><td colspan="8"><div class="spinner"></div></td></tr>';
    Api.get("/api/v1/payments/refunds").then(function (res) {
      refunds = res.data || [];
      renderStats();
      render();
    }).catch(function (err) {
      tbody.innerHTML = '<tr><td colspan="8">' + NF.emptyState("Could not load refunds", err.message, "x") + "</td></tr>";
    });
  }

  NF.qs("#search").addEventListener("input", NF.debounce(function (e) { state.query = e.target.value.trim(); state.page = 1; render(); }, 200));
  NF.qs("#status").addEventListener("change", function (e) { state.status = e.target.value; state.page = 1; render(); });
  NF.qs("#refresh").addEventListener("click", load);

  load();
})();
