/* Citizen — My Fines */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("citizen");

  var state = { fines: [], query: "", filter: "" };
  var tbody = NF.qs("#rows");

  function filtered() {
    var q = state.query.toLowerCase();
    return state.fines.filter(function (f) {
      if (state.filter && f.status !== state.filter) return false;
      if (!q) return true;
      return [f.fine_number, f.offence, f.location, f.registration_number, f.offence_code]
        .some(function (v) { return v && String(v).toLowerCase().indexOf(q) >= 0; });
    });
  }

  function render() {
    var list = filtered();
    if (!list.length) {
      tbody.innerHTML = '<tr><td colspan="8">' + NF.emptyState("No fines found", "Try changing your search or filter.", "fines") + "</td></tr>";
      return;
    }
    tbody.innerHTML = "";
    list.forEach(function (f) {
      var overdue = NF.isOverdue(f);
      var action = "";
      if (f.status === "ISSUED") {
        action = '<button class="btn btn-sm pay-btn" type="button">Pay</button> ' +
          '<button class="btn btn-sm btn-secondary dispute-btn" type="button">Dispute</button>';
      } else {
        action = '<button class="btn btn-sm btn-secondary view-btn" type="button">View</button>';
      }
      var tr = NF.el("tr");
      tr.innerHTML =
        '<td class="mono nowrap">' + NF.esc(f.fine_number) + "</td>" +
        "<td>" + NF.esc(f.offence) + "</td>" +
        '<td class="nowrap">' + NF.esc(f.registration_number || "—") + "</td>" +
        '<td class="nowrap"><strong>' + NF.money(f.amount) + "</strong></td>" +
        '<td class="nowrap">' + NF.fmtDate(f.issue_date) + "</td>" +
        '<td class="nowrap">' + NF.fmtDate(f.due_date) + (overdue ? ' <span class="badge badge-overdue">Overdue</span>' : "") + "</td>" +
        "<td>" + NF.statusBadge(f.status) + "</td>" +
        '<td class="actions">' + action + "</td>";
      NF.qs(".pay-btn", tr) && NF.qs(".pay-btn", tr).addEventListener("click", function (e) { e.stopPropagation(); payFlow(f); });
      NF.qs(".dispute-btn", tr) && NF.qs(".dispute-btn", tr).addEventListener("click", function (e) { e.stopPropagation(); disputeFlow(f); });
      NF.qs(".view-btn", tr) && NF.qs(".view-btn", tr).addEventListener("click", function (e) { e.stopPropagation(); openDetail(f); });
      tr.addEventListener("click", function () { openDetail(f); });
      tbody.appendChild(tr);
    });
  }

  function detailHtml(f) {
    var rows = [
      ["Fine number", f.fine_number],
      ["Offence code", f.offence_code],
      ["Offence", f.offence],
      ["Severity", NF.titleCase(f.severity)],
      ["Amount", NF.money(f.amount)],
      ["Vehicle", f.registration_number ? (f.registration_number + " · " + (f.vehicle_make || "") + " " + (f.vehicle_model || "")) : "—"],
      ["Location", f.location],
      ["Issued by", f.officer_name || "—"],
      ["Issue date", NF.fmtDateTime(f.issue_date)],
      ["Due date", NF.fmtDate(f.due_date)],
      ["Status", NF.statusBadge(f.status)]
    ];
    var html = "<dl class='kv'>";
    rows.forEach(function (r) { html += "<dt>" + NF.esc(r[0]) + "</dt><dd>" + (r[0] === "Status" ? r[1] : NF.esc(r[1])) + "</dd>"; });
    html += "</dl>";
    if (f.remarks) html += "<p class='mt-16'><strong>Remarks:</strong> " + NF.esc(f.remarks) + "</p>";
    if (f.evidence_photo) {
      html += "<div class='mt-16'><strong>Evidence</strong><div class='mt-8'><img src='" + NF.esc(f.evidence_photo) + "' alt='Evidence' style='border:1px solid var(--border);border-radius:var(--radius);max-height:240px;width:auto'></div></div>";
    }
    if (f.paid_date) html += "<p class='mt-16'><strong>Paid on:</strong> " + NF.fmtDateTime(f.paid_date) + "</p>";
    return html;
  }

  function openDetail(f) {
    var overdue = NF.isOverdue(f);
    var actions = [{ label: "Close", class: "btn-secondary", onClick: function (c) { c(); } }];
    if (f.status === "ISSUED") {
      actions.unshift({ label: "Submit dispute", class: "btn-secondary", onClick: function (c) { c(); disputeFlow(f); } });
      actions.unshift({ label: overdue ? "Pay now (overdue)" : "Pay now", class: "btn", onClick: function (c) { c(); payFlow(f); } });
    }
    NF.modal({ title: "Fine " + f.fine_number, size: "lg", content: detailHtml(f), actions: actions });
  }

  function payFlow(f) {
    NF.confirm({
      title: "Pay fine " + f.fine_number,
      message: "You are about to pay " + NF.money(f.amount) + " for this fine. Payment services in this prototype are simulated.",
      confirmLabel: "Continue to payment",
      cancelLabel: "Cancel"
    }).then(function (ok) {
      if (!ok) return;
      var html =
        "<div class='alert alert-info mb-16'>" + NF.icon("payment", "ico") +
        "<span>This is a simulated payment. Choose a gateway and payment method to generate a reference.</span></div>" +
        "<div class='form-group'><label for='pay-gateway'>Payment gateway</label>" +
        "<select class='select' id='pay-gateway'>" +
        "<option value='INTERNAL'>NatiFine Internal (simulated)</option>" +
        "<option value='PAYFAST'>PayFast</option><option value='OZOW'>Ozow</option>" +
        "<option value='PEACH'>Peach Payments</option><option value='STRIPE'>Stripe</option>" +
        "<option value='PAYPAL'>PayPal</option></select></div>" +
        "<div class='form-group'><label for='pay-method'>Payment method</label>" +
        "<select class='select' id='pay-method'>" +
        "<option value='CARD'>Card</option><option value='EFT'>EFT / Bank transfer</option>" +
        "<option value='MOBILE'>Mobile</option><option value='CASH'>Cash</option></select></div>" +
        "<dl class='kv'><dt>Fine</dt><dd>" + NF.esc(f.fine_number) + "</dd>" +
        "<dt>Amount</dt><dd><strong>" + NF.money(f.amount) + "</strong></dd></dl>";

      var m = NF.modal({
        title: "Payment details",
        content: html,
        actions: [
          { label: "Cancel", class: "btn-secondary", onClick: function (c) { c(); } },
          { label: "Pay " + NF.money(f.amount), class: "btn", onClick: function (c, btn) { submitPayment(c, btn, f); } }
        ]
      });
      m._fine = f;

      function submitPayment(close, btn, fine) {
        var gateway = NF.qs("#pay-gateway").value;
        var method = NF.qs("#pay-method").value;
        NF.setLoading(btn, true, "Processing…");
        Api.post("/api/v1/payments", {
          fine_id: fine.fine_id, amount: Number(fine.amount), gateway: gateway, payment_method: method
        }).then(function (res) {
          var p = res.data;
          return Api.post("/api/v1/payments/verify", {
            payment_reference: p.payment_reference, gateway_reference: p.gateway_reference
          }).then(function (vr) { return vr.data; });
        }).then(function (payment) {
          close();
          successModal(f, payment);
          load();
        }).catch(function (err) {
          NF.setLoading(btn, false);
          NF.toast(err.message, "error", "Payment failed");
        });
      }
    });
  }

  function successModal(f, payment) {
    var html =
      "<div class='text-center'><div class='avatar avatar-lg' style='margin:0 auto 12px;background:var(--accent)'>" + NF.icon("check", "ico") + "</div>" +
      "<h3>Payment successful</h3><p class='text-muted'>Your fine " + NF.esc(f.fine_number) + " has been settled.</p></div>" +
      "<dl class='kv mt-16'><dt>Amount paid</dt><dd><strong>" + NF.money(payment.amount) + "</strong></dd>" +
      "<dt>Reference</dt><dd class='mono'>" + NF.esc(payment.payment_reference) + "</dd>" +
      "<dt>Status</dt><dd>" + NF.statusBadge(payment.status || "PAID") + "</dd></dl>";
    NF.modal({
      title: "Payment confirmed", content: html,
      actions: [
        { label: "Close", class: "btn-secondary", onClick: function (c) { c(); } },
        { label: "Download receipt", class: "btn", onClick: function () { downloadReceipt(payment.payment_id, f.fine_number); } }
      ]
    });
  }

  function downloadReceipt(paymentId, fineNumber) {
    NF.toast("Preparing receipt…", "info");
    Api.download("/api/v1/payments/" + paymentId + "/receipt", "NatiFine-Receipt-" + fineNumber + ".pdf")
      .then(function () { NF.toast("Receipt downloaded.", "success"); })
      .catch(function (err) { NF.toast(err.message, "error", "Receipt failed"); });
  }

  function disputeFlow(f) {
    var html =
      "<div class='alert alert-warning mb-16'>" + NF.icon("dispute", "ico") +
      "<span>Disputing a fine places it under review. Provide a clear reason (at least 20 characters). You may attach supporting documents.</span></div>" +
      "<div class='form-group'><label for='dispute-desc'>Reason for dispute <span class='req'>*</span></label>" +
      "<textarea class='textarea' id='dispute-desc' placeholder='Explain why this fine should be reviewed…'></textarea>" +
      "<div class='field-error' data-error-for='description'></div></div>" +
      "<div class='form-group'><label for='dispute-files'>Supporting documents (optional)</label>" +
      "<input class='input' type='file' id='dispute-files' multiple accept='.jpg,.jpeg,.png,.pdf'>" +
      "<div class='field-hint'>JPG, PNG or PDF. Max 16MB each.</div></div>";

    NF.modal({
      title: "Dispute fine " + f.fine_number,
      content: html,
      actions: [
        { label: "Cancel", class: "btn-secondary", onClick: function (c) { c(); } },
        { label: "Submit dispute", class: "btn", onClick: function (c, btn) { submitDispute(c, btn, f); } }
      ]
    });

    function submitDispute(close, btn, fine) {
      var desc = NF.qs("#dispute-desc").value.trim();
      if (desc.length < 20) {
        NF.toast("Please provide at least 20 characters.", "warning");
        return;
      }
      var files = NF.qs("#dispute-files").files;
      NF.setLoading(btn, true, "Submitting…");
      Api.post("/api/v1/disputes", { fine_id: fine.fine_id, description: desc }).then(function (res) {
        var dispute = res.data;
        var chain = Promise.resolve();
        if (files && files.length) {
          for (var i = 0; i < files.length; i++) {
            (function (file) {
              chain = chain.then(function () {
                var fd = new FormData();
                fd.append("file", file);
                return Api.request("POST", "/api/v1/disputes/" + dispute.dispute_id + "/documents", { form: fd });
              });
            })(files[i]);
          }
        }
        return chain.then(function () { return dispute; });
      }).then(function () {
        close();
        NF.toast("Dispute submitted for review.", "success");
        load();
      }).catch(function (err) {
        NF.setLoading(btn, false);
        NF.toast(err.message, "error", "Dispute failed");
      });
    }
  }

  function load() {
    tbody.innerHTML = '<tr><td colspan="8"><div class="spinner"></div></td></tr>';
    return Api.get("/api/v1/fines/my").then(function (res) {
      state.fines = res.data || [];
      render();
    }).catch(function (err) {
      tbody.innerHTML = '<tr><td colspan="8">' + NF.emptyState("Could not load fines", err.message, "x") + "</td></tr>";
    });
  }

  NF.qs("#search").addEventListener("input", NF.debounce(function (e) { state.query = e.target.value; render(); }, 200));
  NF.qs("#filter").addEventListener("change", function (e) { state.filter = e.target.value; render(); });
  NF.qs("#refresh").addEventListener("click", load);

  var params = new URLSearchParams(window.location.search);
  if (params.get("filter")) { state.filter = params.get("filter"); NF.qs("#filter").value = state.filter; }

  load().then(function () {
    var id = params.get("id");
    if (id) {
      var f = state.fines.filter(function (x) { return String(x.fine_id) === String(id); })[0];
      if (f) openDetail(f);
    }
  });
})();
