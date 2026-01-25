document.addEventListener("DOMContentLoaded", () => {
  if (isAuthed()) {
    window.location.href = "/dashboard/";
    return;
  }

  const form = document.getElementById("loginForm");
  const errorBox = document.getElementById("errorBox");
  const successBox = document.getElementById("successBox");
  const btn = document.getElementById("btnLogin");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlert(errorBox);
    if (successBox) clearAlert(successBox);

    const fd = new FormData(form);
    const username = fd.get("username");
    const password = fd.get("password");

    btn.disabled = true;

    try {
      await API.auth.login(username, password);
      // Update nav to show logout button
      if (typeof updateNav === "function") {
        updateNav();
      }
      // Show success message briefly before redirect
      if (successBox) {
        setAlert(successBox, "Login successful! Redirecting...", "success");
        setTimeout(() => {
          window.location.href = "/dashboard/";
        }, 500);
      } else {
        window.location.href = "/dashboard/";
      }
    } catch (err) {
      setAlert(errorBox, err.message || "Login failed.");
      btn.disabled = false;
    }
  });
});

