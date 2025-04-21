/**
 * Main JavaScript file for PyCAM - Photo Editor
 * Contains all the specific functionality for the photo editing application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the photo editor features
    initializePhotoEditor();

    // Initialize gallery functions
    initializeGallery();

    // Add event listeners for photo upload
    setupPhotoUpload();
});

/**
 * Initialize the photo editor features
 */
function initializePhotoEditor() {
    const editorCanvas = document.getElementById('editor-canvas');
    if (!editorCanvas) return;

    const applyEffectButtons = document.querySelectorAll('.effect-button');
    const saveButton = document.getElementById('save-button');
    const resetButton = document.getElementById('reset-button');
    const intensitySlider = document.getElementById('intensity-slider');

    let currentImage = null;
    let originalImage = null;
    let currentEffect = '';

    // Effect application
    applyEffectButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            applyEffectButtons.forEach(btn => btn.classList.remove('active'));

            // Add active class to clicked button
            this.classList.add('active');

            // Get effect name
            currentEffect = this.getAttribute('data-effect');

            // Update hidden input for effect
            const effectInput = document.getElementById('effect-applied');
            if (effectInput) {
                effectInput.value = currentEffect;
            }

            // Apply the effect if an image is loaded
            if (currentImage) {
                applyEffect(currentEffect);
            }
        });
    });

    // Intensity slider
    if (intensitySlider) {
        intensitySlider.addEventListener('input', function() {
            // Only apply if we have an image and an effect selected
            if (currentImage && currentEffect) {
                applyEffect(currentEffect, this.value);
            }
        });
    }

    // Reset button
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            if (originalImage) {
                currentImage = originalImage.cloneNode(true);
                displayImage(currentImage);

                // Reset effect selection
                applyEffectButtons.forEach(btn => btn.classList.remove('active'));
                currentEffect = '';

                // Reset intensity slider
                if (intensitySlider) {
                    intensitySlider.value = 50;
                }

                // Reset hidden input
                const effectInput = document.getElementById('effect-applied');
                if (effectInput) {
                    effectInput.value = '';
                }
            }
        });
    }

    // Helper function to apply an effect to the image
    function applyEffect(effect, intensity = 50) {
        // In a real implementation, this would call an AJAX endpoint
        // Here we'll simulate by showing a loading indicator

        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }

        // Prepare form data
        const formData = new FormData();
        formData.append('effect', effect);
        formData.append('intensity', intensity);

        // Get the image data URL from the canvas
        const canvas = document.createElement('canvas');
        canvas.width = currentImage.naturalWidth;
        canvas.height = currentImage.naturalHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(currentImage, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg', 0.9);

        formData.append('image', imageData);

        // Send request to the server
        fetch('/apply-effect/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken()
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Load the processed image
                const newImage = new Image();
                newImage.onload = function() {
                    currentImage = newImage;
                    displayImage(currentImage);

                    if (loadingIndicator) {
                        loadingIndicator.style.display = 'none';
                    }
                };
                newImage.src = data.image;
            } else {
                console.error('Error applying effect:', data.message);
                if (loadingIndicator) {
                    loadingIndicator.style.display = 'none';
                }

                // Show error notification
                showNotification('Error applying effect: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }

            // Show error notification
            showNotification('Network error. Please try again.', 'error');
        });
    }

    // Helper function to display an image on the canvas
    function displayImage(image) {
        const canvas = editorCanvas;
        const ctx = canvas.getContext('2d');

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Resize canvas to match image aspect ratio
        const maxWidth = canvas.parentElement.clientWidth;
        const maxHeight = 500; // Maximum height for the editor

        let width = image.naturalWidth;
        let height = image.naturalHeight;

        // Scale down if image is larger than available space
        if (width > maxWidth || height > maxHeight) {
            const ratioWidth = maxWidth / width;
            const ratioHeight = maxHeight / height;
            const ratio = Math.min(ratioWidth, ratioHeight);

            width = width * ratio;
            height = height * ratio;
        }

        canvas.width = width;
        canvas.height = height;

        // Draw image
        ctx.drawImage(image, 0, 0, width, height);
    }
}

/**
 * Initialize gallery functionality
 */
function initializeGallery() {
    const gallery = document.querySelector('.image-gallery');
    if (!gallery) return;

    // Delete image functionality
    const deleteButtons = document.querySelectorAll('.delete-image-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            if (confirm('Are you sure you want to delete this image?')) {
                const imageId = this.getAttribute('data-image-id');

                fetch(`/delete/${imageId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCsrfToken()
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove the image card from the gallery
                        const imageCard = this.closest('.image-card');
                        imageCard.remove();

                        showNotification('Image deleted successfully', 'success');
                    } else {
                        showNotification('Error deleting image: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Network error. Please try again.', 'error');
                });
            }
        });
    });

    // Share image functionality
    const shareButtons = document.querySelectorAll('.share-image-btn');
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            const imageId = this.getAttribute('data-image-id');

            fetch(`/share/${imageId}/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Create a temporary input to copy the URL
                    const tempInput = document.createElement('input');
                    tempInput.value = data.url;
                    document.body.appendChild(tempInput);
                    tempInput.select();
                    document.execCommand('copy');
                    document.body.removeChild(tempInput);

                    showNotification('Share link copied to clipboard', 'success');
                } else {
                    showNotification('Error sharing image: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Network error. Please try again.', 'error');
            });
        });
    });
}

/**
 * Set up photo upload functionality
 */
function setupPhotoUpload() {
    const uploadForm = document.getElementById('upload-form');
    const imageUpload = document.getElementById('image-upload');
    const previewArea = document.getElementById('image-preview');
    const editorCanvas = document.getElementById('editor-canvas');

    if (!uploadForm || !imageUpload) return;

    imageUpload.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const file = this.files[0];

            // Check if file is an image
            if (!file.type.match('image.*')) {
                showNotification('Please select an image file (JPEG, PNG, GIF)', 'error');
                return;
            }

            // Display preview
            const reader = new FileReader();
            reader.onload = function(e) {
                if (previewArea) {
                    previewArea.innerHTML = '';
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'preview-image';
                    previewArea.appendChild(img);
                }

                // If we have an editor canvas, load the image there too
                if (editorCanvas) {
                    const img = new Image();
                    img.onload = function() {
                        originalImage = img;
                        currentImage = img.cloneNode(true);
                        displayImage(currentImage);
                    };
                    img.src = e.target.result;
                }
            };
            reader.readAsDataURL(file);

            // Enable the editor section
            const editorSection = document.querySelector('.editor-section');
            if (editorSection) {
                editorSection.classList.remove('disabled');
            }
        }
    });

    // Optionally handle form submission via AJAX
    uploadForm.addEventListener('submit', function(e) {
        // Check if we're in edit mode with the canvas
        if (editorCanvas && currentEffect) {
            e.preventDefault();

            // Save the edited image
            saveEditedImage();
        }
    });

    // Helper function to display an image on the canvas
    function displayImage(image) {
        const canvas = editorCanvas;
        const ctx = canvas.getContext('2d');

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Resize canvas to match image aspect ratio
        const maxWidth = canvas.parentElement.clientWidth;
        const maxHeight = 500; // Maximum height for the editor

        let width = image.naturalWidth;
        let height = image.naturalHeight;

        // Scale down if image is larger than available space
        if (width > maxWidth || height > maxHeight) {
            const ratioWidth = maxWidth / width;
            const ratioHeight = maxHeight / height;
            const ratio = Math.min(ratioWidth, ratioHeight);

            width = width * ratio;
            height = height * ratio;
        }

        canvas.width = width;
        canvas.height = height;

        // Draw image
        ctx.drawImage(image, 0, 0, width, height);
    }

    // Function to save the edited image
    function saveEditedImage() {
        const canvas = editorCanvas;
        const imageData = canvas.toDataURL('image/jpeg', 0.9);

        const formData = new FormData(uploadForm);
        formData.append('image', imageData);
        formData.append('effect_applied', currentEffect);

        fetch('/save/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken()
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Image saved successfully', 'success');
                // Redirect to home page after a short delay
                setTimeout(() => {
                    window.location.href = '/home/';
                }, 1500);
            } else {
                showNotification('Error saving image: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Network error. Please try again.', 'error');
        });
    }
}

/**
 * Helper function to display notifications
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    // Add close button
    const closeButton = document.createElement('span');
    closeButton.className = 'notification-close';
    closeButton.innerHTML = '&times;';
    closeButton.addEventListener('click', function() {
        notification.remove();
    });

    notification.appendChild(closeButton);
    document.body.appendChild(notification);

    // Position the notification
    notification.style.bottom = '20px';
    notification.style.right = '20px';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        notification.classList.add('hiding');
        setTimeout(() => {
            notification.remove();
        }, 500); // Matches the CSS transition duration
    }, 5000);
}

/**
 * Helper function to get CSRF token from cookies
 */
function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.substring('csrftoken='.length, cookie.length);
        }
    }
    return '';
}
