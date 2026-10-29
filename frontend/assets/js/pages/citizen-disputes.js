/* Citizen — Disputes */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("citizen");
  var tbody = NF.qs("#rows");

  function render(list) {
    if (!list.length) {
      tbody.innerHTML = '<tr><td colspan="6">' + NF.emptyState("No disputes", "You have not contested any fines yet.", "dispute") + "</td></tr>";
      return;
    }
    tbody.innerHTML = "";
    list.forEach(function (d) {
      var tr = NF.el("tr");
      tr.innerHTML =
        "<td>#" + NF.esc(d.dispute_id) + "</td>" +
        '<td class="mono nowrap">' + NF.esc(d.fine_number || "—") + "</td>" +
        '<td class="nowrap">' + NF.fmtDate(d.submitted_at) + "</td>" +
        "<td>" + NF.statusBadge(d.status) + "</td>" +
        "<td>" + NF.esc(d.reviewer_name || "—") + "</td>" +
        '<td class="actions"><button class="btn btn-sm btn-secondary view" type="button">View</button></td>';
      NF.qs(".view", tr).addEventListener("click", function () { detail(d.dispute_id); });
      tbody.appendChild(tr);
    });
  }

  function detail(id) {
    Api.get("/api/v1/disputes/" + id).then(function (res) {
      var d = res.data;
      var html =
        "<dl class='kv'>" +
        "<dt>Dispute</dt><dd>#" + NF.esc(d.dispute_id) + "</dd>" +
        "<dt>Fine</dt><dd class='mono'>" + NF.esc(d.fine_number || "—") + "</dd>" +
        "<dt>Status</dt><dd>" + NF.statusBadge(d.status) + "</dd>" +
        "<dt>Submitted</dt><dd>" + NF.fmtDateTime(d.submitted_at) + "</dd>" +
        (d.reviewer_name ? "<dt>Reviewed by</dt><dd>" + NF.esc(d.reviewer_name) + "</dd>" : "") +
        (d.reviewed_at ? "<dt>Reviewed</dt><dd>" + NF.fmtDateTime(d.reviewed_at) + "</dd>" : "") +
        "</dl>" +
        "<div class='mt-16'><strong>Your reason</strong><p class='text-soft mt-8'>" + NF.esc(d.description) + "</p></div>" +
        (d.review_notes ? "<div class='alert alert-info mt-16'>" + NF.icon("dispute", "ico") + "<div><strong>Reviewer notes</strong><div>" + NF.esc(d.review_notes) + "</div></div></div>" : "");
      var docs = d.documents || [];
      if (docs.length) {
        html += "<div class='mt-16'><strong>Documents</strong><ul>";
        docs.forEach(function (doc) {
          html += "<li class='small'>" + NF.esc(doc.original_name || doc.file_name || "document") + "</li>";
        });
        html += "</ul></div>";
      }
      NF.modal({ title: "Dispute #" + d.dispute_id, size: "lg", content: html, actions: [{ label: "Close", class: "btn-secondary", onClick: function (c) { c(); } }] });
    }).catch(function (err) { NF.toast(err.message, "error"); });
  }

  Api.get("/api/v1/disputes").then(function (res) { render(res.data || []); })
    .catch(function (err) {
      tbody.innerHTML = '<tr><td colspan="6">' + NF.emptyState("Could not load disputes", err.message, "x") + "</td></tr>";
    });
})();
