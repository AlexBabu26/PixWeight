document.addEventListener("DOMContentLoaded", () => {
  if (!requireAuthOrRedirect()) return;

  const form = document.getElementById("startForm");
  const errorBox = document.getElementById("errorBox");
  const infoBox = document.getElementById("infoBox");
  const loading = document.getElementById("loading");
  const btn = document.getElementById("btnStart");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlert(errorBox);
    clearAlert(infoBox);

    const fd = new FormData(form);
    const file = fd.get("image");
    const user_hint = (fd.get("user_hint") || "").trim();

    if (!file || !file.name) {
      setAlert(errorBox, "Please select an image file.");
      return;
    }

    btn.disabled = true;
    show(loading);
    setAlert(infoBox, "Uploading image and generating questions...");

    try {
      // 1) Upload image
      const uploadFd = new FormData();
      uploadFd.append("image", file);

      const uploaded = await API.request("/media/upload/", {
        method: "POST",
        body: uploadFd
      }, { auth: true });

      // 2) Create session from image
      const session = await API.request("/sessions/from-image/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_id: uploaded.id, user_hint })
      }, { auth: true });

      window.location.href = `/session/${session.id}/questions/`;
    } catch (err) {
      setAlert(errorBox, err.message || "Failed to start session.");
      hide(loading);
      btn.disabled = false;
    }
  });
});

