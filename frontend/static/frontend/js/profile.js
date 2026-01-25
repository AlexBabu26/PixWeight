document.addEventListener("DOMContentLoaded", async () => {
  if (!requireAuthOrRedirect()) return;

  const errorBox = document.getElementById("errorBox");
  const successBox = document.getElementById("successBox");

  const usernameEl = document.getElementById("username");
  const emailEl = document.getElementById("email");
  const displayName = document.getElementById("displayName");
  const form = document.getElementById("profileForm");

  try {
    const p = await API.auth.profile();
    usernameEl.textContent = p.username || "—";
    emailEl.textContent = p.email || "—";
    displayName.value = p.display_name || "";
  } catch (err) {
    setAlert(errorBox, err.message || "Failed to load profile.");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlert(errorBox);
    clearAlert(successBox);

    const payload = { display_name: displayName.value.trim() };

    try {
      await API.auth.updateProfile(payload);
      setAlert(successBox, "Profile updated successfully.");
    } catch (err) {
      setAlert(errorBox, err.message || "Failed to update profile.");
    }
  });
});

