/* Shared — Dispute review (officer / admin) */
(function () {
  "use strict";
  var NF = window.NF;
  if (!Guard.requireAuth()) return;

  var tbody = NF.qs("#rows");
  var state = { rows: [], query: "", filter: "" };

  var OPEN_STATES = ["NEW", "PENDING", "UNDER_REVIEW", "MORE_INFORMATION_REQUIRED"];

  function render() {
    var rows = state.rows.filter(function (d) {
      if (state.filter && d.status !== state.filter) return false;
      var q = state.query.toLowerCase();
      if (!q) return true;
      return [d.fine_number, d.citizen_name].some(function (v) { return v && String(v).toLowerCase().indexOf(q) >= 0; });
    });
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="6">' + NF.emptyState("No disputes", "Nothing matching your filters.", "dispute") + "</td></tr>";
      return;
    }
    tbody.innerHTML = "";
    rows.forEach(function (d) {
      var tr = NF.el("tr", { class: "row-link" });
      tr.innerHTML =
        "<td>#" + NF.esc(d.dispute_id) + "</td>" +
        '<td class="mono nowrap">' + NF.esc(d.fine_number || "—") + "</td>" +
        "<td>" + NF.esc(d.citizen_name || "—") + "</td>" +
        '<td class="nowrap">' + NF.fmtDate(d.submitted_at) + "</td>" +
        "<td>" + NF.statusBadge(d.status) + "</td>" +
        '<td class="actions"><button class="btn btn-sm btn-secondary view" type="button">Review</button></td>';
      NF.qs(".view", tr).addEventListener("click", function (e) { e.stopPropagation(); detail(d.dispute_id); });
      tr.addEventListener("click", function () { detail(d.dispute_id); });
      tbody.appendChild(tr);
    });
  }

  function detail(id) {
    Api.get("/api/v1/disputes/" + id).then(function (res) {
      var d = res.data;
      var open = OPEN_STATES.indexOf(d.status) >= 0;
      var html =
        "<dl class='kv'>" +
        "<dt>Dispute</dt><dd>#" + NF.esc(d.dispute_id) + "</dd>" +
        "<dt>Fine</dt><dd class='mono'>" + NF.esc(d.fine_number || "—") + "</dd>" +
        "<dt>Citizen</dt><dd>" + NF.esc(d.citizen_name || "—") + "</dd>" +
        "<dt>Status</dt><dd>" + NF.statusBadge(d.status) + "</dd>" +
        "<dt>Submitted</dt><dd>" + NF.fmtDateTime(d.submitted_at) + "</dd>" +
        (d.reviewer_name ? "<dt>Reviewed by</dt><dd>" + NF.esc(d.reviewer_name) + "</dd>" : "") +
        (d.reviewed_at ? "<dt>Reviewed</dt><dd>" + NF.fmtDateTime(d.reviewed_at) + "</dd>" : "") +
        "</dl>" +
        "<div class='mt-16'><strong>Citizen's reason</strong><p class='text-soft mt-8 mb-0'>" + NF.esc(d.description) + "</p></div>" +
        (d.review_notes ? "<div class='alert alert-info mt-16'>" + NF.icon("dispute", "ico") + "<div><strong>Review notes</strong><div>" + NF.esc(d.review_notes) + "</div></div></div>" : "");

      var actions = [{ label: "Close", class: "btn-secondary", onClick: function (c) { c(); } }];
      if (open) {
        actions.unshift({ label: "Approve", class: "btn-success", onClick: function (c) { c(); decide(d, "approve", "review_notes"); } });
        actions.unshift({ label: "Reject", class: "btn-danger", onClick: function (c) { c(); decide(d, "reject", "review_notes"); } });
        actions.unshift({ label: "Request info", class: "btn-secondary", onClick: function (c) { c(); decide(d, "request-information", "message"); } });
      }
      NF.modal({ title: "Dispute #" + d.dispute_id, size: "lg", content: html, actions: actions });
    }).catch(function (err) { NF.toast(err.message, "error", "Dispute"); });
  }

  function decide(d, action, field) {
    var isInfo = field === "message";
    var label = action === "approve" ? "Approve dispute" : action === "reject" ? "Reject dispute" : "Request more information";
    var html = "<div class='form-group'><label for='rev-notes'>" + (isInfo ? "Message to citizen" : "Review notes") + " <span class='req'>*</span></label>" +
      "<textarea class='textarea' id='rev-notes' placeholder='At least 10 characters'></textarea>" +
      "<div class='field-hint'>A minimum of 10 characters is required.</div></div>";
    NF.modal({
      title: label + " — #" + d.dispute_id,
      content: html,
      actions: [
        { label: "Cancel", class: "btn-secondary", onClick: function (c) { c(); } },
        { label: label, class: action === "reject" ? "btn-danger" : "btn", onClick: function (c, btn) {
          var notes = NF.qs("#rev-notes").value.trim();
          if (notes.length < 10) { NF.toast("Please enter at least 10 characters.", "warning"); return; }
          var body = {}; body[field] = notes;
          NF.setLoading(btn, true, "Submitting…");
          Api.patch("/api/v1/disputes/" + d.dispute_id + "/" + action, body).then(function () {
            c(); NF.toast("Dispute updated.", "success"); load();
          }).catch(function (err) { NF.setLoading(btn, false); NF.toast(err.message, "error"); });
        } }
      ]
    });
  }

  function load() {
    tbody.innerHTML = '<tr><td colspan="6"><div class="spinner"></div></td></tr>';
    var req = state.query
      ? Api.get("/api/v1/disputes/search", { query: { keyword: state.query } })
      : Api.get("/api/v1/disputes/pending");
    return req.then(function (res) { state.rows = res.data || []; render(); })
      .catch(function (err) {
        tbody.innerHTML = '<tr><td colspan="6">' + NF.emptyState("Could not load disputes", err.message, "x") + "</td></tr>";
      });
  }

  NF.qs("#search").addEventListener("input", NF.debounce(function (e) { state.query = e.target.value.trim(); load(); }, 300));
  NF.qs("#filter").addEventListener("change", function (e) { state.filter = e.target.value; render(); });
  NF.qs("#refresh").addEventListener("click", load);

  load().then(function () {
    var id = NF.param("id");
    if (id) detail(id);
  });
})();