/* Admin — Vehicle registry */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("admin");

  var tbody = NF.qs("#rows");
  var pager = NF.qs("#pager");
  var SIZE = 20;
  var state = { mode: "browse", page: 1, query: "", searchRows: [] };

  function render(rows, meta) {
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="7">' + NF.emptyState("No vehicles found", "Try a different search.", "vehicle") + "</td></tr>";
      pager.innerHTML = "";
      return;
    }
    tbody.innerHTML = "";
    rows.forEach(function (v) {
      var tr = NF.el("tr", { class: "row-link" });
      tr.innerHTML =
        '<td class="plate nowrap">' + NF.esc(v.registration_number) + "</td>" +
        "<td>" + NF.esc(v.make + " " + v.model) + "</td>" +
        "<td>" + NF.esc(v.year) + "</td>" +
        "<td>" + NF.esc(NF.titleCase(v.vehicle_type)) + "</td>" +
        '<td class="mono small">' + NF.esc(v.vin) + "</td>" +
        "<td>" + NF.statusBadge(v.status) + "</td>" +
        '<td class="actions"><button class="btn btn-sm btn-secondary view" type="button">Details</button>' +
        '<button class="btn btn-sm btn-secondary hist" type="button">History</button></td>';
      NF.qs(".view", tr).addEventListener("click", function (e) { e.stopPropagation(); detail(v); });
      NF.qs(".hist", tr).addEventListener("click", function (e) { e.stopPropagation(); history(v); });
      tr.addEventListener("click", function () { detail(v); });
      tbody.appendChild(tr);
    });
    NF.renderPagination(pager, {
      page: meta.page, pages: meta.pages, total: meta.total,
      onPage: function (p) {
        if (state.mode === "search") { state.page = p; renderSearch(); } else { state.page = p; loadBrowse(); }
      }
    });
  }

  function loadBrowse() {
    tbody.innerHTML = '<tr><td colspan="7"><div class="spinner"></div></td></tr>';
    return Api.get("/api/vehicles", { query: { page: state.page, size: SIZE } }).then(function (res) {
      var d = res.data || {};
      render(d.items || [], { page: d.page || 1, pages: d.pages || 1, total: d.total || 0 });
    }).catch(function (err) {
      tbody.innerHTML = '<tr><td colspan="7">' + NF.emptyState("Could not load vehicles", err.message, "x") + "</td></tr>";
    });
  }

  function runSearch() {
    if (!state.query) { state.mode = "browse"; state.page = 1; loadBrowse(); return; }
    tbody.innerHTML = '<tr><td colspan="7"><div class="spinner"></div></td></tr>';
    Api.get("/api/vehicles/search", { query: { keyword: state.query } }).then(function (res) {
      state.mode = "search";
      state.searchRows = res.data || [];
      state.page = 1;
      renderSearch();
    }).catch(function (err) {
      tbody.innerHTML = '<tr><td colspan="7">' + NF.emptyState("Search failed", err.message, "x") + "</td></tr>";
    });
  }

  function renderSearch() {
    var pages = Math.max(1, Math.ceil(state.searchRows.length / SIZE));
    if (state.page > pages) state.page = pages;
    render(state.searchRows.slice((state.page - 1) * SIZE, state.page * SIZE), { page: state.page, pages: pages, total: state.searchRows.length });
  }

  function detail(v) {
    var html = "<dl class='kv'>" +
      [["Registration", v.registration_number], ["Make", v.make], ["Model", v.model], ["Year", v.year],
       ["Colour", v.color || "—"], ["Type", NF.titleCase(v.vehicle_type)], ["VIN", v.vin],
       ["Engine no.", v.engine_number || "—"], ["Status", NF.titleCase(v.status)], ["Registered", NF.fmtDate(v.created_at)]]
      .map(function (r) { return "<dt>" + NF.esc(r[0]) + "</dt><dd>" + (r[0] === "VIN" ? "<span class='mono small'>" + NF.esc(r[1]) + "</span>" : NF.esc(r[1])) + "</dd>"; }).join("") + "</dl>";
    NF.modal({ title: v.registration_number, content: html, actions: [{ label: "Close", class: "btn-secondary", onClick: function (c) { c(); } }] });
  }

  function history(v) {
    Api.get("/api/vehicles/history/" + v.vehicle_id).then(function (res) {
      var fines = res.data || [];
      var html;
      if (!fines.length) {
        html = NF.emptyState("No fines", "This vehicle has no fines on record.", "check");
      } else {
        html = "<table class='table'><thead><tr><th>Fine</th><th>Offence</th><th>Amount</th><th>Status</th><th>Due</th></tr></thead><tbody>";
        fines.forEach(function (f) {
          html += "<tr><td class='mono nowrap'>" + NF.esc(f.fine_number) + "</td><td>" + NF.esc(f.offence) + "</td>" +
            "<td class='nowrap'><strong>" + NF.money(f.amount) + "</strong></td><td>" + NF.statusBadge(f.status) + "</td><td class='nowrap'>" + NF.fmtDate(f.due_date) + "</td></tr>";
        });
        html += "</tbody></table>";
      }
      NF.modal({ title: "Fine history — " + v.registration_number, size: "lg", content: html, actions: [{ label: "Close", class: "btn-secondary", onClick: function (c) { c(); } }] });
    }).catch(function (err) { NF.toast(err.message, "error", "History"); });
  }

  function reload() { if (state.mode === "search") runSearch(); else loadBrowse(); }

  NF.qs("#search").addEventListener("input", NF.debounce(function (e) { state.query = e.target.value.trim(); state.page = 1; runSearch(); }, 300));
  NF.qs("#refresh").addEventListener("click", reload);

  loadBrowse().then(function () {
    var id = NF.param("id");
    if (id) {
      Api.get("/api/vehicles/" + id).then(function (res) { detail(res.data); }).catch(function () {});
    }
  });
})();
