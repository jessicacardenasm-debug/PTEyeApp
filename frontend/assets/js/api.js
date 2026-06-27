const API_BASE = "/api";

const api = {
  async login(email, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Credenciales inválidas");
    }
    return res.json();
  },

  async analyze(patientId, imageFile) {
    const token = localStorage.getItem("token");
    const form = new FormData();
    form.append("patient_id", patientId);
    form.append("image", imageFile);

    const res = await fetch(`${API_BASE}/analysis/analyze`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: form,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Error en el análisis");
    }
    return res.json();
  },

  saveResult(result) {
    sessionStorage.setItem("last_result", JSON.stringify(result));
  },

  getResult() {
    const raw = sessionStorage.getItem("last_result");
    return raw ? JSON.parse(raw) : null;
  },

  logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/pages/login.html";
  },

  requireAuth() {
    if (!localStorage.getItem("token")) {
      window.location.href = "/pages/login.html";
    }
  },
};
