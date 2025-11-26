/**
 * Teaching Practice Management System
 * Main JavaScript File
 */

// Global Variables
const API_URL = '/api';
let currentUser = null;

// DOM Ready Event
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    checkAuthStatus();
    
    // Initialize UI components
    initializeComponents();
    
    // Add event listeners
    addEventListeners();
});

/**
 * Check user authentication status
 */
function checkAuthStatus() {
    // Get token from localStorage
    const token = localStorage.getItem('token');
    
    // If no token, redirect to login if not already there
    if (!token && !window.location.href.includes('login.html') && !window.location.href.includes('index.html')) {
        window.location.href = '/login.html';
        return;
    }
    
    // If token exists and on login page, redirect to dashboard
    if (token && window.location.href.includes('login.html')) {
        redirectToDashboard();
        return;
    }
    
    // If logged in, get current user info
    if (token) {
        const userStr = localStorage.getItem('user');
        if (userStr) {
            currentUser = JSON.parse(userStr);
            
            // Update UI with user info if needed
            updateUserInfo();
        } else {
            // Fetch user info from API
            fetchCurrentUser();
        }
    }
}

/**
 * Fetch current user information from API
 */
function fetchCurrentUser() {
    const token = localStorage.getItem('token');
    
    if (!token) return;
    
    fetch(`${API_URL}/auth/me`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch user info');
        }
        return response.json();
    })
    .then(data => {
        currentUser = data.user;
        localStorage.setItem('user', JSON.stringify(currentUser));
        updateUserInfo();
    })
    .catch(error => {
        console.error('Error fetching user info:', error);
        // Handle token expiration
        if (error.message.includes('401')) {
            logout();
        }
    });
}

/**
 * Update UI with user information
 */
function updateUserInfo() {
    if (!currentUser) return;
    
    // Update user name in navbar if element exists
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
        userNameElement.textContent = `${currentUser.first_name} ${currentUser.last_name}`;
    }
    
    // Update user role if element exists
    const userRoleElement = document.getElementById('userRole');
    if (userRoleElement) {
        userRoleElement.textContent = currentUser.role.charAt(0).toUpperCase() + currentUser.role.slice(1);
    }
    
    // Update profile image if exists (placeholder for now)
    const userImageElement = document.getElementById('userImage');
    if (userImageElement) {
        // Use initials as placeholder
        const initials = `${currentUser.first_name.charAt(0)}${currentUser.last_name.charAt(0)}`;
        userImageElement.setAttribute('data-initials', initials);
    }
}

/**
 * Redirect to appropriate dashboard based on user role
 */
function redirectToDashboard() {
    const userStr = localStorage.getItem('user');
    
    if (!userStr) {
        window.location.href = '/login.html';
        return;
    }
    
    const user = JSON.parse(userStr);
    
    switch (user.role) {
        case 'admin':
            window.location.href = '/admin/dashboard.html';
            break;
        case 'lecturer':
            window.location.href = '/lecturer/dashboard.html';
            break;
        case 'student':
            window.location.href = '/student/dashboard.html';
            break;
        default:
            window.location.href = '/login.html';
    }
}

/**
 * Initialize UI components
 */
function initializeComponents() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize popovers if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Popover) {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Mark active nav link based on current page
    markActiveNavLink();
}

/**
 * Mark the active navigation link based on current URL
 */
function markActiveNavLink() {
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    const currentPath = window.location.pathname;
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href)) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * Add global event listeners
 */
function addEventListeners() {
    // Logout button click
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
    
    // Contact form submission
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Handle contact form submission (could be replaced with actual API call)
            alert('Thank you for your message. We will get back to you soon!');
            contactForm.reset();
        });
    }
}

/**
 * Logout user and redirect to login page
 */
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login.html';
}

/**
 * Helper function to format dates
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

/**
 * Helper function to make authenticated API calls
 * @param {string} endpoint - API endpoint
 * @param {string} method - HTTP method
 * @param {object} data - Request data
 * @returns {Promise} Fetch promise
 */
function apiCall(endpoint, method = 'GET', data = null) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        window.location.href = '/login.html';
        return Promise.reject('No authentication token found');
    }
    
    const url = `${API_URL}${endpoint}`;
    const options = {
        method: method,
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };
    
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => {
            if (response.status === 401) {
                // Token expired or invalid
                logout();
                throw new Error('Authentication failed');
            }
            
            if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || 'API request failed');
                });
            }
            
            return response.json();
        });
}

/**
 * Show alert message
 * @param {string} message - Message to display
 * @param {string} type - Alert type (success, danger, warning, info)
 * @param {string} containerId - ID of container element
 */
function showAlert(message, type = 'success', containerId = 'alertContainer') {
    const container = document.getElementById(containerId);
    
    if (!container) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    container.innerHTML = '';
    container.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = bootstrap.Alert.getOrCreateInstance(alertDiv);
        if (alert) {
            alert.close();
        }
    }, 5000);
}

/**
 * Create dynamic table with data
 * @param {array} data - Array of objects
 * @param {array} columns - Array of column definitions
 * @param {string} tableId - ID of table element
 */
function createDataTable(data, columns, tableId) {
    const tableElement = document.getElementById(tableId);
    
    if (!tableElement) return;
    
    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    columns.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column.title;
        if (column.width) {
            th.style.width = column.width;
        }
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    
    // Create table body
    const tbody = document.createElement('tbody');
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        columns.forEach(column => {
            const td = document.createElement('td');
            
            if (column.render) {
                // Use custom renderer function
                td.innerHTML = column.render(item);
            } else if (column.property) {
                // Use simple property value
                td.textContent = item[column.property] || '';
            }
            
            row.appendChild(td);
        });
        
        tbody.appendChild(row);
    });
    
    // Clear table and append new content
    tableElement.innerHTML = '';
    tableElement.appendChild(thead);
    tableElement.appendChild(tbody);
}