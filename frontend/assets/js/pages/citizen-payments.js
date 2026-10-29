/* Citizen — Payments */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("citizen");
  var tbody = NF.qs("#rows");
  var refundBody = NF.qs("#refund-rows");
  var payments = [];
  var refunds = [];

  var OPEN_REFUND = ["PENDING", "APPROVED", "PROCESSING", "COMPLETED"];

  function refundFor(paymentId) {
    for (var i = 0; i < refunds.length; i++) {
      if (String(refunds[i].payment_id) === String(paymentId) &&
        OPEN_REFUND.indexOf(refunds[i].status) >= 0) return refunds[i];
    }
    return null;
  }

  function render() {
    if (!payments.length) {
      tbody.innerHTML = '<tr><td colspan="7">' + NF.emptyState("No payments yet", "Once you pay a fine it will appear here.", "payment") + "</td></tr>";
      return;
    }
    tbody.innerHTML = "";
    payments.forEach(function (p) {
      var actions = "";
      if (p.status === "PAID") {
        actions += '<button class="btn btn-sm btn-secondary rcpt" type="button">Receipt</button> ';
        var existing = refundFor(p.payment_id);
        if (existing) {
          actions += '<button class="btn btn-sm btn-secondary" type="button" disabled>Refund ' + NF.esc(NF.titleCase(existing.status)) + "</button>";
        } else {
          actions += '<button class="btn btn-sm refund" type="button">Request refund</button>';
        }
      }
      var tr = NF.el("tr");
      tr.innerHTML =
        '<td class="mono nowrap">' + NF.esc(p.payment_reference) + "</td>" +
        '<td class="nowrap">' + NF.esc(p.fine_number || "—") + "</td>" +
        "<td>" + NF.esc(NF.titleCase(p.payment_method)) + "</td>" +
        '<td class="nowrap"><strong>' + NF.money(p.amount) + "</strong></td>" +
        "<td>" + NF.statusBadge(p.status) + "</td>" +
        '<td class="nowrap">' + NF.fmtDateTime(p.paid_at || p.created_at) + "</td>" +
        '<td class="actions">' + (actions || "—") + "</td>";
      var rbtn = NF.qs(".rcpt", tr);
      if (rbtn) rbtn.addEventListener("click", function () { download(p); });
      var fbtn = NF.qs(".refund", tr);
      if (fbtn) fbtn.addEventListener("click", function () { requestRefund(p); });
      tbody.appendChild(tr);
    });
  }

  function renderRefunds() {
    if (!refunds.length) {
      refundBody.innerHTML = '<tr><td colspan="7">' + NF.emptyState("No refund requests", "Request a refund on a paid transaction and track it here.", "refund") + "</td></tr>";
      return;
    }
    refundBody.innerHTML = "";
    refunds.forEach(function (r) {
      var tr = NF.el("tr");
      tr.innerHTML =
        '<td class="mono nowrap">' + NF.esc(r.refund_reference || "—") + "</td>" +
        '<td class="mono nowrap">' + NF.esc(r.payment_reference || "—") + "</td>" +
        '<td class="nowrap">' + NF.esc(r.fine_number || "—") + "</td>" +
        '<td class="nowrap"><strong>' + NF.money(r.amount) + "</strong></td>" +
        "<td>" + NF.statusBadge(r.status) + (r.admin_note ? '<div class="text-muted small">' + NF.esc(r.admin_note) + "</div>" : "") + "</td>" +
        '<td class="nowrap">' + NF.fmtDateTime(r.created_at) + "</td>" +
        '<td class="nowrap">' + (r.approved_date ? NF.fmtDateTime(r.approved_date) : "—") + "</td>";
      refundBody.appendChild(tr);
    });
  }

  function requestRefund(p) {
    var html =
      "<div class='alert alert-info mb-16'>" + NF.icon("refund", "ico") +
      "<span>Refund requests are reviewed by an administrator. Approved refunds are simulated in this prototype.</span></div>" +
      "<dl class='kv mb-16'><dt>Payment</dt><dd class='mono'>" + NF.esc(p.payment_reference) + "</dd>" +
      "<dt>Fine</dt><dd>" + NF.esc(p.fine_number || "—") + "</dd>" +
      "<dt>Refund amount</dt><dd><strong>" + NF.money(p.amount) + "</strong></dd></dl>" +
      "<div class='form-group'><label for='refund-reason'>Reason for refund <span class='req'>*</span></label>" +
      "<textarea class='textarea' id='refund-reason' maxlength='500' placeholder='Explain why this payment should be refunded (10–500 characters)…'></textarea>" +
      "<div class='field-error' data-error-for='reason'></div></div>";

    NF.modal({
      title: "Request refund",
      size: "lg",
      content: html,
      actions: [
        { label: "Cancel", class: "btn-secondary", onClick: function (c) { c(); } },
        { label: "Submit request", class: "btn", onClick: function (c, btn) { submit(c, btn, p); } }
      ]
    });

    function submit(close, btn, payment) {
      var reason = NF.qs("#refund-reason").value.trim();
      if (reason.length < 10) { NF.toast("Please provide at least 10 characters.", "warning"); return; }
      if (reason.length > 500) { NF.toast("Reason must be 500 characters or fewer.", "warning"); return; }
      NF.setLoading(btn, true, "Submitting…");
      Api.post("/api/v1/payments/" + payment.payment_id + "/refund", {
        amount: Number(payment.amount),
        reason: reason
      }).then(function () {
        close();
        NF.toast("Refund request submitted.", "success");
        loadRefunds();
      }).catch(function (err) {
        NF.setLoading(btn, false);
        NF.toast(err.message, "error", "Request failed");
      });
    }
  }

  function download(p) {
    NF.toast("Preparing receipt…", "info");
    Api.download("/api/v1/payments/" + p.payment_id + "/receipt", "NatiFine-Receipt-" + p.payment_reference + ".pdf")
      .then(function () { NF.toast("Receipt downloaded.", "success"); })
      .catch(function (err) { NF.toast(err.message, "error", "Receipt failed"); });
  }

  function loadRefunds() {
    refundBody.innerHTML = '<tr><td colspan="7"><div class="spinner"></div></td></tr>';
    return Api.get("/api/v1/payments/refunds").then(function (res) {
      refunds = res.data || [];
      renderRefunds();
      render();
    }).catch(function (err) {
      refundBody.innerHTML = '<tr><td colspan="7">' + NF.emptyState("Could not load refunds", err.message, "x") + "</td></tr>";
    });
  }

  function load() {
    tbody.innerHTML = '<tr><td colspan="7"><div class="spinner"></div></td></tr>';
    Api.get("/api/v1/payments/history").then(function (res) {
      payments = res.data || [];
      render();
    }).catch(function (err) {
      tbody.innerHTML = '<tr><td colspan="7">' + NF.emptyState("Could not load payments", err.message, "x") + "</td></tr>";
    });

    Api.get("/api/v1/payments/totals").then(function (res) {
      var t = res.data || {};
      NF.qs("#t-paid").textContent = NF.money(t.total_paid || 0);
      NF.qs("#t-refund").textContent = NF.money(t.total_refunded || 0);
    }).catch(function () {});

    Api.get("/api/v1/payments/history").then(function (res) {
      var list = res.data || [];
      NF.qs("#t-count").textContent = list.length;
      NF.qs("#t-pending").textContent = list.filter(function (p) { return p.status === "PENDING"; }).length;
    }).catch(function () {});
  }

  NF.qs("#refresh-refunds").addEventListener("click", loadRefunds);

  load();
  loadRefunds();
})();
