/**
 * BiScheduler Venezuelan K12 Dashboard Layouts
 * Responsive dashboard components for teachers and administrators
 * Optimized for Venezuelan educational workflows
 */

class DashboardLayouts {
    constructor() {
        this.breakpoints = {
            mobile: 768,
            tablet: 1024,
            desktop: 1440
        };

        this.venezuelanSchedule = {
            startTime: '07:00',
            endTime: '14:20',
            periods: 10,
            breaks: ['09:00', '11:20']
        };

        this.init();
    }

    init() {
        this.setupViewportDetection();
        this.registerLayoutHandlers();
    }

    setupViewportDetection() {
        this.currentViewport = this.getViewportSize();

        window.addEventListener('resize', () => {
            const newViewport = this.getViewportSize();
            if (newViewport !== this.currentViewport) {
                this.currentViewport = newViewport;
                this.handleViewportChange();
            }
        });
    }

    getViewportSize() {
        const width = window.innerWidth;
        if (width < this.breakpoints.mobile) return 'mobile';
        if (width < this.breakpoints.tablet) return 'tablet';
        if (width < this.breakpoints.desktop) return 'desktop';
        return 'large';
    }

    handleViewportChange() {
        // Reorganize dashboard layout based on viewport
        this.reorganizeDashboard();
        this.adjustScheduleGrid();
        this.updateNavigationMenu();
    }

    registerLayoutHandlers() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeDashboard();
        });
    }

    /**
     * Teacher Dashboard Layout
     */
    renderTeacherDashboard(userData) {
        const container = document.getElementById('dashboard-content');
        if (!container) return;

        const layout = this.getTeacherLayout();
        container.innerHTML = `
            <div class="dashboard-grid teacher-dashboard" data-viewport="${this.currentViewport}">
                ${this.renderTeacherHeader(userData)}
                ${this.renderCurrentClassCard(userData.current_class)}
                ${this.renderNextClassCard(userData.next_class)}
                ${this.renderTodayScheduleCard(userData.today_schedule)}
                ${this.renderWorkloadCard(userData.workload_status)}
                ${this.renderConflictsCard(userData.conflicts)}
                ${this.renderQuickActionsCard()}
            </div>
        `;

        this.attachTeacherEventHandlers();
        this.startRealTimeUpdates();
    }

    getTeacherLayout() {
        switch (this.currentViewport) {
            case 'mobile':
                return {
                    columns: 1,
                    order: ['header', 'current-class', 'next-class', 'today-schedule', 'conflicts', 'workload', 'actions']
                };
            case 'tablet':
                return {
                    columns: 2,
                    order: ['header', 'current-class', 'next-class', 'today-schedule', 'workload', 'conflicts', 'actions']
                };
            default:
                return {
                    columns: 3,
                    order: ['header', 'current-class', 'next-class', 'today-schedule', 'workload', 'conflicts', 'actions']
                };
        }
    }

    renderTeacherHeader(userData) {
        const currentTime = new Date().toLocaleString('es-VE', {
            timeZone: 'America/Caracas',
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        return `
            <div class="dashboard-card header-card">
                <div class="card-header">
                    <h1>Panel del Profesor</h1>
                    <div class="teacher-info">
                        <span class="teacher-name">${userData.teacher_name || 'Profesor'}</span>
                        <span class="current-time">${currentTime}</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderCurrentClassCard(currentClass) {
        if (!currentClass) {
            return `
                <div class="dashboard-card current-class-card no-class">
                    <div class="card-header">
                        <h2><i class="fas fa-clock"></i> Clase Actual</h2>
                    </div>
                    <div class="card-content">
                        <div class="no-class-message">
                            <i class="fas fa-coffee"></i>
                            <p>No hay clases en este momento</p>
                            <span class="next-class-hint">Revisa tu próxima clase</span>
                        </div>
                    </div>
                </div>
            `;
        }

        return `
            <div class="dashboard-card current-class-card active-class">
                <div class="card-header">
                    <h2><i class="fas fa-play-circle"></i> Clase Actual</h2>
                    <span class="class-status">En Progreso</span>
                </div>
                <div class="card-content">
                    <div class="class-details">
                        <div class="subject-info">
                            <h3>${currentClass.subject}</h3>
                            <p class="section">${currentClass.section}</p>
                        </div>
                        <div class="time-info">
                            <span class="time-range">${currentClass.start_time} - ${currentClass.end_time}</span>
                            <span class="classroom">${currentClass.classroom}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="class-progress"></div>
                        </div>
                    </div>
                    <div class="class-actions">
                        <button class="btn btn-primary btn-sm" onclick="openAttendance(${currentClass.assignment_id})">
                            <i class="fas fa-users"></i> Asistencia
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="openGrades(${currentClass.assignment_id})">
                            <i class="fas fa-clipboard-list"></i> Notas
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderNextClassCard(nextClass) {
        if (!nextClass) {
            return `
                <div class="dashboard-card next-class-card no-class">
                    <div class="card-header">
                        <h2><i class="fas fa-forward"></i> Próxima Clase</h2>
                    </div>
                    <div class="card-content">
                        <div class="no-class-message">
                            <i class="fas fa-home"></i>
                            <p>No hay más clases hoy</p>
                            <span class="day-end-hint">Fin del día escolar</span>
                        </div>
                    </div>
                </div>
            `;
        }

        const timeUntil = this.calculateTimeUntil(nextClass.start_time);

        return `
            <div class="dashboard-card next-class-card upcoming-class">
                <div class="card-header">
                    <h2><i class="fas fa-forward"></i> Próxima Clase</h2>
                    <span class="time-until">${timeUntil}</span>
                </div>
                <div class="card-content">
                    <div class="class-details">
                        <div class="subject-info">
                            <h3>${nextClass.subject}</h3>
                            <p class="section">${nextClass.section}</p>
                        </div>
                        <div class="time-info">
                            <span class="time-range">${nextClass.start_time} - ${nextClass.end_time}</span>
                            <span class="classroom">${nextClass.classroom}</span>
                        </div>
                    </div>
                    <div class="preparation-actions">
                        <button class="btn btn-outline-primary btn-sm" onclick="prepareClass(${nextClass.assignment_id})">
                            <i class="fas fa-book"></i> Preparar
                        </button>
                        <button class="btn btn-outline-secondary btn-sm" onclick="viewClassroom('${nextClass.classroom}')">
                            <i class="fas fa-map-marker-alt"></i> Ubicación
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderTodayScheduleCard(todaySchedule) {
        const schedule = todaySchedule || [];
        const currentTime = new Date().toLocaleTimeString('es-VE', {
            timeZone: 'America/Caracas',
            hour: '2-digit',
            minute: '2-digit'
        });

        return `
            <div class="dashboard-card schedule-card">
                <div class="card-header">
                    <h2><i class="fas fa-calendar-day"></i> Horario de Hoy</h2>
                    <span class="schedule-count">${schedule.length} clases</span>
                </div>
                <div class="card-content">
                    <div class="schedule-timeline">
                        ${schedule.map(cls => this.renderScheduleItem(cls, currentTime)).join('')}
                        ${schedule.length === 0 ? '<p class="no-schedule">No hay clases programadas para hoy</p>' : ''}
                    </div>
                </div>
            </div>
        `;
    }

    renderScheduleItem(classItem, currentTime) {
        const isCurrentClass = classItem.is_current;
        const isPastClass = this.isTimeAfter(currentTime, classItem.end_time);
        const isUpcomingClass = this.isTimeBefore(currentTime, classItem.start_time);

        let statusClass = '';
        let statusIcon = '';

        if (isCurrentClass) {
            statusClass = 'current';
            statusIcon = 'fas fa-play-circle';
        } else if (isPastClass) {
            statusClass = 'completed';
            statusIcon = 'fas fa-check-circle';
        } else if (isUpcomingClass) {
            statusClass = 'upcoming';
            statusIcon = 'fas fa-clock';
        }

        return `
            <div class="schedule-item ${statusClass}" data-assignment-id="${classItem.assignment_id}">
                <div class="time-indicator">
                    <i class="${statusIcon}"></i>
                    <span class="time">${classItem.start_time}</span>
                </div>
                <div class="class-info">
                    <h4>${classItem.subject}</h4>
                    <p>${classItem.section} • ${classItem.classroom}</p>
                </div>
                <div class="duration">
                    <span>${this.calculateDuration(classItem.start_time, classItem.end_time)}</span>
                </div>
            </div>
        `;
    }

    renderWorkloadCard(workloadStatus) {
        const workload = workloadStatus || {};
        const currentHours = workload.current_hours || 0;
        const maxHours = workload.max_hours || 40;
        const percentage = Math.min(100, (currentHours / maxHours) * 100);

        let statusClass = 'normal';
        let statusText = 'Normal';

        if (percentage > 100) {
            statusClass = 'overload';
            statusText = 'Sobrecargado';
        } else if (percentage > 90) {
            statusClass = 'warning';
            statusText = 'Cerca del límite';
        } else if (percentage < 50) {
            statusClass = 'underload';
            statusText = 'Subutilizado';
        }

        return `
            <div class="dashboard-card workload-card ${statusClass}">
                <div class="card-header">
                    <h2><i class="fas fa-chart-pie"></i> Carga Horaria</h2>
                    <span class="workload-status">${statusText}</span>
                </div>
                <div class="card-content">
                    <div class="workload-summary">
                        <div class="hours-display">
                            <span class="current-hours">${currentHours}</span>
                            <span class="max-hours">/ ${maxHours} horas</span>
                        </div>
                        <div class="workload-progress">
                            <div class="progress-bar">
                                <div class="progress-fill ${statusClass}" style="width: ${percentage}%"></div>
                            </div>
                            <span class="percentage">${percentage.toFixed(1)}%</span>
                        </div>
                    </div>
                    <div class="workload-breakdown">
                        <div class="breakdown-item">
                            <span>Clases Semanales:</span>
                            <span>${workload.weekly_classes || 0}</span>
                        </div>
                        <div class="breakdown-item">
                            <span>Materias:</span>
                            <span>${workload.subjects_count || 0}</span>
                        </div>
                        <div class="breakdown-item">
                            <span>Secciones:</span>
                            <span>${workload.sections_count || 0}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderConflictsCard(conflicts) {
        const conflictList = conflicts || [];
        const criticalConflicts = conflictList.filter(c => c.severity === 'critical');
        const warningConflicts = conflictList.filter(c => c.severity === 'warning');

        return `
            <div class="dashboard-card conflicts-card ${conflictList.length > 0 ? 'has-conflicts' : ''}">
                <div class="card-header">
                    <h2><i class="fas fa-exclamation-triangle"></i> Conflictos</h2>
                    <span class="conflict-count ${conflictList.length > 0 ? 'active' : ''}">${conflictList.length}</span>
                </div>
                <div class="card-content">
                    ${conflictList.length === 0 ? `
                        <div class="no-conflicts">
                            <i class="fas fa-check-circle"></i>
                            <p>No hay conflictos en tu horario</p>
                        </div>
                    ` : `
                        <div class="conflicts-summary">
                            ${criticalConflicts.length > 0 ? `
                                <div class="conflict-group critical">
                                    <h4><i class="fas fa-times-circle"></i> Críticos (${criticalConflicts.length})</h4>
                                    ${criticalConflicts.slice(0, 2).map(conflict => `
                                        <div class="conflict-item critical">
                                            <span class="conflict-type">${this.translateConflictType(conflict.type)}</span>
                                            <span class="conflict-description">${conflict.description}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : ''}
                            ${warningConflicts.length > 0 ? `
                                <div class="conflict-group warning">
                                    <h4><i class="fas fa-exclamation-circle"></i> Advertencias (${warningConflicts.length})</h4>
                                    ${warningConflicts.slice(0, 2).map(conflict => `
                                        <div class="conflict-item warning">
                                            <span class="conflict-type">${this.translateConflictType(conflict.type)}</span>
                                            <span class="conflict-description">${conflict.description}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : ''}
                        </div>
                        <div class="conflicts-actions">
                            <button class="btn btn-primary btn-sm" onclick="viewAllConflicts()">
                                <i class="fas fa-list"></i> Ver Todos
                            </button>
                            <button class="btn btn-secondary btn-sm" onclick="resolveConflicts()">
                                <i class="fas fa-tools"></i> Resolver
                            </button>
                        </div>
                    `}
                </div>
            </div>
        `;
    }

    renderQuickActionsCard() {
        return `
            <div class="dashboard-card actions-card">
                <div class="card-header">
                    <h2><i class="fas fa-bolt"></i> Acciones Rápidas</h2>
                </div>
                <div class="card-content">
                    <div class="quick-actions-grid">
                        <button class="quick-action-btn" onclick="openScheduleView()">
                            <i class="fas fa-calendar"></i>
                            <span>Ver Horario Completo</span>
                        </button>
                        <button class="quick-action-btn" onclick="requestSubstitution()">
                            <i class="fas fa-user-plus"></i>
                            <span>Solicitar Suplencia</span>
                        </button>
                        <button class="quick-action-btn" onclick="reportIssue()">
                            <i class="fas fa-bug"></i>
                            <span>Reportar Problema</span>
                        </button>
                        <button class="quick-action-btn" onclick="exportSchedule()">
                            <i class="fas fa-download"></i>
                            <span>Exportar Horario</span>
                        </button>
                        <button class="quick-action-btn" onclick="viewStudents()">
                            <i class="fas fa-users"></i>
                            <span>Mis Estudiantes</span>
                        </button>
                        <button class="quick-action-btn" onclick="viewResources()">
                            <i class="fas fa-book"></i>
                            <span>Recursos</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Admin Dashboard Layout
     */
    renderAdminDashboard(userData) {
        const container = document.getElementById('dashboard-content');
        if (!container) return;

        container.innerHTML = `
            <div class="dashboard-grid admin-dashboard" data-viewport="${this.currentViewport}">
                ${this.renderAdminHeader(userData)}
                ${this.renderPlatformOverviewCard(userData.platform_overview)}
                ${this.renderCriticalConflictsCard(userData.critical_conflicts)}
                ${this.renderTeacherAlertsCard(userData.teacher_alerts)}
                ${this.renderScheduleCompletionCard(userData.schedule_completion)}
                ${this.renderAdminActionsCard()}
            </div>
        `;

        this.attachAdminEventHandlers();
        this.startRealTimeUpdates();
    }

    renderAdminHeader(userData) {
        const currentTime = new Date().toLocaleString('es-VE', {
            timeZone: 'America/Caracas',
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        return `
            <div class="dashboard-card header-card admin-header">
                <div class="card-header">
                    <h1>Panel Administrativo</h1>
                    <div class="admin-info">
                        <span class="admin-name">${userData.admin_name || 'Administrador'}</span>
                        <span class="current-time">${currentTime}</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderPlatformOverviewCard(overview) {
        const data = overview || {};

        return `
            <div class="dashboard-card overview-card">
                <div class="card-header">
                    <h2><i class="fas fa-chart-line"></i> Resumen General</h2>
                </div>
                <div class="card-content">
                    <div class="overview-stats">
                        <div class="stat-item">
                            <div class="stat-value">${data.total_assignments || 0}</div>
                            <div class="stat-label">Asignaciones</div>
                        </div>
                        <div class="stat-item ${data.total_conflicts > 0 ? 'has-issues' : ''}">
                            <div class="stat-value">${data.total_conflicts || 0}</div>
                            <div class="stat-label">Conflictos</div>
                        </div>
                        <div class="stat-item ${data.critical_conflicts > 0 ? 'critical' : ''}">
                            <div class="stat-value">${data.critical_conflicts || 0}</div>
                            <div class="stat-label">Críticos</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${data.conflict_rate || 0}%</div>
                            <div class="stat-label">Tasa de Conflicto</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderCriticalConflictsCard(criticalConflicts) {
        const conflicts = criticalConflicts || [];

        return `
            <div class="dashboard-card critical-conflicts-card ${conflicts.length > 0 ? 'has-critical' : ''}">
                <div class="card-header">
                    <h2><i class="fas fa-exclamation-triangle"></i> Conflictos Críticos</h2>
                    <span class="critical-count">${conflicts.length}</span>
                </div>
                <div class="card-content">
                    ${conflicts.length === 0 ? `
                        <div class="no-critical-conflicts">
                            <i class="fas fa-check-circle"></i>
                            <p>No hay conflictos críticos</p>
                        </div>
                    ` : `
                        <div class="critical-conflicts-list">
                            ${conflicts.map(conflict => `
                                <div class="critical-conflict-item" data-conflict-id="${conflict.id}">
                                    <div class="conflict-info">
                                        <h4>${this.translateConflictType(conflict.type)}</h4>
                                        <p>${conflict.description}</p>
                                        <span class="conflict-time">${new Date(conflict.detected_at).toLocaleString('es-VE')}</span>
                                    </div>
                                    <div class="conflict-actions">
                                        <button class="btn btn-sm btn-primary" onclick="resolveConflict(${conflict.id})">
                                            <i class="fas fa-tools"></i> Resolver
                                        </button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <div class="view-all-conflicts">
                            <button class="btn btn-outline-primary" onclick="viewAllConflicts()">
                                <i class="fas fa-list"></i> Ver Todos los Conflictos
                            </button>
                        </div>
                    `}
                </div>
            </div>
        `;
    }

    renderTeacherAlertsCard(teacherAlerts) {
        const alerts = teacherAlerts || [];

        return `
            <div class="dashboard-card teacher-alerts-card">
                <div class="card-header">
                    <h2><i class="fas fa-user-clock"></i> Alertas de Profesores</h2>
                    <span class="alerts-count">${alerts.length}</span>
                </div>
                <div class="card-content">
                    ${alerts.length === 0 ? `
                        <div class="no-alerts">
                            <i class="fas fa-user-check"></i>
                            <p>Todos los profesores dentro de límites normales</p>
                        </div>
                    ` : `
                        <div class="teacher-alerts-list">
                            ${alerts.map(alert => `
                                <div class="teacher-alert-item ${alert.severity}" data-teacher-id="${alert.teacher_id}">
                                    <div class="alert-info">
                                        <h4>${alert.teacher_name}</h4>
                                        <p class="alert-type">${this.translateAlertType(alert.alert_type)}</p>
                                        <div class="hours-info">
                                            <span class="current">${alert.current_hours}h</span>
                                            <span class="separator">/</span>
                                            <span class="max">${alert.max_hours}h</span>
                                            ${alert.excess_hours ? `<span class="excess">+${alert.excess_hours}h</span>` : ''}
                                        </div>
                                    </div>
                                    <div class="alert-actions">
                                        <button class="btn btn-sm btn-secondary" onclick="viewTeacherSchedule(${alert.teacher_id})">
                                            <i class="fas fa-calendar"></i> Ver Horario
                                        </button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `}
                </div>
            </div>
        `;
    }

    renderScheduleCompletionCard(completionData) {
        const sections = completionData || [];

        return `
            <div class="dashboard-card completion-card">
                <div class="card-header">
                    <h2><i class="fas fa-tasks"></i> Completitud de Horarios</h2>
                </div>
                <div class="card-content">
                    <div class="completion-list">
                        ${sections.map(section => {
                            const completionClass = section.completion_percentage < 50 ? 'low' :
                                                  section.completion_percentage < 80 ? 'medium' : 'high';
                            return `
                                <div class="completion-item ${completionClass}">
                                    <div class="section-info">
                                        <h4>${section.section_name}</h4>
                                        <span class="assignments-count">${section.assignments_count} asignaciones</span>
                                    </div>
                                    <div class="completion-progress">
                                        <div class="progress-bar">
                                            <div class="progress-fill" style="width: ${section.completion_percentage}%"></div>
                                        </div>
                                        <span class="percentage">${section.completion_percentage}%</span>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderAdminActionsCard() {
        return `
            <div class="dashboard-card admin-actions-card">
                <div class="card-header">
                    <h2><i class="fas fa-cogs"></i> Acciones Administrativas</h2>
                </div>
                <div class="card-content">
                    <div class="admin-actions-grid">
                        <button class="admin-action-btn" onclick="openScheduleManager()">
                            <i class="fas fa-calendar-plus"></i>
                            <span>Gestionar Horarios</span>
                        </button>
                        <button class="admin-action-btn" onclick="openTeacherManager()">
                            <i class="fas fa-users-cog"></i>
                            <span>Gestionar Profesores</span>
                        </button>
                        <button class="admin-action-btn" onclick="openConflictResolver()">
                            <i class="fas fa-tools"></i>
                            <span>Resolver Conflictos</span>
                        </button>
                        <button class="admin-action-btn" onclick="generateReports()">
                            <i class="fas fa-chart-bar"></i>
                            <span>Generar Reportes</span>
                        </button>
                        <button class="admin-action-btn" onclick="exportSchedules()">
                            <i class="fas fa-file-export"></i>
                            <span>Exportar Horarios</span>
                        </button>
                        <button class="admin-action-btn" onclick="systemSettings()">
                            <i class="fas fa-cog"></i>
                            <span>Configuración</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Responsive Layout Management
     */
    reorganizeDashboard() {
        const dashboard = document.querySelector('.dashboard-grid');
        if (!dashboard) return;

        dashboard.setAttribute('data-viewport', this.currentViewport);

        // Reorder cards based on viewport
        this.reorderDashboardCards(dashboard);

        // Adjust card sizes
        this.adjustCardSizes(dashboard);
    }

    reorderDashboardCards(dashboard) {
        const cards = Array.from(dashboard.children);
        const viewport = this.currentViewport;

        if (viewport === 'mobile') {
            // Mobile-first approach: prioritize current information
            const priorityOrder = [
                '.header-card',
                '.current-class-card',
                '.next-class-card',
                '.conflicts-card',
                '.workload-card',
                '.schedule-card',
                '.actions-card'
            ];

            this.reorderElements(dashboard, cards, priorityOrder);
        }
    }

    reorderElements(container, elements, priorityOrder) {
        priorityOrder.forEach(selector => {
            const element = container.querySelector(selector);
            if (element) {
                container.appendChild(element);
            }
        });
    }

    adjustCardSizes(dashboard) {
        const cards = dashboard.querySelectorAll('.dashboard-card');

        cards.forEach(card => {
            // Reset any existing size classes
            card.classList.remove('card-small', 'card-medium', 'card-large');

            // Apply size based on viewport and card type
            if (this.currentViewport === 'mobile') {
                card.classList.add('card-small');
            } else if (this.currentViewport === 'tablet') {
                card.classList.add('card-medium');
            } else {
                card.classList.add('card-large');
            }
        });
    }

    adjustScheduleGrid() {
        const scheduleGrid = document.querySelector('.schedule-grid');
        if (!scheduleGrid) return;

        if (this.currentViewport === 'mobile') {
            scheduleGrid.classList.add('mobile-layout');
        } else {
            scheduleGrid.classList.remove('mobile-layout');
        }
    }

    updateNavigationMenu() {
        const nav = document.querySelector('.main-navigation');
        if (!nav) return;

        if (this.currentViewport === 'mobile') {
            nav.classList.add('mobile-nav');
        } else {
            nav.classList.remove('mobile-nav');
        }
    }

    /**
     * Event Handlers
     */
    attachTeacherEventHandlers() {
        // Real-time class progress update
        this.updateClassProgress();

        // Auto-refresh dashboard data
        this.scheduleDataRefresh();
    }

    attachAdminEventHandlers() {
        // Real-time conflict monitoring
        this.monitorConflicts();

        // Auto-refresh admin data
        this.scheduleAdminRefresh();
    }

    /**
     * Real-time Updates
     */
    startRealTimeUpdates() {
        // Update every 30 seconds
        this.realTimeInterval = setInterval(() => {
            this.refreshDashboardData();
        }, 30000);

        // Update class progress every 5 seconds
        this.progressInterval = setInterval(() => {
            this.updateClassProgress();
        }, 5000);
    }

    stopRealTimeUpdates() {
        if (this.realTimeInterval) {
            clearInterval(this.realTimeInterval);
        }

        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
    }

    updateClassProgress() {
        const progressBar = document.getElementById('class-progress');
        if (!progressBar) return;

        const currentClassCard = document.querySelector('.current-class-card.active-class');
        if (!currentClassCard) return;

        // Calculate progress based on current time
        const now = new Date();
        const currentTime = now.toTimeString().slice(0, 5); // HH:MM format

        // Extract start and end times (you would get these from the class data)
        const timeInfo = currentClassCard.querySelector('.time-range');
        if (!timeInfo) return;

        const timeRange = timeInfo.textContent.split(' - ');
        const startTime = timeRange[0];
        const endTime = timeRange[1];

        const progress = this.calculateClassProgress(startTime, endTime, currentTime);
        progressBar.style.width = `${progress}%`;

        // Add pulsing effect when near end
        if (progress > 90) {
            progressBar.classList.add('ending-soon');
        } else {
            progressBar.classList.remove('ending-soon');
        }
    }

    /**
     * Utility Functions
     */
    calculateTimeUntil(targetTime) {
        const now = new Date();
        const [hours, minutes] = targetTime.split(':').map(Number);
        const target = new Date(now);
        target.setHours(hours, minutes, 0, 0);

        if (target < now) {
            target.setDate(target.getDate() + 1);
        }

        const diff = target - now;
        const diffMinutes = Math.floor(diff / (1000 * 60));

        if (diffMinutes < 60) {
            return `${diffMinutes} min`;
        } else {
            const diffHours = Math.floor(diffMinutes / 60);
            const remainingMinutes = diffMinutes % 60;
            return `${diffHours}h ${remainingMinutes}m`;
        }
    }

    calculateDuration(startTime, endTime) {
        const [startHours, startMinutes] = startTime.split(':').map(Number);
        const [endHours, endMinutes] = endTime.split(':').map(Number);

        const startTotalMinutes = startHours * 60 + startMinutes;
        const endTotalMinutes = endHours * 60 + endMinutes;

        const durationMinutes = endTotalMinutes - startTotalMinutes;

        if (durationMinutes < 60) {
            return `${durationMinutes} min`;
        } else {
            const hours = Math.floor(durationMinutes / 60);
            const minutes = durationMinutes % 60;
            return `${hours}h ${minutes > 0 ? minutes + 'm' : ''}`;
        }
    }

    calculateClassProgress(startTime, endTime, currentTime) {
        const timeToMinutes = (time) => {
            const [hours, minutes] = time.split(':').map(Number);
            return hours * 60 + minutes;
        };

        const startMinutes = timeToMinutes(startTime);
        const endMinutes = timeToMinutes(endTime);
        const currentMinutes = timeToMinutes(currentTime);

        if (currentMinutes < startMinutes || currentMinutes > endMinutes) {
            return 0;
        }

        const totalDuration = endMinutes - startMinutes;
        const elapsed = currentMinutes - startMinutes;

        return Math.min(100, (elapsed / totalDuration) * 100);
    }

    isTimeAfter(currentTime, targetTime) {
        const timeToMinutes = (time) => {
            const [hours, minutes] = time.split(':').map(Number);
            return hours * 60 + minutes;
        };

        return timeToMinutes(currentTime) > timeToMinutes(targetTime);
    }

    isTimeBefore(currentTime, targetTime) {
        const timeToMinutes = (time) => {
            const [hours, minutes] = time.split(':').map(Number);
            return hours * 60 + minutes;
        };

        return timeToMinutes(currentTime) < timeToMinutes(targetTime);
    }

    translateConflictType(type) {
        const translations = {
            'teacher_double_booking': 'Profesor Duplicado',
            'classroom_conflict': 'Conflicto de Aula',
            'workload_violation': 'Violación de Carga',
            'teacher_subject_mismatch': 'Materia Incorrecta',
            'time_conflict': 'Conflicto de Horario',
            'resource_unavailable': 'Recurso No Disponible'
        };

        return translations[type] || type;
    }

    translateAlertType(type) {
        const translations = {
            'overloaded': 'Sobrecargado',
            'underutilized': 'Subutilizado',
            'missing_qualification': 'Falta Calificación',
            'schedule_gap': 'Hueco en Horario'
        };

        return translations[type] || type;
    }

    refreshDashboardData() {
        // This would typically fetch fresh data from the API
        // Implementation depends on the current user type and dashboard
        if (window.currentUser && window.currentUser.role === 'teacher') {
            this.refreshTeacherData();
        } else if (window.currentUser && ['school_admin', 'academic_coordinator'].includes(window.currentUser.role)) {
            this.refreshAdminData();
        }
    }

    async refreshTeacherData() {
        try {
            const response = await fetch(`/api/schedule/realtime/dashboard/${window.currentUser.id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'X-Tenant-ID': window.currentTenant.id
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderTeacherDashboard(data);
            }
        } catch (error) {
            console.error('Error refreshing teacher data:', error);
        }
    }

    async refreshAdminData() {
        try {
            const response = await fetch(`/api/schedule/realtime/dashboard/${window.currentUser.id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'X-Tenant-ID': window.currentTenant.id
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderAdminDashboard(data);
            }
        } catch (error) {
            console.error('Error refreshing admin data:', error);
        }
    }

    /**
     * Initialize Dashboard
     */
    initializeDashboard() {
        // This method is called when the page loads
        // It determines which dashboard to show based on user role
        if (window.currentUser) {
            if (window.currentUser.role === 'teacher') {
                this.loadTeacherDashboard();
            } else if (['school_admin', 'academic_coordinator'].includes(window.currentUser.role)) {
                this.loadAdminDashboard();
            }
        }
    }

    async loadTeacherDashboard() {
        try {
            const response = await fetch(`/api/schedule/realtime/dashboard/${window.currentUser.id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'X-Tenant-ID': window.currentTenant.id
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderTeacherDashboard(data);
            } else {
                throw new Error('Failed to load teacher dashboard');
            }
        } catch (error) {
            console.error('Error loading teacher dashboard:', error);
            this.showErrorDashboard('Error cargando el panel del profesor');
        }
    }

    async loadAdminDashboard() {
        try {
            const response = await fetch(`/api/schedule/realtime/dashboard/${window.currentUser.id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'X-Tenant-ID': window.currentTenant.id
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderAdminDashboard(data);
            } else {
                throw new Error('Failed to load admin dashboard');
            }
        } catch (error) {
            console.error('Error loading admin dashboard:', error);
            this.showErrorDashboard('Error cargando el panel administrativo');
        }
    }

    showErrorDashboard(message) {
        const container = document.getElementById('dashboard-content');
        if (container) {
            container.innerHTML = `
                <div class="dashboard-error">
                    <div class="error-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h2>Error en el Panel</h2>
                    <p>${message}</p>
                    <button class="btn btn-primary" onclick="location.reload()">
                        <i class="fas fa-refresh"></i> Recargar
                    </button>
                </div>
            `;
        }
    }

    destroy() {
        this.stopRealTimeUpdates();

        window.removeEventListener('resize', this.handleViewportChange);

        // Remove event listeners
        document.removeEventListener('DOMContentLoaded', this.initializeDashboard);
    }
}

// Export for global use
window.DashboardLayouts = DashboardLayouts;

// Auto-initialize when script loads
document.addEventListener('DOMContentLoaded', () => {
    if (!window.dashboardLayouts) {
        window.dashboardLayouts = new DashboardLayouts();
    }
});