/* Admin — User Management */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("admin");

  var tbody = NF.qs("#rows");
  var pager = NF.qs("#pager");
  var SIZE = 12;
  var users = [];
  var state = { page: 1, query: "", role: "", status: "" };

  var ROLES = ["ADMIN", "OFFICER", "CITIZEN"];
  var STATUSES = ["ACTIVE", "INACTIVE", "SUSPENDED"];

  function filtered() {
    var q = state.query.toLowerCase();
    return users.filter(function (u) {
      if (state.role && u.role !== state.role) return false;
      if (state.status && u.status !== state.status) return false;
      if (!q) return true;
      return [u.full_name, u.email, u.id_number, u.phone].some(function (v) { return v && String(v).toLowerCase().indexOf(q) >= 0; });
    });
  }

  function render() {
    var rows = filtered();
    var pages = Math.max(1, Math.ceil(rows.length / SIZE));
    if (state.page > pages) state.page = pages;
    var slice = rows.slice((state.page - 1) * SIZE, state.page * SIZE);

    if (!slice.length) {
      tbody.innerHTML = '<tr><td colspan="7">' + NF.emptyState("No users found", "Try adjusting your filters.", "users") + "</td></tr>";
      pager.innerHTML = "";
      return;
    }
    tbody.innerHTML = "";
    slice.forEach(function (u) {
      var tr = NF.el("tr", { class: "row-link" });
      var isActive = u.status === "ACTIVE";
      tr.innerHTML =
        "<td><div class='flex items-center gap-12'><span class='avatar avatar-sm'>" + NF.esc(NF.initials(u.full_name)) + "</span><strong>" + NF.esc(u.full_name) + "</strong></div></td>" +
        "<td>" + NF.esc(u.email) + "</td>" +
        '<td class="mono nowrap">' + NF.esc(u.id_number) + "</td>" +
        "<td>" + NF.esc(u.phone) + "</td>" +
        "<td>" + NF.statusBadge(u.role) + "</td>" +
        "<td>" + NF.statusBadge(u.status) + "</td>" +
        '<td class="actions">' +
        '<button class="btn btn-sm btn-secondary edit" type="button">Edit</button>' +
        '<button class="btn btn-sm btn-secondary toggle" type="button">' + (isActive ? "Deactivate" : "Activate") + "</button>" +
        '<button class="btn btn-sm btn-secondary reset" type="button">Reset PW</button>' +
        '<button class="btn btn-sm btn-danger del" type="button">Delete</button>' +
        "</td>";
      NF.qs(".edit", tr).addEventListener("click", function (e) { e.stopPropagation(); edit(u); });
      NF.qs(".toggle", tr).addEventListener("click", function (e) { e.stopPropagation(); toggle(u); });
      NF.qs(".reset", tr).addEventListener("click", function (e) { e.stopPropagation(); resetPw(u); });
      NF.qs(".del", tr).addEventListener("click", function (e) { e.stopPropagation(); remove(u); });
      tbody.appendChild(tr);
    });
    NF.renderPagination(pager, { page: state.page, pages: pages, total: rows.length, onPage: function (p) { state.page = p; render(); } });
  }

  function roleOptions(sel) {
    return ROLES.map(function (r) { return "<option value='" + r + "'" + (r === sel ? " selected" : "") + ">" + NF.titleCase(r) + "</option>"; }).join("");
  }

  function create() {
    var html =
      "<div class='form-grid'>" +
      inp("first_name", "First name", true) + inp("last_name", "Last name", true) +
      inp("email", "Email", true, "email") + inp("phone", "Phone", true, "tel") +
      inp("id_number", "ID number (13 digits)", true) +
      "<div class='form-group'><label for='f-role'>Role <span class='req'>*</span></label><select class='select' id='f-role'>" + roleOptions("CITIZEN") + "</select></div>" +
      inp("password", "Temporary password (min 8)", true, "password") +
      "</div>";
    NF.modal({
      title: "Create user", size: "lg", content: html,
      actions: [
        { label: "Cancel", class: "btn-secondary", onClick: function (c) { c(); } },
        { label: "Create", class: "btn", onClick: function (c, btn) {
          var body = {
            first_name: NF.qs("#f-first_name").value.trim(), last_name: NF.qs("#f-last_name").value.trim(),
            email: NF.qs("#f-email").value.trim(), phone: NF.qs("#f-phone").value.trim(),
            id_number: NF.qs("#f-id_number").value.trim(), role: NF.qs("#f-role").value,
            password: NF.qs("#f-password").value
          };
          if (Object.keys(body).some(function (k) { return !body[k]; })) { NF.toast("Please complete all fields.", "warning"); return; }
          if (body.password.length < 8) { NF.toast("Password must be at least 8 characters.", "warning"); return; }
          NF.setLoading(btn, true, "Creating…");
          Api.post("/api/admin/users", body).then(function () { c(); NF.toast("User created.", "success"); load(); })
            .catch(function (err) { NF.setLoading(btn, false); NF.toast(err.message, "error", "Create failed"); });
        } }
      ]
    });
    function inp(name, label, req, type) {
      return "<div class='form-group'><label for='f-" + name + "'>" + label + (req ? " <span class='req'>*</span>" : "") + "</label><input class='input' id='f-" + name + "' type='" + (type || "text") + "'></div>";
    }
  }

  function edit(u) {
    var html =
      "<div class='form-grid'>" +
      "<div class='form-group'><label for='f-first_name'>First name</label><input class='input' id='f-first_name' value='" + NF.esc(u.first_name) + "'></div>" +
      "<div class='form-group'><label for='f-last_name'>Last name</label><input class='input' id='f-last_name' value='" + NF.esc(u.last_name) + "'></div>" +
      "<div class='form-group'><label for='f-phone'>Phone</label><input class='input' id='f-phone' value='" + NF.esc(u.phone) + "'></div>" +
      "<div class='form-group'><label for='f-role'>Role</label><select class='select' id='f-role'>" + roleOptions(u.role) + "</select></div>" +
      "<div class='form-group'><label for='f-status'>Status</label><select class='select' id='f-status'>" + STATUSES.map(function (s) { return "<option value='" + s + "'" + (s === u.status ? " selected" : "") + ">" + NF.titleCase(s) + "</option>"; }).join("") + "</select></div>" +
      "</div>";
    NF.modal({
      title: "Edit " + u.full_name, size: "lg", content: html,
      actions: [
        { label: "Cancel", class: "btn-secondary", onClick: function (c) { c(); } },
        { label: "Save", class: "btn", onClick: function (c, btn) {
          var body = {
            first_name: NF.qs("#f-first_name").value.trim(), last_name: NF.qs("#f-last_name").value.trim(),
            phone: NF.qs("#f-phone").value.trim(), role: NF.qs("#f-role").value, status: NF.qs("#f-status").value
          };
          NF.setLoading(btn, true, "Saving…");
          Api.put("/api/admin/users/" + u.user_id, body).then(function () { c(); NF.toast("User updated.", "success"); load(); })
            .catch(function (err) { NF.setLoading(btn, false); NF.toast(err.message, "error"); });
        } }
      ]
    });
  }

  function toggle(u) {
    var active = u.status === "ACTIVE";
    var msg = active ? "Deactivate this account? They will not be able to sign in." : "Activate this account?";
    NF.confirm({ title: (active ? "Deactivate" : "Activate") + " " + u.full_name, message: msg, confirmLabel: active ? "Deactivate" : "Activate", danger: active })
      .then(function (ok) {
        if (!ok) return;
        Api.put("/api/admin/users/" + u.user_id + (active ? "/deactivate" : "/activate"), {})
          .then(function () { NF.toast("User " + (active ? "deactivated" : "activated") + ".", "success"); load(); })
          .catch(function (err) { NF.toast(err.message, "error"); });
      });
  }

  function resetPw(u) {
    NF.confirm({ title: "Reset password", message: "Generate a new temporary password for " + u.full_name + "?", confirmLabel: "Reset" })
      .then(function (ok) {
        if (!ok) return;
        Api.post("/api/admin/users/" + u.user_id + "/reset-password", {}).then(function (res) {
          var pw = (res.data && res.data.temporary_password) || "";
          NF.modal({
            title: "Temporary password",
            content: "<p>Share this one-time password with the user. It will not be shown again.</p>" +
              "<div class='alert alert-info'><strong class='mono' style='font-size:1.1rem'>" + NF.esc(pw) + "</strong></div>",
            actions: [{ label: "Done", class: "btn", onClick: function (c) { c(); } }]
          });
        }).catch(function (err) { NF.toast(err.message, "error"); });
      });
  }

  function remove(u) {
    NF.confirm({ title: "Delete " + u.full_name, message: "This permanently deletes the account. This cannot be undone.", confirmLabel: "Delete", danger: true })
      .then(function (ok) {
        if (!ok) return;
        Api.del("/api/admin/users/" + u.user_id).then(function () { NF.toast("User deleted.", "success"); load(); })
          .catch(function (err) { NF.toast(err.message, "error"); });
      });
  }

  function load() {
    tbody.innerHTML = '<tr><td colspan="7"><div class="spinner"></div></td></tr>';
    Api.get("/api/admin/users").then(function (res) {
      users = res.data || [];
      render();
    }).catch(function (err) {
      tbody.innerHTML = '<tr><td colspan="7">' + NF.emptyState("Could not load users", err.message, "x") + "</td></tr>";
    });
  }

  NF.qs("#search").addEventListener("input", NF.debounce(function (e) { state.query = e.target.value.trim(); state.page = 1; render(); }, 200));
  NF.qs("#role").addEventListener("change", function (e) { state.role = e.target.value; state.page = 1; render(); });
  NF.qs("#status").addEventListener("change", function (e) { state.status = e.target.value; state.page = 1; render(); });
  NF.qs("#add").addEventListener("click", create);

  load();
})();