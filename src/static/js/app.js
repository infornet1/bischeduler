/**
 * BiScheduler Frontend Application
 * Venezuelan K12 Scheduling Platform
 * Enhanced with real-time features and multi-tenant support
 */

class BiSchedulerApp {
    constructor() {
        this.apiBase = '/api';
        this.currentUser = null;
        this.currentTenant = null;
        this.wsConnection = null;

        // Venezuelan localization
        this.locale = 'es-VE';
        this.timezone = 'America/Caracas';

        this.init();
    }

    async init() {
        console.log('🚀 BiScheduler - Inicializando aplicación');

        // Load user session
        await this.loadUserSession();

        // Setup event listeners
        this.setupEventListeners();

        // Initialize routing
        this.initializeRouting();

        // Setup real-time connections
        this.setupRealTimeUpdates();

        // Load initial view
        this.loadInitialView();
    }

    async loadUserSession() {
        const token = localStorage.getItem('bischeduler_token');
        if (token) {
            try {
                const response = await this.apiCall('/auth/profile', 'GET');
                if (response.success) {
                    this.currentUser = response.user;
                    this.updateNavigation();
                }
            } catch (error) {
                console.error('Error loading user session:', error);
                this.logout();
            }
        }
    }

    setupEventListeners() {
        // Global error handling
        window.addEventListener('error', (event) => {
            this.showNotification('Error inesperado', 'error');
            console.error('Global error:', event.error);
        });

        // Navigation events
        document.addEventListener('click', (event) => {
            if (event.target.matches('[data-route]')) {
                event.preventDefault();
                const route = event.target.getAttribute('data-route');
                this.navigate(route);
            }
        });

        // Form submissions
        document.addEventListener('submit', (event) => {
            if (event.target.matches('.ajax-form')) {
                event.preventDefault();
                this.handleFormSubmission(event.target);
            }
        });
    }

    initializeRouting() {
        this.routes = {
            '/': () => this.loadDashboard(),
            '/login': () => this.loadLoginForm(),
            '/schedule': () => this.loadScheduleView(),
            '/teachers': () => this.loadTeachersView(),
            '/conflicts': () => this.loadConflictsView(),
            '/reports': () => this.loadReportsView(),
            '/admin': () => this.loadAdminPanel()
        };

        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            this.handleRoute(window.location.pathname);
        });
    }

    navigate(path) {
        history.pushState(null, '', path);
        this.handleRoute(path);
    }

    handleRoute(path) {
        const handler = this.routes[path] || this.routes['/'];
        handler();
    }

    loadInitialView() {
        if (this.currentUser) {
            this.loadDashboard();
        } else {
            this.loadLoginForm();
        }
    }

    // =====================================================
    // AUTHENTICATION
    // =====================================================

    async login(email, password, tenantId = null) {
        try {
            const response = await this.apiCall('/auth/login', 'POST', {
                email,
                password,
                tenant_id: tenantId
            });

            if (response.success) {
                localStorage.setItem('bischeduler_token', response.access_token);
                localStorage.setItem('bischeduler_refresh_token', response.refresh_token);

                this.currentUser = response.user;
                this.currentTenant = response.user.tenant_id;

                this.showNotification('¡Bienvenido a BiScheduler!', 'success');
                this.loadDashboard();

                return true;
            } else {
                this.showNotification(response.message || 'Error de autenticación', 'error');
                return false;
            }
        } catch (error) {
            this.showNotification('Error de conexión', 'error');
            console.error('Login error:', error);
            return false;
        }
    }

    logout() {
        localStorage.removeItem('bischeduler_token');
        localStorage.removeItem('bischeduler_refresh_token');
        this.currentUser = null;
        this.currentTenant = null;

        this.closeRealTimeConnection();
        this.loadLoginForm();
        this.showNotification('Sesión cerrada', 'info');
    }

    // =====================================================
    // API COMMUNICATION
    // =====================================================

    async apiCall(endpoint, method = 'GET', data = null) {
        const token = localStorage.getItem('bischeduler_token');

        const config = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            config.body = JSON.stringify(data);
        }

        const response = await fetch(`${this.apiBase}${endpoint}`, config);

        if (response.status === 401) {
            // Token expired, try refresh
            if (await this.refreshToken()) {
                // Retry with new token
                return this.apiCall(endpoint, method, data);
            } else {
                this.logout();
                throw new Error('Authentication required');
            }
        }

        return response.json();
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('bischeduler_refresh_token');
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${this.apiBase}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('bischeduler_token', data.access_token);
                localStorage.setItem('bischeduler_refresh_token', data.refresh_token);
                return true;
            }
        } catch (error) {
            console.error('Token refresh error:', error);
        }

        return false;
    }

    // =====================================================
    // REAL-TIME UPDATES
    // =====================================================

    setupRealTimeUpdates() {
        if (!this.currentUser || !this.currentTenant) return;

        // Simulate real-time updates with polling for demo
        this.realTimeInterval = setInterval(() => {
            this.updateRealTimeData();
        }, 30000); // Update every 30 seconds
    }

    async updateRealTimeData() {
        try {
            // Update conflicts
            const conflicts = await this.apiCall(`/schedule/${this.currentTenant}/conflicts`);
            this.updateConflictIndicators(conflicts);

            // Update workload alerts
            const alerts = await this.apiCall(`/schedule/${this.currentTenant}/realtime/workload/alerts`);
            this.updateWorkloadAlerts(alerts);

        } catch (error) {
            console.error('Real-time update error:', error);
        }
    }

    closeRealTimeConnection() {
        if (this.realTimeInterval) {
            clearInterval(this.realTimeInterval);
            this.realTimeInterval = null;
        }
    }

    // =====================================================
    // VIEW LOADING
    // =====================================================

    loadLoginForm() {
        const content = `
            <div class="login-container">
                <div class="login-card">
                    <div class="login-header">
                        <img src="/static/images/bischeduler-logo.png" alt="BiScheduler" class="logo" onerror="this.style.display='none'">
                        <h1>BiScheduler</h1>
                        <p>Plataforma de Horarios para Educación Venezolana K12</p>
                    </div>

                    <form class="ajax-form" data-action="login">
                        <div class="form-group">
                            <label for="email">Correo Electrónico</label>
                            <input type="email" id="email" name="email" required
                                   placeholder="usuario@ueipab.edu.ve" class="form-control">
                        </div>

                        <div class="form-group">
                            <label for="password">Contraseña</label>
                            <input type="password" id="password" name="password" required
                                   placeholder="••••••••" class="form-control">
                        </div>

                        <div class="form-group">
                            <label for="tenant_id">Institución (Opcional)</label>
                            <select id="tenant_id" name="tenant_id" class="form-control">
                                <option value="">Seleccionar...</option>
                                <option value="ueipab">UEIPAB</option>
                            </select>
                        </div>

                        <button type="submit" class="btn btn-primary btn-block">
                            Iniciar Sesión
                        </button>
                    </form>

                    <div class="login-footer">
                        <p>🇻🇪 Desarrollado para instituciones educativas venezolanas</p>
                        <p>Soporte: <a href="mailto:soporte@bischeduler.com">soporte@bischeduler.com</a></p>
                    </div>
                </div>
            </div>
        `;

        this.setMainContent(content);
        this.setPageTitle('Iniciar Sesión - BiScheduler');
    }

    async loadDashboard() {
        if (!this.currentUser) {
            this.loadLoginForm();
            return;
        }

        try {
            const dashboardData = await this.apiCall(
                `/schedule/${this.currentTenant}/realtime/dashboard/${this.currentUser.id}`
            );

            let dashboardContent = '';

            if (this.currentUser.role === 'teacher') {
                dashboardContent = this.renderTeacherDashboard(dashboardData);
            } else {
                dashboardContent = this.renderAdminDashboard(dashboardData);
            }

            this.setMainContent(dashboardContent);
            this.setPageTitle('Panel Principal - BiScheduler');
            this.updateNavigation();

        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.setMainContent(this.renderErrorMessage('Error cargando el panel principal'));
        }
    }

    renderTeacherDashboard(data) {
        const currentClass = data.current_class;
        const nextClass = data.next_class;
        const todaySchedule = data.today_schedule || [];
        const conflicts = data.conflicts || [];
        const workload = data.workload_status || {};

        return `
            <div class="dashboard-container">
                <div class="dashboard-header">
                    <h1>¡Bienvenido, ${this.currentUser.first_name}!</h1>
                    <p class="dashboard-subtitle">Panel del Docente - ${this.formatDate(new Date())}</p>
                </div>

                <div class="dashboard-grid">
                    <!-- Current Class -->
                    <div class="dashboard-card current-class">
                        <h3>Clase Actual</h3>
                        ${currentClass ? `
                            <div class="class-info active">
                                <div class="subject">${currentClass.subject}</div>
                                <div class="details">
                                    <span class="section">${currentClass.section}</span>
                                    <span class="time">${currentClass.start_time} - ${currentClass.end_time}</span>
                                    <span class="classroom">${currentClass.classroom}</span>
                                </div>
                            </div>
                        ` : `
                            <div class="no-class">
                                <p>No hay clase en este momento</p>
                            </div>
                        `}
                    </div>

                    <!-- Next Class -->
                    <div class="dashboard-card next-class">
                        <h3>Próxima Clase</h3>
                        ${nextClass ? `
                            <div class="class-info">
                                <div class="subject">${nextClass.subject}</div>
                                <div class="details">
                                    <span class="section">${nextClass.section}</span>
                                    <span class="time">${nextClass.start_time} - ${nextClass.end_time}</span>
                                    <span class="classroom">${nextClass.classroom}</span>
                                </div>
                            </div>
                        ` : `
                            <div class="no-class">
                                <p>No hay más clases hoy</p>
                            </div>
                        `}
                    </div>

                    <!-- Workload Status -->
                    <div class="dashboard-card workload-status">
                        <h3>Carga Horaria</h3>
                        <div class="workload-info">
                            <div class="hours-display">
                                <span class="current">${workload.current_hours || 0}</span>
                                <span class="separator">/</span>
                                <span class="max">${workload.max_hours || 40}</span>
                                <span class="unit">horas</span>
                            </div>
                            <div class="workload-bar">
                                <div class="progress" style="width: ${((workload.current_hours || 0) / (workload.max_hours || 40)) * 100}%"></div>
                            </div>
                            ${workload.is_valid === false ? '<div class="alert">⚠️ Sobrecarga detectada</div>' : ''}
                        </div>
                    </div>

                    <!-- Conflicts -->
                    <div class="dashboard-card conflicts">
                        <h3>Conflictos</h3>
                        ${conflicts.length > 0 ? `
                            <div class="conflict-list">
                                ${conflicts.map(conflict => `
                                    <div class="conflict-item ${conflict.severity}">
                                        <span class="conflict-type">${this.formatConflictType(conflict.type)}</span>
                                        <span class="conflict-desc">${conflict.description}</span>
                                    </div>
                                `).join('')}
                            </div>
                        ` : `
                            <div class="no-conflicts">
                                <p>✅ Sin conflictos detectados</p>
                            </div>
                        `}
                    </div>
                </div>

                <!-- Today's Schedule -->
                <div class="today-schedule">
                    <h3>Horario de Hoy</h3>
                    <div class="schedule-grid">
                        ${todaySchedule.map(classItem => `
                            <div class="schedule-item ${classItem.is_current ? 'current' : ''} ${classItem.is_next ? 'next' : ''}">
                                <div class="time">${classItem.start_time} - ${classItem.end_time}</div>
                                <div class="subject">${classItem.subject}</div>
                                <div class="section">${classItem.section}</div>
                                <div class="classroom">${classItem.classroom}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderAdminDashboard(data) {
        const overview = data.platform_overview || {};
        const criticalConflicts = data.critical_conflicts || [];
        const teacherAlerts = data.teacher_alerts || [];

        return `
            <div class="dashboard-container admin">
                <div class="dashboard-header">
                    <h1>Panel Administrativo</h1>
                    <p class="dashboard-subtitle">Gestión de Horarios - ${this.formatDate(new Date())}</p>
                </div>

                <div class="admin-stats">
                    <div class="stat-card">
                        <div class="stat-value">${overview.total_assignments || 0}</div>
                        <div class="stat-label">Asignaciones Totales</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${overview.total_conflicts || 0}</div>
                        <div class="stat-label">Conflictos Activos</div>
                    </div>
                    <div class="stat-card ${overview.critical_conflicts > 0 ? 'critical' : ''}">
                        <div class="stat-value">${overview.critical_conflicts || 0}</div>
                        <div class="stat-label">Conflictos Críticos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${overview.conflict_rate || 0}%</div>
                        <div class="stat-label">Tasa de Conflictos</div>
                    </div>
                </div>

                <div class="admin-grid">
                    <div class="admin-card critical-conflicts">
                        <h3>Conflictos Críticos</h3>
                        ${criticalConflicts.length > 0 ? `
                            <div class="conflict-list">
                                ${criticalConflicts.map(conflict => `
                                    <div class="conflict-item critical">
                                        <div class="conflict-type">${this.formatConflictType(conflict.type)}</div>
                                        <div class="conflict-desc">${conflict.description}</div>
                                        <div class="conflict-time">${this.formatDateTime(conflict.detected_at)}</div>
                                        <button class="btn btn-sm btn-resolve" data-conflict-id="${conflict.id}">
                                            Resolver
                                        </button>
                                    </div>
                                `).join('')}
                            </div>
                        ` : `
                            <div class="no-conflicts">
                                <p>✅ No hay conflictos críticos</p>
                            </div>
                        `}
                    </div>

                    <div class="admin-card teacher-alerts">
                        <h3>Alertas de Docentes</h3>
                        ${teacherAlerts.length > 0 ? `
                            <div class="alert-list">
                                ${teacherAlerts.map(alert => `
                                    <div class="alert-item">
                                        <div class="teacher-name">${alert.teacher_name}</div>
                                        <div class="alert-details">
                                            <span class="hours">${alert.current_hours}/${alert.max_hours} horas</span>
                                            <span class="excess">+${alert.excess_hours} exceso</span>
                                        </div>
                                        <button class="btn btn-sm btn-view" data-teacher-id="${alert.teacher_id}">
                                            Ver Horario
                                        </button>
                                    </div>
                                `).join('')}
                            </div>
                        ` : `
                            <div class="no-alerts">
                                <p>✅ Todas las cargas horarias son válidas</p>
                            </div>
                        `}
                    </div>
                </div>

                <div class="admin-actions">
                    <button class="btn btn-primary" data-route="/schedule">
                        📅 Gestionar Horarios
                    </button>
                    <button class="btn btn-secondary" data-route="/teachers">
                        👨‍🏫 Gestionar Docentes
                    </button>
                    <button class="btn btn-secondary" data-route="/reports">
                        📊 Generar Reportes
                    </button>
                </div>
            </div>
        `;
    }

    // =====================================================
    // UTILITY FUNCTIONS
    // =====================================================

    setMainContent(html) {
        const main = document.getElementById('main-content') || document.body;
        main.innerHTML = html;
    }

    setPageTitle(title) {
        document.title = title;
    }

    updateNavigation() {
        const nav = document.getElementById('main-navigation');
        if (nav && this.currentUser) {
            nav.innerHTML = this.renderNavigation();
        }
    }

    renderNavigation() {
        const userRole = this.currentUser.role;

        return `
            <nav class="main-nav">
                <div class="nav-brand">
                    <span class="brand-text">BiScheduler</span>
                    <span class="brand-subtitle">🇻🇪 K12</span>
                </div>

                <div class="nav-items">
                    <a href="#" data-route="/" class="nav-item">
                        📊 Panel
                    </a>
                    <a href="#" data-route="/schedule" class="nav-item">
                        📅 Horarios
                    </a>
                    ${userRole !== 'teacher' ? `
                        <a href="#" data-route="/teachers" class="nav-item">
                            👨‍🏫 Docentes
                        </a>
                        <a href="#" data-route="/conflicts" class="nav-item">
                            ⚠️ Conflictos
                        </a>
                        <a href="#" data-route="/reports" class="nav-item">
                            📊 Reportes
                        </a>
                    ` : ''}
                    ${userRole === 'platform_admin' ? `
                        <a href="#" data-route="/admin" class="nav-item">
                            ⚙️ Admin
                        </a>
                    ` : ''}
                </div>

                <div class="nav-user">
                    <div class="user-info">
                        <span class="user-name">${this.currentUser.first_name}</span>
                        <span class="user-role">${this.currentUser.display_role}</span>
                    </div>
                    <button class="btn btn-logout" onclick="app.logout()">
                        Salir
                    </button>
                </div>
            </nav>
        `;
    }

    renderErrorMessage(message) {
        return `
            <div class="error-container">
                <div class="error-card">
                    <h2>Error</h2>
                    <p>${message}</p>
                    <button class="btn btn-primary" onclick="location.reload()">
                        Recargar Página
                    </button>
                </div>
            </div>
        `;
    }

    async handleFormSubmission(form) {
        const formData = new FormData(form);
        const action = form.getAttribute('data-action');

        if (action === 'login') {
            const email = formData.get('email');
            const password = formData.get('password');
            const tenantId = formData.get('tenant_id');

            await this.login(email, password, tenantId);
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    updateConflictIndicators(conflicts) {
        // Update conflict indicators in real-time
        const indicators = document.querySelectorAll('.conflict-indicator');
        indicators.forEach(indicator => {
            indicator.textContent = conflicts.total_conflicts || 0;
            indicator.className = `conflict-indicator ${conflicts.total_conflicts > 0 ? 'has-conflicts' : ''}`;
        });
    }

    updateWorkloadAlerts(alerts) {
        // Update workload alerts in real-time
        const alertContainer = document.querySelector('.workload-alerts');
        if (alertContainer && alerts.alerts) {
            alertContainer.innerHTML = `
                <span class="alert-count">${alerts.alerts.length}</span>
                <span class="alert-text">alertas activas</span>
            `;
        }
    }

    formatDate(date) {
        return new Intl.DateTimeFormat('es-VE', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(date);
    }

    formatDateTime(isoString) {
        const date = new Date(isoString);
        return new Intl.DateTimeFormat('es-VE', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    formatConflictType(type) {
        const types = {
            'teacher_double_booking': 'Docente Doble Asignación',
            'classroom_conflict': 'Conflicto de Aula',
            'section_overlap': 'Solapamiento de Sección',
            'workload_violation': 'Violación de Carga',
            'teacher_subject_mismatch': 'Materia No Asignada'
        };
        return types[type] || type;
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BiSchedulerApp();
});

// Global error handler
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    if (window.app) {
        window.app.showNotification('Error de aplicación', 'error');
    }
});