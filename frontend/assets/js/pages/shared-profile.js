/* Shared — Profile & password (citizen / officer / admin) */
(function () {
  "use strict";
  var NF = window.NF;
  if (!Guard.requireAuth()) return;

  var form = NF.qs("#pw-form");

  Api.profile().then(function (u) {
    NF.qs("#pro-avatar").textContent = NF.initials(u.full_name);
    NF.qs("#pro-name").textContent = u.full_name;
    NF.qs("#pro-role").textContent = NF.titleCase(u.role);
    NF.qs("#pro-status").innerHTML = NF.statusBadge(u.status);
    if (NF.qs("#pro-status-cell")) NF.qs("#pro-status-cell").value = u.status;
    NF.qs("#kv-rows").innerHTML = [
      ["ID number", u.id_number], ["Email", u.email], ["Phone", u.phone],
      ["User ID", u.user_id], ["Member since", NF.fmtDate(u.created_at)]
    ].map(function (r) {
      return "<dt>" + NF.esc(r[0]) + "</dt><dd>" + (r[0] === "User ID" ? '<span class="mono small">' + NF.esc(r[1]) + "</span>" : NF.esc(r[1]) || "—") + "</dd>";
    }).join("");
  }).catch(function (err) {
    NF.toast(err.message, "error", "Profile");
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var cur = NF.qs("#pw-current").value;
    var nw = NF.qs("#pw-new").value;
    var cf = NF.qs("#pw-confirm").value;
    NF.formErrors(form, null);
    if (nw !== cf) {
      NF.qs("[data-error-for='confirm']").textContent = "Passwords do not match.";
      NF.qs("#pw-confirm").classList.add("is-invalid");
      return;
    }
    if (nw.length < 8) {
      NF.qs("[data-error-for='new']").textContent = "Password must be at least 8 characters.";
      NF.qs("#pw-new").classList.add("is-invalid");
      return;
    }
    var btn = NF.qs("#pw-submit");
    NF.setLoading(btn, true, "Saving…");
    Api.put("/api/auth/change-password", { current_password: cur, new_password: nw }).then(function () {
      NF.setLoading(btn, false);
      NF.toast("Password changed successfully.", "success");
      form.reset();
    }).catch(function (err) {
      NF.setLoading(btn, false);
      NF.toast(err.message, "error", "Password not changed");
    });
  });
})();