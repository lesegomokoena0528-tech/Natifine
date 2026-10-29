/* ==========================================================================
   NatiFine SA — API client + session management
   Exposes: window.Session, window.Api, window.ApiError
   No build step. Plain ES2019. Uses fetch.
   ========================================================================== */

(function () {
  "use strict";

  var ACCESS_KEY = "nf_access_token";
  var REFRESH_KEY = "nf_refresh_token";
  var USER_KEY = "nf_user";

  /* --------------------------------------------------------------- Session */
  var Session = {
    set: function (payload) {
      if (payload.access_token) sessionStorage.setItem(ACCESS_KEY, payload.access_token);
      if (payload.refresh_token) sessionStorage.setItem(REFRESH_KEY, payload.refresh_token);
      if (payload.user) sessionStorage.setItem(USER_KEY, JSON.stringify(payload.user));
    },
    setUser: function (user) {
      if (user) sessionStorage.setItem(USER_KEY, JSON.stringify(user));
    },
    access: function () { return sessionStorage.getItem(ACCESS_KEY); },
    refreshToken: function () { return sessionStorage.getItem(REFRESH_KEY); },
    user: function () {
      try { return JSON.parse(sessionStorage.getItem(USER_KEY) || "null"); }
      catch (e) { return null; }
    },
    role: function () {
      var u = this.user();
      return u && u.role ? String(u.role).toLowerCase() : null;
    },
    isLoggedIn: function () { return !!this.access(); },
    clear: function () {
      sessionStorage.removeItem(ACCESS_KEY);
      sessionStorage.removeItem(REFRESH_KEY);
      sessionStorage.removeItem(USER_KEY);
    }
  };

  /* ------------------------------------------------------------- ApiError */
  function ApiError(message, status, errors) {
    this.name = "ApiError";
    this.message = message || "Something went wrong.";
    this.status = status || 0;
    this.errors = errors || null;
  }
  ApiError.prototype = Object.create(Error.prototype);

  // Resolved at request time so config.js can set window.NF_API_BASE.
  // Empty value = same origin (Flask serving the frontend locally).
  function apiBase() {
    var b = window.NF_API_BASE;
    if (typeof b === "string" && b) return b.replace(/\/+$/, "");
    return "";
  }

  function buildUrl(path, query) {
    var url = apiBase() + path;
    if (query && typeof query === "object") {
      var parts = [];
      Object.keys(query).forEach(function (k) {
        var v = query[k];
        if (v !== undefined && v !== null && v !== "") {
          parts.push(encodeURIComponent(k) + "=" + encodeURIComponent(v));
        }
      });
      if (parts.length) url += (url.indexOf("?") >= 0 ? "&" : "?") + parts.join("&");
    }
    return url;
  }

  function extractMessage(payload, fallback) {
    if (!payload) return fallback;
    if (typeof payload.message === "string" && payload.message) return payload.message;
    var errors = payload.errors;
    if (errors && typeof errors === "object") {
      var first = Object.keys(errors)[0];
      if (first) {
        var v = errors[first];
        if (Array.isArray(v) && v.length) return v[0];
        if (typeof v === "string") return v;
      }
    }
    return fallback;
  }

  var refreshing = null;

  function doRefresh() {
    var rt = Session.refreshToken();
    if (!rt) return Promise.reject(new ApiError("Session expired.", 401));
    if (refreshing) return refreshing;
    refreshing = fetch(buildUrl("/api/auth/refresh"), {
      method: "POST",
      headers: { "Authorization": "Bearer " + rt }
    }).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (payload) {
        refreshing = null;
        if (!res.ok || !payload.success) {
          Session.clear();
          throw new ApiError(extractMessage(payload, "Session expired."), res.status, payload.errors);
        }
        Session.set({ access_token: payload.data.access_token });
        return payload.data.access_token;
      });
    }, function (err) {
      refreshing = null;
      throw err;
    });
    return refreshing;
  }

  function request(method, path, options) {
    options = options || {};
    var opts = {
      method: method,
      headers: {},
      credentials: "same-origin"
    };
    var isForm = options.form instanceof FormData;
    if (options.body !== undefined && !isForm) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(options.body);
    } else if (isForm) {
      opts.body = options.form;
    }
    var auth = options.auth !== false;
    if (auth && Session.access()) {
      opts.headers["Authorization"] = "Bearer " + Session.access();
    }

    return fetch(buildUrl(path, options.query), opts).then(function (res) {
      if (res.status === 401 && auth && Session.refreshToken() && !options._retried) {
        return doRefresh().then(function () {
          var retry = Object.assign({}, options, { _retried: true });
          return request(method, path, retry);
        });
      }
      if (options.raw) {
        if (!res.ok) {
          return res.json().catch(function () { return {}; }).then(function (payload) {
            throw new ApiError(extractMessage(payload, "Request failed."), res.status, payload.errors);
          });
        }
        return res;
      }
      return res.json().catch(function () {
        throw new ApiError("Unexpected server response (" + res.status + ").", res.status);
      }).then(function (payload) {
        if (!res.ok || payload.success === false) {
          throw new ApiError(extractMessage(payload, "Request failed."), res.status, payload.errors);
        }
        return payload;
      });
    });
  }

  var Api = {
    request: request,
    get: function (p, o) { return request("GET", p, o); },
    post: function (p, body, o) { o = o || {}; o.body = body; return request("POST", p, o); },
    put: function (p, body, o) { o = o || {}; o.body = body; return request("PUT", p, o); },
    patch: function (p, body, o) { o = o || {}; o.body = body; return request("PATCH", p, o); },
    del: function (p, o) { return request("DELETE", p, o); },

    /* Download a binary file (e.g. receipt PDF) and trigger save. */
    download: function (path, filename) {
      return request("GET", path, { raw: true }).then(function (res) {
        return res.blob();
      }).then(function (blob) {
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = filename || "natifine-download";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
      });
    },

    /* ----- Auth convenience ----- */
    login: function (username, password) {
      return Api.post("/api/auth/login", { username: username, password: password }, { auth: false })
        .then(function (res) { Session.set(res.data); return res.data; });
    },
    register: function (data) {
      return Api.post("/api/auth/register", data, { auth: false });
    },
    logout: function () { Session.clear(); },
    profile: function () {
      return Api.get("/api/auth/profile").then(function (res) { Session.setUser(res.data); return res.data; });
    }
  };

  window.Session = Session;
  window.Api = Api;
  window.ApiError = ApiError;
})();
