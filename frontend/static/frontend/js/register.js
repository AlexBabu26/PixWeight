document.addEventListener("DOMContentLoaded", () => {
  if (isAuthed()) {
    window.location.href = "/dashboard/";
    return;
  }

  const form = document.getElementById("registerForm");
  const errorBox = document.getElementById("errorBox");
  const successBox = document.getElementById("successBox");
  const btn = document.getElementById("btnRegister");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlert(errorBox);

    const fd = new FormData(form);
    const username = (fd.get("username") || "").trim();
    const email = (fd.get("email") || "").trim();
    const password = fd.get("password");

    btn.disabled = true;

    try {
      await API.auth.register(username, email, password);
      // Redirect to login page after successful registration
      if (successBox) {
        setAlert(successBox, "Registration successful! Redirecting to login...", "success");
      } else {
        setAlert(errorBox, "Registration successful! Redirecting to login...", "success");
      }
      setTimeout(() => {
        window.location.href = "/login/";
      }, 1500);
    } catch (err) {
      setAlert(errorBox, err.message || "Registration failed.");
      btn.disabled = false;
    }
  });
});

