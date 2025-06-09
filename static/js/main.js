// Main JavaScript file for School Platform

// Global variables
let currentUser = null;
let notifications = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadNotifications();
});

// Initialize application
function initializeApp() {
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds (except for file display alerts)
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-warning):not(.alert-info)');
        alerts.forEach(function(alert) {
            // Skip alerts that are used for displaying files
            if (!alert.closest('.mb-4') || !alert.querySelector('[download]')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 5000);
}

// Setup event listeners
function setupEventListeners() {
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Auto-save for forms
    const autoSaveForms = document.querySelectorAll('.auto-save');
    autoSaveForms.forEach(function(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(function(input) {
            input.addEventListener('input', debounce(function() {
                autoSaveForm(form);
            }, 1000));
        });
    });
}

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search functionality
function handleSearch(event) {
    const query = event.target.value.toLowerCase();
    const searchableItems = document.querySelectorAll('.searchable');
    
    searchableItems.forEach(function(item) {
        const text = item.textContent.toLowerCase();
        if (text.includes(query)) {
            item.style.display = '';
            item.classList.add('search-highlight');
        } else {
            item.style.display = 'none';
            item.classList.remove('search-highlight');
        }
    });
}

// Theme toggle functionality
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update theme toggle icon
    const themeIcon = document.querySelector('#themeToggle i');
    if (themeIcon) {
        themeIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Auto-save form data
function autoSaveForm(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const formId = form.id || 'unnamed-form';
    
    localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
    
    // Show auto-save indicator
    showNotification('Draft saved automatically', 'info', 2000);
}

// Load auto-saved form data
function loadAutoSavedData(formId) {
    const savedData = localStorage.getItem(`autosave_${formId}`);
    if (savedData) {
        const data = JSON.parse(savedData);
        const form = document.getElementById(formId);
        
        if (form) {
            Object.keys(data).forEach(function(key) {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            });
        }
    }
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notificationContainer = getOrCreateNotificationContainer();
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-item`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    notificationContainer.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(function() {
        if (notification.parentNode) {
            const bsAlert = new bootstrap.Alert(notification);
            bsAlert.close();
        }
    }, duration);
}

function getOrCreateNotificationContainer() {
    let container = document.getElementById('notificationContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificationContainer';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

// Load notifications
function loadNotifications() {
    // This would typically fetch from an API
    // For now, we'll use mock data
    notifications = [
        {
            id: 1,
            message: 'Welcome to the School Platform!',
            type: 'info',
            timestamp: new Date()
        }
    ];
}

// Analytics tracking
function trackEvent(eventType, eventData) {
    const analyticsData = {
        event_type: eventType,
        event_data: eventData,
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent,
        url: window.location.href
    };
    
    // Send to analytics endpoint
    fetch('/api/track_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(analyticsData)
    }).catch(function(error) {
        console.log('Analytics tracking failed:', error);
    });
}

// Progress tracking for lessons and quizzes
function updateProgress(contentType, contentId, progress) {
    const progressData = {
        content_type: contentType,
        content_id: contentId,
        progress: progress,
        timestamp: new Date().toISOString()
    };
    
    fetch('/api/update_progress', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(progressData)
    }).catch(function(error) {
        console.log('Progress update failed:', error);
    });
}

// Quiz timer functionality
class QuizTimer {
    constructor(duration = null) {
        this.duration = duration; // in seconds, null for unlimited
        this.startTime = Date.now();
        this.timerElement = document.getElementById('timer');
        this.warningShown = false;
        
        if (this.timerElement) {
            this.start();
        }
    }
    
    start() {
        this.interval = setInterval(() => {
            this.update();
        }, 1000);
    }
    
    update() {
        const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
        
        if (this.duration) {
            const remaining = this.duration - elapsed;
            
            if (remaining <= 0) {
                this.timeUp();
                return;
            }
            
            if (remaining <= 300 && !this.warningShown) { // 5 minutes warning
                this.showTimeWarning();
                this.warningShown = true;
            }
            
            this.timerElement.textContent = this.formatTime(remaining);
            this.timerElement.className = remaining <= 60 ? 'text-danger' : '';
        } else {
            this.timerElement.textContent = this.formatTime(elapsed);
        }
    }
    
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
    
    showTimeWarning() {
        showNotification('Warning: 5 minutes remaining!', 'warning', 10000);
    }
    
    timeUp() {
        clearInterval(this.interval);
        showNotification('Time is up! Submitting quiz automatically.', 'danger');
        
        // Auto-submit quiz
        const quizForm = document.getElementById('quizForm');
        if (quizForm) {
            quizForm.submit();
        }
    }
    
    stop() {
        if (this.interval) {
            clearInterval(this.interval);
        }
    }
}

// File upload with progress
function uploadFile(file, progressCallback, successCallback, errorCallback) {
    const formData = new FormData();
    formData.append('file', file);
    
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            if (progressCallback) {
                progressCallback(percentComplete);
            }
        }
    });
    
    xhr.addEventListener('load', function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            if (successCallback) {
                successCallback(response);
            }
        } else {
            if (errorCallback) {
                errorCallback('Upload failed');
            }
        }
    });
    
    xhr.addEventListener('error', function() {
        if (errorCallback) {
            errorCallback('Upload error');
        }
    });
    
    xhr.open('POST', '/api/upload');
    xhr.send(formData);
}

// Utility functions
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

function formatTime(date) {
    return new Intl.DateTimeFormat('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

function formatDateTime(date) {
    return `${formatDate(date)} at ${formatTime(date)}`;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Copied to clipboard!', 'success', 2000);
    }).catch(function() {
        showNotification('Failed to copy to clipboard', 'danger', 3000);
    });
}

// Export functions for global use
window.SchoolPlatform = {
    showNotification,
    trackEvent,
    updateProgress,
    QuizTimer,
    uploadFile,
    formatDate,
    formatTime,
    formatDateTime,
    copyToClipboard,
    loadAutoSavedData
};

// Initialize theme from localStorage
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
        const themeIcon = document.querySelector('#themeToggle i');
        if (themeIcon) {
            themeIcon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
});
