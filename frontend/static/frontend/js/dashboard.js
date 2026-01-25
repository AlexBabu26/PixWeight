document.addEventListener("DOMContentLoaded", () => {
  if (!requireAuthOrRedirect()) return;

  const form = document.getElementById("startForm");
  const errorBox = document.getElementById("errorBox");
  const infoBox = document.getElementById("infoBox");
  const loading = document.getElementById("loading");
  const btn = document.getElementById("btnStart");
  const uploadZone = document.getElementById("uploadZone");
  const imageInput = document.getElementById("imageInput");
  
  let selectedFile = null;

  // Drag and drop functionality
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadZone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ['dragenter', 'dragover'].forEach(eventName => {
    uploadZone.addEventListener(eventName, () => {
      uploadZone.classList.add('drag-over');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    uploadZone.addEventListener(eventName, () => {
      uploadZone.classList.remove('drag-over');
    }, false);
  });

  uploadZone.addEventListener('drop', handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
      selectedFile = files[0];
      handleFileSelect(selectedFile);
    }
  }

  // Click to upload
  uploadZone.addEventListener('click', () => {
    imageInput.click();
  });

  imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      selectedFile = e.target.files[0];
      handleFileSelect(selectedFile);
    }
  });

  function handleFileSelect(file) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      setAlert(errorBox, 'Please select an image file.');
      return;
    }

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      setAlert(errorBox, 'File size must be less than 10MB.');
      return;
    }

    clearAlert(errorBox);

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
      showPreview(e.target.result, file.name);
    };
    reader.readAsDataURL(file);
  }

  function showPreview(dataUrl, filename) {
    uploadZone.innerHTML = `
      <div class="image-preview">
        <img src="${dataUrl}" alt="Preview" style="max-width: 100%; max-height: 200px; border-radius: 8px; margin-bottom: 1rem;">
        <div class="d-flex align-items-center justify-content-between">
          <span class="small text-muted">${filename}</span>
          <button type="button" class="btn btn-sm btn-outline-danger" id="removeImage">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
            Remove
          </button>
        </div>
      </div>
    `;

    document.getElementById('removeImage').addEventListener('click', (e) => {
      e.stopPropagation();
      resetUploadZone();
    });
  }

  function resetUploadZone() {
    selectedFile = null;
    imageInput.value = '';
    uploadZone.innerHTML = `
      <div class="upload-icon mx-auto">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
      </div>
      <h5 class="fw-semibold mt-3 mb-1">Drop your image here</h5>
      <p class="text-muted mb-3">or click to browse from your device</p>
      <input class="form-control" type="file" name="image" accept="image/*" required id="imageInput">
    `;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlert(errorBox);
    clearAlert(infoBox);

    if (!selectedFile) {
      setAlert(errorBox, "Please select an image file.");
      return;
    }

    const user_hint = (form.user_hint.value || "").trim();

    btn.disabled = true;
    show(loading);
    setAlert(infoBox, "Uploading image and generating questions...");

    try {
      // 1) Upload image
      const uploadFd = new FormData();
      uploadFd.append("image", selectedFile);

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

