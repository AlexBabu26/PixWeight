document.addEventListener("DOMContentLoaded", () => {
  // If user is already authenticated, redirect to dashboard
  if (isAuthed()) {
    window.location.href = "/dashboard/";
  }
});

