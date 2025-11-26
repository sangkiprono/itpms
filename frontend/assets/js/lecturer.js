/**
 * Teaching Practice Management System
 * Lecturer JavaScript File
 */

// DOM Ready Event
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is a lecturer
    checkLecturerRole();
    
    // Add lecturer specific event listeners
    addLecturerEventListeners();
});

/**
 * Check if current user is a lecturer
 */
function checkLecturerRole() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!user || user.role !== 'lecturer') {
        window.location.href = '/login.html';
        return;
    }
}

/**
 * Add lecturer specific event listeners
 */
function addLecturerEventListeners() {
    // Evaluation form submission
    const evaluationForm = document.getElementById('evaluationForm');
    if (evaluationForm) {
        evaluationForm.addEventListener('submit', handleEvaluationFormSubmit);
    }
    
    // Student filter
    const studentFilter = document.getElementById('studentFilter');
    if (studentFilter) {
        studentFilter.addEventListener('change', function(e) {
            const studentId = e.target.value;
            filterEvaluations(studentId);
        });
    }
}

/**
 * Handle evaluation form submission
 * @param {Event} e - Form submit event
 */
function handleEvaluationFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const evaluationId = form.getAttribute('data-evaluation-id');
    const isEdit = !!evaluationId;
    
    // Gather form data
    const formData = {
        student_id: form.student_id.value,
        visit_date: form.visit_date.value,
        teaching_skills: parseInt(form.teaching_skills.value),
        classroom_management: parseInt(form.classroom_management.value),
        lesson_preparation: parseInt(form.lesson_preparation.value),
        professionalism: parseInt(form.professionalism.value),
        comments: form.comments.value,
        overall_grade: form.overall_grade.value
    };
    
    // API endpoint and method based on create/edit
    const endpoint = isEdit ? `/lecturer/evaluations/${evaluationId}` : '/lecturer/evaluations';
    const method = isEdit ? 'PUT' : 'POST';
    
    // Make API call
    apiCall(endpoint, method, formData)
        .then(response => {
            showAlert(`Evaluation ${isEdit ? 'updated' : 'submitted'} successfully!`, 'success');
            
            // Redirect to evaluations list after a short delay
            setTimeout(() => {
                window.location.href = 'evaluations.html';
            }, 1500);
        })
        .catch(error => {
            console.error('Error saving evaluation:', error);
            showAlert(`Failed to ${isEdit ? 'update' : 'submit'} evaluation: ${error.message}`, 'danger');
        });
}

/**
 * Filter evaluations by student
 * @param {string} studentId - Student ID to filter by
 */
function filterEvaluations(studentId) {
    if (!studentId) {
        // If no student selected, show all evaluations
        loadEvaluations();
        return;
    }
    
    // Load evaluations filtered by student ID
    apiCall(`/lecturer/evaluations?student_id=${studentId}`)
        .then(data => {
            updateEvaluationsTable(data.evaluations || []);
        })
        .catch(error => {
            console.error('Error filtering evaluations:', error);
            showAlert('Failed to filter evaluations. Please try again later.', 'danger');
        });
}

/**
 * Update evaluations table with data
 * @param {Array} evaluations - Evaluations data
 */
function updateEvaluationsTable(evaluations) {
    const tableContainer = document.getElementById('evaluationsTableContainer');
    if (!tableContainer) return;
    
    // Define table columns
    const columns = [
        { 
            title: 'Student',
            render: eval => eval.student ? `${eval.student.first_name} ${eval.student.last_name}` : 'Unknown'
        },
        {
            title: 'Visit Date',
            render: eval => formatDate(eval.visit_date)
        },
        {
            title: 'Teaching Skills',
            render: eval => `<span class="badge bg-${getRatingBadgeColor(eval.teaching_skills)}">${eval.teaching_skills}/10</span>`
        },
        {
            title: 'Classroom Management',
            render: eval => `<span class="badge bg-${getRatingBadgeColor(eval.classroom_management)}">${eval.classroom_management}/10</span>`
        },
        {
            title: 'Overall Grade',
            render: eval => `<span class="badge bg-${getGradeBadgeColor(eval.overall_grade)}">${eval.overall_grade}</span>`
        },
        {
            title: 'Submission Date',
            render: eval => formatDate(eval.submission_date)
        },
        {
            title: 'Actions',
            render: eval => `
                <div class="action-buttons">
                    <a href="view-evaluation.html?id=${eval.id}" class="btn btn-sm btn-info">
                        <i class="bi bi-eye"></i>
                    </a>
                    <a href="edit-evaluation.html?id=${eval.id}" class="btn btn-sm btn-primary">
                        <i class="bi bi-pencil"></i>
                    </a>
                </div>
            `
        }
    ];
    
    // Clear previous table
    tableContainer.innerHTML = '';
    
    // Create table element
    const table = document.createElement('table');
    table.className = 'table table-hover data-table';
    table.id = 'evaluationsTable';
    
    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    columns.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column.title;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create table body
    const tbody = document.createElement('tbody');
    
    if (evaluations.length === 0) {
        // If no evaluations, show a message
        const emptyRow = document.createElement('tr');
        const emptyCell = document.createElement('td');
        emptyCell.colSpan = columns.length;
        emptyCell.className = 'text-center';
        emptyCell.textContent = 'No evaluations found.';
        emptyRow.appendChild(emptyCell);
        tbody.appendChild(emptyRow);
    } else {
        // Add evaluation rows
        evaluations.forEach(evaluation => {
            const row = document.createElement('tr');
            
            columns.forEach(column => {
                const cell = document.createElement('td');
                if (column.render) {
                    cell.innerHTML = column.render(evaluation);
                } else {
                    cell.textContent = evaluation[column.property] || '';
                }
                row.appendChild(cell);
            });
            
            tbody.appendChild(row);
        });
    }
    
    table.appendChild(tbody);
    tableContainer.appendChild(table);
}

/**
 * Load evaluations
 */
function loadEvaluations() {
    apiCall('/lecturer/evaluations')
        .then(data => {
            updateEvaluationsTable(data.evaluations || []);
        })
        .catch(error => {
            console.error('Error loading evaluations:', error);
            showAlert('Failed to load evaluations. Please try again later.', 'danger');
        });
}

/**
 * Load assigned students for a dropdown
 * @param {string} selectId - ID of select element to populate
 * @param {function} callback - Optional callback after loading
 */
function loadStudentsForSelect(selectId, callback) {
    apiCall('/lecturer/students')
        .then(data => {
            const students = data.students || [];
            const selectElement = document.getElementById(selectId);
            
            if (!selectElement) return;
            
            // Clear existing options except the first placeholder
            const firstOption = selectElement.querySelector('option:first-child');
            selectElement.innerHTML = '';
            if (firstOption) {
                selectElement.appendChild(firstOption);
            }
            
            // Add student options
            students.forEach(student => {
                const option = document.createElement('option');
                option.value = student.id;
                option.textContent = `${student.first_name} ${student.last_name}`;
                selectElement.appendChild(option);
            });
            
            // Call callback if provided
            if (typeof callback === 'function') {
                callback();
            }
        })
        .catch(error => {
            console.error('Error loading students:', error);
            showAlert('Failed to load students. Please try again later.', 'danger');
        });
}

/**
 * Load a specific evaluation for editing
 * @param {string} evaluationId - Evaluation ID to load
 */
function loadEvaluationForEdit(evaluationId) {
    apiCall(`/lecturer/evaluations/${evaluationId}`)
        .then(data => {
            const evaluation = data.evaluation;
            const form = document.getElementById('evaluationForm');
            
            if (!form) return;
            
            // Set form values
            form.setAttribute('data-evaluation-id', evaluation.id);
            form.student_id.value = evaluation.student_id;
            form.visit_date.value = evaluation.visit_date.split('T')[0]; // Extract just the date part
            form.teaching_skills.value = evaluation.teaching_skills;
            form.classroom_management.value = evaluation.classroom_management;
            form.lesson_preparation.value = evaluation.lesson_preparation;
            form.professionalism.value = evaluation.professionalism;
            form.comments.value = evaluation.comments || '';
            form.overall_grade.value = evaluation.overall_grade;
            
            // Update form title
            const formTitle = document.querySelector('.form-title');
            if (formTitle) {
                formTitle.textContent = 'Edit Evaluation';
            }
            
            // Update submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Update Evaluation';
            }
            
            // Student field may be disabled for editing
            const studentField = form.student_id;
            if (studentField) {
                studentField.disabled = true;
            }
        })
        .catch(error => {
            console.error('Error loading evaluation:', error);
            showAlert('Failed to load evaluation data. Please try again later.', 'danger');
        });
}

/**
 * Get badge color based on rating (1-10)
 * @param {number} rating - Rating value
 * @returns {string} - Bootstrap color class
 */
function getRatingBadgeColor(rating) {
    if (rating >= 9) return 'success';
    if (rating >= 7) return 'info';
    if (rating >= 5) return 'warning';
    return 'danger';
}

/**
 * Get badge color based on grade
 * @param {string} grade - Grade value (A+, A, B+, etc.)
 * @returns {string} - Bootstrap color class
 */
function getGradeBadgeColor(grade) {
    if (['A+', 'A', 'A-'].includes(grade)) return 'success';
    if (['B+', 'B', 'B-'].includes(grade)) return 'info';
    if (['C+', 'C', 'C-'].includes(grade)) return 'warning';
    return 'danger';
}