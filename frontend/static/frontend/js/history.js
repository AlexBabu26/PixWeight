let allSessions = [];
let currentStatistics = null;

document.addEventListener("DOMContentLoaded", async () => {
  if (!requireAuthOrRedirect()) return;

  const errorBox = document.getElementById("errorBox");
  const body = document.getElementById("historyBody");
  const empty = document.getElementById("emptyState");
  
  const searchInput = document.getElementById("searchInput");
  const categoryFilter = document.getElementById("categoryFilter");
  const statusFilter = document.getElementById("statusFilter");
  const sortFilter = document.getElementById("sortFilter");
  const exportBtn = document.getElementById("exportBtn");

  // Load history with filters
  async function loadHistory() {
    try {
      // Build query params
      const params = new URLSearchParams();
      
      const search = searchInput.value.trim();
      if (search) params.append("search", search);
      
      const category = categoryFilter.value;
      if (category) params.append("category", category);
      
      const status = statusFilter.value;
      if (status) params.append("status", status);
      
      const sort = sortFilter.value;
      if (sort) params.append("sort_by", sort);
      
      const queryString = params.toString();
      const url = `/sessions/${queryString ? '?' + queryString : ''}`;
      
      const response = await API.request(url, { method: "GET" }, { auth: true });
      
      // Handle both old format (array) and new format (object with sessions + statistics)
      if (Array.isArray(response)) {
        allSessions = response;
        currentStatistics = null;
      } else {
        allSessions = response.sessions || [];
        currentStatistics = response.statistics || null;
      }
      
      body.innerHTML = "";
      empty.textContent = "";

      if (!allSessions || allSessions.length === 0) {
        empty.textContent = "No sessions found. Start a new estimation from the dashboard.";
        return;
      }

      allSessions.forEach(s => {
        const tr = document.createElement("tr");

        const dt = document.createElement("td");
        dt.textContent = new Date(s.created_at).toLocaleString();

        const obj = document.createElement("td");
        // Add category badge
        const category = s.object_json?.detected_category || 'general';
        const categoryBadge = `<span class="badge me-2 category-badge-${category}">${category}</span>`;
        obj.innerHTML = categoryBadge + (s.object_label || "(unlabeled)");

        const st = document.createElement("td");
        const statusBadge = getStatusBadge(s.status);
        st.innerHTML = statusBadge;

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
      
      // Update statistics if available
      if (currentStatistics) {
        updateStatistics(currentStatistics);
      }

    } catch (err) {
      setAlert(errorBox, err.message || "Failed to load history.");
    }
  }
  
  function getStatusBadge(status) {
    const badges = {
      'ESTIMATED': '<span class="badge bg-success">Completed</span>',
      'QUESTIONS_ASKED': '<span class="badge bg-warning">Pending</span>',
      'IN_PROGRESS': '<span class="badge bg-info">In Progress</span>',
      'FAILED': '<span class="badge bg-danger">Failed</span>'
    };
    return badges[status] || `<span class="badge bg-secondary">${status}</span>`;
  }
  
  function updateStatistics(stats) {
    const totalEl = document.getElementById("totalSessions");
    const completedEl = document.getElementById("completedSessions");
    const pendingEl = document.getElementById("pendingSessions");
    
    if (totalEl) totalEl.textContent = stats.total_sessions || '0';
    if (completedEl) completedEl.textContent = stats.completed_sessions || '0';
    if (pendingEl) pendingEl.textContent = stats.pending_sessions || '0';
  }

  // Event listeners for filters
  searchInput.addEventListener("input", () => {
    // Debounce search
    clearTimeout(searchInput.debounceTimer);
    searchInput.debounceTimer = setTimeout(loadHistory, 500);
  });
  
  categoryFilter.addEventListener("change", loadHistory);
  statusFilter.addEventListener("change", loadHistory);
  sortFilter.addEventListener("change", loadHistory);
  
  // Export button
  exportBtn.addEventListener("click", () => {
    if (allSessions.length === 0) {
      alert("No data to export");
      return;
    }
    
    const timestamp = new Date().toISOString().split('T')[0];
    exportHistoryToCSV(allSessions, `weight_estimates_${timestamp}.csv`);
  });

  // Initial load
  await loadHistory();
});

