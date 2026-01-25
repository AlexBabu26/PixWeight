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

  function renderWeightComparison(grams) {
    const best = getBestComparison(grams);
    if (!best) return "";
    
    return `
      <div class="card mt-4" style="background: linear-gradient(135deg, rgba(168, 85, 247, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%); border: 1px solid rgba(168, 85, 247, 0.15);">
        <div class="card-body p-4">
          <h2 class="h6 fw-bold mb-3">
            <svg class="me-2" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
            Weight Comparison
          </h2>
          <p class="mb-0">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">${best.icon}</span>
            <span class="text-muted">${formatComparisonText(best)}</span>
          </p>
        </div>
      </div>
    `;
  }

  function renderCategoryDetails(estimate) {
    const category = estimate.category || "general";
    let html = "";
    
    if (category === "food" && estimate.food_details) {
      const fd = estimate.food_details;
      html = `
        <div class="card mt-4" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(52, 211, 153, 0.05) 100%); border: 1px solid rgba(16, 185, 129, 0.15);">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold mb-3" style="color: #10b981;">
              <svg class="me-2" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
                <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"></path>
                <path d="M7 2v20"></path>
                <path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"></path>
              </svg>
              Nutrition Information
            </h2>
            <div class="row g-3">
              <div class="col-md-3">
                <div class="text-center p-3 rounded" style="background: rgba(16, 185, 129, 0.1);">
                  <div class="h3 fw-bold mb-1" style="color: #10b981;">${Math.round(fd.estimated_calories)}</div>
                  <div class="small text-muted">Calories</div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="text-center p-3 rounded" style="background: rgba(59, 130, 246, 0.1);">
                  <div class="h3 fw-bold mb-1" style="color: #3b82f6;">${fd.estimated_protein.toFixed(1)}g</div>
                  <div class="small text-muted">Protein</div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="text-center p-3 rounded" style="background: rgba(251, 191, 36, 0.1);">
                  <div class="h3 fw-bold mb-1" style="color: #fbbf24;">${fd.estimated_carbs.toFixed(1)}g</div>
                  <div class="small text-muted">Carbs</div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="text-center p-3 rounded" style="background: rgba(239, 68, 68, 0.1);">
                  <div class="h3 fw-bold mb-1" style="color: #ef4444;">${fd.estimated_fat.toFixed(1)}g</div>
                  <div class="small text-muted">Fat</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    } else if (category === "package" && estimate.package_details) {
      const pd = estimate.package_details;
      html = `
        <div class="card mt-4" style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 197, 253, 0.05) 100%); border: 1px solid rgba(59, 130, 246, 0.15);">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold mb-3" style="color: #3b82f6;">
              <svg class="me-2" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              </svg>
              Shipping Estimates
            </h2>
            <div class="mb-3">
              <div class="small text-muted mb-2">Dimensions: ${pd.length_cm} × ${pd.width_cm} × ${pd.height_cm} cm</div>
              ${pd.volumetric_weight_g ? `<div class="small text-muted mb-2">Volumetric Weight: ${(pd.volumetric_weight_g / 1000).toFixed(2)} kg</div>` : ''}
              <div class="small text-muted">Chargeable Weight: ${(pd.chargeable_weight_g / 1000).toFixed(2)} kg</div>
            </div>
            <table class="table table-sm">
              <thead>
                <tr>
                  <th>Carrier & Service</th>
                  <th class="text-end">Estimated Cost</th>
                </tr>
              </thead>
              <tbody>
                ${Object.entries(pd.estimated_shipping_costs || {}).map(([carrier, cost]) => `
                  <tr>
                    <td>${carrier}</td>
                    <td class="text-end">$${cost.toFixed(2)}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
      `;
    } else if (category === "pet" && estimate.pet_details) {
      const pd = estimate.pet_details;
      const statusColors = {
        healthy: '#10b981',
        slightly_underweight: '#fbbf24',
        slightly_overweight: '#fb923c',
        underweight: '#ef4444',
        overweight: '#dc2626'
      };
      const statusColor = statusColors[pd.health_status] || '#6b7280';
      
      html = `
        <div class="card mt-4" style="background: linear-gradient(135deg, rgba(251, 146, 60, 0.05) 0%, rgba(251, 191, 36, 0.05) 100%); border: 1px solid rgba(251, 146, 60, 0.15);">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold mb-3" style="color: #fb923c;">
              <svg class="me-2" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fb923c" stroke-width="2">
                <circle cx="12" cy="4" r="2"></circle>
                <path d="M10.2 3.2C9.5 2 8 2 6.5 2c-2 0-3 1.5-3 3.5S3.5 9 5.5 9c.6 0 1.2-.1 1.6-.3"></path>
                <path d="M13.8 3.2c.7-1.2 2.2-1.2 3.7-1.2c2 0 3 1.5 3 3.5S19.5 9 17.5 9c-.6 0-1.2-.1-1.6-.3"></path>
                <path d="M12 9v13"></path>
                <path d="M6.5 20h11"></path>
              </svg>
              Pet Health Assessment
            </h2>
            <div class="mb-3">
              <div class="fw-semibold mb-1">${pd.species.charAt(0).toUpperCase() + pd.species.slice(1)}${pd.breed ? ` - ${pd.breed}` : ''}</div>
              <div class="d-flex align-items-center gap-2 mb-2">
                <span class="badge" style="background-color: ${statusColor};">${pd.health_status.replace(/_/g, ' ').toUpperCase()}</span>
                <span class="small text-muted">${pd.age_category}</span>
              </div>
              ${pd.ideal_weight_min && pd.ideal_weight_max ? `
                <div class="small text-muted">Ideal Range: ${pd.ideal_weight_min} - ${pd.ideal_weight_max} kg</div>
              ` : ''}
            </div>
            <div class="alert alert-info mb-0" style="border-left: 4px solid ${statusColor};">
              <small>${pd.weight_recommendation}</small>
            </div>
          </div>
        </div>
      `;
    } else if (category === "person" && estimate.body_details) {
      const bd = estimate.body_details;
      html = `
        <div class="card mt-4" style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(167, 139, 250, 0.05) 100%); border: 1px solid rgba(139, 92, 246, 0.15);">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold mb-3" style="color: #8b5cf6;">
              <svg class="me-2" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              BMI & Body Composition
            </h2>
            <div class="row g-3 mb-3">
              <div class="col-md-4">
                <div class="text-center p-3 rounded" style="background: rgba(139, 92, 246, 0.1);">
                  <div class="h3 fw-bold mb-1" style="color: #8b5cf6;">${bd.bmi.toFixed(1)}</div>
                  <div class="small text-muted">BMI</div>
                  <div class="small fw-semibold">${bd.bmi_category}</div>
                </div>
              </div>
              <div class="col-md-4">
                <div class="text-center p-3 rounded" style="background: rgba(16, 185, 129, 0.1);">
                  <div class="h3 fw-bold mb-1" style="color: #10b981;">${bd.height_cm} cm</div>
                  <div class="small text-muted">Height</div>
                </div>
              </div>
              <div class="col-md-4">
                <div class="text-center p-3 rounded" style="background: rgba(251, 191, 36, 0.1);">
                  <div class="h3 fw-bold mb-1" style="color: #fbbf24;">${bd.ideal_weight_min_kg.toFixed(1)}-${bd.ideal_weight_max_kg.toFixed(1)}kg</div>
                  <div class="small text-muted">Ideal Range</div>
                </div>
              </div>
            </div>
            ${bd.body_fat_estimate ? `
              <div class="mb-3">
                <div class="small text-muted mb-1">Estimated Body Fat: ${bd.body_fat_estimate}%</div>
                ${bd.lean_mass_estimate ? `<div class="small text-muted">Estimated Lean Mass: ${bd.lean_mass_estimate}kg</div>` : ''}
              </div>
            ` : ''}
            <div class="alert alert-warning mb-0">
              <small><strong>⚠️ Disclaimer:</strong> ${bd.health_recommendation}</small>
            </div>
          </div>
        </div>
      `;
    }
    
    return html;
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

    // Add weight comparison
    const comparisonHtml = renderWeightComparison(e.value_grams);
    if (comparisonHtml) {
      const rationaleCard = document.querySelector('.card-body .h6.fw-bold').closest('.card');
      rationaleCard.insertAdjacentHTML('afterend', comparisonHtml);
    }

    // Add category-specific details
    const categoryHtml = renderCategoryDetails(e);
    if (categoryHtml) {
      const rationaleCard = document.querySelector('.card-body .h6.fw-bold').closest('.card');
      rationaleCard.insertAdjacentHTML('afterend', categoryHtml);
    }

    hide(loading);
    show(resultBox);

    // Setup feedback form
    setupFeedbackForm(e.id);

  } catch (err) {
    setAlert(errorBox, err.message || "Failed to load result.");
    hide(loading);
  }
});

function setupFeedbackForm(estimateId) {
  let selectedRating = null;
  
  // Rating button selection
  document.querySelectorAll('.rating-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      // Remove active class from all buttons
      document.querySelectorAll('.rating-btn').forEach(b => {
        b.classList.remove('btn-primary');
        b.classList.add('btn-outline-secondary');
      });
      
      // Add active class to clicked button
      this.classList.remove('btn-outline-secondary');
      this.classList.add('btn-primary');
      
      selectedRating = parseInt(this.getAttribute('data-rating'));
    });
  });
  
  // Submit feedback
  document.getElementById('submitFeedback').addEventListener('click', async function() {
    const actualWeight = parseFloat(document.getElementById('actualWeight').value);
    const notes = document.getElementById('feedbackNotes').value.trim();
    
    if (!actualWeight || actualWeight <= 0) {
      document.getElementById('feedbackErrorText').textContent = "Please enter a valid actual weight.";
      show(document.getElementById('feedbackError'));
      return;
    }
    
    hide(document.getElementById('feedbackError'));
    this.disabled = true;
    this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';
    
    try {
      await API.request(`/estimates/${estimateId}/feedback/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          actual_weight_grams: actualWeight,
          accuracy_rating: selectedRating,
          user_notes: notes,
          helpful: true
        })
      }, { auth: true });
      
      // Show success message
      hide(document.getElementById('feedbackForm'));
      show(document.getElementById('feedbackSuccess'));
      
    } catch (err) {
      document.getElementById('feedbackErrorText').textContent = err.message || "Failed to submit feedback.";
      show(document.getElementById('feedbackError'));
      this.disabled = false;
      this.innerHTML = 'Submit Feedback';
    }
  });
  
  // Check if feedback already exists
  API.request(`/estimates/${estimateId}/feedback/get/`, {
    method: 'GET'
  }, { auth: true }).then(() => {
    // Feedback exists, show success message
    hide(document.getElementById('feedbackForm'));
    show(document.getElementById('feedbackSuccess'));
  }).catch(() => {
    // No feedback yet, keep form visible
  });
}

