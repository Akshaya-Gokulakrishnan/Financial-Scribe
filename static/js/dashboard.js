// Dashboard JavaScript functionality

// Global variables
let refreshInterval;
let isRefreshing = false;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded');
    
    // Set up auto-refresh every 5 minutes
    refreshInterval = setInterval(refreshPortfolio, 300000); // 5 minutes
    
    // Add event listeners
    setupEventListeners();
    
    // Update timestamps
    updateTimestamps();
});

function setupEventListeners() {
    // Refresh button click handler
    const refreshBtn = document.querySelector('button[onclick="refreshPortfolio()"]');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function(e) {
            e.preventDefault();
            refreshPortfolio();
        });
    }
    
    // Add tooltips to elements
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function refreshPortfolio() {
    if (isRefreshing) {
        return;
    }
    
    isRefreshing = true;
    const refreshBtn = document.querySelector('button[onclick="refreshPortfolio()"]');
    const originalText = refreshBtn.innerHTML;
    
    // Show loading state
    refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Refreshing...';
    refreshBtn.disabled = true;
    
    fetch('/api/refresh_portfolio')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                showToast('Portfolio refreshed successfully!', 'success');
                
                // Reload the page to show updated data
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                showToast('Error refreshing portfolio: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Error refreshing portfolio:', error);
            showToast('Error refreshing portfolio: ' + error.message, 'error');
        })
        .finally(() => {
            // Reset button state
            refreshBtn.innerHTML = originalText;
            refreshBtn.disabled = false;
            isRefreshing = false;
        });
}

function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to toast container or create one
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function updateTimestamps() {
    const timeElements = document.querySelectorAll('[data-timestamp]');
    timeElements.forEach(element => {
        const timestamp = element.getAttribute('data-timestamp');
        if (timestamp) {
            const date = new Date(timestamp);
            element.textContent = formatTimeAgo(date);
        }
    });
}

function formatTimeAgo(date) {
    const now = new Date();
    const diffInMs = now - date;
    const diffInMinutes = Math.floor(diffInMs / 60000);
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);
    
    if (diffInMinutes < 1) {
        return 'Just now';
    } else if (diffInMinutes < 60) {
        return `${diffInMinutes}m ago`;
    } else if (diffInHours < 24) {
        return `${diffInHours}h ago`;
    } else if (diffInDays < 30) {
        return `${diffInDays}d ago`;
    } else {
        return date.toLocaleDateString();
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatPercentage(percentage) {
    return (percentage >= 0 ? '+' : '') + percentage.toFixed(2) + '%';
}

function animateValue(element, start, end, duration) {
    const startTime = performance.now();
    const animate = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = start + (end - start) * progress;
        element.textContent = formatCurrency(current);
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    };
    
    requestAnimationFrame(animate);
}

// Utility functions for stock data
function getStockColor(change) {
    if (change > 0) return 'success';
    if (change < 0) return 'danger';
    return 'secondary';
}

function getSentimentColor(sentiment) {
    if (sentiment > 0.1) return 'success';
    if (sentiment < -0.1) return 'danger';
    return 'secondary';
}

function getSentimentLabel(sentiment) {
    if (sentiment > 0.1) return 'Positive';
    if (sentiment < -0.1) return 'Negative';
    return 'Neutral';
}

// Export functions for global use
window.refreshPortfolio = refreshPortfolio;
window.showToast = showToast;
window.formatCurrency = formatCurrency;
window.formatPercentage = formatPercentage;
window.animateValue = animateValue;
