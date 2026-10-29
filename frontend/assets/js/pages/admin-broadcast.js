/* Admin — Broadcast notifications */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("admin");

  var TYPES = [
    "SYSTEM_NOTIFICATION", "WELCOME", "PASSWORD_RESET", "ACCOUNT_VERIFIED",
    "ACCOUNT_LOCKED", "FINE_ISSUED", "FINE_DUE", "PAYMENT_RECEIVED",
    "PAYMENT_FAILED", "PAYMENT_REFUNDED", "DISPUTE_SUBMITTED",
    "DISPUTE_APPROVED", "DISPUTE_REJECTED", "MORE_INFORMATION_REQUIRED"
  ];

  var users = [];
  var templates = [];
  var mode = "custom";
  var vars = {};

  var elAudience = NF.qs("#audience");
  var elUser = NF.qs("#user");
  var elChannel = NF.qs("#channel");
  var elType = NF.qs("#type");
  var elTemplate = NF.qs("#template");

  elType.innerHTML = TYPES.map(function (t) { return "<option value='" + t + "'>" + NF.titleCase(t.replace(/_/g, " ")) + "</option>"; }).join("");

  function audienceUsers() {
    var a = elAudience.value;
    if (a === "single") {
      var u = users.filter(function (x) { return x.user_id === elUser.value; })[0];
      return u ? [u] : [];
    }
    if (a === "all") return users;
    return users.filter(function (u) { return u.role === a; });
  }

  function recipientFor(u, channel) {
    if (channel === "EMAIL") return u.email || "";
    return u.phone || u.email || "";
  }

  function updateCount() {
    var list = audienceUsers();
    var ok = list.filter(function (u) { return recipientFor(u, elChannel.value); });
    NF.qs("#target-count").textContent = ok.length + " recipient" + (ok.length === 1 ? "" : "s") + " will receive this message";
    NF.qs("#send").disabled = ok.length === 0;
  }

  function setMode(next) {
    mode = next;
    Array.prototype.forEach.call(NF.qsa("#mode .tab"), function (b) {
      b.classList.toggle("active", b.dataset.mode === next);
    });
    NF.qs("#custom-fields").classList.toggle("hidden", next !== "custom");
    NF.qs("#template-fields").classList.toggle("hidden", next !== "template");
    updateCount();
  }

  function usersForSelect() {
    elUser.innerHTML = '<option value="">Select a user…</option>' +
      users.map(function (u) { return "<option value='" + u.user_id + "'>" + NF.esc(u.full_name) + " · " + NF.esc(u.email) + "</option>"; }).join("");
  }

  function placeholders(text) {
    var out = {}; var m; var re = /\{\{\s*([\w.]+)\s*\}\}/g;
    while ((m = re.exec(text || ""))) out[m[1]] = true;
    return Object.keys(out);
  }

  function renderTemplateVars() {
    var t = templates.filter(function (x) { return x.name === elTemplate.value; })[0];
    var preview = NF.qs("#template-preview");
    var bodyBox = NF.qs("#template-body");
    var wrap = NF.qs("#variables");
    if (!t) { preview.classList.add("hidden"); wrap.innerHTML = ""; vars = {}; updateCount(); return; }
    preview.classList.remove("hidden");
    bodyBox.textContent = (t.subject ? "Subject: " + t.subject + "\n\n" : "") + (t.body || "");
    var keys = placeholders((t.subject || "") + " " + (t.body || ""));
    vars = {};
    if (!keys.length) { wrap.innerHTML = "<p class='text-soft'>This template has no placeholders.</p>"; return; }
    wrap.innerHTML = "<div class='form-grid mt-16'>" + keys.map(function (k) {
      return "<div class='form-group'><label for='v-" + k + "'>{{" + k + "}}</label><input class='input' id='v-" + k + "' data-var='" + NF.esc(k) + "'></div>";
    }).join("") + "</div>";
    Array.prototype.forEach.call(wrap.querySelectorAll("[data-var]"), function (input) {
      input.addEventListener("input", function () { vars[input.dataset.var] = input.value; });
    });
  }

  function validate() {
    if (mode === "custom") {
      if (!NF.qs("#title").value.trim()) return "Please enter a title.";
      if (!NF.qs("#message").value.trim()) return "Please enter a message.";
    } else {
      if (!elTemplate.value) return "Please choose a template.";
    }
    if (!audienceUsers().length) return "Please choose at least one recipient.";
    return null;
  }

  function send() {
    var err = validate();
    if (err) { NF.toast(err, "warning"); return; }
    var list = audienceUsers();
    var channel = elChannel.value;
    var btn = NF.qs("#send");
    NF.setLoading(btn, true, "Sending…");

    var sent = 0, failed = 0, skipped = 0, failures = [];
    var queue = list.slice();

    function step() {
      if (!queue.length) return done();
      var u = queue.shift();
      var recipient = recipientFor(u, channel);
      if (!recipient || recipient.length < 5) { skipped++; return step(); }

      var req;
      if (mode === "custom") {
        req = Api.post("/api/notifications/send", {
          user_id: u.user_id, channel: channel, recipient: recipient.substring(0, 255),
          type: elType.value, title: NF.qs("#title").value.trim(), message: NF.qs("#message").value.trim()
        });
      } else {
        req = Api.post("/api/notifications/template", {
          template: elTemplate.value, user_id: u.user_id, variables: vars
        });
      }
      req.then(function () { sent++; step(); })
        .catch(function (e) { failed++; failures.push(u.full_name + ": " + e.message); step(); });
    }

    function done() {
      NF.setLoading(btn, false);
      updateCount();
      NF.qs("#result").innerHTML =
        "<div class='stat mb-16'><div class='stat-label'>Delivered / queued</div><div class='stat-value'>" + sent + "</div></div>" +
        "<p><strong>" + sent + "</strong> queued, <strong>" + failed + "</strong> failed, <strong>" + skipped + "</strong> skipped (no address).</p>" +
        (failures.length ? "<div class='alert alert-danger mt-8'><ul style='margin:0;padding-left:18px'>" + failures.slice(0, 20).map(function (f) { return "<li>" + NF.esc(f) + "</li>"; }).join("") + "</ul></div>" : "");
      NF.toast("Broadcast finished: " + sent + " queued.", sent ? "success" : "warning");
    }

    step();
  }

  Array.prototype.forEach.call(NF.qsa("#mode .tab"), function (b) {
    b.addEventListener("click", function () { setMode(b.dataset.mode); });
  });
  elAudience.addEventListener("change", function () {
    NF.qs("#user-wrap").classList.toggle("hidden", elAudience.value !== "single");
    updateCount();
  });
  elUser.addEventListener("change", updateCount);
  elChannel.addEventListener("change", updateCount);
  elTemplate.addEventListener("change", renderTemplateVars);
  NF.qs("#send").addEventListener("click", send);

  Api.get("/api/admin/users").then(function (res) { users = res.data || []; usersForSelect(); updateCount(); })
    .catch(function (e) { NF.toast("Could not load users: " + e.message, "error"); });

  Api.get("/api/notifications/templates").then(function (res) { templates = res.data || []; })
    .catch(function () { templates = []; })
    .then(function () {
      elTemplate.innerHTML = '<option value="">Select a template…</option>' +
        templates.map(function (t) { return "<option value='" + NF.esc(t.name) + "'>" + NF.esc(t.name) + " (" + NF.esc(t.channel) + ")</option>"; }).join("");
      if (!templates.length) elTemplate.innerHTML = '<option value="">No templates available</option>';
    });

  updateCount();
})();
