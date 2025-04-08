import { defineStore } from "pinia";
import axios from "axios";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: null,
    user: null, // { id, username, role }
  }),
  actions: {
    async login(identifier, password) {
      try {
        const response = await axios.post("http://127.0.0.1:8000/api/auth/login", { identifier, password });
        this.token = response.data.access_token;
        const payload = JSON.parse(atob(response.data.access_token.split('.')[1]));
        this.user = { id: payload.user_id, role: payload.role, username: payload.username || identifier };
        localStorage.setItem("token", this.token);
        localStorage.setItem("user", JSON.stringify(this.user));
        return true;
      } catch (error) {
        console.error("Login error:", error);
        throw error;
      }
    },
    async register(username, password, role = "User") {
      try {
        const response = await axios.post("http://127.0.0.1:8000/api/auth/register", { username, password, role });
        this.token = response.data.access_token;
        const payload = JSON.parse(atob(response.data.access_token.split('.')[1]));
        this.user = { id: payload.user_id, role: payload.role, username };
        localStorage.setItem("token", this.token);
        localStorage.setItem("user", JSON.stringify(this.user));
        return true;
      } catch (error) {
        console.error("Registration error:", error);
        throw error;
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    },
    loadStoredAuth() {
      const token = localStorage.getItem("token");
      const user = localStorage.getItem("user");
      if (token && user) {
        this.token = token;
        this.user = JSON.parse(user);
      }
    }
  },
});