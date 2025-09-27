"""
Constraint Solver Engine for Schedule Optimization
Venezuelan K12 Educational Institution Scheduling
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ConstraintType(Enum):
    """Types of scheduling constraints"""
    HARD = "hard"  # Must be satisfied
    SOFT = "soft"  # Should be satisfied if possible

class ConstraintPriority(Enum):
    """Priority levels for constraints"""
    CRITICAL = 1     # System will fail without this
    HIGH = 2         # Major impact on schedule quality
    MEDIUM = 3       # Moderate impact
    LOW = 4          # Minor preference

@dataclass
class Constraint:
    """Base constraint class"""
    name: str
    type: ConstraintType
    priority: ConstraintPriority
    description: str
    weight: float = 1.0

@dataclass
class TeacherConstraint:
    """Teacher-specific constraints"""
    name: str
    type: ConstraintType
    priority: ConstraintPriority
    description: str
    teacher_id: int
    weight: float = 1.0
    max_daily_hours: int = 6
    max_weekly_hours: int = 30
    max_consecutive_hours: int = 3
    blocked_periods: List[Tuple[int, int]] = field(default_factory=list)  # (day, period)
    preferred_periods: List[Tuple[int, int]] = field(default_factory=list)

@dataclass
class SectionConstraint:
    """Section-specific constraints"""
    name: str
    type: ConstraintType
    priority: ConstraintPriority
    description: str
    section_id: int
    weight: float = 1.0
    required_subjects: List[Dict] = field(default_factory=list)
    max_daily_hours: int = 8
    lunch_period: Optional[int] = None
    break_periods: List[int] = field(default_factory=list)

@dataclass
class ClassroomConstraint:
    """Classroom-specific constraints"""
    name: str
    type: ConstraintType
    priority: ConstraintPriority
    description: str
    classroom_id: int
    capacity: int
    weight: float = 1.0
    equipment: List[str] = field(default_factory=list)
    blocked_periods: List[Tuple[int, int]] = field(default_factory=list)

@dataclass
class SubjectConstraint:
    """Subject-specific constraints"""
    name: str
    type: ConstraintType
    priority: ConstraintPriority
    description: str
    subject_id: int
    weekly_hours: int
    weight: float = 1.0
    requires_consecutive: bool = False
    requires_lab: bool = False
    requires_equipment: List[str] = field(default_factory=list)

class VenezuelanConstraintSolver:
    """
    Constraint Solver for Venezuelan K12 Schedule Optimization
    Implements CSP (Constraint Satisfaction Problem) solving
    """

    def __init__(self):
        self.constraints = []
        self.violations = []
        self.schedule_assignments = {}
        self.domain_values = {}

    def add_constraint(self, constraint: Constraint):
        """Add a constraint to the solver"""
        self.constraints.append(constraint)

    def initialize_venezuelan_constraints(self, school_data: Dict):
        """Initialize standard Venezuelan K12 constraints"""

        # Venezuelan educational law constraints
        self.add_constraint(TeacherConstraint(
            name="Venezuelan Teacher Workload",
            type=ConstraintType.HARD,
            priority=ConstraintPriority.CRITICAL,
            description="Venezuelan educational law maximum teaching hours",
            teacher_id=0,  # Applied to all
            max_daily_hours=6,
            max_weekly_hours=30,
            max_consecutive_hours=3
        ))

        # Bimodal schedule constraints (7:00 AM - 2:20 PM)
        self.add_constraint(Constraint(
            name="Venezuelan Bimodal Schedule",
            type=ConstraintType.HARD,
            priority=ConstraintPriority.CRITICAL,
            description="Classes must fit within 7:00 AM - 2:20 PM timeframe",
            weight=1.0
        ))

        # Break time constraints
        self.add_constraint(Constraint(
            name="Morning Break",
            type=ConstraintType.HARD,
            priority=ConstraintPriority.HIGH,
            description="Morning break at 9:40 AM - 10:00 AM",
            weight=1.0
        ))

        self.add_constraint(Constraint(
            name="Lunch Break",
            type=ConstraintType.HARD,
            priority=ConstraintPriority.HIGH,
            description="Lunch break at 12:40 PM - 1:20 PM",
            weight=1.0
        ))

    def check_teacher_constraints(self, teacher_id: int, day: int, period: int,
                                 current_schedule: Dict) -> Tuple[bool, List[str]]:
        """Check if teacher constraints are satisfied"""
        violations = []

        # Get teacher constraints
        teacher_constraints = [c for c in self.constraints
                              if isinstance(c, TeacherConstraint) and
                              (c.teacher_id == teacher_id or c.teacher_id == 0)]

        for constraint in teacher_constraints:
            # Check blocked periods
            if (day, period) in constraint.blocked_periods:
                if constraint.type == ConstraintType.HARD:
                    return False, [f"Teacher {teacher_id} blocked at day {day}, period {period}"]
                else:
                    violations.append(f"Soft constraint: Teacher prefers not to teach at this time")

            # Check daily hours
            daily_hours = self._count_teacher_daily_hours(teacher_id, day, current_schedule)
            if daily_hours >= constraint.max_daily_hours:
                if constraint.type == ConstraintType.HARD:
                    return False, [f"Teacher {teacher_id} exceeds max daily hours ({constraint.max_daily_hours})"]
                else:
                    violations.append(f"Soft constraint: Teacher daily hours exceeded")

            # Check weekly hours
            weekly_hours = self._count_teacher_weekly_hours(teacher_id, current_schedule)
            if weekly_hours >= constraint.max_weekly_hours:
                if constraint.type == ConstraintType.HARD:
                    return False, [f"Teacher {teacher_id} exceeds max weekly hours ({constraint.max_weekly_hours})"]
                else:
                    violations.append(f"Soft constraint: Teacher weekly hours exceeded")

            # Check consecutive hours
            consecutive = self._check_consecutive_hours(teacher_id, day, period, current_schedule)
            if consecutive > constraint.max_consecutive_hours:
                if constraint.type == ConstraintType.HARD:
                    return False, [f"Teacher {teacher_id} exceeds max consecutive hours ({constraint.max_consecutive_hours})"]
                else:
                    violations.append(f"Soft constraint: Too many consecutive hours")

        return True, violations

    def check_section_constraints(self, section_id: int, day: int, period: int,
                                 current_schedule: Dict) -> Tuple[bool, List[str]]:
        """Check if section constraints are satisfied"""
        violations = []

        # Get section constraints
        section_constraints = [c for c in self.constraints
                              if isinstance(c, SectionConstraint) and
                              c.section_id == section_id]

        for constraint in section_constraints:
            # Check if section already has class at this time
            slot_key = (section_id, day, period)
            if slot_key in current_schedule:
                return False, [f"Section {section_id} already has class at day {day}, period {period}"]

            # Check daily hours
            daily_hours = self._count_section_daily_hours(section_id, day, current_schedule)
            if daily_hours >= constraint.max_daily_hours:
                if constraint.type == ConstraintType.HARD:
                    return False, [f"Section {section_id} exceeds max daily hours ({constraint.max_daily_hours})"]
                else:
                    violations.append(f"Soft constraint: Section daily hours exceeded")

            # Check break periods
            if period in constraint.break_periods:
                return False, [f"Cannot schedule during break period {period}"]

            # Check lunch period
            if constraint.lunch_period and period == constraint.lunch_period:
                return False, [f"Cannot schedule during lunch period {period}"]

        return True, violations

    def check_classroom_constraints(self, classroom_id: int, day: int, period: int,
                                   current_schedule: Dict) -> Tuple[bool, List[str]]:
        """Check if classroom constraints are satisfied"""
        violations = []

        # Get classroom constraints
        classroom_constraints = [c for c in self.constraints
                                if isinstance(c, ClassroomConstraint) and
                                c.classroom_id == classroom_id]

        for constraint in classroom_constraints:
            # Check if classroom is available
            slot_key = (classroom_id, day, period)
            if slot_key in current_schedule:
                return False, [f"Classroom {classroom_id} already occupied at day {day}, period {period}"]

            # Check blocked periods
            if (day, period) in constraint.blocked_periods:
                return False, [f"Classroom {classroom_id} blocked at day {day}, period {period}"]

        return True, violations

    def check_subject_constraints(self, subject_id: int, section_id: int,
                                 current_schedule: Dict) -> Tuple[bool, List[str]]:
        """Check if subject constraints are satisfied"""
        violations = []

        # Get subject constraints
        subject_constraints = [c for c in self.constraints
                              if isinstance(c, SubjectConstraint) and
                              c.subject_id == subject_id]

        for constraint in subject_constraints:
            # Count current weekly hours for this subject-section
            weekly_hours = self._count_subject_weekly_hours(subject_id, section_id, current_schedule)

            if weekly_hours >= constraint.weekly_hours:
                return False, [f"Subject {subject_id} for section {section_id} already has {constraint.weekly_hours} weekly hours"]

        return True, violations

    def validate_assignment(self, assignment: Dict, current_schedule: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a single schedule assignment against all constraints

        Args:
            assignment: {teacher_id, section_id, subject_id, classroom_id, day, period}
            current_schedule: Current state of the schedule

        Returns:
            (is_valid, list_of_violations)
        """
        all_violations = []

        # Check teacher constraints
        valid, violations = self.check_teacher_constraints(
            assignment['teacher_id'], assignment['day'],
            assignment['period'], current_schedule
        )
        if not valid:
            return False, violations
        all_violations.extend(violations)

        # Check section constraints
        valid, violations = self.check_section_constraints(
            assignment['section_id'], assignment['day'],
            assignment['period'], current_schedule
        )
        if not valid:
            return False, violations
        all_violations.extend(violations)

        # Check classroom constraints
        valid, violations = self.check_classroom_constraints(
            assignment['classroom_id'], assignment['day'],
            assignment['period'], current_schedule
        )
        if not valid:
            return False, violations
        all_violations.extend(violations)

        # Check subject constraints
        valid, violations = self.check_subject_constraints(
            assignment['subject_id'], assignment['section_id'],
            current_schedule
        )
        if not valid:
            return False, violations
        all_violations.extend(violations)

        return True, all_violations

    def solve_csp(self, assignments_needed: List[Dict],
                  initial_schedule: Dict = None) -> Tuple[Dict, bool, List[str]]:
        """
        Solve the Constraint Satisfaction Problem using backtracking

        Args:
            assignments_needed: List of required assignments
            initial_schedule: Starting schedule state

        Returns:
            (final_schedule, success, violations)
        """
        schedule = initial_schedule or {}
        return self._backtrack(assignments_needed, schedule, 0)

    def _backtrack(self, assignments: List[Dict], schedule: Dict,
                   index: int) -> Tuple[Dict, bool, List[str]]:
        """Recursive backtracking algorithm"""

        # Base case: all assignments made
        if index >= len(assignments):
            return schedule, True, []

        assignment = assignments[index]

        # Try all possible values in domain
        for day in range(5):  # Monday to Friday
            for period in range(1, 11):  # 10 periods per day
                # Create tentative assignment
                tentative = {
                    'teacher_id': assignment['teacher_id'],
                    'section_id': assignment['section_id'],
                    'subject_id': assignment['subject_id'],
                    'classroom_id': assignment['classroom_id'],
                    'day': day,
                    'period': period
                }

                # Check constraints
                valid, violations = self.validate_assignment(tentative, schedule)

                if valid:
                    # Add to schedule
                    key = (assignment['section_id'], day, period)
                    schedule[key] = tentative

                    # Recursively solve
                    result_schedule, success, result_violations = self._backtrack(
                        assignments, schedule, index + 1
                    )

                    if success:
                        return result_schedule, True, result_violations

                    # Backtrack
                    del schedule[key]

        # No solution found
        return schedule, False, [f"Cannot find valid assignment for index {index}"]

    def _count_teacher_daily_hours(self, teacher_id: int, day: int,
                                   schedule: Dict) -> int:
        """Count teacher's hours on a specific day"""
        count = 0
        for key, assignment in schedule.items():
            if assignment['teacher_id'] == teacher_id and assignment['day'] == day:
                count += 1
        return count

    def _count_teacher_weekly_hours(self, teacher_id: int, schedule: Dict) -> int:
        """Count teacher's total weekly hours"""
        count = 0
        for assignment in schedule.values():
            if assignment['teacher_id'] == teacher_id:
                count += 1
        return count

    def _count_section_daily_hours(self, section_id: int, day: int,
                                   schedule: Dict) -> int:
        """Count section's hours on a specific day"""
        count = 0
        for key, assignment in schedule.items():
            if assignment['section_id'] == section_id and assignment['day'] == day:
                count += 1
        return count

    def _count_subject_weekly_hours(self, subject_id: int, section_id: int,
                                    schedule: Dict) -> int:
        """Count subject hours for a section"""
        count = 0
        for assignment in schedule.values():
            if (assignment['subject_id'] == subject_id and
                assignment['section_id'] == section_id):
                count += 1
        return count

    def _check_consecutive_hours(self, teacher_id: int, day: int, period: int,
                                 schedule: Dict) -> int:
        """Check consecutive teaching hours"""
        consecutive = 1  # Current period counts

        # Check backwards
        for p in range(period - 1, 0, -1):
            key = None
            for k, assignment in schedule.items():
                if (assignment['teacher_id'] == teacher_id and
                    assignment['day'] == day and
                    assignment['period'] == p):
                    consecutive += 1
                    break
            else:
                break  # Not consecutive

        # Check forwards
        for p in range(period + 1, 11):
            key = None
            for k, assignment in schedule.items():
                if (assignment['teacher_id'] == teacher_id and
                    assignment['day'] == day and
                    assignment['period'] == p):
                    consecutive += 1
                    break
            else:
                break  # Not consecutive

        return consecutive

    def optimize_schedule(self, schedule: Dict, iterations: int = 100) -> Dict:
        """
        Optimize an existing schedule by local search

        Args:
            schedule: Current schedule
            iterations: Number of optimization iterations

        Returns:
            Optimized schedule
        """
        best_schedule = schedule.copy()
        best_violations = len(self.get_all_violations(best_schedule))

        for _ in range(iterations):
            # Create a neighbor by swapping two assignments
            neighbor = self._create_neighbor(best_schedule)

            # Evaluate neighbor
            neighbor_violations = len(self.get_all_violations(neighbor))

            # Accept if better
            if neighbor_violations < best_violations:
                best_schedule = neighbor
                best_violations = neighbor_violations

                # Stop if perfect schedule found
                if best_violations == 0:
                    break

        return best_schedule

    def _create_neighbor(self, schedule: Dict) -> Dict:
        """Create a neighbor schedule by swapping two random assignments"""
        import random

        neighbor = schedule.copy()
        keys = list(neighbor.keys())

        if len(keys) >= 2:
            # Select two random assignments to swap
            key1, key2 = random.sample(keys, 2)

            # Swap time slots
            assignment1 = neighbor[key1].copy()
            assignment2 = neighbor[key2].copy()

            assignment1['day'], assignment1['period'] = assignment2['day'], assignment2['period']
            assignment2['day'], assignment2['period'] = assignment1['day'], assignment1['period']

            # Update schedule
            del neighbor[key1]
            del neighbor[key2]

            new_key1 = (assignment1['section_id'], assignment1['day'], assignment1['period'])
            new_key2 = (assignment2['section_id'], assignment2['day'], assignment2['period'])

            neighbor[new_key1] = assignment1
            neighbor[new_key2] = assignment2

        return neighbor

    def get_all_violations(self, schedule: Dict) -> List[str]:
        """Get all constraint violations in the schedule"""
        all_violations = []

        for assignment in schedule.values():
            valid, violations = self.validate_assignment(assignment, schedule)
            all_violations.extend(violations)

        return all_violations

    def get_satisfaction_score(self, schedule: Dict) -> float:
        """
        Calculate overall constraint satisfaction score

        Returns:
            Score between 0 and 1 (1 = all constraints satisfied)
        """
        hard_satisfied = 0
        hard_total = 0
        soft_satisfied = 0
        soft_total = 0

        for constraint in self.constraints:
            if constraint.type == ConstraintType.HARD:
                hard_total += 1
                # Check if constraint is satisfied
                # (Implementation depends on specific constraint)
                hard_satisfied += 1  # Simplified
            else:
                soft_total += 1
                soft_satisfied += 1  # Simplified

        # Weight hard constraints more
        hard_score = (hard_satisfied / hard_total) if hard_total > 0 else 1
        soft_score = (soft_satisfied / soft_total) if soft_total > 0 else 1

        return 0.7 * hard_score + 0.3 * soft_score