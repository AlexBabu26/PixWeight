document.addEventListener("DOMContentLoaded", async () => {
  if (!requireAuthOrRedirect()) return;

  const errorBox = document.getElementById("errorBox");
  const infoBox = document.getElementById("infoBox");
  const container = document.getElementById("questionsContainer");
  const meta = document.getElementById("objectMeta");
  const form = document.getElementById("questionsForm");
  const loading = document.getElementById("loading");
  const btn = document.getElementById("btnSubmit");

  const parts = window.location.pathname.split("/");
  const sessionId = parts[2];

  function renderQuestion(q) {
    const wrap = document.createElement("div");
    wrap.className = "mb-3";

    const label = document.createElement("label");
    label.className = "form-label";
    label.textContent = q.text + (q.required ? " *" : "");
    wrap.appendChild(label);

    let input;

    if (q.answer_type === "number") {
      input = document.createElement("input");
      input.type = "number";
      input.step = "any";
      input.className = "form-control";
      input.dataset.qid = q.id;
      input.dataset.type = "number";
      input.placeholder = q.unit ? `Unit: ${q.unit}` : "";
    } else if (q.answer_type === "boolean") {
      input = document.createElement("select");
      input.className = "form-select";
      input.dataset.qid = q.id;
      input.dataset.type = "boolean";

      const opt0 = document.createElement("option");
      opt0.value = "";
      opt0.textContent = "Select...";
      input.appendChild(opt0);

      const opt1 = document.createElement("option");
      opt1.value = "true";
      opt1.textContent = "Yes / True";
      input.appendChild(opt1);

      const opt2 = document.createElement("option");
      opt2.value = "false";
      opt2.textContent = "No / False";
      input.appendChild(opt2);

    } else if (q.answer_type === "select") {
      input = document.createElement("select");
      input.className = "form-select";
      input.dataset.qid = q.id;
      input.dataset.type = "select";

      const opt0 = document.createElement("option");
      opt0.value = "";
      opt0.textContent = "Select...";
      input.appendChild(opt0);

      (q.options || []).forEach(v => {
        const opt = document.createElement("option");
        opt.value = v;
        opt.textContent = v;
        input.appendChild(opt);
      });
    } else {
      input = document.createElement("input");
      input.type = "text";
      input.className = "form-control";
      input.dataset.qid = q.id;
      input.dataset.type = "text";
      input.placeholder = q.unit ? `Unit: ${q.unit}` : "";
    }

    if (q.required) input.required = true;

    wrap.appendChild(input);

    if (q.unit) {
      const help = document.createElement("div");
      help.className = "form-text";
      help.textContent = `Unit: ${q.unit}`;
      wrap.appendChild(help);
    }

    return wrap;
  }

  try {
    const session = await API.request(`/sessions/${sessionId}/`, { method: "GET" }, { auth: true });

    meta.textContent = session.object_label
      ? `${session.object_label} — ${session.object_summary || ""}`
      : (session.object_summary || "");

    container.innerHTML = "";
    if (!session.questions || session.questions.length === 0) {
      setAlert(infoBox, "No questions were generated for this session.");
      btn.disabled = true;
      return;
    }

    session.questions.forEach(q => container.appendChild(renderQuestion(q)));
  } catch (err) {
    setAlert(errorBox, err.message || "Failed to load session.");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlert(errorBox);
    clearAlert(infoBox);

    btn.disabled = true;
    show(loading);

    const inputs = container.querySelectorAll("[data-qid]");
    const answers = [];

    inputs.forEach(inp => {
      const qid = inp.dataset.qid;
      const type = inp.dataset.type;
      const raw = (inp.value || "").trim();

      if (raw === "") return;

      let value = raw;
      if (type === "number") value = Number(raw);
      if (type === "boolean") value = (raw.toLowerCase() === "true");

      answers.push({ question_id: qid, value });
    });

    try {
      const resp = await API.request(`/sessions/${sessionId}/answers/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers })
      }, { auth: true });

      if (resp.estimate) {
        window.location.href = `/session/${sessionId}/result/`;
        return;
      }

      setAlert(infoBox, resp.detail || "Answers saved.");
      hide(loading);
      btn.disabled = false;

    } catch (err) {
      setAlert(errorBox, err.message || "Failed to submit answers.");
      hide(loading);
      btn.disabled = false;
    }
  });
});

