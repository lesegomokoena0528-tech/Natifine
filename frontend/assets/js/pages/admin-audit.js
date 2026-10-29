/* Admin — Audit Log */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("admin");

  var tbody = NF.qs("#rows");
  var pager = NF.qs("#pager");
  var SIZE = 20;
  var logs = [];
  var state = { page: 1, query: "", role: "" };

  function filtered() {
    var q = state.query.toLowerCase();
    return logs.filter(function (l) {
      if (state.role && l.role !== state.role) return false;
      if (!q) return true;
      return [l.username, l.action, l.entity, l.description, l.endpoint, l.ip_address].some(function (v) {
        return v && String(v).toLowerCase().indexOf(q) >= 0;
      });
    });
  }

  function statusClass(code) {
    if (!code) return "";
    if (code < 300) return "accent";
    if (code < 400) return "";
    return "danger";
  }

  function render() {
    var rows = filtered();
    var pages = Math.max(1, Math.ceil(rows.length / SIZE));
    if (state.page > pages) state.page = pages;
    var slice = rows.slice((state.page - 1) * SIZE, state.page * SIZE);
    if (!slice.length) {
      tbody.innerHTML = '<tr><td colspan="7">' + NF.emptyState("No audit entries", "Nothing matches your filters.", "audit") + "</td></tr>";
      pager.innerHTML = "";
      return;
    }
    tbody.innerHTML = "";
    slice.forEach(function (l) {
      var tr = NF.el("tr", { class: "row-link" });
      tr.innerHTML =
        '<td class="nowrap">' + NF.fmtDateTime(l.created_at) + "</td>" +
        "<td><strong>" + NF.esc(l.username) + "</strong></td>" +
        "<td>" + NF.statusBadge(l.role) + "</td>" +
        '<td class="mono small">' + NF.esc(l.action) + "</td>" +
        "<td>" + NF.esc(l.entity) + (l.entity_id ? ' <span class="text-muted small">#' + NF.esc(l.entity_id) + "</span>" : "") + "</td>" +
        '<td><span class="badge">' + (l.status_code != null ? l.status_code : "—") + "</span></td>" +
        '<td class="actions"><button class="btn btn-sm btn-secondary view" type="button">View</button></td>';
      tr.addEventListener("click", function () { detail(l); });
      tbody.appendChild(tr);
    });
    NF.renderPagination(pager, { page: state.page, pages: pages, total: rows.length, onPage: function (p) { state.page = p; render(); } });
  }

  function detail(l) {
    var html =
      "<dl class='kv'>" +
      "<dt>When</dt><dd>" + NF.fmtDateTime(l.created_at) + "</dd>" +
      "<dt>User</dt><dd>" + NF.esc(l.username) + " (" + NF.esc(l.role) + ")</dd>" +
      "<dt>Action</dt><dd class='mono'>" + NF.esc(l.action) + "</dd>" +
      "<dt>Entity</dt><dd>" + NF.esc(l.entity) + (l.entity_id ? " #" + NF.esc(l.entity_id) : "") + "</dd>" +
      "<dt>Endpoint</dt><dd class='mono small'>" + NF.esc((l.request_method || "") + " " + (l.endpoint || "")) + "</dd>" +
      "<dt>Status</dt><dd>" + (l.status_code != null ? l.status_code : "—") + "</dd>" +
      "<dt>IP address</dt><dd class='mono small'>" + NF.esc(l.ip_address || "—") + "</dd>" +
      "<dt>Correlation</dt><dd class='mono small'>" + NF.esc(l.correlation_id || "—") + "</dd>" +
      "</dl>" +
      (l.description ? "<p class='text-soft mt-16 mb-0'>" + NF.esc(l.description) + "</p>" : "") +
      changes(l.old_value, l.new_value);
    NF.modal({ title: "Audit #" + l.audit_id, size: "lg", content: html, actions: [{ label: "Close", class: "btn", onClick: function (c) { c(); } }] });
  }

  function changes(oldV, newV) {
    if (!oldV && !newV) return "";
    return "<div class='mt-16'><strong>Changes</strong><div class='grid grid-2 mt-8'>" +
      "<div><div class='small text-muted'>Before</div><pre class='code'>" + NF.esc(pretty(oldV)) + "</pre></div>" +
      "<div><div class='small text-muted'>After</div><pre class='code'>" + NF.esc(pretty(newV)) + "</pre></div>" +
      "</div></div>";
  }

  function pretty(v) {
    if (v == null) return "—";
    try { return JSON.stringify(v, null, 2); } catch (e) { return String(v); }
  }

  function load() {
    tbody.innerHTML = '<tr><td colspan="7"><div class="spinner"></div></td></tr>';
    Api.get("/api/admin/audit").then(function (res) {
      logs = res.data || [];
      render();
    }).catch(function (err) {
      tbody.innerHTML = '<tr><td colspan="7">' + NF.emptyState("Could not load audit log", err.message, "x") + "</td></tr>";
    });
  }

  NF.qs("#search").addEventListener("input", NF.debounce(function (e) { state.query = e.target.value.trim(); state.page = 1; render(); }, 200));
  NF.qs("#role").addEventListener("change", function (e) { state.role = e.target.value; state.page = 1; render(); });
  NF.qs("#refresh").addEventListener("click", load);

  load();
})();