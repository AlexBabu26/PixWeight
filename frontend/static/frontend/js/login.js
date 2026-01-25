document.addEventListener("DOMContentLoaded", () => {
  // Redirect if already authenticated
  if (isAuthed()) {
    window.location.href = "/dashboard/";
    return;
  }

  // DOM Elements - Login Form
  const loginForm = document.getElementById("loginForm");
  const errorBox = document.getElementById("errorBox");
  const successBox = document.getElementById("successBox");
  const btnLogin = document.getElementById("btnLogin");
  const forgotPasswordLink = document.getElementById("forgotPasswordLink");
  
  // DOM Elements - Custom Modal
  const modalOverlay = document.getElementById("forgotPasswordOverlay");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const backToLoginLink = document.getElementById("backToLoginLink");
  const modalTitleText = document.getElementById("modalTitleText");
  const modalFooter = document.getElementById("modalFooter");
  
  // DOM Elements - Step 1: Find Account
  const stepFindAccount = document.getElementById("stepFindAccount");
  const forgotPasswordForm = document.getElementById("forgotPasswordForm");
  const forgotErrorBox = document.getElementById("forgotErrorBox");
  const forgotSuccessBox = document.getElementById("forgotSuccessBox");
  const btnFindAccount = document.getElementById("btnFindAccount");
  
  // DOM Elements - Step 2: Reset Password
  const stepResetPassword = document.getElementById("stepResetPassword");
  const resetPasswordForm = document.getElementById("resetPasswordForm");
  const resetUsername = document.getElementById("resetUsername");
  const foundUsername = document.getElementById("foundUsername");
  const foundEmail = document.getElementById("foundEmail");
  const foundEmailRow = document.getElementById("foundEmailRow");
  const btnResetPassword = document.getElementById("btnResetPassword");
  const btnBackToFind = document.getElementById("btnBackToFind");

  // =========================================================================
  // Custom Modal Functions
  // =========================================================================
  
  function openModal() {
    document.body.classList.add("custom-modal-open");
    resetModalToStep1();
    modalOverlay.classList.add("active");
    
    setTimeout(() => {
      const input = document.getElementById("forgotIdentifier");
      if (input) input.focus();
    }, 300);
  }
  
  function closeModal() {
    modalOverlay.classList.remove("active");
    setTimeout(() => {
      document.body.classList.remove("custom-modal-open");
      resetModalToStep1();
    }, 250);
  }
  
  function resetModalToStep1() {
    // Clear alerts
    clearAlert(forgotErrorBox);
    clearAlert(forgotSuccessBox);
    
    // Reset forms
    forgotPasswordForm.reset();
    resetPasswordForm.reset();
    
    // Show step 1, hide step 2
    stepFindAccount.classList.remove("d-none");
    stepResetPassword.classList.add("d-none");
    
    // Reset title and footer
    modalTitleText.textContent = "Forgot Password";
    modalFooter.classList.remove("d-none");
    
    // Reset buttons
    btnFindAccount.disabled = false;
    btnFindAccount.innerHTML = `
      <svg class="me-2" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
      Find Account
    `;
  }
  
  function showStep2(username, maskedEmail) {
    // Clear alerts
    clearAlert(forgotErrorBox);
    clearAlert(forgotSuccessBox);
    
    // Update found user info
    resetUsername.value = username;
    foundUsername.textContent = username;
    
    if (maskedEmail) {
      foundEmail.textContent = maskedEmail;
      foundEmailRow.classList.remove("d-none");
    } else {
      foundEmailRow.classList.add("d-none");
    }
    
    // Hide step 1, show step 2
    stepFindAccount.classList.add("d-none");
    stepResetPassword.classList.remove("d-none");
    
    // Update title and hide footer
    modalTitleText.textContent = "Reset Password";
    modalFooter.classList.add("d-none");
    
    // Focus on new password field
    setTimeout(() => {
      document.getElementById("newPassword").focus();
    }, 100);
  }

  // =========================================================================
  // Login Form Handler
  // =========================================================================
  
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlert(errorBox);
    clearAlert(successBox);

    const fd = new FormData(loginForm);
    const username = (fd.get("username") || "").trim();
    const password = fd.get("password");

    if (!username || !password) {
      setAlert(errorBox, "Please enter both username and password.");
      return;
    }

    btnLogin.disabled = true;
    const originalText = btnLogin.innerHTML;
    btnLogin.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Signing in...';

    try {
      await API.auth.login(username, password);
      setAlert(successBox, "Login successful! Redirecting...", "success");
      
      setTimeout(() => {
        window.location.href = "/dashboard/";
      }, 1000);
    } catch (err) {
      setAlert(errorBox, err.message || "Invalid username or password.");
      btnLogin.disabled = false;
      btnLogin.innerHTML = originalText;
    }
  });

  // =========================================================================
  // Modal Event Listeners
  // =========================================================================
  
  forgotPasswordLink.addEventListener("click", (e) => {
    e.preventDefault();
    openModal();
  });
  
  closeModalBtn.addEventListener("click", (e) => {
    e.preventDefault();
    closeModal();
  });
  
  backToLoginLink.addEventListener("click", (e) => {
    e.preventDefault();
    closeModal();
  });
  
  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) {
      closeModal();
    }
  });
  
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modalOverlay.classList.contains("active")) {
      closeModal();
    }
  });
  
  // Back button in step 2
  btnBackToFind.addEventListener("click", (e) => {
    e.preventDefault();
    resetModalToStep1();
  });

  // =========================================================================
  // Step 1: Find Account Handler
  // =========================================================================
  
  forgotPasswordForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlert(forgotErrorBox);
    clearAlert(forgotSuccessBox);

    const fd = new FormData(forgotPasswordForm);
    const identifier = (fd.get("identifier") || "").trim();

    if (!identifier) {
      setAlert(forgotErrorBox, "Please enter your username or email.");
      return;
    }

    btnFindAccount.disabled = true;
    const originalText = btnFindAccount.innerHTML;
    btnFindAccount.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Searching...';

    try {
      const response = await API.auth.forgotPassword(identifier);
      
      if (response.found) {
        // Account found - show step 2
        showStep2(response.username, response.masked_email);
      } else {
        // Account not found
        setAlert(forgotErrorBox, response.message || "No account found with this username or email.");
      }
      
      btnFindAccount.disabled = false;
      btnFindAccount.innerHTML = originalText;
    } catch (err) {
      const errorMsg = err.data?.error || err.message || "An error occurred. Please try again.";
      setAlert(forgotErrorBox, errorMsg);
      btnFindAccount.disabled = false;
      btnFindAccount.innerHTML = originalText;
    }
  });

  // =========================================================================
  // Step 2: Reset Password Handler
  // =========================================================================
  
  resetPasswordForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlert(forgotErrorBox);
    clearAlert(forgotSuccessBox);

    const username = resetUsername.value;
    const newPassword = document.getElementById("newPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    // Validation
    if (!newPassword) {
      setAlert(forgotErrorBox, "Please enter a new password.");
      return;
    }
    
    if (newPassword.length < 8) {
      setAlert(forgotErrorBox, "Password must be at least 8 characters long.");
      return;
    }
    
    if (newPassword !== confirmPassword) {
      setAlert(forgotErrorBox, "Passwords do not match.");
      return;
    }

    btnResetPassword.disabled = true;
    const originalText = btnResetPassword.innerHTML;
    btnResetPassword.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Resetting...';

    try {
      const response = await API.auth.resetPassword(username, newPassword, confirmPassword);
      
      if (response.success) {
        setAlert(forgotSuccessBox, response.message || "Password reset successfully!", "success");
        
        // Close modal and redirect to login after 2 seconds
        setTimeout(() => {
          closeModal();
          // Show success on main page
          setAlert(successBox, "Password reset successfully! Please log in with your new password.", "success");
        }, 2000);
      } else {
        setAlert(forgotErrorBox, response.message || "Failed to reset password.");
        btnResetPassword.disabled = false;
        btnResetPassword.innerHTML = originalText;
      }
    } catch (err) {
      const errorMsg = err.data?.error || err.message || "An error occurred. Please try again.";
      setAlert(forgotErrorBox, errorMsg);
      btnResetPassword.disabled = false;
      btnResetPassword.innerHTML = originalText;
    }
  });
});
