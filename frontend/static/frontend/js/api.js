const API = {
  base: "/api",

  tokens: {
    get() {
      return {
        access: localStorage.getItem("access_token"),
        refresh: localStorage.getItem("refresh_token"),
      };
    },
    set(access, refresh) {
      if (access) localStorage.setItem("access_token", access);
      if (refresh) localStorage.setItem("refresh_token", refresh);
    },
    clear() {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    },
  },

  async request(path, options = {}, { auth = true, retry = true } = {}) {
    const url = `${this.base}${path}`;
    const headers = options.headers ? { ...options.headers } : {};

    if (auth) {
      const { access } = this.tokens.get();
      if (access) headers["Authorization"] = `Bearer ${access}`;
    }

    const res = await fetch(url, { ...options, headers });

    // If unauthorized, attempt refresh once
    if (res.status === 401 && retry) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        return this.request(path, options, { auth, retry: false });
      }
    }

    const contentType = res.headers.get("content-type") || "";
    let data = null;

    if (contentType.includes("application/json")) {
      data = await res.json();
    } else {
      data = await res.text();
    }

    if (!res.ok) {
      const detail = (data && data.detail) ? data.detail : "Request failed.";
      const err = new Error(detail);
      err.status = res.status;
      err.data = data;
      throw err;
    }

    return data;
  },

  async refreshAccessToken() {
    const { refresh } = this.tokens.get();
    if (!refresh) {
      // Clear tokens if refresh token is missing
      this.tokens.clear();
      return false;
    }

    try {
      const res = await fetch(`${this.base}/accounts/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
      });

      if (!res.ok) {
        // If refresh fails, clear tokens and redirect to login
        if (res.status === 401) {
          this.tokens.clear();
          if (window.location.pathname !== "/login/") {
            window.location.href = "/login/";
          }
        }
        return false;
      }
      const data = await res.json();
      if (data && data.access) {
        // Keep the refresh token if provided, otherwise keep existing one
        this.tokens.set(data.access, data.refresh || refresh);
        return true;
      }
      return false;
    } catch {
      // On error, clear tokens
      this.tokens.clear();
      return false;
    }
  },

  auth: {
    async login(username, password) {
      const data = await API.request("/accounts/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      }, { auth: false });

      API.tokens.set(data.access, data.refresh);
      // Trigger nav update after login (updateNav is called via token.set wrapper)
      return data;
    },

    async register(username, email, password) {
      return API.request("/accounts/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      }, { auth: false });
    },

    async profile() {
      return API.request("/accounts/profile/", { method: "GET" }, { auth: true });
    },

    async updateProfile(payload) {
      return API.request("/accounts/profile/", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }, { auth: true });
    },
  }
};

