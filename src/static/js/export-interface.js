/**
 * BiScheduler Venezuelan Schedule Export Interface
 * User-friendly export functionality for Venezuelan educational formats
 * Supports Excel (HORARIO), CSV, and CARGA HORARIA formats
 */

class ExportInterface {
    constructor() {
        this.apiBase = '/api/schedule/export';
        this.supportedFormats = {
            'horario_excel': {
                name: 'Horario Completo (Excel)',
                description: 'Horario completo en formato Excel venezolano',
                extension: 'xlsx',
                icon: 'fas fa-file-excel',
                color: '#1f7244'
            },
            'carga_horaria': {
                name: 'Carga Horaria (Excel)',
                description: 'Resumen de carga horaria por profesor',
                extension: 'xlsx',
                icon: 'fas fa-chart-bar',
                color: '#c65911'
            },
            'horario_csv': {
                name: 'Horario (CSV)',
                description: 'Datos del horario en formato CSV',
                extension: 'csv',
                icon: 'fas fa-file-csv',
                color: '#28a745'
            },
            'section_schedule': {
                name: 'Horario por Sección (PDF)',
                description: 'Horario individual de cada sección',
                extension: 'pdf',
                icon: 'fas fa-file-pdf',
                color: '#dc3545'
            },
            'teacher_schedule': {
                name: 'Horario por Profesor (PDF)',
                description: 'Horario individual de cada profesor',
                extension: 'pdf',
                icon: 'fas fa-user-tie',
                color: '#007bff'
            }
        };

        this.exportQueue = [];
        this.activeExports = new Map();

        this.init();
    }

    init() {
        this.createExportModal();
        this.attachEventHandlers();
    }

    createExportModal() {
        const modalHTML = `
            <div id="export-modal" class="modal" style="display: none;">
                <div class="modal-overlay" onclick="exportInterface.closeModal()"></div>
                <div class="modal-container export-modal-container">
                    <div class="modal-header">
                        <h2><i class="fas fa-download"></i> Exportar Horarios</h2>
                        <button class="modal-close" onclick="exportInterface.closeModal()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-content">
                        <div class="export-wizard">
                            <!-- Step 1: Format Selection -->
                            <div class="export-step active" id="step-format">
                                <div class="step-header">
                                    <h3>1. Seleccionar Formato</h3>
                                    <p>Elige el tipo de reporte que deseas generar</p>
                                </div>
                                <div class="format-grid">
                                    ${this.renderFormatOptions()}
                                </div>
                            </div>

                            <!-- Step 2: Configuration -->
                            <div class="export-step" id="step-config">
                                <div class="step-header">
                                    <h3>2. Configurar Exportación</h3>
                                    <p>Personaliza los parámetros del reporte</p>
                                </div>
                                <div class="config-form">
                                    <div class="form-group">
                                        <label for="academic-year">Año Académico:</label>
                                        <select id="academic-year" class="form-control">
                                            <option value="2025-2026">2025-2026</option>
                                            <option value="2024-2025">2024-2025</option>
                                        </select>
                                    </div>

                                    <div class="form-group">
                                        <label for="export-scope">Alcance de Exportación:</label>
                                        <select id="export-scope" class="form-control">
                                            <option value="all">Todos los datos</option>
                                            <option value="sections">Solo secciones específicas</option>
                                            <option value="teachers">Solo profesores específicos</option>
                                            <option value="subjects">Solo materias específicas</option>
                                        </select>
                                    </div>

                                    <!-- Dynamic filters based on scope -->
                                    <div id="scope-filters" class="scope-filters">
                                        <!-- Will be populated dynamically -->
                                    </div>

                                    <div class="form-group">
                                        <label for="include-conflicts">
                                            <input type="checkbox" id="include-conflicts" checked>
                                            Incluir indicadores de conflictos
                                        </label>
                                    </div>

                                    <div class="form-group">
                                        <label for="include-workload">
                                            <input type="checkbox" id="include-workload" checked>
                                            Incluir datos de carga horaria
                                        </label>
                                    </div>

                                    <div class="form-group">
                                        <label for="report-title">Título del Reporte:</label>
                                        <input type="text" id="report-title" class="form-control"
                                               placeholder="Ej: Horario Escolar 2025-2026">
                                    </div>

                                    <div class="form-group">
                                        <label for="institution-name">Nombre de la Institución:</label>
                                        <input type="text" id="institution-name" class="form-control"
                                               placeholder="Ej: U.E.I.P. Antonio Bello">
                                    </div>
                                </div>
                            </div>

                            <!-- Step 3: Preview -->
                            <div class="export-step" id="step-preview">
                                <div class="step-header">
                                    <h3>3. Vista Previa</h3>
                                    <p>Revisa la configuración antes de generar el reporte</p>
                                </div>
                                <div class="preview-content">
                                    <!-- Will be populated with preview data -->
                                </div>
                            </div>

                            <!-- Step 4: Export Progress -->
                            <div class="export-step" id="step-progress">
                                <div class="step-header">
                                    <h3>4. Generando Reporte</h3>
                                    <p>Por favor espera mientras se procesa tu solicitud</p>
                                </div>
                                <div class="progress-content">
                                    <div class="export-progress">
                                        <div class="progress-bar">
                                            <div class="progress-fill" id="export-progress-fill"></div>
                                        </div>
                                        <div class="progress-text" id="export-progress-text">Iniciando...</div>
                                    </div>
                                    <div class="progress-details" id="export-progress-details">
                                        <!-- Progress details will be shown here -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <div class="export-actions">
                            <button id="btn-previous" class="btn btn-secondary" onclick="exportInterface.previousStep()" style="display: none;">
                                <i class="fas fa-arrow-left"></i> Anterior
                            </button>
                            <button id="btn-next" class="btn btn-primary" onclick="exportInterface.nextStep()">
                                Siguiente <i class="fas fa-arrow-right"></i>
                            </button>
                            <button id="btn-export" class="btn btn-success" onclick="exportInterface.startExport()" style="display: none;">
                                <i class="fas fa-download"></i> Exportar
                            </button>
                            <button id="btn-cancel" class="btn btn-outline-secondary" onclick="exportInterface.closeModal()">
                                Cancelar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    renderFormatOptions() {
        return Object.entries(this.supportedFormats).map(([key, format]) => `
            <div class="format-option" data-format="${key}">
                <div class="format-icon" style="color: ${format.color};">
                    <i class="${format.icon}"></i>
                </div>
                <div class="format-info">
                    <h4>${format.name}</h4>
                    <p>${format.description}</p>
                    <span class="format-extension">.${format.extension}</span>
                </div>
                <div class="format-selection">
                    <i class="fas fa-check-circle"></i>
                </div>
            </div>
        `).join('');
    }

    attachEventHandlers() {
        // Format selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.format-option')) {
                this.selectFormat(e.target.closest('.format-option'));
            }
        });

        // Scope selection changes
        document.addEventListener('change', (e) => {
            if (e.target.id === 'export-scope') {
                this.updateScopeFilters(e.target.value);
            }
        });

        // Quick export buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-quick-export]')) {
                const format = e.target.closest('[data-quick-export]').dataset.quickExport;
                this.quickExport(format);
            }
        });
    }

    openModal() {
        const modal = document.getElementById('export-modal');
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';

        // Reset wizard to first step
        this.currentStep = 1;
        this.selectedFormat = null;
        this.updateWizardStep();
    }

    closeModal() {
        const modal = document.getElementById('export-modal');
        modal.style.display = 'none';
        document.body.style.overflow = '';

        // Cancel any ongoing exports
        this.cancelActiveExports();
    }

    selectFormat(formatElement) {
        // Remove previous selection
        document.querySelectorAll('.format-option').forEach(option => {
            option.classList.remove('selected');
        });

        // Add selection to clicked format
        formatElement.classList.add('selected');
        this.selectedFormat = formatElement.dataset.format;

        // Enable next button
        document.getElementById('btn-next').disabled = false;
    }

    nextStep() {
        if (this.currentStep < 4) {
            this.currentStep++;
            this.updateWizardStep();
        }
    }

    previousStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateWizardStep();
        }
    }

    updateWizardStep() {
        // Hide all steps
        document.querySelectorAll('.export-step').forEach(step => {
            step.classList.remove('active');
        });

        // Show current step
        document.getElementById(`step-${this.getStepName(this.currentStep)}`).classList.add('active');

        // Update navigation buttons
        this.updateNavigationButtons();

        // Load step-specific content
        this.loadStepContent();
    }

    getStepName(stepNumber) {
        const steps = ['format', 'config', 'preview', 'progress'];
        return steps[stepNumber - 1];
    }

    updateNavigationButtons() {
        const btnPrevious = document.getElementById('btn-previous');
        const btnNext = document.getElementById('btn-next');
        const btnExport = document.getElementById('btn-export');

        // Previous button
        btnPrevious.style.display = this.currentStep > 1 ? 'inline-block' : 'none';

        // Next button
        if (this.currentStep < 3) {
            btnNext.style.display = 'inline-block';
            btnNext.disabled = this.currentStep === 1 && !this.selectedFormat;
        } else {
            btnNext.style.display = 'none';
        }

        // Export button
        btnExport.style.display = this.currentStep === 3 ? 'inline-block' : 'none';
    }

    loadStepContent() {
        switch (this.currentStep) {
            case 2:
                this.loadConfigurationStep();
                break;
            case 3:
                this.loadPreviewStep();
                break;
            case 4:
                // Progress step is handled in startExport()
                break;
        }
    }

    async loadConfigurationStep() {
        // Load available sections, teachers, and subjects for filters
        try {
            const [sections, teachers, subjects] = await Promise.all([
                this.fetchSections(),
                this.fetchTeachers(),
                this.fetchSubjects()
            ]);

            // Store for use in filters
            this.availableData = { sections, teachers, subjects };

            // Set default values
            this.setDefaultConfiguration();

        } catch (error) {
            console.error('Error loading configuration data:', error);
            this.showError('Error al cargar datos de configuración');
        }
    }

    setDefaultConfiguration() {
        // Set default institution name from tenant data
        if (window.currentTenant) {
            document.getElementById('institution-name').value = window.currentTenant.name || '';
        }

        // Set default report title based on selected format
        const format = this.supportedFormats[this.selectedFormat];
        const currentYear = new Date().getFullYear();
        document.getElementById('report-title').value =
            `${format.name} ${currentYear}-${currentYear + 1}`;
    }

    updateScopeFilters(scope) {
        const filtersContainer = document.getElementById('scope-filters');

        switch (scope) {
            case 'sections':
                filtersContainer.innerHTML = this.renderSectionFilters();
                break;
            case 'teachers':
                filtersContainer.innerHTML = this.renderTeacherFilters();
                break;
            case 'subjects':
                filtersContainer.innerHTML = this.renderSubjectFilters();
                break;
            default:
                filtersContainer.innerHTML = '';
        }
    }

    renderSectionFilters() {
        const sections = this.availableData?.sections || [];
        return `
            <div class="form-group">
                <label>Secciones a incluir:</label>
                <div class="checkbox-grid">
                    ${sections.map(section => `
                        <label class="checkbox-item">
                            <input type="checkbox" name="selected-sections" value="${section.id}" checked>
                            ${section.name}
                        </label>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderTeacherFilters() {
        const teachers = this.availableData?.teachers || [];
        return `
            <div class="form-group">
                <label>Profesores a incluir:</label>
                <div class="checkbox-grid">
                    ${teachers.map(teacher => `
                        <label class="checkbox-item">
                            <input type="checkbox" name="selected-teachers" value="${teacher.id}" checked>
                            ${teacher.teacher_name}
                        </label>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderSubjectFilters() {
        const subjects = this.availableData?.subjects || [];
        return `
            <div class="form-group">
                <label>Materias a incluir:</label>
                <div class="checkbox-grid">
                    ${subjects.map(subject => `
                        <label class="checkbox-item">
                            <input type="checkbox" name="selected-subjects" value="${subject.id}" checked>
                            ${subject.subject_name}
                        </label>
                    `).join('')}
                </div>
            </div>
        `;
    }

    loadPreviewStep() {
        const config = this.getExportConfiguration();
        const format = this.supportedFormats[this.selectedFormat];

        const previewContent = document.querySelector('.preview-content');
        previewContent.innerHTML = `
            <div class="preview-summary">
                <div class="preview-header">
                    <div class="format-preview">
                        <i class="${format.icon}" style="color: ${format.color};"></i>
                        <div>
                            <h4>${format.name}</h4>
                            <p>${format.description}</p>
                        </div>
                    </div>
                </div>

                <div class="preview-details">
                    <div class="detail-group">
                        <h5>Configuración General</h5>
                        <ul>
                            <li><strong>Año Académico:</strong> ${config.academicYear}</li>
                            <li><strong>Alcance:</strong> ${this.getScopeDescription(config.scope)}</li>
                            <li><strong>Título:</strong> ${config.reportTitle}</li>
                            <li><strong>Institución:</strong> ${config.institutionName}</li>
                        </ul>
                    </div>

                    <div class="detail-group">
                        <h5>Opciones Incluidas</h5>
                        <ul>
                            <li>
                                <i class="fas fa-${config.includeConflicts ? 'check' : 'times'}"
                                   style="color: ${config.includeConflicts ? 'green' : 'red'};"></i>
                                Indicadores de conflictos
                            </li>
                            <li>
                                <i class="fas fa-${config.includeWorkload ? 'check' : 'times'}"
                                   style="color: ${config.includeWorkload ? 'green' : 'red'};"></i>
                                Datos de carga horaria
                            </li>
                        </ul>
                    </div>

                    ${this.renderScopePreview(config)}
                </div>

                <div class="preview-warning">
                    <i class="fas fa-info-circle"></i>
                    <p>La generación del reporte puede tomar algunos minutos dependiendo de la cantidad de datos.</p>
                </div>
            </div>
        `;
    }

    getScopeDescription(scope) {
        const descriptions = {
            'all': 'Todos los datos disponibles',
            'sections': 'Secciones específicas',
            'teachers': 'Profesores específicos',
            'subjects': 'Materias específicas'
        };
        return descriptions[scope] || scope;
    }

    renderScopePreview(config) {
        if (config.scope === 'all') {
            return '';
        }

        const selectedItems = config.selectedItems || [];
        const itemType = config.scope.slice(0, -1); // Remove 's' from end

        return `
            <div class="detail-group">
                <h5>${this.getScopeDescription(config.scope)} Seleccionadas</h5>
                <div class="selected-items">
                    ${selectedItems.length > 0 ?
                        selectedItems.slice(0, 5).map(item => `<span class="item-tag">${item.name}</span>`).join('') +
                        (selectedItems.length > 5 ? `<span class="item-count">+${selectedItems.length - 5} más</span>` : '')
                        : '<em>Ningún elemento seleccionado</em>'
                    }
                </div>
            </div>
        `;
    }

    getExportConfiguration() {
        return {
            format: this.selectedFormat,
            academicYear: document.getElementById('academic-year')?.value || '2025-2026',
            scope: document.getElementById('export-scope')?.value || 'all',
            reportTitle: document.getElementById('report-title')?.value || '',
            institutionName: document.getElementById('institution-name')?.value || '',
            includeConflicts: document.getElementById('include-conflicts')?.checked || false,
            includeWorkload: document.getElementById('include-workload')?.checked || false,
            selectedItems: this.getSelectedItems()
        };
    }

    getSelectedItems() {
        const scope = document.getElementById('export-scope')?.value;
        if (scope === 'all') return [];

        const fieldName = `selected-${scope}`;
        const checkboxes = document.querySelectorAll(`input[name="${fieldName}"]:checked`);

        return Array.from(checkboxes).map(cb => ({
            id: cb.value,
            name: cb.closest('label').textContent.trim()
        }));
    }

    async startExport() {
        this.currentStep = 4;
        this.updateWizardStep();

        const config = this.getExportConfiguration();
        const exportId = this.generateExportId();

        try {
            // Add to active exports
            this.activeExports.set(exportId, {
                config,
                startTime: new Date(),
                status: 'starting'
            });

            // Update progress
            this.updateExportProgress(0, 'Preparando exportación...');

            // Start the export process
            const result = await this.performExport(config, exportId);

            // Handle successful export
            this.handleExportSuccess(result, exportId);

        } catch (error) {
            console.error('Export failed:', error);
            this.handleExportError(error, exportId);
        }
    }

    async performExport(config, exportId) {
        const endpoint = `${this.apiBase}/${config.format}`;

        // Prepare request payload
        const payload = {
            academic_year: config.academicYear,
            scope: config.scope,
            include_conflicts: config.includeConflicts,
            include_workload: config.includeWorkload,
            report_title: config.reportTitle,
            institution_name: config.institutionName,
            export_id: exportId
        };

        // Add selected items if scope is not 'all'
        if (config.scope !== 'all') {
            payload.selected_items = config.selectedItems.map(item => item.id);
        }

        // Simulate progress updates
        const progressUpdates = [
            { progress: 20, message: 'Consultando datos del horario...' },
            { progress: 40, message: 'Procesando asignaciones...' },
            { progress: 60, message: 'Generando formato de salida...' },
            { progress: 80, message: 'Aplicando formato venezolano...' },
            { progress: 95, message: 'Finalizando reporte...' }
        ];

        // Update progress incrementally
        for (const update of progressUpdates) {
            await new Promise(resolve => setTimeout(resolve, 500));
            this.updateExportProgress(update.progress, update.message);
        }

        // Make the actual API call
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'X-Tenant-ID': window.currentTenant?.id
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Export failed: ${response.statusText}`);
        }

        // Get the response data
        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('application/json')) {
            // JSON response with download URL
            return await response.json();
        } else {
            // Direct file download
            const blob = await response.blob();
            const filename = this.getExportFilename(config);
            return { blob, filename };
        }
    }

    updateExportProgress(progress, message) {
        const progressFill = document.getElementById('export-progress-fill');
        const progressText = document.getElementById('export-progress-text');
        const progressDetails = document.getElementById('export-progress-details');

        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }

        if (progressText) {
            progressText.textContent = message;
        }

        if (progressDetails) {
            const timestamp = new Date().toLocaleTimeString('es-VE');
            progressDetails.innerHTML += `<div class="progress-log">${timestamp}: ${message}</div>`;
            progressDetails.scrollTop = progressDetails.scrollHeight;
        }
    }

    handleExportSuccess(result, exportId) {
        this.updateExportProgress(100, 'Exportación completada');

        // Update active export status
        const exportData = this.activeExports.get(exportId);
        if (exportData) {
            exportData.status = 'completed';
            exportData.result = result;
        }

        setTimeout(() => {
            if (result.download_url) {
                // Download from URL
                this.downloadFromUrl(result.download_url, result.filename);
            } else if (result.blob) {
                // Direct blob download
                this.downloadBlob(result.blob, result.filename);
            }

            // Show success message
            this.showExportSuccess(result);

            // Close modal after download
            setTimeout(() => {
                this.closeModal();
            }, 2000);

        }, 1000);
    }

    handleExportError(error, exportId) {
        // Update active export status
        const exportData = this.activeExports.get(exportId);
        if (exportData) {
            exportData.status = 'failed';
            exportData.error = error;
        }

        // Show error in progress step
        const progressContent = document.querySelector('.progress-content');
        progressContent.innerHTML = `
            <div class="export-error">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h4>Error en la Exportación</h4>
                <p>${error.message || 'Ha ocurrido un error inesperado durante la exportación.'}</p>
                <div class="error-actions">
                    <button class="btn btn-primary" onclick="exportInterface.previousStep()">
                        <i class="fas fa-arrow-left"></i> Volver a Intentar
                    </button>
                    <button class="btn btn-secondary" onclick="exportInterface.closeModal()">
                        Cerrar
                    </button>
                </div>
            </div>
        `;
    }

    showExportSuccess(result) {
        const progressContent = document.querySelector('.progress-content');
        progressContent.innerHTML = `
            <div class="export-success">
                <div class="success-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h4>Exportación Completada</h4>
                <p>El reporte ha sido generado exitosamente.</p>
                <div class="download-info">
                    <i class="fas fa-download"></i>
                    <span>La descarga debería comenzar automáticamente...</span>
                </div>
            </div>
        `;
    }

    downloadFromUrl(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename || 'horario_export';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        this.downloadFromUrl(url, filename);
        window.URL.revokeObjectURL(url);
    }

    getExportFilename(config) {
        const format = this.supportedFormats[config.format];
        const timestamp = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
        const baseName = config.reportTitle.replace(/[^a-zA-Z0-9]/g, '_') || 'horario_export';

        return `${baseName}_${timestamp}.${format.extension}`;
    }

    generateExportId() {
        return `export_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Quick export functions for common formats
    quickExport(format) {
        this.selectedFormat = format;

        // Use default configuration
        const config = {
            format: format,
            academicYear: '2025-2026',
            scope: 'all',
            reportTitle: this.supportedFormats[format].name,
            institutionName: window.currentTenant?.name || '',
            includeConflicts: true,
            includeWorkload: true,
            selectedItems: []
        };

        // Start export directly
        this.startQuickExport(config);
    }

    async startQuickExport(config) {
        const exportId = this.generateExportId();

        try {
            // Show quick export notification
            this.showQuickExportNotification('Iniciando exportación...');

            // Perform export
            const result = await this.performExport(config, exportId);

            // Handle download
            if (result.download_url) {
                this.downloadFromUrl(result.download_url, result.filename);
            } else if (result.blob) {
                this.downloadBlob(result.blob, result.filename);
            }

            // Show success notification
            this.showQuickExportNotification('Exportación completada', 'success');

        } catch (error) {
            console.error('Quick export failed:', error);
            this.showQuickExportNotification('Error en la exportación', 'error');
        }
    }

    showQuickExportNotification(message, type = 'info') {
        // Create or update notification
        let notification = document.getElementById('quick-export-notification');

        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'quick-export-notification';
            notification.className = 'quick-export-notification';
            document.body.appendChild(notification);
        }

        notification.className = `quick-export-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : 'spinner fa-spin'}"></i>
                <span>${message}</span>
            </div>
        `;

        // Auto-hide after 3 seconds
        setTimeout(() => {
            if (notification && notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    // API helper methods
    async fetchSections() {
        try {
            const response = await fetch('/api/sections', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'X-Tenant-ID': window.currentTenant?.id
                }
            });

            if (response.ok) {
                const data = await response.json();
                return data.sections || [];
            } else {
                throw new Error('Failed to fetch sections');
            }
        } catch (error) {
            console.error('Error fetching sections:', error);
            return [];
        }
    }

    async fetchTeachers() {
        try {
            const response = await fetch('/api/teachers', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'X-Tenant-ID': window.currentTenant?.id
                }
            });

            if (response.ok) {
                const data = await response.json();
                return data.teachers || [];
            } else {
                throw new Error('Failed to fetch teachers');
            }
        } catch (error) {
            console.error('Error fetching teachers:', error);
            return [];
        }
    }

    async fetchSubjects() {
        try {
            const response = await fetch('/api/subjects', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'X-Tenant-ID': window.currentTenant?.id
                }
            });

            if (response.ok) {
                const data = await response.json();
                return data.subjects || [];
            } else {
                throw new Error('Failed to fetch subjects');
            }
        } catch (error) {
            console.error('Error fetching subjects:', error);
            return [];
        }
    }

    showError(message) {
        console.error(message);
        // You could show a toast notification or modal here
    }

    cancelActiveExports() {
        // Cancel any ongoing exports
        this.activeExports.forEach((exportData, exportId) => {
            if (exportData.status === 'starting' || exportData.status === 'in_progress') {
                exportData.status = 'cancelled';
            }
        });
    }

    // Public method to add quick export buttons to the UI
    addQuickExportButtons(container) {
        const buttonsHTML = `
            <div class="quick-export-buttons">
                <h4>Exportación Rápida</h4>
                <div class="quick-buttons-grid">
                    <button class="quick-export-btn" data-quick-export="horario_excel">
                        <i class="fas fa-file-excel"></i>
                        <span>Horario Completo</span>
                    </button>
                    <button class="quick-export-btn" data-quick-export="carga_horaria">
                        <i class="fas fa-chart-bar"></i>
                        <span>Carga Horaria</span>
                    </button>
                    <button class="quick-export-btn" data-quick-export="horario_csv">
                        <i class="fas fa-file-csv"></i>
                        <span>Datos CSV</span>
                    </button>
                </div>
                <button class="btn btn-primary btn-lg export-wizard-btn" onclick="exportInterface.openModal()">
                    <i class="fas fa-cog"></i> Exportación Avanzada
                </button>
            </div>
        `;

        if (typeof container === 'string') {
            container = document.querySelector(container);
        }

        if (container) {
            container.innerHTML = buttonsHTML;
        }
    }
}

// Export for global use
window.ExportInterface = ExportInterface;

// Auto-initialize when script loads
document.addEventListener('DOMContentLoaded', () => {
    if (!window.exportInterface) {
        window.exportInterface = new ExportInterface();
    }
});