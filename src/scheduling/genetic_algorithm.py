"""
Genetic Algorithm for Schedule Optimization
Venezuelan K12 Educational Institution Scheduling
"""

import random
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, time
import copy

@dataclass
class Gene:
    """Represents a single scheduling assignment"""
    teacher_id: int
    subject_id: int
    section_id: int
    classroom_id: int
    time_period_id: int
    day_of_week: int

@dataclass
class Chromosome:
    """Represents a complete schedule solution"""
    genes: List[Gene]
    fitness_score: float = 0.0

class VenezuelanScheduleGA:
    """
    Genetic Algorithm for Venezuelan K12 Schedule Optimization
    Optimizes for teacher preferences, workload balance, and constraints
    """

    def __init__(self,
                 teachers: List[Dict],
                 subjects: List[Dict],
                 sections: List[Dict],
                 classrooms: List[Dict],
                 time_periods: List[Dict],
                 preferences: Dict,
                 constraints: Dict):
        """Initialize the genetic algorithm with scheduling data"""
        self.teachers = teachers
        self.subjects = subjects
        self.sections = sections
        self.classrooms = classrooms
        self.time_periods = time_periods
        self.preferences = preferences
        self.constraints = constraints

        # GA parameters
        self.population_size = 100
        self.generations = 500
        self.mutation_rate = 0.02
        self.crossover_rate = 0.8
        self.elitism_rate = 0.1
        self.tournament_size = 5

        # Venezuelan K12 specific weights
        self.weight_preferences = 0.4  # Teacher preferences
        self.weight_workload = 0.2     # Balanced workload
        self.weight_conflicts = 0.3    # No scheduling conflicts
        self.weight_continuity = 0.1   # Subject continuity

    def generate_initial_population(self) -> List[Chromosome]:
        """Generate initial population of random valid schedules"""
        population = []

        for _ in range(self.population_size):
            chromosome = self._create_random_schedule()
            population.append(chromosome)

        return population

    def _create_random_schedule(self) -> Chromosome:
        """Create a random but valid schedule"""
        genes = []

        # Track assignments to avoid conflicts
        teacher_slots = {}
        classroom_slots = {}
        section_slots = {}

        # Iterate through all required assignments
        for section in self.sections:
            for subject in section.get('subjects', []):
                # Find qualified teachers
                qualified_teachers = self._get_qualified_teachers(subject['id'])

                if not qualified_teachers:
                    continue

                # Assign periods for this subject
                periods_needed = subject.get('weekly_hours', 4)
                periods_assigned = 0

                while periods_assigned < periods_needed:
                    # Random selection
                    teacher = random.choice(qualified_teachers)
                    classroom = random.choice(self.classrooms)
                    day = random.randint(0, 4)  # Monday to Friday

                    # Find available time period
                    available_periods = self._get_available_periods(
                        teacher['id'], section['id'], classroom['id'],
                        day, teacher_slots, section_slots, classroom_slots
                    )

                    if not available_periods:
                        break  # Try next subject

                    period = random.choice(available_periods)

                    # Create gene
                    gene = Gene(
                        teacher_id=teacher['id'],
                        subject_id=subject['id'],
                        section_id=section['id'],
                        classroom_id=classroom['id'],
                        time_period_id=period['id'],
                        day_of_week=day
                    )

                    genes.append(gene)

                    # Update tracking
                    slot_key = (day, period['id'])
                    teacher_slots.setdefault(teacher['id'], set()).add(slot_key)
                    classroom_slots.setdefault(classroom['id'], set()).add(slot_key)
                    section_slots.setdefault(section['id'], set()).add(slot_key)

                    periods_assigned += 1

        return Chromosome(genes=genes)

    def _get_qualified_teachers(self, subject_id: int) -> List[Dict]:
        """Get teachers qualified for a subject"""
        qualified = []
        for teacher in self.teachers:
            if subject_id in teacher.get('qualified_subjects', []):
                qualified.append(teacher)
        return qualified

    def _get_available_periods(self, teacher_id, section_id, classroom_id, day,
                               teacher_slots, section_slots, classroom_slots) -> List[Dict]:
        """Get available time periods without conflicts"""
        available = []

        for period in self.time_periods:
            slot_key = (day, period['id'])

            # Check conflicts
            if slot_key in teacher_slots.get(teacher_id, set()):
                continue
            if slot_key in section_slots.get(section_id, set()):
                continue
            if slot_key in classroom_slots.get(classroom_id, set()):
                continue

            # Check teacher availability
            if not self._is_teacher_available(teacher_id, day, period['id']):
                continue

            available.append(period)

        return available

    def _is_teacher_available(self, teacher_id: int, day: int, period_id: int) -> bool:
        """Check if teacher is available at given time"""
        if teacher_id not in self.preferences:
            return True

        teacher_pref = self.preferences[teacher_id]

        # Check blocked times
        blocked_times = teacher_pref.get('blocked_times', [])
        for blocked in blocked_times:
            if blocked['day'] == day and blocked['period_id'] == period_id:
                return False

        return True

    def calculate_fitness(self, chromosome: Chromosome) -> float:
        """Calculate fitness score for a schedule"""
        score = 0.0

        # Preference satisfaction
        pref_score = self._calculate_preference_score(chromosome)
        score += pref_score * self.weight_preferences

        # Workload balance
        workload_score = self._calculate_workload_score(chromosome)
        score += workload_score * self.weight_workload

        # Conflict penalties
        conflict_score = self._calculate_conflict_score(chromosome)
        score += conflict_score * self.weight_conflicts

        # Subject continuity
        continuity_score = self._calculate_continuity_score(chromosome)
        score += continuity_score * self.weight_continuity

        chromosome.fitness_score = score
        return score

    def _calculate_preference_score(self, chromosome: Chromosome) -> float:
        """Calculate how well schedule matches teacher preferences"""
        total_score = 0
        max_score = len(chromosome.genes)

        for gene in chromosome.genes:
            if gene.teacher_id not in self.preferences:
                total_score += 0.5  # Neutral score
                continue

            pref = self.preferences[gene.teacher_id]
            gene_score = 0

            # Time preference
            time_pref = pref.get('preferred_times', [])
            for tp in time_pref:
                if tp['day'] == gene.day_of_week and tp['period_id'] == gene.time_period_id:
                    gene_score += 0.4
                    break

            # Subject preference
            subject_pref = pref.get('preferred_subjects', [])
            if gene.subject_id in subject_pref:
                gene_score += 0.3

            # Classroom preference
            classroom_pref = pref.get('preferred_classrooms', [])
            if gene.classroom_id in classroom_pref:
                gene_score += 0.2

            # Day preference
            day_pref = pref.get('preferred_days', [])
            if gene.day_of_week in day_pref:
                gene_score += 0.1

            total_score += gene_score

        return total_score / max_score if max_score > 0 else 0

    def _calculate_workload_score(self, chromosome: Chromosome) -> float:
        """Calculate workload balance across teachers"""
        teacher_loads = {}

        for gene in chromosome.genes:
            teacher_loads[gene.teacher_id] = teacher_loads.get(gene.teacher_id, 0) + 1

        if not teacher_loads:
            return 1.0

        loads = list(teacher_loads.values())
        mean_load = np.mean(loads)
        std_load = np.std(loads)

        # Lower standard deviation = better balance
        if mean_load > 0:
            balance_score = 1 - (std_load / mean_load)
            return max(0, min(1, balance_score))
        return 1.0

    def _calculate_conflict_score(self, chromosome: Chromosome) -> float:
        """Calculate penalty for scheduling conflicts"""
        conflicts = 0
        total_checks = 0

        # Check for conflicts
        schedule_map = {}

        for gene in chromosome.genes:
            # Teacher conflict check
            teacher_key = (gene.teacher_id, gene.day_of_week, gene.time_period_id)
            if teacher_key in schedule_map:
                conflicts += 1
            schedule_map[teacher_key] = gene

            # Section conflict check
            section_key = (gene.section_id, gene.day_of_week, gene.time_period_id)
            if section_key in schedule_map:
                conflicts += 1
            schedule_map[section_key] = gene

            # Classroom conflict check
            classroom_key = (gene.classroom_id, gene.day_of_week, gene.time_period_id)
            if classroom_key in schedule_map:
                conflicts += 1
            schedule_map[classroom_key] = gene

            total_checks += 3

        # Return inverse of conflict ratio (fewer conflicts = higher score)
        if total_checks > 0:
            return 1 - (conflicts / total_checks)
        return 1.0

    def _calculate_continuity_score(self, chromosome: Chromosome) -> float:
        """Calculate subject continuity score (consecutive periods for same subject)"""
        continuity_score = 0
        max_score = 0

        # Group by section and subject
        section_subjects = {}
        for gene in chromosome.genes:
            key = (gene.section_id, gene.subject_id, gene.day_of_week)
            if key not in section_subjects:
                section_subjects[key] = []
            section_subjects[key].append(gene.time_period_id)

        # Check for consecutive periods
        for periods in section_subjects.values():
            if len(periods) > 1:
                periods.sort()
                consecutive = 0
                for i in range(len(periods) - 1):
                    if periods[i+1] - periods[i] == 1:
                        consecutive += 1
                continuity_score += consecutive
                max_score += len(periods) - 1

        return continuity_score / max_score if max_score > 0 else 1.0

    def selection(self, population: List[Chromosome]) -> Chromosome:
        """Tournament selection"""
        tournament = random.sample(population, min(self.tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness_score)

    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """Uniform crossover between two parents"""
        if random.random() > self.crossover_rate:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)

        child1_genes = []
        child2_genes = []

        for i in range(min(len(parent1.genes), len(parent2.genes))):
            if random.random() < 0.5:
                child1_genes.append(copy.deepcopy(parent1.genes[i]))
                child2_genes.append(copy.deepcopy(parent2.genes[i]))
            else:
                child1_genes.append(copy.deepcopy(parent2.genes[i]))
                child2_genes.append(copy.deepcopy(parent1.genes[i]))

        return Chromosome(genes=child1_genes), Chromosome(genes=child2_genes)

    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """Mutate a chromosome by randomly changing some genes"""
        mutated = copy.deepcopy(chromosome)

        for gene in mutated.genes:
            if random.random() < self.mutation_rate:
                # Randomly mutate one attribute
                mutation_type = random.choice(['teacher', 'classroom', 'time'])

                if mutation_type == 'teacher':
                    qualified = self._get_qualified_teachers(gene.subject_id)
                    if qualified:
                        gene.teacher_id = random.choice(qualified)['id']

                elif mutation_type == 'classroom':
                    gene.classroom_id = random.choice(self.classrooms)['id']

                elif mutation_type == 'time':
                    gene.day_of_week = random.randint(0, 4)
                    gene.time_period_id = random.choice(self.time_periods)['id']

        return mutated

    def evolve(self, progress_callback=None) -> Chromosome:
        """Main evolution loop"""
        # Initialize population
        population = self.generate_initial_population()

        # Calculate initial fitness
        for chromosome in population:
            self.calculate_fitness(chromosome)

        best_chromosome = max(population, key=lambda x: x.fitness_score)

        for generation in range(self.generations):
            # Sort by fitness
            population.sort(key=lambda x: x.fitness_score, reverse=True)

            # Elitism - keep best chromosomes
            elite_count = int(self.population_size * self.elitism_rate)
            new_population = population[:elite_count]

            # Generate offspring
            while len(new_population) < self.population_size:
                parent1 = self.selection(population)
                parent2 = self.selection(population)

                child1, child2 = self.crossover(parent1, parent2)

                child1 = self.mutate(child1)
                child2 = self.mutate(child2)

                self.calculate_fitness(child1)
                self.calculate_fitness(child2)

                new_population.extend([child1, child2])

            # Trim to population size
            population = new_population[:self.population_size]

            # Track best
            current_best = max(population, key=lambda x: x.fitness_score)
            if current_best.fitness_score > best_chromosome.fitness_score:
                best_chromosome = current_best

            # Progress callback
            if progress_callback:
                progress_callback(generation, best_chromosome.fitness_score)

            # Early termination if perfect score
            if best_chromosome.fitness_score >= 0.95:
                break

        return best_chromosome

    def chromosome_to_schedule(self, chromosome: Chromosome) -> List[Dict]:
        """Convert chromosome to schedule format"""
        schedule = []

        for gene in chromosome.genes:
            # Get details
            teacher = next((t for t in self.teachers if t['id'] == gene.teacher_id), None)
            subject = next((s for s in self.subjects if s['id'] == gene.subject_id), None)
            section = next((s for s in self.sections if s['id'] == gene.section_id), None)
            classroom = next((c for c in self.classrooms if c['id'] == gene.classroom_id), None)
            period = next((p for p in self.time_periods if p['id'] == gene.time_period_id), None)

            if all([teacher, subject, section, classroom, period]):
                schedule.append({
                    'teacher': teacher,
                    'subject': subject,
                    'section': section,
                    'classroom': classroom,
                    'time_period': period,
                    'day_of_week': gene.day_of_week,
                    'day_name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][gene.day_of_week]
                })

        return schedule