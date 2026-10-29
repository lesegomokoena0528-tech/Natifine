/* Officer — Traffic Fines list & management */
(function () {
  "use strict";
  var NF = window.NF;
  if (!Guard.requireAuth()) return;
  var ROLE = Session.role();
  if (ROLE !== "officer" && ROLE !== "admin") { window.location.href = "/pages/" + (ROLE || "login") + "/dashboard.html"; return; }
  var IS_ADMIN = ROLE === "admin";

  var tbody = NF.qs("#rows");
  var pager = NF.qs("#pager");
  var SIZE = 20;
  var state = { mode: "browse", page: 1, query: "", filter: "", searchRows: [] };

  function matches(f) {
    if (!state.filter) return true;
    return f.status === state.filter;
  }

  function render(rows, meta) {
    rows = rows.filter(matches);
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="8">' + NF.emptyState("No fines found", "Try adjusting your search or filter.", "fines") + "</td></tr>";
      pager.innerHTML = "";
      return;
    }
    tbody.innerHTML = "";
    rows.forEach(function (f) {
      var tr = NF.el("tr", { class: "row-link" });
      var overdue = NF.isOverdue(f);
      var actions =
        '<button class="btn btn-sm btn-secondary view" type="button">View</button>';
      if (["ISSUED", "DISPUTED", "UNDER_REVIEW"].indexOf(f.status) >= 0) {
        actions += '<button class="btn btn-sm btn-secondary cancel" type="button">Cancel</button>';
      }
      if (IS_ADMIN) {
        actions += '<button class="btn btn-sm btn-danger del" type="button">Delete</button>';
      }
      tr.innerHTML =
        '<td class="mono nowrap">' + NF.esc(f.fine_number) + "</td>" +
        "<td>" + NF.esc(f.offence) + "</td>" +
        "<td>" + NF.esc(f.owner_name || "—") + "</td>" +
        '<td class="nowrap">' + NF.esc(f.registration_number || "—") + "</td>" +
        '<td class="nowrap"><strong>' + NF.money(f.amount) + "</strong></td>" +
        '<td class="nowrap">' + NF.fmtDate(f.due_date) + (overdue ? ' <span class="badge badge-overdue">Overdue</span>' : "") + "</td>" +
        "<td>" + NF.statusBadge(f.status) + "</td>" +
        '<td class="actions">' + actions + "</td>";
      NF.qs(".view", tr).addEventListener("click", function (e) { e.stopPropagation(); detail(f.fine_id); });
      var cancel = NF.qs(".cancel", tr);
      if (cancel) cancel.addEventListener("click", function (e) { e.stopPropagation(); cancelFine(f); });
      var del = NF.qs(".del", tr);
      if (del) del.addEventListener("click", function (e) { e.stopPropagation(); deleteFine(f); });
      tr.addEventListener("click", function () { detail(f.fine_id); });
      tbody.appendChild(tr);
    });
    NF.renderPagination(pager, {
      page: meta.page, pages: meta.pages, total: meta.total,
      onPage: function (p) {
        if (state.mode === "search") { state.page = p; renderSearch(); }
        else { state.page = p; loadBrowse(); }
      }
    });
  }

  /* browse — server side pagination */
  function loadBrowse() {
    tbody.innerHTML = '<tr><td colspan="8"><div class="spinner"></div></td></tr>';
    return Api.get("/api/v1/fines", { query: { page: state.page, size: SIZE } }).then(function (res) {
      var d = res.data || {};
      render(d.items || [], { page: d.page || 1, pages: d.pages || 1, total: d.total || 0 });
    }).catch(function (err) {
      tbody.innerHTML = '<tr><td colspan="8">' + NF.emptyState("Could not load fines", err.message, "x") + "</td></tr>";
    });
  }

  /* search — client side pagination over full result set */
  function runSearch() {
    if (!state.query) { state.mode = "browse"; state.page = 1; loadBrowse(); return; }
    tbody.innerHTML = '<tr><td colspan="8"><div class="spinner"></div></td></tr>';
    Api.get("/api/v1/fines/search", { query: { keyword: state.query } }).then(function (res) {
      state.mode = "search";
      state.searchRows = res.data || [];
      state.page = 1;
      renderSearch();
    }).catch(function (err) {
      tbody.innerHTML = '<tr><td colspan="8">' + NF.emptyState("Search failed", err.message, "x") + "</td></tr>";
    });
  }

  function renderSearch() {
    var rows = state.searchRows.filter(matches);
    var pages = Math.max(1, Math.ceil(rows.length / SIZE));
    if (state.page > pages) state.page = pages;
    var slice = rows.slice((state.page - 1) * SIZE, state.page * SIZE);
    render(slice, { page: state.page, pages: pages, total: rows.length });
  }

  /* ---------- fine detail ---------- */
  function detail(fineId) {
    Api.get("/api/v1/fines/" + fineId).then(function (res) {
      var f = res.data;
      var html =
        "<dl class='kv'>" +
        "<dt>Fine number</dt><dd class='mono'>" + NF.esc(f.fine_number) + "</dd>" +
        "<dt>Offence</dt><dd>" + NF.esc(f.offence) + " <span class='badge badge-" + NF.esc(String(f.severity).toLowerCase()) + "'>" + NF.esc(NF.titleCase(f.severity)) + "</span></dd>" +
        "<dt>Offence code</dt><dd class='mono'>" + NF.esc(f.offence_code) + "</dd>" +
        "<dt>Amount</dt><dd><strong>" + NF.money(f.amount) + "</strong></dd>" +
        "<dt>Citizen</dt><dd>" + NF.esc(f.owner_name || "—") + "</dd>" +
        "<dt>ID number</dt><dd class='mono'>" + NF.esc(f.owner_id_number || "—") + "</dd>" +
        "<dt>Vehicle</dt><dd>" + NF.esc((f.registration_number || "—") + (f.vehicle_make ? " · " + f.vehicle_make + " " + f.vehicle_model : "")) + "</dd>" +
        "<dt>Location</dt><dd>" + NF.esc(f.location) + "</dd>" +
        "<dt>Issued by</dt><dd>" + NF.esc(f.officer_name || "—") + "</dd>" +
        "<dt>Issue date</dt><dd>" + NF.fmtDateTime(f.issue_date) + "</dd>" +
        "<dt>Due date</dt><dd>" + NF.fmtDate(f.due_date) + "</dd>" +
        "<dt>Status</dt><dd>" + NF.statusBadge(f.status) + "</dd>" +
        (f.paid_date ? "<dt>Paid</dt><dd>" + NF.fmtDateTime(f.paid_date) + "</dd>" : "") +
        "</dl>";
      if (f.remarks) html += "<p class='mt-16'><strong>Remarks:</strong> " + NF.esc(f.remarks) + "</p>";
      if (f.evidence_photo) html += "<div class='mt-16'><img src='" + NF.esc(f.evidence_photo) + "' alt='Evidence' style='border-radius:var(--radius);max-height:200px'></div>";

      var actions = [{ label: "Close", class: "btn-secondary", onClick: function (c) { c(); } }];
      actions.unshift({ label: "History", class: "btn-secondary", onClick: function (c) { c(); history(f.fine_id); } });
      if (["ISSUED", "DISPUTED", "UNDER_REVIEW"].indexOf(f.status) >= 0) {
        actions.unshift({ label: "Edit", class: "btn-secondary", onClick: function (c) { c(); edit(f); } });
        actions.unshift({ label: "Cancel fine", class: "btn-danger", onClick: function (c) { c(); cancelFine(f); } });
      }
      if (IS_ADMIN) {
        actions.push({ label: "Delete", class: "btn-danger", onClick: function (c) { c(); deleteFine(f); } });
      }
      NF.modal({ title: "Fine " + f.fine_number, size: "lg", content: html, actions: actions });
    }).catch(function (err) { NF.toast(err.message, "error", "Fine"); });
  }

  function history(fineId) {
    Api.get("/api/v1/fines/history/" + fineId).then(function (res) {
      var items = res.data || [];
      if (!items.length) {
        NF.toast("No history recorded for this fine.", "info");
        return;
      }
      var html = "";
      items.forEach(function (h) {
        html += "<div class='history-item'><div class='history-marker'></div>" +
          "<div><strong>" + NF.esc(NF.titleCase(h.new_status)) + "</strong>" +
          (h.old_status ? " <span class='text-muted'>was " + NF.esc(NF.titleCase(h.old_status)) + "</span>" : "") +
          "<div class='small text-muted'>" + NF.esc(h.reason || "") + "</div>" +
          "<div class='small text-muted'>" + NF.fmtDateTime(h.change_date) + "</div></div></div>";
      });
      NF.modal({ title: "Fine history", size: "lg", content: html, actions: [{ label: "Close", class: "btn-secondary", onClick: function (c) { c(); } }] });
    }).catch(function (err) { NF.toast(err.message, "error", "History"); });
  }

  function cancelFine(f) {
    var html = "<div class='form-group'><label for='cancel-reason'>Reason for cancellation <span class='req'>*</span></label>" +
      "<textarea class='textarea' id='cancel-reason' placeholder='e.g. issued in error'></textarea></div>";
    NF.modal({
      title: "Cancel fine " + f.fine_number,
      content: html,
      actions: [
        { label: "Cancel", class: "btn-secondary", onClick: function (c) { c(); } },
        { label: "Cancel fine", class: "btn-danger", onClick: function (c, btn) {
          var reason = NF.qs("#cancel-reason").value.trim();
          if (!reason) { NF.toast("Please provide a reason.", "warning"); return; }
          NF.setLoading(btn, true, "Cancelling…");
          Api.patch("/api/v1/fines/" + f.fine_id + "/cancel", { reason: reason }).then(function () {
            c(); NF.toast("Fine cancelled.", "success"); reload();
          }).catch(function (err) { NF.setLoading(btn, false); NF.toast(err.message, "error"); });
        } }
      ]
    });
  }

  function deleteFine(f) {
    NF.confirm({
      title: "Delete fine " + f.fine_number,
      message: "This permanently removes the fine and its history. This cannot be undone.",
      confirmLabel: "Delete",
      danger: true
    }).then(function (ok) {
      if (!ok) return;
      Api.del("/api/v1/fines/" + f.fine_id).then(function () {
        NF.toast("Fine deleted.", "success"); reload();
      }).catch(function (err) { NF.toast(err.message, "error"); });
    });
  }

  function edit(f) {
    var html =
      "<div class='form-grid'>" +
      "<div class='form-group'><label for='e-offence'>Offence</label><input class='input' id='e-offence' value='" + NF.esc(f.offence) + "'></div>" +
      "<div class='form-group'><label for='e-location'>Location</label><input class='input' id='e-location' value='" + NF.esc(f.location) + "'></div>" +
      "<div class='form-group'><label for='e-amount'>Amount (ZAR)</label><input class='input' id='e-amount' type='number' step='0.01' value='" + NF.esc(f.amount) + "'></div>" +
      "<div class='form-group'><label for='e-remarks'>Remarks</label><input class='input' id='e-remarks' value='" + NF.esc(f.remarks || "") + "'></div>" +
      "</div>";
    NF.modal({
      title: "Edit fine " + f.fine_number,
      content: html,
      actions: [
        { label: "Cancel", class: "btn-secondary", onClick: function (c) { c(); } },
        { label: "Save changes", class: "btn", onClick: function (c, btn) {
          var body = {
            offence: NF.qs("#e-offence").value.trim(),
            location: NF.qs("#e-location").value.trim(),
            amount: NF.qs("#e-amount").value,
            remarks: NF.qs("#e-remarks").value.trim() || null
          };
          NF.setLoading(btn, true, "Saving…");
          Api.put("/api/v1/fines/" + f.fine_id, body).then(function () {
            c(); NF.toast("Fine updated.", "success"); reload();
          }).catch(function (err) { NF.setLoading(btn, false); NF.toast(err.message, "error"); });
        } }
      ]
    });
  }

  function reload() {
    if (state.mode === "search") runSearch();
    else loadBrowse();
  }

  NF.qs("#search").addEventListener("input", NF.debounce(function (e) { state.query = e.target.value.trim(); state.page = 1; runSearch(); }, 300));
  NF.qs("#filter").addEventListener("change", function (e) { state.filter = e.target.value; state.page = 1; reload(); });
  NF.qs("#refresh").addEventListener("click", reload);

  var params = new URLSearchParams(window.location.search);
  loadBrowse().then(function () {
    var id = params.get("id");
    if (id) detail(id);
  });
})();