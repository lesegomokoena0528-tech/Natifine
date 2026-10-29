/* Officer — Issue Fine */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("officer");

  var form = NF.qs("#fine-form");
  var selected = null;
  var searchInput = NF.qs("#v-search");
  var results = NF.qs("#v-results");
  var selectedBox = NF.qs("#v-selected");

  function clearSelected() {
    selected = null;
    selectedBox.classList.add("hidden");
    selectedBox.innerHTML = "";
  }

  function showSelected(v) {
    selected = v;
    results.classList.add("hidden");
    searchInput.value = v.registration_number;
    selectedBox.classList.remove("hidden");
    selectedBox.innerHTML =
      "<div class='flex items-center gap-12'>" + NF.icon("vehicle", "ico") +
      "<div class='flex-1'><strong>" + NF.esc(v.registration_number) + "</strong> · " +
      NF.esc(v.make + " " + v.model + " (" + v.year + ")") + "</div>" +
      "<button type='button' class='icon-btn' id='v-clear' aria-label='Clear'>" + NF.icon("x") + "</button></div>";
    NF.qs("#v-clear").addEventListener("click", function () { clearSelected(); searchInput.value = ""; searchInput.focus(); });
  }

  searchInput.addEventListener("input", NF.debounce(function () {
    var q = searchInput.value.trim();
    clearSelected();
    if (q.length < 2) { results.classList.add("hidden"); return; }
    Api.get("/api/vehicles/search", { query: { keyword: q } }).then(function (res) {
      var list = res.data || [];
      if (!list.length) {
        results.innerHTML = "<div class='suggestion muted'>No matching vehicles</div>";
        results.classList.remove("hidden");
        return;
      }
      results.innerHTML = "";
      list.slice(0, 8).forEach(function (v) {
        var item = NF.el("button", { type: "button", class: "suggestion" });
        item.innerHTML = "<strong>" + NF.esc(v.registration_number) + "</strong> · " + NF.esc(v.make + " " + v.model);
        item.addEventListener("click", function () { showSelected(v); });
        results.appendChild(item);
      });
      results.classList.remove("hidden");
    }).catch(function (err) { NF.toast(err.message, "error", "Vehicle search"); });
  }, 250));

  document.addEventListener("click", function (e) {
    if (!results.contains(e.target) && e.target !== searchInput) results.classList.add("hidden");
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    NF.formErrors(form, null);
    var body = {
      vehicle_id: selected ? selected.vehicle_id : null,
      offence_code: NF.qs("#offence_code").value.trim(),
      offence: NF.qs("#offence").value.trim(),
      severity: NF.qs("#severity").value,
      amount: NF.qs("#amount").value,
      location: NF.qs("#location").value.trim(),
      remarks: NF.qs("#remarks").value.trim() || null
    };
    if (!body.vehicle_id) { NF.toast("Please select a vehicle.", "warning"); return; }
    if (!body.offence_code || !body.offence || !body.amount || !body.location) {
      NF.toast("Please complete all required fields.", "warning"); return;
    }
    var btn = NF.qs("#submit");
    NF.setLoading(btn, true, "Issuing…");
    Api.post("/api/v1/fines", body).then(function (res) {
      NF.setLoading(btn, false);
      var f = res.data;
      var html =
        "<div class='text-center'><div class='avatar avatar-lg' style='margin:0 auto 12px;background:var(--accent)'>" + NF.icon("check", "ico") + "</div>" +
        "<h3>Fine issued</h3><p class='text-muted'>The fine has been recorded and the owner notified.</p></div>" +
        "<dl class='kv mt-16'><dt>Fine number</dt><dd class='mono'>" + NF.esc(f.fine_number) + "</dd>" +
        "<dt>Vehicle</dt><dd>" + NF.esc(f.registration_number) + "</dd>" +
        "<dt>Amount</dt><dd><strong>" + NF.money(f.amount) + "</strong></dd>" +
        "<dt>Due date</dt><dd>" + NF.fmtDate(f.due_date) + "</dd>" +
        "<dt>Status</dt><dd>" + NF.statusBadge(f.status) + "</dd></dl>";
      NF.modal({
        title: "Success", content: html,
        actions: [
          { label: "Issue another", class: "btn-secondary", onClick: function (c) { c(); form.reset(); clearSelected(); } },
          { label: "Go to fines", class: "btn", onClick: function () { window.location.href = "/pages/officer/fines.html?id=" + f.fine_id; } }
        ]
      });
    }).catch(function (err) {
      NF.setLoading(btn, false);
      NF.formErrors(form, err.errors);
      NF.toast(err.message, "error", "Could not issue fine");
    });
  });
})();