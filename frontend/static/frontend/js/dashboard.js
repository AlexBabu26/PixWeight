document.addEventListener("DOMContentLoaded", () => {
  if (!requireAuthOrRedirect()) return;

  const form = document.getElementById("startForm");
  const errorBox = document.getElementById("errorBox");
  const infoBox = document.getElementById("infoBox");
  const loading = document.getElementById("loading");
  const btn = document.getElementById("btnStart");
  const uploadZone = document.getElementById("uploadZone");
  const imageInput = document.getElementById("imageInput");
  
  if (!form || !uploadZone || !imageInput) {
    console.error("Required elements not found");
    return;
  }
  
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

  // Click to upload - make sure it works even after preview is shown
  uploadZone.addEventListener('click', (e) => {
    // Don't trigger if clicking on the remove button or inside preview image
    if (e.target.closest('#removeImage') || e.target.tagName === 'IMG') {
      return;
    }
    // Get the current file input (might be recreated)
    const currentInput = document.getElementById('imageInput');
    if (currentInput) {
      currentInput.click();
    }
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

    // Ensure selectedFile is set
    selectedFile = file;
    console.log('File selected:', file.name, 'Size:', file.size, 'Type:', file.type);

    clearAlert(errorBox);

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
      showPreview(e.target.result, file.name);
    };
    reader.readAsDataURL(file);
  }

  function showPreview(dataUrl, filename) {
    // Keep the file input in the form but hidden
    const currentInput = document.getElementById('imageInput');
    
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
      <input type="file" name="image" accept="image/*" id="imageInput" style="position: absolute; opacity: 0; width: 0; height: 0; pointer-events: none;">
    `;

    // Re-attach file input change handler
    const newImageInput = document.getElementById('imageInput');
    if (newImageInput) {
      // Ensure it's part of the form
      if (!form.contains(newImageInput)) {
        form.appendChild(newImageInput);
      }
      
      // Remove required attribute since we validate manually
      newImageInput.removeAttribute('required');
      
      newImageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
          selectedFile = e.target.files[0];
          handleFileSelect(selectedFile);
        }
      });
    }

    document.getElementById('removeImage').addEventListener('click', (e) => {
      e.stopPropagation();
      resetUploadZone();
    });
  }

  function resetUploadZone() {
    selectedFile = null;
    const currentInput = document.getElementById('imageInput');
    if (currentInput) {
      currentInput.value = '';
    }
    
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
      <input class="form-control" type="file" name="image" accept="image/*" id="imageInput">
    `;
    
    // Re-attach event listeners after resetting
    const newImageInput = document.getElementById('imageInput');
    if (newImageInput) {
      // Add required attribute back
      newImageInput.setAttribute('required', 'required');
      
      newImageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
          selectedFile = e.target.files[0];
          handleFileSelect(selectedFile);
        }
      });
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlert(errorBox);
    clearAlert(infoBox);

    // Try to get file from selectedFile first (this should always be set when file is selected)
    let fileToUpload = selectedFile;
    
    // Debug logging (remove in production)
    console.log('Form submit - selectedFile:', selectedFile);
    
    // If selectedFile is not set, try to get from form
    if (!fileToUpload) {
      // Try multiple ways to access the file input
      const formImageInput = form.querySelector('input[name="image"]') || 
                             form.querySelector('#imageInput') ||
                             document.getElementById('imageInput');
      
      console.log('Form submit - formImageInput:', formImageInput);
      
      if (formImageInput && formImageInput.files && formImageInput.files.length > 0) {
        fileToUpload = formImageInput.files[0];
        console.log('Form submit - got file from input:', fileToUpload);
      }
    }

    if (!fileToUpload) {
      setAlert(errorBox, "Please select an image file.");
      console.error('No file found for upload');
      return;
    }

    // Validate file one more time
    if (!fileToUpload.type.startsWith('image/')) {
      setAlert(errorBox, "Please select a valid image file.");
      return;
    }

    const user_hint = (form.user_hint?.value || form.querySelector('input[name="user_hint"]')?.value || "").trim();

    btn.disabled = true;
    show(loading);
    setAlert(infoBox, "Uploading image and generating questions...");

    try {
      // 1) Upload image
      const uploadFd = new FormData();
      uploadFd.append("image", fileToUpload);

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
      console.error('Upload error:', err);
      setAlert(errorBox, err.message || "Failed to start session.");
      hide(loading);
      btn.disabled = false;
    }
  });
});

