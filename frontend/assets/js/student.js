/**
 * Teaching Practice Management System
 * Student JavaScript File
 */

// DOM Ready Event
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is a student
    checkStudentRole();
    
    // Add student specific event listeners
    addStudentEventListeners();
});

/**
 * Check if current user is a student
 */
function checkStudentRole() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!user || user.role !== 'student') {
        window.location.href = '/login.html';
        return;
    }
}

/**
 * Add student specific event listeners
 */
function addStudentEventListeners() {
    // Report form submission
    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        reportForm.addEventListener('submit', handleReportFormSubmit);
    }
    
    // Report type filter
    const reportTypeFilter = document.getElementById('reportTypeFilter');
    if (reportTypeFilter) {
        reportTypeFilter.addEventListener('change', function(e) {
            const reportType = e.target.value;
            filterReports(reportType);
        });
    }
}

/**
 * Handle report form submission
 * @param {Event} e - Form submit event
 */
function handleReportFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const reportId = form.getAttribute('data-report-id');
    const isEdit = !!reportId;
    
    // Check if form has file upload
    const hasFileUpload = form.querySelector('input[type="file"]') !== null;
    
    if (hasFileUpload) {
        // Handle form with file upload using FormData
        const formData = new FormData(form);
        
        // API endpoint and method based on create/edit
        const endpoint = isEdit ? `/student/reports/${reportId}` : '/student/reports';
        const method = isEdit ? 'PUT' : 'POST';
        
        // Make API call with FormData
        const token = localStorage.getItem('token');
        
        if (!token) {
            showAlert('You are not logged in. Please log in and try again.', 'danger');
            return;
        }
        
        fetch(`/api${endpoint}`, {
            method: method,
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'API request failed');
                });
            }
            return response.json();
        })
        .then(data => {
            showAlert(`Report ${isEdit ? 'updated' : 'submitted'} successfully!`, 'success');
            
            // Redirect to reports list after a short delay
            setTimeout(() => {
                window.location.href = 'reports.html';
            }, 1500);
        })
        .catch(error => {
            console.error('Error saving report:', error);
            showAlert(`Failed to ${isEdit ? 'update' : 'submit'} report: ${error.message}`, 'danger');
        });
    } else {
        // Handle regular form submission
        const formData = {
            title: form.title.value,
            content: form.content.value,
            report_type: form.report_type.value
        };
        
        // API endpoint and method based on create/edit
        const endpoint = isEdit ? `/student/reports/${reportId}` : '/student/reports';
        const method = isEdit ? 'PUT' : 'POST';
        
        // Make API call
        apiCall(endpoint, method, formData)
            .then(response => {
                showAlert(`Report ${isEdit ? 'updated' : 'submitted'} successfully!`, 'success');
                
                // Redirect to reports list after a short delay
                setTimeout(() => {
                    window.location.href = 'reports.html';
                }, 1500);
            })
            .catch(error => {
                console.error('Error saving report:', error);
                showAlert(`Failed to ${isEdit ? 'update' : 'submit'} report: ${error.message}`, 'danger');
            });
    }
}

/**
 * Filter reports by type
 * @param {string} reportType - Report type to filter by
 */
function filterReports(reportType) {
    if (!reportType) {
        // If no report type selected, show all reports
        loadReports();
        return;
    }
    
    // Load reports filtered by report type
    apiCall(`/student/reports?report_type=${reportType}`)
        .then(data => {
            updateReportsTable(data.reports || []);
        })
        .catch(error => {
            console.error('Error filtering reports:', error);
            showAlert('Failed to filter reports. Please try again later.', 'danger');
        });
}

/**
 * Update reports table with data
 * @param {Array} reports - Reports data
 */
function updateReportsTable(reports) {
    const tableContainer = document.getElementById('reportsTableContainer');
    if (!tableContainer) return;
    
    // Define table columns
    const columns = [
        { 
            title: 'Title',
            property: 'title'
        },
        {
            title: 'Type',
            render: report => `<span class="badge bg-${getReportTypeBadgeColor(report.report_type)}">${formatReportType(report.report_type)}</span>`
        },
        {
            title: 'Submitted',
            render: report => formatDate(report.submission_date)
        },
        {
            title: 'Status',
            render: report => `<span class="badge bg-${getStatusBadgeColor(report.status)}">${formatStatus(report.status)}</span>`
        },
        {
            title: 'Actions',
            render: report => `
                <div class="action-buttons">
                    <a href="view-report.html?id=${report.id}" class="btn btn-sm btn-info">
                        <i class="bi bi-eye"></i>
                    </a>
                    <a href="edit-report.html?id=${report.id}" class="btn btn-sm btn-primary">
                        <i class="bi bi-pencil"></i>
                    </a>
                    <button class="btn btn-sm btn-danger" onclick="deleteReport(${report.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            `
        }
    ];
    
    // Clear previous table
    tableContainer.innerHTML = '';
    
    // Create table element
    const table = document.createElement('table');
    table.className = 'table table-hover data-table';
    table.id = 'reportsTable';
    
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
    
    if (reports.length === 0) {
        // If no reports, show a message
        const emptyRow = document.createElement('tr');
        const emptyCell = document.createElement('td');
        emptyCell.colSpan = columns.length;
        emptyCell.className = 'text-center';
        emptyCell.textContent = 'No reports found.';
        emptyRow.appendChild(emptyCell);
        tbody.appendChild(emptyRow);
    } else {
        // Add report rows
        reports.forEach(report => {
            const row = document.createElement('tr');
            
            columns.forEach(column => {
                const cell = document.createElement('td');
                if (column.render) {
                    cell.innerHTML = column.render(report);
                } else {
                    cell.textContent = report[column.property] || '';
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
 * Load reports
 */
function loadReports() {
    apiCall('/student/reports')
        .then(data => {
            updateReportsTable(data.reports || []);
        })
        .catch(error => {
            console.error('Error loading reports:', error);
            showAlert('Failed to load reports. Please try again later.', 'danger');
        });
}

/**
 * Load a specific report for editing
 * @param {string} reportId - Report ID to load
 */
function loadReportForEdit(reportId) {
    apiCall(`/student/reports/${reportId}`)
        .then(data => {
            const report = data.report;
            const form = document.getElementById('reportForm');
            
            if (!form) return;
            
            // Set form values
            form.setAttribute('data-report-id', report.id);
            form.title.value = report.title;
            form.content.value = report.content;
            form.report_type.value = report.report_type;
            
            // Update form title
            const formTitle = document.querySelector('.form-title');
            if (formTitle) {
                formTitle.textContent = 'Edit Report';
            }
            
            // Update submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Update Report';
            }
            
            // Show file name if available
            const fileInfo = document.getElementById('fileInfo');
            if (fileInfo && report.file_path) {
                const fileName = report.file_path.split('/').pop();
                fileInfo.innerHTML = `
                    <div class="alert alert-info">
                        <i class="bi bi-paperclip me-2"></i>
                        Current file: ${fileName}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading report:', error);
            showAlert('Failed to load report data. Please try again later.', 'danger');
        });
}

/**
 * Delete a report
 * @param {string} reportId - Report ID to delete
 */
function deleteReport(reportId) {
    if (confirm('Are you sure you want to delete this report? This action cannot be undone.')) {
        apiCall(`/student/reports/${reportId}`, 'DELETE')
            .then(response => {
                showAlert('Report deleted successfully!', 'success');
                
                // Refresh reports list if on reports page
                if (window.location.href.includes('reports.html')) {
                    setTimeout(() => {
                        loadReports();
                    }, 1500);
                }
            })
            .catch(error => {
                console.error('Error deleting report:', error);
                showAlert(`Failed to delete report: ${error.message}`, 'danger');
            });
    }
}

/**
 * Load evaluations
 */
function loadEvaluations() {
    apiCall('/student/evaluations')
        .then(data => {
            const evaluations = data.evaluations || [];
            const evaluationsContainer = document.getElementById('evaluationsContainer');
            
            if (!evaluationsContainer) return;
            
            if (evaluations.length === 0) {
                evaluationsContainer.innerHTML = `
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        No evaluations have been submitted for you yet.
                    </div>
                `;
                return;
            }
            
            let html = '';
            evaluations.forEach(evaluation => {
                // Calculate average rating
                const ratings = [
                    evaluation.teaching_skills, 
                    evaluation.classroom_management, 
                    evaluation.lesson_preparation, 
                    evaluation.professionalism
                ];
                const avgRating = ratings.reduce((a, b) => a + b, 0) / ratings.length;
                
                html += `
                    <div class="evaluation-card mb-4">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="evaluation-title mb-0">
                                Evaluation from ${evaluation.lecturer ? evaluation.lecturer.first_name + ' ' + evaluation.lecturer.last_name : 'Supervisor'}
                            </h5>
                            <span class="badge bg-${getGradeBadgeColor(evaluation.overall_grade)} p-2">${evaluation.overall_grade}</span>
                        </div>
                        
                        <div class="evaluation-date mb-3">
                            <i class="bi bi-calendar3 me-2"></i>
                            Visit Date: ${formatDate(evaluation.visit_date)}
                        </div>
                        
                        <div class="row mb-4">
                            <div class="col-md-3 mb-3">
                                <div class="rating-item">
                                    <h6>Teaching Skills</h6>
                                    <div class="progress mb-2" style="height: 10px;">
                                        <div class="progress-bar bg-${getRatingColor(evaluation.teaching_skills)}" 
                                             style="width: ${evaluation.teaching_skills * 10}%"></div>
                                    </div>
                                    <div class="d-flex justify-content-between">
                                        <span>Rating:</span>
                                        <span>${evaluation.teaching_skills}/10</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-3 mb-3">
                                <div class="rating-item">
                                    <h6>Classroom Management</h6>
                                    <div class="progress mb-2" style="height: 10px;">
                                        <div class="progress-bar bg-${getRatingColor(evaluation.classroom_management)}" 
                                             style="width: ${evaluation.classroom_management * 10}%"></div>
                                    </div>
                                    <div class="d-flex justify-content-between">
                                        <span>Rating:</span>
                                        <span>${evaluation.classroom_management}/10</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-3 mb-3">
                                <div class="rating-item">
                                    <h6>Lesson Preparation</h6>
                                    <div class="progress mb-2" style="height: 10px;">
                                        <div class="progress-bar bg-${getRatingColor(evaluation.lesson_preparation)}" 
                                             style="width: ${evaluation.lesson_preparation * 10}%"></div>
                                    </div>
                                    <div class="d-flex justify-content-between">
                                        <span>Rating:</span>
                                        <span>${evaluation.lesson_preparation}/10</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-3 mb-3">
                                <div class="rating-item">
                                    <h6>Professionalism</h6>
                                    <div class="progress mb-2" style="height: 10px;">
                                        <div class="progress-bar bg-${getRatingColor(evaluation.professionalism)}" 
                                             style="width: ${evaluation.professionalism * 10}%"></div>
                                    </div>
                                    <div class="d-flex justify-content-between">
                                        <span>Rating:</span>
                                        <span>${evaluation.professionalism}/10</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="evaluation-comments mb-3">
                            <h6>Comments</h6>
                            <p>${evaluation.comments || 'No comments provided.'}</p>
                        </div>
                        
                        <div class="evaluation-summary">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6>Overall Rating</h6>
                                    <div class="progress mb-2" style="height: 10px; width: 200px;">
                                        <div class="progress-bar bg-${getRatingColor(avgRating)}" 
                                             style="width: ${avgRating * 10}%"></div>
                                    </div>
                                    <div class="d-flex justify-content-between" style="width: 200px;">
                                        <span>Average:</span>
                                        <span>${avgRating.toFixed(1)}/10</span>
                                    </div>
                                </div>
                                <div>
                                    <span class="evaluation-date">
                                        <i class="bi bi-clock me-1"></i>
                                        Submitted: ${formatDate(evaluation.submission_date)}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            evaluationsContainer.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading evaluations:', error);
            const evaluationsContainer = document.getElementById('evaluationsContainer');
            if (evaluationsContainer) {
                evaluationsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>
                        Failed to load evaluations. Please try again later.
                    </div>
                `;
            }
        });
}

/**
 * Helper function to format report type
 * @param {string} type - Report type
 * @returns {string} - Formatted report type
 */
function formatReportType(type) {
    switch (type) {
        case 'daily':
            return 'Daily Report';
        case 'weekly':
            return 'Weekly Report';
        case 'lesson_plan':
            return 'Lesson Plan';
        case 'reflection':
            return 'Reflection';
        case 'final':
            return 'Final Report';
        default:
            return type.charAt(0).toUpperCase() + type.slice(1);
    }
}

/**
 * Helper function to get report type badge color
 * @param {string} type - Report type
 * @returns {string} - Bootstrap color class
 */
function getReportTypeBadgeColor(type) {
    switch (type) {
        case 'daily':
            return 'info';
        case 'weekly':
            return 'primary';
        case 'lesson_plan':
            return 'success';
        case 'reflection':
            return 'warning';
        case 'final':
            return 'danger';
        default:
            return 'secondary';
    }
}

/**
 * Helper function to format status
 * @param {string} status - Status value
 * @returns {string} - Formatted status
 */
function formatStatus(status) {
    switch (status) {
        case 'submitted':
            return 'Submitted';
        case 'reviewed':
            return 'Reviewed';
        default:
            return status.charAt(0).toUpperCase() + status.slice(1);
    }
}

/**
 * Helper function to get status badge color
 * @param {string} status - Status value
 * @returns {string} - Bootstrap color class
 */
function getStatusBadgeColor(status) {
    switch (status) {
        case 'submitted':
            return 'warning';
        case 'reviewed':
            return 'success';
        default:
            return 'secondary';
    }
}

/**
 * Helper function to get rating color
 * @param {number} rating - Rating value
 * @returns {string} - Bootstrap color class
 */
function getRatingColor(rating) {
    if (rating >= 8) return 'success';
    if (rating >= 6) return 'info';
    if (rating >= 4) return 'warning';
    return 'danger';
}

/**
 * Helper function to get grade badge color
 * @param {string} grade - Grade value (A+, A, B+, etc.)
 * @returns {string} - Bootstrap color class
 */
function getGradeBadgeColor(grade) {
    if (['A+', 'A', 'A-'].includes(grade)) return 'success';
    if (['B+', 'B', 'B-'].includes(grade)) return 'info';
    if (['C+', 'C', 'C-'].includes(grade)) return 'warning';
    return 'danger';
}