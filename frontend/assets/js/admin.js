/**
 * Teaching Practice Management System
 * Admin JavaScript File
 */

// DOM Ready Event
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is an admin
    checkAdminRole();
    
    // Add admin specific event listeners
    addAdminEventListeners();
});

/**
 * Check if current user is an admin
 */
function checkAdminRole() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!user || user.role !== 'admin') {
        window.location.href = '/login.html';
        return;
    }
}

/**
 * Add admin specific event listeners
 */
function addAdminEventListeners() {
    // User form submission
    const userForm = document.getElementById('userForm');
    if (userForm) {
        userForm.addEventListener('submit', handleUserFormSubmit);
    }
    
    // School form submission
    const schoolForm = document.getElementById('schoolForm');
    if (schoolForm) {
        schoolForm.addEventListener('submit', handleSchoolFormSubmit);
    }
    
    // Teaching session form submission
    const sessionForm = document.getElementById('sessionForm');
    if (sessionForm) {
        sessionForm.addEventListener('submit', handleSessionFormSubmit);
    }
    
    // Student assignment form submission
    const assignmentForm = document.getElementById('assignmentForm');
    if (assignmentForm) {
        assignmentForm.addEventListener('submit', handleAssignmentFormSubmit);
    }
}

/**
 * Handle user form submission
 * @param {Event} e - Form submit event
 */
function handleUserFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const userId = form.getAttribute('data-user-id');
    const isEdit = !!userId;
    
    // Gather form data
    const formData = {
        username: form.username.value,
        email: form.email.value,
        first_name: form.first_name.value,
        last_name: form.last_name.value,
        role: form.role.value,
        is_active: form.is_active ? form.is_active.checked : true
    };
    
    // Add password for new users
    if (!isEdit) {
        formData.password = form.password.value;
    }
    
    // API endpoint and method based on create/edit
    const endpoint = isEdit ? `/admin/users/${userId}` : '/auth/register';
    const method = isEdit ? 'PUT' : 'POST';
    
    // Make API call
    apiCall(endpoint, method, formData)
        .then(response => {
            showAlert(`School ${isEdit ? 'updated' : 'created'} successfully!`, 'success');
            
            // Redirect to schools list after a short delay
            setTimeout(() => {
                window.location.href = 'manage-schools.html';
            }, 1500);
        })
        .catch(error => {
            console.error('Error saving school:', error);
                    showAlert(`Failed to ${isEdit ? 'update' : 'create'} school: ${error.message}`, 'danger');
                });
}

/**
 * Handle school form submission
 * @param {Event} e - Form submit event
 */
function handleSchoolFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const schoolId = form.getAttribute('data-school-id');
    const isEdit = !!schoolId;
    
    // Gather form data
    const formData = {
        name: form.name.value,
        address: form.address.value,
        city: form.city.value,
        state: form.state.value,
        contact_person: form.contact_person.value,
        contact_email: form.contact_email.value,
        contact_phone: form.contact_phone.value
    };
    
    // API endpoint and method based on create/edit
    const endpoint = isEdit ? `/admin/schools/${schoolId}` : '/admin/schools';
    const method = isEdit ? 'PUT' : 'POST';
    
    // Make API call
    apiCall(endpoint, method, formData)
        .then(response => {
            showAlert(`School ${isEdit ? 'updated' : 'created'} successfully!`, 'success');
            
            // Redirect to schools list after a short delay
            setTimeout(() => {
                window.location.href = 'manage-schools.html';
            }, 1500);
        })
        .catch(error => {
            console.error('Error saving school:', error);
            showAlert(`Failed to ${isEdit ? 'update' : 'create'} school: ${error.message}`, 'danger');
        });
    }