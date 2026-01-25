document.addEventListener("DOMContentLoaded", async () => {
  if (!requireAuthOrRedirect()) return;

  const errorBox = document.getElementById("errorBox");
  const infoBox = document.getElementById("infoBox");
  const resultBox = document.getElementById("resultBox");
  const loading = document.getElementById("loading");
  const meta = document.getElementById("objectMeta");

  const estValue = document.getElementById("estValue");
  const estRange = document.getElementById("estRange");
  const estConfidence = document.getElementById("estConfidence");
  const estRationale = document.getElementById("estRationale");

  const btnQuestions = document.getElementById("btnQuestions");

  const parts = window.location.pathname.split("/");
  const sessionId = parts[2];

  btnQuestions.href = `/session/${sessionId}/questions/`;

  show(loading);

  function fmtKgFromG(g) {
    const kg = g / 1000.0;
    return (kg >= 1) ? `${kg.toFixed(2)} kg` : `${g.toFixed(0)} g`;
  }

  try {
    const session = await API.request(`/sessions/${sessionId}/`, { method: "GET" }, { auth: true });

    meta.textContent = session.object_label
      ? `${session.object_label} — ${session.object_summary || ""}`
      : (session.object_summary || "");

    if (!session.estimate) {
      setAlert(infoBox, "No estimate available yet. Please answer the questions.");
      hide(loading);
      return;
    }

    const e = session.estimate;

    estValue.textContent = fmtKgFromG(e.value_grams);
    estRange.textContent = `${fmtKgFromG(e.min_grams)} – ${fmtKgFromG(e.max_grams)}`;
    estConfidence.textContent = `${Math.round((e.confidence || 0) * 100)}%`;
    estRationale.textContent = e.rationale || "—";

    hide(loading);
    show(resultBox);

  } catch (err) {
    setAlert(errorBox, err.message || "Failed to load result.");
    hide(loading);
  }
});

