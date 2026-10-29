/* Admin — Reports & Exports */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("admin");

  function kv(target, obj, money) {
    var box = NF.qs(target);
    if (!box) return;
    box.innerHTML = Object.keys(obj).map(function (k) {
      var v = obj[k];
      var display = (money && /revenue|amount|total_paid/.test(k)) ? NF.money(v) : NF.esc(v == null ? "—" : v);
      return "<dt>" + NF.titleCase(k.replace(/_/g, " ")) + "</dt><dd>" + display + "</dd>";
    }).join("");
  }

  function load() {
    Api.get("/api/admin/reports/system").then(function (res) {
      var d = res.data || {};
      if (d.generated) NF.qs("#generated").textContent = "Report generated " + NF.fmtDateTime(d.generated);

      kv("#r-revenue", d.revenue || {}, true);
      kv("#r-fines", d.fines || {});
      kv("#r-users", d.users || {});
      kv("#r-vehicles", d.vehicles || {});
      kv("#r-disputes", d.disputes || {});
      kv("#r-notifications", d.notifications || {});

      var dash = d.dashboard || {};
      var box = NF.qs("#r-dashboard");
      var keys = Object.keys(dash);
      box.innerHTML = "";
      keys.forEach(function (k) {
        var val = dash[k];
        var isMoney = /revenue/.test(k);
        var el = NF.el("div", { class: "stat" });
        el.innerHTML = "<div class='stat-label'>" + NF.titleCase(k.replace(/_/g, " ")) + "</div>" +
          "<div class='stat-value'>" + (isMoney ? NF.money(val) : NF.esc(val == null ? 0 : val)) + "</div>";
        box.appendChild(el);
      });
    }).catch(function (err) {
      NF.qs("#generated").textContent = "Could not load report: " + err.message;
    });
  }

  function exportReport(format, btn) {
    var ext = format === "excel" ? "xlsx" : format;
    NF.setLoading(btn, true, "Preparing…");
    Api.download("/api/admin/reports/export?format=" + format, "NatiFine-System-Report." + ext)
      .then(function () { NF.setLoading(btn, false); NF.toast("Report exported.", "success"); })
      .catch(function (err) { NF.setLoading(btn, false); NF.toast(err.message, "error", "Export failed"); });
  }

  NF.qs("#exp-pdf").addEventListener("click", function () { exportReport("pdf", this); });
  NF.qs("#exp-excel").addEventListener("click", function () { exportReport("excel", this); });
  NF.qs("#exp-csv").addEventListener("click", function () { exportReport("csv", this); });

  load();
})();