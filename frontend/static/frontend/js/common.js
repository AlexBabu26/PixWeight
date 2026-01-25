function isAuthed() {
  const t = API.tokens.get();
  return !!t.access && !!t.refresh;
}

function show(el) { el.classList.remove("d-none"); }
function hide(el) { el.classList.add("d-none"); }

function setAlert(box, message, type = "error") {
  if (!box) return;
  box.textContent = message;
  // Remove existing alert classes
  box.classList.remove("alert-danger", "alert-success", "alert-info", "alert-warning");
  // Add appropriate class
  if (type === "success") {
    box.classList.add("alert-success");
  } else if (type === "info") {
    box.classList.add("alert-info");
  } else if (type === "warning") {
    box.classList.add("alert-warning");
  } else {
    box.classList.add("alert-danger");
  }
  show(box);
}

function clearAlert(box) {
  if (!box) return;
  box.textContent = "";
  hide(box);
}

function updateNav() {
  const authed = isAuthed();
  
  // Force display style for auth-only elements
  document.querySelectorAll(".auth-only").forEach(el => {
    if (authed) {
      // Explicitly set display to override CSS .auth-only { display: none; }
      el.style.display = "block";
      el.classList.remove("d-none"); // Remove Bootstrap d-none if present
    } else {
      el.style.display = "none";
      el.classList.add("d-none");
    }
  });
  
  // Force display style for guest-only elements
  document.querySelectorAll(".guest-only").forEach(el => {
    if (authed) {
      el.style.display = "none";
      el.classList.add("d-none");
    } else {
      // Explicitly set display to override CSS .guest-only { display: none; }
      el.style.display = "block";
      el.classList.remove("d-none");
    }
  });
}

function requireAuthOrRedirect() {
  if (!isAuthed()) {
    window.location.href = "/login/";
    return false;
  }
  return true;
}

// Don't call updateNav here - wait for DOMContentLoaded and API to be ready

document.addEventListener("DOMContentLoaded", () => {
  // Wait a bit for API to be loaded
  setTimeout(() => {
    updateNav();
    
    // Update again after a short delay to ensure everything is ready
    setTimeout(updateNav, 100);
  }, 50);

  const btnLogout = document.getElementById("btnLogout");
  if (btnLogout) {
    btnLogout.addEventListener("click", () => {
      API.tokens.clear();
      updateNav();
      window.location.href = "/login/";
    });
  }

  // Update nav on token changes (e.g., after login)
  window.addEventListener("storage", () => {
    updateNav();
  });
});

// Also update nav when tokens might have changed
// Wait for API to be defined
(function() {
  function setupTokenWatcher() {
    if (typeof API !== "undefined" && API.tokens) {
      const originalSet = API.tokens.set;
      API.tokens.set = function(access, refresh) {
        originalSet.call(this, access, refresh);
        setTimeout(updateNav, 50);
      };
    } else {
      // Retry if API not ready yet
      setTimeout(setupTokenWatcher, 50);
    }
  }
  setupTokenWatcher();
})();

