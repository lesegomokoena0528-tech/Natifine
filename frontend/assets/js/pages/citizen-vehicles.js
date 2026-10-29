/* Citizen — My Vehicles */
(function () {
  "use strict";
  var NF = window.NF;
  Guard.requireRole("citizen");
  var box = NF.qs("#cards");
  var vehicles = [];

  function render() {
    if (!vehicles.length) {
      box.innerHTML = "<div class='card' style='grid-column:1/-1'><div class='card-body'>" +
        NF.emptyState("No vehicles registered", "Register a vehicle to start receiving fines.", "vehicle") + "</div></div>";
      return;
    }
    box.innerHTML = "";
    vehicles.forEach(function (v) {
      var card = NF.el("div", { class: "card" });
      card.innerHTML =
        "<div class='card-body'>" +
        "<div class='flex items-center gap-12 mb-16'>" +
        "<span class='avatar avatar-sm'>" + NF.icon("vehicle", "ico") + "</span>" +
        "<div class='flex-1'><strong class='plate'>" + NF.esc(v.registration_number) + "</strong>" +
        "<div class='small text-muted'>" + NF.esc(v.make + " " + v.model) + "</div></div>" +
        "<span class='badge badge-" + NF.esc(String(v.status).toLowerCase()) + "'>" + NF.esc(NF.titleCase(v.status)) + "</span>" +
        "</div>" +
        "<dl class='kv'>" +
        "<dt>Year</dt><dd>" + NF.esc(v.year) + "</dd>" +
        "<dt>Colour</dt><dd>" + NF.esc(v.color || "—") + "</dd>" +
        "<dt>Type</dt><dd>" + NF.esc(NF.titleCase(v.vehicle_type)) + "</dd>" +
        "<dt>VIN</dt><dd class='mono small'>" + NF.esc(v.vin) + "</dd>" +
        "</dl>" +
        "<div class='flex gap-8 mt-16'><button class='btn btn-sm btn-secondary detail' type='button'>Details</button>" +
        "<a class='btn btn-sm btn-secondary' href='/pages/citizen/fines.html'>Fines</a></div>" +
        "</div>";
      NF.qs(".detail", card).addEventListener("click", function () { detail(v); });
      box.appendChild(card);
    });
  }

  function detail(v) {
    var html = "<dl class='kv'>" +
      ["Registration|" + v.registration_number, "Make|" + v.make, "Model|" + v.model,
       "Year|" + v.year, "Colour|" + (v.color || "—"), "Type|" + NF.titleCase(v.vehicle_type),
       "VIN|" + v.vin, "Engine no.|" + (v.engine_number || "—"), "Status|" + NF.titleCase(v.status),
       "Registered|" + NF.fmtDate(v.created_at)].map(function (r) {
        var p = r.split("|");
        return "<dt>" + NF.esc(p[0]) + "</dt><dd>" + (p[0] === "VIN" ? "<span class='mono small'>" + NF.esc(p[1]) + "</span>" : NF.esc(p[1])) + "</dd>";
      }).join("") + "</dl>";
    NF.modal({ title: v.registration_number, content: html, actions: [{ label: "Close", class: "btn-secondary", onClick: function (c) { c(); } }] });
  }

  function registerModal() {
    var html =
      "<div class='form-grid'>" +
      field("registration_number", "Registration number", "e.g. CA 123-456", true, "text") +
      field("make", "Make", "e.g. Toyota", true) +
      field("model", "Model", "e.g. Corolla", true) +
      field("year", "Year", "e.g. 2019", true, "number") +
      field("color", "Colour", "e.g. White") +
      "<div class='form-group'><label for='f-vehicle_type'>Type <span class='req'>*</span></label>" +
      "<select class='select' id='f-vehicle_type'><option value='CAR'>Car</option><option value='TRUCK'>Truck</option>" +
      "<option value='BUS'>Bus</option><option value='MOTORCYCLE'>Motorcycle</option><option value='TAXI'>Taxi</option>" +
      "<option value='OTHER'>Other</option></select></div>" +
      field("vin", "VIN (17 characters)", "17-character vehicle identification number", true, "text") +
      field("engine_number", "Engine number", "Optional") +
      "</div>" +
      "<div class='field-hint'>The VIN must be exactly 17 characters.</div>";

    NF.modal({
      title: "Register a vehicle", size: "lg", content: html,
      actions: [
        { label: "Cancel", class: "btn-secondary", onClick: function (c) { c(); } },
        { label: "Register", class: "btn", onClick: function (c, btn) { submit(c, btn); } }
      ]
    });

    function submit(close, btn) {
      var body = {
        registration_number: NF.qs("#f-registration_number").value.trim(),
        make: NF.qs("#f-make").value.trim(),
        model: NF.qs("#f-model").value.trim(),
        year: parseInt(NF.qs("#f-year").value, 10),
        color: NF.qs("#f-color").value.trim() || null,
        vehicle_type: NF.qs("#f-vehicle_type").value,
        vin: NF.qs("#f-vin").value.trim().toUpperCase(),
        engine_number: NF.qs("#f-engine_number").value.trim() || null
      };
      if (!body.registration_number || !body.make || !body.model || !body.year || !body.vin) {
        NF.toast("Please complete all required fields.", "warning"); return;
      }
      if (body.vin.length !== 17) {
        NF.toast("VIN must be exactly 17 characters (currently " + body.vin.length + ").", "warning"); return;
      }
      NF.setLoading(btn, true, "Registering…");
      Api.post("/api/vehicles", body).then(function (res) {
        close();
        NF.toast("Vehicle registered successfully.", "success");
        vehicles.unshift(res.data);
        render();
      }).catch(function (err) {
        NF.setLoading(btn, false);
        NF.toast(err.message, "error", "Registration failed");
      });
    }

    function field(name, label, ph, req, type) {
      return "<div class='form-group'><label for='f-" + name + "'>" + label + (req ? " <span class='req'>*</span>" : "") +
        "</label><input class='input' id='f-" + name + "' type='" + (type || "text") + "' placeholder='" + NF.esc(ph) + "'></div>";
    }
  }

  function load() {
    Api.get("/api/vehicles/my").then(function (res) { vehicles = res.data || []; render(); })
      .catch(function (err) {
        box.innerHTML = "<div class='card' style='grid-column:1/-1'><div class='card-body'>" +
          NF.emptyState("Could not load vehicles", err.message, "x") + "</div></div>";
      });
  }

  NF.qs("#add").addEventListener("click", registerModal);
  load();
})();
