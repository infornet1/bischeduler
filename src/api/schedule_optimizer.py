"""
Schedule Optimization API Endpoints
Venezuelan K12 Educational Institution Scheduling
"""

from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.master import Tenant
from src.models.tenant import (
    Schedule,
    ScheduleAssignment,
    Teacher,
    TeacherPreference,
    Subject,
    Section,
    Classroom,
    TimePeriod
)
from src.scheduling.genetic_algorithm import VenezuelanScheduleGA
from src.scheduling.constraint_solver import (
    VenezuelanConstraintSolver,
    TeacherConstraint,
    SectionConstraint,
    ClassroomConstraint,
    SubjectConstraint,
    ConstraintType,
    ConstraintPriority
)
from src.core.app import db
from functools import wraps
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

schedule_optimizer_bp = Blueprint('schedule_optimizer', __name__)

def tenant_required(f):
    """Decorator to ensure tenant context"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tenant_id = session.get('tenant_id')
        if not tenant_id:
            return jsonify({'error': 'No tenant selected'}), 400
        return f(*args, **kwargs)
    return decorated_function

@schedule_optimizer_bp.route('/api/schedule/optimize/config', methods=['GET'])
@jwt_required()
@tenant_required
def get_optimization_config():
    """Get current optimization configuration"""
    try:
        tenant_id = session.get('tenant_id')
        db_session = db.session

        # Get optimization parameters
        config = {
            'algorithms': [
                {
                    'id': 'genetic',
                    'name': 'Genetic Algorithm',
                    'description': 'Evolutionary optimization using natural selection',
                    'parameters': {
                        'population_size': 100,
                        'generations': 500,
                        'mutation_rate': 0.02,
                        'crossover_rate': 0.8,
                        'elitism_rate': 0.1
                    }
                },
                {
                    'id': 'constraint',
                    'name': 'Constraint Solver',
                    'description': 'CSP solver with backtracking and local search',
                    'parameters': {
                        'iterations': 100,
                        'backtrack_limit': 10000
                    }
                },
                {
                    'id': 'hybrid',
                    'name': 'Hybrid Approach',
                    'description': 'Combines genetic algorithm with constraint solving',
                    'parameters': {}
                }
            ],
            'weights': {
                'preferences': 0.4,
                'workload': 0.2,
                'conflicts': 0.3,
                'continuity': 0.1
            },
            'constraints': {
                'max_daily_hours_teacher': 6,
                'max_weekly_hours_teacher': 30,
                'max_consecutive_hours': 3,
                'max_daily_hours_section': 8,
                'break_periods': [4, 8]  # Period 4 and 8 are breaks
            }
        }

        return jsonify(config), 200

    except Exception as e:
        logger.error(f"Error getting optimization config: {str(e)}")
        return jsonify({'error': str(e)}), 500

@schedule_optimizer_bp.route('/api/schedule/optimize/start', methods=['POST'])
@jwt_required()
@tenant_required
def start_optimization():
    """Start schedule optimization process"""
    try:
        tenant_id = session.get('tenant_id')
        db_session = db.session
        data = request.json

        algorithm = data.get('algorithm', 'genetic')
        parameters = data.get('parameters', {})
        constraints = data.get('constraints', {})

        # Get scheduling data
        teachers = db_session.query(Teacher).filter_by(tenant_id=tenant_id).all()
        subjects = db_session.query(Subject).filter_by(tenant_id=tenant_id).all()
        sections = db_session.query(Section).filter_by(tenant_id=tenant_id).all()
        classrooms = db_session.query(Classroom).filter_by(tenant_id=tenant_id).all()
        time_periods = db_session.query(TimePeriod).filter_by(tenant_id=tenant_id).all()
        preferences = db_session.query(TeacherPreference).filter_by(tenant_id=tenant_id).all()

        # Convert to dictionaries
        teachers_data = [t.to_dict() for t in teachers]
        subjects_data = [s.to_dict() for s in subjects]
        sections_data = [s.to_dict() for s in sections]
        classrooms_data = [c.to_dict() for c in classrooms]
        periods_data = [p.to_dict() for p in time_periods]

        # Process preferences
        preferences_dict = {}
        for pref in preferences:
            if pref.teacher_id not in preferences_dict:
                preferences_dict[pref.teacher_id] = {
                    'preferred_times': [],
                    'preferred_subjects': [],
                    'preferred_classrooms': [],
                    'preferred_days': [],
                    'blocked_times': []
                }

            pref_data = preferences_dict[pref.teacher_id]

            if pref.preference_type == 'time':
                pref_data['preferred_times'].append({
                    'day': pref.day_of_week,
                    'period_id': pref.time_period_id
                })
            elif pref.preference_type == 'subject':
                pref_data['preferred_subjects'].append(pref.subject_id)
            elif pref.preference_type == 'classroom':
                pref_data['preferred_classrooms'].append(pref.classroom_id)
            elif pref.preference_type == 'blocked':
                pref_data['blocked_times'].append({
                    'day': pref.day_of_week,
                    'period_id': pref.time_period_id
                })

        result = None
        if algorithm == 'genetic':
            result = run_genetic_algorithm(
                teachers_data, subjects_data, sections_data,
                classrooms_data, periods_data, preferences_dict,
                constraints, parameters
            )
        elif algorithm == 'constraint':
            result = run_constraint_solver(
                teachers_data, subjects_data, sections_data,
                classrooms_data, periods_data, preferences_dict,
                constraints, parameters
            )
        elif algorithm == 'hybrid':
            result = run_hybrid_algorithm(
                teachers_data, subjects_data, sections_data,
                classrooms_data, periods_data, preferences_dict,
                constraints, parameters
            )

        if result:
            # Save optimization result
            optimization_id = save_optimization_result(tenant_id, result, algorithm)

            return jsonify({
                'success': True,
                'optimization_id': optimization_id,
                'algorithm': algorithm,
                'fitness_score': result.get('fitness_score', 0),
                'violations': result.get('violations', []),
                'schedule_count': len(result.get('schedule', []))
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Optimization failed'
            }), 500

    except Exception as e:
        logger.error(f"Error starting optimization: {str(e)}")
        return jsonify({'error': str(e)}), 500

def run_genetic_algorithm(teachers, subjects, sections, classrooms,
                         time_periods, preferences, constraints, parameters):
    """Run genetic algorithm optimization"""
    try:
        # Initialize GA
        ga = VenezuelanScheduleGA(
            teachers=teachers,
            subjects=subjects,
            sections=sections,
            classrooms=classrooms,
            time_periods=time_periods,
            preferences=preferences,
            constraints=constraints
        )

        # Apply custom parameters
        if parameters:
            ga.population_size = parameters.get('population_size', ga.population_size)
            ga.generations = parameters.get('generations', ga.generations)
            ga.mutation_rate = parameters.get('mutation_rate', ga.mutation_rate)
            ga.crossover_rate = parameters.get('crossover_rate', ga.crossover_rate)
            ga.elitism_rate = parameters.get('elitism_rate', ga.elitism_rate)

        # Run evolution
        best_chromosome = ga.evolve()

        # Convert to schedule
        schedule = ga.chromosome_to_schedule(best_chromosome)

        return {
            'schedule': schedule,
            'fitness_score': best_chromosome.fitness_score,
            'violations': []
        }

    except Exception as e:
        logger.error(f"Genetic algorithm error: {str(e)}")
        return None

def run_constraint_solver(teachers, subjects, sections, classrooms,
                         time_periods, preferences, constraints, parameters):
    """Run constraint solver optimization"""
    try:
        # Initialize solver
        solver = VenezuelanConstraintSolver()

        # Add Venezuelan constraints
        solver.initialize_venezuelan_constraints({})

        # Add teacher constraints
        for teacher in teachers:
            teacher_id = teacher['id']
            pref = preferences.get(teacher_id, {})

            solver.add_constraint(TeacherConstraint(
                name=f"Teacher {teacher_id} constraints",
                type=ConstraintType.HARD,
                priority=ConstraintPriority.HIGH,
                description=f"Constraints for teacher {teacher['name']}",
                teacher_id=teacher_id,
                max_daily_hours=constraints.get('max_daily_hours_teacher', 6),
                max_weekly_hours=constraints.get('max_weekly_hours_teacher', 30),
                max_consecutive_hours=constraints.get('max_consecutive_hours', 3),
                blocked_periods=pref.get('blocked_times', [])
            ))

        # Add section constraints
        for section in sections:
            solver.add_constraint(SectionConstraint(
                name=f"Section {section['id']} constraints",
                type=ConstraintType.HARD,
                priority=ConstraintPriority.HIGH,
                description=f"Constraints for section {section['name']}",
                section_id=section['id'],
                required_subjects=section.get('subjects', []),
                max_daily_hours=constraints.get('max_daily_hours_section', 8),
                break_periods=constraints.get('break_periods', [4, 8])
            ))

        # Add classroom constraints
        for classroom in classrooms:
            solver.add_constraint(ClassroomConstraint(
                name=f"Classroom {classroom['id']} constraints",
                type=ConstraintType.HARD,
                priority=ConstraintPriority.MEDIUM,
                description=f"Constraints for classroom {classroom['name']}",
                classroom_id=classroom['id'],
                capacity=classroom.get('capacity', 30)
            ))

        # Add subject constraints
        for subject in subjects:
            solver.add_constraint(SubjectConstraint(
                name=f"Subject {subject['id']} constraints",
                type=ConstraintType.HARD,
                priority=ConstraintPriority.HIGH,
                description=f"Constraints for subject {subject['name']}",
                subject_id=subject['id'],
                weekly_hours=subject.get('weekly_hours', 4)
            ))

        # Create assignments needed
        assignments_needed = []
        for section in sections:
            for subject_data in section.get('subjects', []):
                subject_id = subject_data['id']
                weekly_hours = subject_data.get('weekly_hours', 4)

                # Find qualified teacher
                qualified_teachers = [t for t in teachers
                                     if subject_id in t.get('qualified_subjects', [])]

                if qualified_teachers:
                    for _ in range(weekly_hours):
                        assignments_needed.append({
                            'teacher_id': qualified_teachers[0]['id'],  # Will be optimized
                            'section_id': section['id'],
                            'subject_id': subject_id,
                            'classroom_id': classrooms[0]['id']  # Will be optimized
                        })

        # Solve CSP
        schedule, success, violations = solver.solve_csp(assignments_needed)

        if success:
            # Optimize further
            iterations = parameters.get('iterations', 100)
            optimized_schedule = solver.optimize_schedule(schedule, iterations)

            # Convert to list format
            schedule_list = []
            for assignment in optimized_schedule.values():
                # Get details
                teacher = next((t for t in teachers if t['id'] == assignment['teacher_id']), None)
                subject = next((s for s in subjects if s['id'] == assignment['subject_id']), None)
                section = next((s for s in sections if s['id'] == assignment['section_id']), None)
                classroom = next((c for c in classrooms if c['id'] == assignment['classroom_id']), None)
                period = next((p for p in time_periods if p['id'] == assignment['period']), None)

                if all([teacher, subject, section, classroom, period]):
                    schedule_list.append({
                        'teacher': teacher,
                        'subject': subject,
                        'section': section,
                        'classroom': classroom,
                        'time_period': period,
                        'day_of_week': assignment['day'],
                        'day_name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][assignment['day']]
                    })

            satisfaction_score = solver.get_satisfaction_score(optimized_schedule)

            return {
                'schedule': schedule_list,
                'fitness_score': satisfaction_score,
                'violations': solver.get_all_violations(optimized_schedule)
            }
        else:
            return {
                'schedule': [],
                'fitness_score': 0,
                'violations': violations
            }

    except Exception as e:
        logger.error(f"Constraint solver error: {str(e)}")
        return None

def run_hybrid_algorithm(teachers, subjects, sections, classrooms,
                        time_periods, preferences, constraints, parameters):
    """Run hybrid optimization (GA + Constraint Solver)"""
    try:
        # First run genetic algorithm
        ga_result = run_genetic_algorithm(
            teachers, subjects, sections, classrooms,
            time_periods, preferences, constraints, parameters
        )

        if not ga_result:
            return None

        # Then refine with constraint solver
        solver = VenezuelanConstraintSolver()
        solver.initialize_venezuelan_constraints({})

        # Convert GA schedule to constraint solver format
        schedule_dict = {}
        for idx, assignment in enumerate(ga_result['schedule']):
            key = (
                assignment['section']['id'],
                assignment['day_of_week'],
                assignment['time_period']['id']
            )
            schedule_dict[key] = {
                'teacher_id': assignment['teacher']['id'],
                'section_id': assignment['section']['id'],
                'subject_id': assignment['subject']['id'],
                'classroom_id': assignment['classroom']['id'],
                'day': assignment['day_of_week'],
                'period': assignment['time_period']['id']
            }

        # Optimize
        optimized_schedule = solver.optimize_schedule(schedule_dict, 50)

        # Convert back to list format
        schedule_list = []
        for assignment in optimized_schedule.values():
            teacher = next((t for t in teachers if t['id'] == assignment['teacher_id']), None)
            subject = next((s for s in subjects if s['id'] == assignment['subject_id']), None)
            section = next((s for s in sections if s['id'] == assignment['section_id']), None)
            classroom = next((c for c in classrooms if c['id'] == assignment['classroom_id']), None)
            period = next((p for p in time_periods if p['id'] == assignment['period']), None)

            if all([teacher, subject, section, classroom, period]):
                schedule_list.append({
                    'teacher': teacher,
                    'subject': subject,
                    'section': section,
                    'classroom': classroom,
                    'time_period': period,
                    'day_of_week': assignment['day'],
                    'day_name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][assignment['day']]
                })

        return {
            'schedule': schedule_list,
            'fitness_score': ga_result['fitness_score'] * 0.7 + solver.get_satisfaction_score(optimized_schedule) * 0.3,
            'violations': solver.get_all_violations(optimized_schedule)
        }

    except Exception as e:
        logger.error(f"Hybrid algorithm error: {str(e)}")
        return None

def save_optimization_result(tenant_id, result, algorithm):
    """Save optimization result to database"""
    try:
        db_session = db.session

        # Create new schedule
        schedule = Schedule(
            tenant_id=tenant_id,
            name=f"Optimized Schedule - {algorithm.title()}",
            description=f"Generated using {algorithm} algorithm",
            academic_year=datetime.now().year,
            semester=1,
            status='draft',
            created_by=get_jwt_identity(),
            meta_data=json.dumps({
                'algorithm': algorithm,
                'fitness_score': result['fitness_score'],
                'violations': result['violations'],
                'generated_at': datetime.now().isoformat()
            })
        )
        db_session.add(schedule)
        db_session.commit()

        # Add assignments
        for assignment in result['schedule']:
            sched_assignment = ScheduleAssignment(
                schedule_id=schedule.id,
                teacher_id=assignment['teacher']['id'],
                subject_id=assignment['subject']['id'],
                section_id=assignment['section']['id'],
                classroom_id=assignment['classroom']['id'],
                time_period_id=assignment['time_period']['id'],
                day_of_week=assignment['day_of_week'],
                tenant_id=tenant_id
            )
            db_session.add(sched_assignment)

        db_session.commit()

        return schedule.id

    except Exception as e:
        logger.error(f"Error saving optimization result: {str(e)}")
        db_session.rollback()
        return None

@schedule_optimizer_bp.route('/api/schedule/optimize/preview/<int:optimization_id>', methods=['GET'])
@jwt_required()
@tenant_required
def preview_optimized_schedule(optimization_id):
    """Preview optimized schedule before applying"""
    try:
        tenant_id = session.get('tenant_id')
        db_session = db.session

        # Get schedule
        schedule = db_session.query(Schedule).filter_by(
            id=optimization_id,
            tenant_id=tenant_id
        ).first()

        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404

        # Get assignments
        assignments = db_session.query(ScheduleAssignment).filter_by(
            schedule_id=schedule.id
        ).all()

        # Format for preview
        preview_data = {
            'schedule_info': {
                'id': schedule.id,
                'name': schedule.name,
                'description': schedule.description,
                'status': schedule.status,
                'metadata': json.loads(schedule.meta_data) if schedule.meta_data else {}
            },
            'assignments': [],
            'statistics': {
                'total_assignments': len(assignments),
                'teachers_involved': len(set([a.teacher_id for a in assignments])),
                'sections_covered': len(set([a.section_id for a in assignments])),
                'classrooms_used': len(set([a.classroom_id for a in assignments]))
            }
        }

        # Add assignments
        for assignment in assignments:
            preview_data['assignments'].append({
                'teacher': assignment.teacher.name if assignment.teacher else 'Unknown',
                'subject': assignment.subject.name if assignment.subject else 'Unknown',
                'section': assignment.section.name if assignment.section else 'Unknown',
                'classroom': assignment.classroom.name if assignment.classroom else 'Unknown',
                'time_period': assignment.time_period.name if assignment.time_period else 'Unknown',
                'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][assignment.day_of_week]
            })

        return jsonify(preview_data), 200

    except Exception as e:
        logger.error(f"Error previewing schedule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@schedule_optimizer_bp.route('/api/schedule/optimize/apply/<int:optimization_id>', methods=['POST'])
@jwt_required()
@tenant_required
def apply_optimized_schedule(optimization_id):
    """Apply optimized schedule as active schedule"""
    try:
        tenant_id = session.get('tenant_id')
        db_session = db.session

        # Get schedule
        schedule = db_session.query(Schedule).filter_by(
            id=optimization_id,
            tenant_id=tenant_id
        ).first()

        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404

        # Deactivate current active schedules
        db.query(Schedule).filter_by(
            tenant_id=tenant_id,
            status='active'
        ).update({'status': 'archived'})

        # Activate this schedule
        schedule.status = 'active'
        db_session.commit()

        return jsonify({
            'success': True,
            'message': 'Optimized schedule applied successfully',
            'schedule_id': schedule.id
        }), 200

    except Exception as e:
        logger.error(f"Error applying schedule: {str(e)}")
        db_session.rollback()
        return jsonify({'error': str(e)}), 500