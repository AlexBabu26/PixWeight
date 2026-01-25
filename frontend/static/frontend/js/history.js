document.addEventListener("DOMContentLoaded", async () => {
  if (!requireAuthOrRedirect()) return;

  const errorBox = document.getElementById("errorBox");
  const body = document.getElementById("historyBody");
  const empty = document.getElementById("emptyState");

  try {
    const sessions = await API.request("/sessions/", { method: "GET" }, { auth: true });

    body.innerHTML = "";
    empty.textContent = "";

    if (!sessions || sessions.length === 0) {
      empty.textContent = "No sessions found. Start a new estimation from the dashboard.";
      return;
    }

    sessions.forEach(s => {
      const tr = document.createElement("tr");

      const dt = document.createElement("td");
      dt.textContent = new Date(s.created_at).toLocaleString();

      const obj = document.createElement("td");
      obj.textContent = s.object_label || "(unlabeled)";

      const st = document.createElement("td");
      st.textContent = s.status;

      const act = document.createElement("td");
      act.className = "text-end";

      const link = document.createElement("a");
      link.className = "btn btn-sm btn-outline-primary";
      link.textContent = (s.status === "ESTIMATED") ? "View result" : "Continue";
      link.href = (s.status === "ESTIMATED")
        ? `/session/${s.id}/result/`
        : `/session/${s.id}/questions/`;

      act.appendChild(link);

      tr.appendChild(dt);
      tr.appendChild(obj);
      tr.appendChild(st);
      tr.appendChild(act);
      body.appendChild(tr);
    });

  } catch (err) {
    setAlert(errorBox, err.message || "Failed to load history.");
  }
});

