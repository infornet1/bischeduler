/**
 * BiScheduler Schedule Visualization Components
 * Venezuelan K12 Schedule Display and Management
 * Interactive schedule grid with real-time updates
 */

class ScheduleComponents {
    constructor() {
        this.venezualanDays = [
            { key: 'lunes', label: 'Lunes' },
            { key: 'martes', label: 'Martes' },
            { key: 'miercoles', label: 'Miércoles' },
            { key: 'jueves', label: 'Jueves' },
            { key: 'viernes', label: 'Viernes' }
        ];

        this.venezualanPeriods = [
            { key: 'P1', label: 'P1', time: '07:00-07:40', isBreak: false },
            { key: 'P2', label: 'P2', time: '07:40-08:20', isBreak: false },
            { key: 'P3', label: 'P3', time: '08:20-09:00', isBreak: false },
            { key: 'REC1', label: 'RECREO', time: '09:00-09:20', isBreak: true },
            { key: 'P4', label: 'P4', time: '09:20-10:00', isBreak: false },
            { key: 'P5', label: 'P5', time: '10:00-10:40', isBreak: false },
            { key: 'P6', label: 'P6', time: '10:40-11:20', isBreak: false },
            { key: 'REC2', label: 'RECREO', time: '11:20-11:40', isBreak: true },
            { key: 'P7', label: 'P7', time: '11:40-12:20', isBreak: false },
            { key: 'P8', label: 'P8', time: '12:20-13:00', isBreak: false },
            { key: 'P9', label: 'P9', time: '13:00-13:40', isBreak: false },
            { key: 'P10', label: 'P10', time: '13:40-14:20', isBreak: false }
        ];
    }

    /**
     * Render Venezuelan K12 schedule grid
     * @param {Object} scheduleData - Schedule data from API
     * @param {string} containerId - Container element ID
     * @param {Object} options - Display options
     */
    renderScheduleGrid(scheduleData, containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        const config = {
            showTeacherNames: true,
            showClassrooms: true,
            showConflicts: true,
            allowEditing: false,
            compactView: false,
            ...options
        };

        const gridHTML = this.generateScheduleGridHTML(scheduleData, config);
        container.innerHTML = gridHTML;

        // Add event listeners for interactive features
        this.attachScheduleEventListeners(container, config);
    }

    generateScheduleGridHTML(scheduleData, config) {
        const schedule = scheduleData.schedule || {};

        return `
            <div class="venezuelan-schedule-grid">
                <div class="schedule-header">
                    <div class="schedule-title">
                        <h3>Horario de Clases</h3>
                        ${scheduleData.section_name ? `
                            <div class="section-info">
                                <span class="section-name">${scheduleData.section_name}</span>
                                <span class="academic-year-badge">${scheduleData.academic_year || '2025-2026'}</span>
                            </div>
                        ` : ''}
                    </div>
                    <div class="schedule-controls">
                        ${config.allowEditing ? `
                            <button class="btn btn-primary btn-sm" onclick="scheduleComponents.openAddAssignmentModal()">
                                ➕ Agregar Clase
                            </button>
                        ` : ''}
                        <button class="btn btn-secondary btn-sm" onclick="scheduleComponents.exportSchedule('${scheduleData.section_id}')">
                            📊 Exportar
                        </button>
                    </div>
                </div>

                <div class="schedule-table-container">
                    <table class="schedule-table venezuelan-format">
                        <thead>
                            <tr>
                                <th class="time-column">HORA</th>
                                ${this.venezualanDays.map(day => `
                                    <th class="day-column">${day.label.toUpperCase()}</th>
                                `).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${this.venezualanPeriods.map(period => `
                                <tr class="period-row ${period.isBreak ? 'break-row' : ''}">
                                    <td class="time-cell">
                                        <div class="period-name">${period.label}</div>
                                        <div class="period-time">${period.time}</div>
                                    </td>
                                    ${this.venezualanDays.map(day => {
                                        const assignment = this.getAssignment(schedule, day.key, period.key);
                                        return this.renderScheduleCell(assignment, period, day, config);
                                    }).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>

                ${config.showConflicts ? this.renderConflictLegend() : ''}
            </div>
        `;
    }

    getAssignment(schedule, day, period) {
        return schedule[day] && schedule[day][period] ? schedule[day][period] : null;
    }

    renderScheduleCell(assignment, period, day, config) {
        if (period.isBreak) {
            return `
                <td class="schedule-cell break-cell">
                    <div class="break-content">
                        <span class="break-label">RECREO</span>
                    </div>
                </td>
            `;
        }

        if (!assignment) {
            return `
                <td class="schedule-cell empty-cell"
                    data-day="${day.key}"
                    data-period="${period.key}"
                    ${config.allowEditing ? 'onclick="scheduleComponents.openAssignmentEditor(this)"' : ''}>
                    <div class="empty-content">
                        ${config.allowEditing ? '<span class="add-indicator">+</span>' : ''}
                    </div>
                </td>
            `;
        }

        const hasConflict = assignment.conflicts && assignment.conflicts.length > 0;
        const conflictClass = hasConflict ? 'has-conflict' : '';

        return `
            <td class="schedule-cell assigned-cell ${conflictClass}"
                data-day="${day.key}"
                data-period="${period.key}"
                data-assignment-id="${assignment.assignment_id || ''}"
                ${config.allowEditing ? 'onclick="scheduleComponents.openAssignmentEditor(this)"' : ''}>
                <div class="assignment-content">
                    <div class="subject-name">${assignment.subject || ''}</div>
                    ${config.showTeacherNames && assignment.teacher ? `
                        <div class="teacher-name">${assignment.teacher}</div>
                    ` : ''}
                    ${config.showClassrooms && assignment.classroom ? `
                        <div class="classroom-name">(${assignment.classroom})</div>
                    ` : ''}
                    ${hasConflict && config.showConflicts ? `
                        <div class="conflict-indicator" title="Conflicto detectado">⚠️</div>
                    ` : ''}
                </div>
            </td>
        `;
    }

    renderConflictLegend() {
        return `
            <div class="conflict-legend">
                <h4>Leyenda</h4>
                <div class="legend-items">
                    <div class="legend-item">
                        <span class="legend-color normal-class"></span>
                        <span class="legend-text">Clase Normal</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color break-class"></span>
                        <span class="legend-text">Recreo</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color conflict-class"></span>
                        <span class="legend-text">Conflicto Detectado</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color empty-class"></span>
                        <span class="legend-text">Período Libre</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render teacher schedule view
     */
    renderTeacherSchedule(teacherData, containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const config = {
            showSections: true,
            showWorkload: true,
            highlightCurrent: true,
            ...options
        };

        const schedule = teacherData.schedule || {};
        const teacher = teacherData.teacher || {};
        const workload = teacherData.workload || {};

        const html = `
            <div class="teacher-schedule-container">
                <div class="teacher-header">
                    <div class="teacher-info">
                        <h3>${teacher.name || 'Docente'}</h3>
                        <span class="teacher-specialization">${teacher.specialization || ''}</span>
                    </div>
                    ${config.showWorkload ? `
                        <div class="teacher-workload">
                            <div class="workload-summary">
                                <span class="hours-current">${workload.current_hours || 0}</span>
                                <span class="hours-separator">/</span>
                                <span class="hours-max">${workload.max_hours || 40}</span>
                                <span class="hours-unit">horas</span>
                            </div>
                            <div class="workload-status ${workload.is_valid === false ? 'invalid' : 'valid'}">
                                ${workload.is_valid === false ? '⚠️ Sobrecarga' : '✅ Válida'}
                            </div>
                            ${workload.subjects_taught ? `
                                <div class="subjects-taught">
                                    <strong>Materias:</strong> ${workload.subjects_taught.join(', ')}
                                </div>
                            ` : ''}
                        </div>
                    ` : ''}
                </div>

                <div class="teacher-schedule-grid">
                    ${this.generateScheduleGridHTML({
                        schedule: schedule,
                        teacher_name: teacher.name
                    }, {
                        ...config,
                        showTeacherNames: false,
                        showSections: config.showSections
                    })}
                </div>
            </div>
        `;

        container.innerHTML = html;

        // Highlight current class if enabled
        if (config.highlightCurrent) {
            this.highlightCurrentClass(container);
        }
    }

    /**
     * Render conflict indicators on schedule
     */
    updateConflictIndicators(conflicts, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Clear existing conflict indicators
        container.querySelectorAll('.conflict-indicator').forEach(el => el.remove());
        container.querySelectorAll('.has-conflict').forEach(el => el.classList.remove('has-conflict'));

        // Add new conflict indicators
        conflicts.forEach(conflict => {
            if (conflict.assignment_id) {
                const cell = container.querySelector(`[data-assignment-id="${conflict.assignment_id}"]`);
                if (cell) {
                    cell.classList.add('has-conflict');
                    const content = cell.querySelector('.assignment-content');
                    if (content && !content.querySelector('.conflict-indicator')) {
                        const indicator = document.createElement('div');
                        indicator.className = 'conflict-indicator';
                        indicator.innerHTML = '⚠️';
                        indicator.title = conflict.description || 'Conflicto detectado';
                        content.appendChild(indicator);
                    }
                }
            }
        });
    }

    /**
     * Highlight current class based on time
     */
    highlightCurrentClass(container) {
        const now = new Date();
        const currentTime = now.getHours() * 60 + now.getMinutes(); // Minutes since midnight
        const currentDay = now.getDay(); // 0 = Sunday, 1 = Monday, etc.

        // Only highlight on weekdays (Monday-Friday)
        if (currentDay < 1 || currentDay > 5) return;

        const venezualanDayIndex = currentDay - 1; // Convert to 0-based Venezuelan week
        const dayKey = this.venezualanDays[venezualanDayIndex]?.key;

        if (!dayKey) return;

        // Find current period
        const currentPeriod = this.venezualanPeriods.find(period => {
            if (period.isBreak) return false;

            const [startHour, startMin] = period.time.split('-')[0].split(':').map(Number);
            const [endHour, endMin] = period.time.split('-')[1].split(':').map(Number);

            const startTime = startHour * 60 + startMin;
            const endTime = endHour * 60 + endMin;

            return currentTime >= startTime && currentTime <= endTime;
        });

        if (currentPeriod) {
            const cell = container.querySelector(`[data-day="${dayKey}"][data-period="${currentPeriod.key}"]`);
            if (cell) {
                cell.classList.add('current-class');
            }
        }
    }

    /**
     * Attach event listeners for interactive features
     */
    attachScheduleEventListeners(container, config) {
        // Tooltip on hover
        container.addEventListener('mouseenter', (event) => {
            if (event.target.closest('.assigned-cell')) {
                this.showScheduleTooltip(event.target.closest('.assigned-cell'), event);
            }
        }, true);

        container.addEventListener('mouseleave', (event) => {
            if (event.target.closest('.assigned-cell')) {
                this.hideScheduleTooltip();
            }
        }, true);

        // Conflict details on click
        container.addEventListener('click', (event) => {
            if (event.target.closest('.conflict-indicator')) {
                event.stopPropagation();
                this.showConflictDetails(event.target.closest('.assigned-cell'));
            }
        });
    }

    showScheduleTooltip(cell, event) {
        const assignmentId = cell.dataset.assignmentId;
        if (!assignmentId) return;

        const tooltip = document.createElement('div');
        tooltip.className = 'schedule-tooltip';
        tooltip.innerHTML = `
            <div class="tooltip-content">
                <div class="tooltip-title">Detalles de la Clase</div>
                <div class="tooltip-info">ID: ${assignmentId}</div>
                <div class="tooltip-actions">
                    <button class="btn btn-sm btn-primary" onclick="scheduleComponents.viewAssignmentDetails('${assignmentId}')">
                        Ver Detalles
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(tooltip);

        // Position tooltip
        const rect = cell.getBoundingClientRect();
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = (rect.bottom + 5) + 'px';

        this.currentTooltip = tooltip;
    }

    hideScheduleTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }

    /**
     * Export schedule functionality
     */
    async exportSchedule(sectionId, format = 'excel') {
        try {
            const response = await app.apiCall(`/schedule/${app.currentTenant}/export/section/${sectionId}/${format}`);

            if (response.status === 'success') {
                if (format === 'csv') {
                    this.downloadCSV(response.csv_data, response.filename);
                } else {
                    app.showNotification('Exportación iniciada', 'success');
                }
            } else {
                app.showNotification('Error en la exportación', 'error');
            }
        } catch (error) {
            console.error('Export error:', error);
            app.showNotification('Error en la exportación', 'error');
        }
    }

    downloadCSV(csvData, filename) {
        const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
    }

    /**
     * Assignment editing functionality
     */
    openAssignmentEditor(cell) {
        const day = cell.dataset.day;
        const period = cell.dataset.period;
        const assignmentId = cell.dataset.assignmentId;

        const modal = this.createAssignmentModal(day, period, assignmentId);
        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    openAddAssignmentModal() {
        const modal = this.createAssignmentModal();
        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    createAssignmentModal(day = '', period = '', assignmentId = '') {
        const isEdit = !!assignmentId;

        const modal = document.createElement('div');
        modal.className = 'assignment-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${isEdit ? 'Editar' : 'Agregar'} Asignación</h3>
                    <button class="modal-close" onclick="this.closest('.assignment-modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <form class="assignment-form" onsubmit="scheduleComponents.handleAssignmentSubmit(event)">
                        <input type="hidden" name="assignment_id" value="${assignmentId}">

                        <div class="form-group">
                            <label for="day_of_week">Día de la Semana</label>
                            <select name="day_of_week" required class="form-control">
                                ${this.venezualanDays.map(d => `
                                    <option value="${d.key}" ${d.key === day ? 'selected' : ''}>${d.label}</option>
                                `).join('')}
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="time_period">Período</label>
                            <select name="time_period" required class="form-control">
                                ${this.venezualanPeriods.filter(p => !p.isBreak).map(p => `
                                    <option value="${p.key}" ${p.key === period ? 'selected' : ''}>${p.label} (${p.time})</option>
                                `).join('')}
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="teacher_id">Docente</label>
                            <select name="teacher_id" required class="form-control">
                                <option value="">Seleccionar docente...</option>
                                <!-- Will be populated dynamically -->
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="subject_id">Materia</label>
                            <select name="subject_id" required class="form-control">
                                <option value="">Seleccionar materia...</option>
                                <!-- Will be populated dynamically -->
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="classroom_id">Aula</label>
                            <select name="classroom_id" required class="form-control">
                                <option value="">Seleccionar aula...</option>
                                <!-- Will be populated dynamically -->
                            </select>
                        </div>

                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="validate_conflicts" checked>
                                Validar conflictos automáticamente
                            </label>
                        </div>

                        <div class="modal-actions">
                            <button type="button" class="btn btn-secondary" onclick="this.closest('.assignment-modal').remove()">
                                Cancelar
                            </button>
                            <button type="submit" class="btn btn-primary">
                                ${isEdit ? 'Actualizar' : 'Crear'} Asignación
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        // Load dropdown data
        this.loadAssignmentFormData(modal);

        return modal;
    }

    async loadAssignmentFormData(modal) {
        try {
            // Load teachers, subjects, and classrooms
            // This would typically come from API calls
            // For now, we'll use placeholder data

            const teacherSelect = modal.querySelector('[name="teacher_id"]');
            const subjectSelect = modal.querySelector('[name="subject_id"]');
            const classroomSelect = modal.querySelector('[name="classroom_id"]');

            // Placeholder data - would come from API
            const teachers = [
                { id: 1, name: 'MARIA NIETO' },
                { id: 2, name: 'ISMARY ARCILA' },
                { id: 3, name: 'FLORMAR HERNANDEZ' }
            ];

            const subjects = [
                { id: 1, name: 'MATEMÁTICAS' },
                { id: 2, name: 'CASTELLANO Y LITERATURA' },
                { id: 3, name: 'QUÍMICA' }
            ];

            const classrooms = [
                { id: 1, name: 'Aula 1' },
                { id: 2, name: 'Aula 2' },
                { id: 3, name: 'Laboratorio' }
            ];

            teachers.forEach(teacher => {
                teacherSelect.innerHTML += `<option value="${teacher.id}">${teacher.name}</option>`;
            });

            subjects.forEach(subject => {
                subjectSelect.innerHTML += `<option value="${subject.id}">${subject.name}</option>`;
            });

            classrooms.forEach(classroom => {
                classroomSelect.innerHTML += `<option value="${classroom.id}">${classroom.name}</option>`;
            });

        } catch (error) {
            console.error('Error loading form data:', error);
        }
    }

    async handleAssignmentSubmit(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const assignmentData = Object.fromEntries(formData.entries());

        try {
            const response = await app.apiCall(`/schedule/${app.currentTenant}/assignments`, 'POST', {
                teacher_id: parseInt(assignmentData.teacher_id),
                subject_id: parseInt(assignmentData.subject_id),
                section_id: 1, // Would be dynamic based on current view
                classroom_id: parseInt(assignmentData.classroom_id),
                time_period_id: parseInt(assignmentData.time_period), // Would map from period key
                day_of_week: assignmentData.day_of_week,
                validate_conflicts: assignmentData.validate_conflicts === 'on'
            });

            if (response.status === 'success') {
                app.showNotification('Asignación creada exitosamente', 'success');
                event.target.closest('.assignment-modal').remove();

                // Refresh the schedule view
                app.loadScheduleView();
            } else {
                app.showNotification(response.message || 'Error creando asignación', 'error');
            }
        } catch (error) {
            console.error('Assignment creation error:', error);
            app.showNotification('Error creando asignación', 'error');
        }
    }

    /**
     * View assignment details
     */
    async viewAssignmentDetails(assignmentId) {
        try {
            const response = await app.apiCall(`/schedule/${app.currentTenant}/assignments/${assignmentId}`);

            if (response.assignment) {
                this.showAssignmentDetailsModal(response.assignment);
            }
        } catch (error) {
            console.error('Error loading assignment details:', error);
            app.showNotification('Error cargando detalles', 'error');
        }
    }

    showAssignmentDetailsModal(assignment) {
        const modal = document.createElement('div');
        modal.className = 'assignment-details-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Detalles de Asignación</h3>
                    <button class="modal-close" onclick="this.closest('.assignment-details-modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="assignment-details">
                        <div class="detail-group">
                            <label>Materia:</label>
                            <span>${assignment.subject.name}</span>
                        </div>
                        <div class="detail-group">
                            <label>Docente:</label>
                            <span>${assignment.teacher.name}</span>
                        </div>
                        <div class="detail-group">
                            <label>Sección:</label>
                            <span>${assignment.section.name}</span>
                        </div>
                        <div class="detail-group">
                            <label>Aula:</label>
                            <span>${assignment.classroom.name}</span>
                        </div>
                        <div class="detail-group">
                            <label>Horario:</label>
                            <span>${assignment.day_of_week} - ${assignment.time_period.start_time} a ${assignment.time_period.end_time}</span>
                        </div>
                        <div class="detail-group">
                            <label>Estado:</label>
                            <span class="${assignment.is_active ? 'active' : 'inactive'}">${assignment.is_active ? 'Activa' : 'Inactiva'}</span>
                        </div>
                    </div>
                    <div class="modal-actions">
                        <button class="btn btn-secondary" onclick="this.closest('.assignment-details-modal').remove()">
                            Cerrar
                        </button>
                        <button class="btn btn-warning" onclick="scheduleComponents.editAssignment('${assignment.id}')">
                            Editar
                        </button>
                        <button class="btn btn-danger" onclick="scheduleComponents.deleteAssignment('${assignment.id}')">
                            Eliminar
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    /**
     * Delete assignment
     */
    async deleteAssignment(assignmentId) {
        if (!confirm('¿Está seguro de eliminar esta asignación?')) {
            return;
        }

        try {
            const response = await app.apiCall(`/schedule/${app.currentTenant}/assignments/${assignmentId}`, 'DELETE');

            if (response.status === 'success') {
                app.showNotification('Asignación eliminada', 'success');

                // Close modal and refresh view
                document.querySelectorAll('.assignment-details-modal').forEach(modal => modal.remove());
                app.loadScheduleView();
            } else {
                app.showNotification('Error eliminando asignación', 'error');
            }
        } catch (error) {
            console.error('Delete assignment error:', error);
            app.showNotification('Error eliminando asignación', 'error');
        }
    }
}

// Initialize schedule components
const scheduleComponents = new ScheduleComponents();

// Make it globally available
window.scheduleComponents = scheduleComponents;