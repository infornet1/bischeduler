// Schedule Optimizer JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Configuration
    let optimizationConfig = {};
    let currentOptimizationId = null;
    let optimizationTimer = null;
    let startTime = null;

    // Algorithm descriptions
    const algorithmDescriptions = {
        'genetic': 'Evolutionary optimization using natural selection principles',
        'constraint': 'CSP solver with backtracking and local search optimization',
        'hybrid': 'Combines genetic algorithm with constraint solving for best results'
    };

    // Initialize
    init();

    function init() {
        loadConfiguration();
        setupEventListeners();
        updateAlgorithmParams();
    }

    function setupEventListeners() {
        // Algorithm selection
        document.getElementById('algorithm').addEventListener('change', function() {
            updateAlgorithmParams();
            document.getElementById('algorithmDescription').textContent =
                algorithmDescriptions[this.value];
        });

        // Weight sliders
        document.querySelectorAll('input[type="range"]').forEach(slider => {
            slider.addEventListener('input', function() {
                const valueSpan = this.parentElement.querySelector('.weight-value');
                if (valueSpan) {
                    valueSpan.textContent = this.value + '%';
                }
            });
        });

        // Buttons
        document.getElementById('startOptimization').addEventListener('click', startOptimization);
        document.getElementById('loadDefaults').addEventListener('click', loadDefaults);

        // Note: Theme toggle handled in HTML inline script for consistency
    }

    function updateAlgorithmParams() {
        const algorithm = document.getElementById('algorithm').value;

        // Hide all parameter sections
        document.getElementById('geneticParams').style.display = 'none';
        document.getElementById('constraintParams').style.display = 'none';

        // Show relevant parameters
        if (algorithm === 'genetic' || algorithm === 'hybrid') {
            document.getElementById('geneticParams').style.display = 'block';
        }
        if (algorithm === 'constraint' || algorithm === 'hybrid') {
            document.getElementById('constraintParams').style.display = 'block';
        }
    }

    async function loadConfiguration() {
        try {
            const response = await fetch('/api/schedule/optimize/config', {
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('token')
                }
            });

            if (response.ok) {
                optimizationConfig = await response.json();
                applyConfiguration(optimizationConfig);
            }
        } catch (error) {
            console.error('Error loading configuration:', error);
        }
    }

    function applyConfiguration(config) {
        // Apply weights
        if (config.weights) {
            document.getElementById('weightPreferences').value = config.weights.preferences * 100;
            document.getElementById('weightWorkload').value = config.weights.workload * 100;
            document.getElementById('weightConflicts').value = config.weights.conflicts * 100;
            document.getElementById('weightContinuity').value = config.weights.continuity * 100;

            // Update displayed values
            document.querySelectorAll('input[type="range"]').forEach(slider => {
                const valueSpan = slider.parentElement.querySelector('.weight-value');
                if (valueSpan) {
                    valueSpan.textContent = slider.value + '%';
                }
            });
        }

        // Apply constraints
        if (config.constraints) {
            document.getElementById('maxDailyTeacher').value = config.constraints.max_daily_hours_teacher;
            document.getElementById('maxWeeklyTeacher').value = config.constraints.max_weekly_hours_teacher;
            document.getElementById('maxConsecutive').value = config.constraints.max_consecutive_hours;
            document.getElementById('maxDailySection').value = config.constraints.max_daily_hours_section;
        }
    }

    function loadDefaults() {
        // Reset to default values
        document.getElementById('algorithm').value = 'genetic';
        document.getElementById('populationSize').value = 100;
        document.getElementById('generations').value = 500;
        document.getElementById('mutationRate').value = 0.02;
        document.getElementById('crossoverRate').value = 0.8;
        document.getElementById('elitismRate').value = 0.1;
        document.getElementById('iterations').value = 100;
        document.getElementById('backtrackLimit').value = 10000;

        // Reset weights
        document.getElementById('weightPreferences').value = 40;
        document.getElementById('weightWorkload').value = 20;
        document.getElementById('weightConflicts').value = 30;
        document.getElementById('weightContinuity').value = 10;

        // Reset constraints
        document.getElementById('maxDailyTeacher').value = 6;
        document.getElementById('maxWeeklyTeacher').value = 30;
        document.getElementById('maxConsecutive').value = 3;
        document.getElementById('maxDailySection').value = 8;

        // Update displayed values
        document.querySelectorAll('input[type="range"]').forEach(slider => {
            const valueSpan = slider.parentElement.querySelector('.weight-value');
            if (valueSpan) {
                valueSpan.textContent = slider.value + '%';
            }
        });

        updateAlgorithmParams();
    }

    async function startOptimization() {
        // Gather parameters
        const algorithm = document.getElementById('algorithm').value;
        const parameters = {};
        const constraints = {};

        // Genetic algorithm parameters
        if (algorithm === 'genetic' || algorithm === 'hybrid') {
            parameters.population_size = parseInt(document.getElementById('populationSize').value);
            parameters.generations = parseInt(document.getElementById('generations').value);
            parameters.mutation_rate = parseFloat(document.getElementById('mutationRate').value);
            parameters.crossover_rate = parseFloat(document.getElementById('crossoverRate').value);
            parameters.elitism_rate = parseFloat(document.getElementById('elitismRate').value);
        }

        // Constraint solver parameters
        if (algorithm === 'constraint' || algorithm === 'hybrid') {
            parameters.iterations = parseInt(document.getElementById('iterations').value);
            parameters.backtrack_limit = parseInt(document.getElementById('backtrackLimit').value);
        }

        // Constraints
        constraints.max_daily_hours_teacher = parseInt(document.getElementById('maxDailyTeacher').value);
        constraints.max_weekly_hours_teacher = parseInt(document.getElementById('maxWeeklyTeacher').value);
        constraints.max_consecutive_hours = parseInt(document.getElementById('maxConsecutive').value);
        constraints.max_daily_hours_section = parseInt(document.getElementById('maxDailySection').value);

        // Show loading
        showLoading();
        showProgressSection();

        // Start timer
        startTime = Date.now();
        updateTimer();
        optimizationTimer = setInterval(updateTimer, 1000);

        try {
            const response = await fetch('/api/schedule/optimize/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('token')
                },
                body: JSON.stringify({
                    algorithm: algorithm,
                    parameters: parameters,
                    constraints: constraints
                })
            });

            const result = await response.json();

            if (result.success) {
                currentOptimizationId = result.optimization_id;
                await showResults(result);
            } else {
                showError('Optimization failed: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Optimization error:', error);
            showError('Error during optimization: ' + error.message);
        } finally {
            hideLoading();
            clearInterval(optimizationTimer);
        }
    }

    function showProgressSection() {
        document.getElementById('progressSection').style.display = 'block';
        document.getElementById('resultsSection').style.display = 'none';

        // Simulate progress (in real implementation, this would be updated via WebSocket)
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 95) progress = 95;

            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('currentGeneration').textContent = Math.floor(progress * 5);
            document.getElementById('bestFitness').textContent = (progress / 100).toFixed(3);

            if (progress >= 95) {
                clearInterval(progressInterval);
            }
        }, 500);
    }

    async function showResults(result) {
        // Hide progress, show results
        document.getElementById('progressSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';

        // Update summary
        document.getElementById('finalFitness').textContent = result.fitness_score.toFixed(3);
        document.getElementById('assignmentCount').textContent = result.schedule_count;
        document.getElementById('prefSatisfaction').textContent =
            Math.round(result.fitness_score * 100) + '%';

        // Show violations
        const violationsList = document.getElementById('violationsList');
        violationsList.innerHTML = '';

        if (result.violations && result.violations.length > 0) {
            result.violations.forEach(violation => {
                const li = document.createElement('li');
                li.textContent = violation;
                violationsList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'No violations found - Perfect schedule!';
            li.style.color = '#4CAF50';
            violationsList.appendChild(li);
        }

        // Load preview
        if (currentOptimizationId) {
            await loadSchedulePreview(currentOptimizationId);
        }

        // Setup result buttons
        document.getElementById('applySchedule').onclick = applySchedule;
        document.getElementById('exportResults').onclick = exportResults;
        document.getElementById('reoptimize').onclick = () => {
            document.getElementById('resultsSection').style.display = 'none';
            window.scrollTo(0, 0);
        };
    }

    async function loadSchedulePreview(optimizationId) {
        try {
            const response = await fetch(`/api/schedule/optimize/preview/${optimizationId}`, {
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('token')
                }
            });

            if (response.ok) {
                const preview = await response.json();
                renderSchedulePreview(preview);
            }
        } catch (error) {
            console.error('Error loading preview:', error);
        }
    }

    function renderSchedulePreview(preview) {
        const container = document.getElementById('schedulePreview');

        // Create simple table preview
        let html = `
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Monday</th>
                        <th>Tuesday</th>
                        <th>Wednesday</th>
                        <th>Thursday</th>
                        <th>Friday</th>
                    </tr>
                </thead>
                <tbody>
        `;

        // Group assignments by time and day
        const schedule = {};
        preview.assignments.forEach(assignment => {
            const key = `${assignment.time_period}_${assignment.day}`;
            if (!schedule[key]) {
                schedule[key] = [];
            }
            schedule[key].push(assignment);
        });

        // Render rows (simplified)
        for (let period = 1; period <= 10; period++) {
            html += '<tr>';
            html += `<td>Period ${period}</td>`;

            for (let day = 0; day < 5; day++) {
                const key = `Period ${period}_${['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][day]}`;
                const assignments = schedule[key] || [];

                if (assignments.length > 0) {
                    html += '<td>';
                    assignments.forEach(a => {
                        html += `<div class="assignment-cell">
                            <strong>${a.subject}</strong><br>
                            ${a.teacher}<br>
                            ${a.section} - ${a.classroom}
                        </div>`;
                    });
                    html += '</td>';
                } else {
                    html += '<td>-</td>';
                }
            }
            html += '</tr>';
        }

        html += '</tbody></table>';
        container.innerHTML = html;
    }

    async function applySchedule() {
        if (!currentOptimizationId) {
            showError('No optimization to apply');
            return;
        }

        if (!confirm('Are you sure you want to apply this optimized schedule? This will replace the current active schedule.')) {
            return;
        }

        showLoading();

        try {
            const response = await fetch(`/api/schedule/optimize/apply/${currentOptimizationId}`, {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('token')
                }
            });

            const result = await response.json();

            if (result.success) {
                document.getElementById('successModal').style.display = 'block';
            } else {
                showError('Failed to apply schedule: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error applying schedule:', error);
            showError('Error applying schedule: ' + error.message);
        } finally {
            hideLoading();
        }
    }

    function exportResults() {
        // In a real implementation, this would export to Excel/PDF
        alert('Export functionality will be implemented soon!');
    }

    function updateTimer() {
        if (!startTime) return;

        const elapsed = Date.now() - startTime;
        const minutes = Math.floor(elapsed / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);

        document.getElementById('timeElapsed').textContent =
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    function showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    function hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    function showError(message) {
        alert('Error: ' + message);
    }

    // Theme management handled in HTML inline script for consistency with other pages
});

// Additional styling for schedule table
const style = document.createElement('style');
style.textContent = `
    .schedule-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }

    .schedule-table th, .schedule-table td {
        border: 1px solid var(--border-color, #ddd);
        padding: 0.5rem;
        text-align: center;
        color: var(--text-primary, #333);
    }

    .schedule-table th {
        background: var(--primary-color, #003366);
        color: white;
        font-weight: bold;
    }

    .assignment-cell {
        background: rgba(74, 144, 226, 0.1);
        padding: 0.25rem;
        border-radius: 4px;
        margin: 0.25rem 0;
        font-size: 0.85rem;
    }

    .assignment-cell strong {
        color: var(--primary-color, #003366);
    }

    [data-theme="dark"] .schedule-table th {
        background: var(--primary-color, #4A90E2);
    }

    [data-theme="dark"] .assignment-cell {
        background: rgba(74, 144, 226, 0.2);
    }

    [data-theme="dark"] .assignment-cell strong {
        color: var(--primary-color, #4A90E2);
    }
`;
document.head.appendChild(style);