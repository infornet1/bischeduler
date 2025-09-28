#!/usr/bin/env python3
"""
Phase 11: Populate Sample Students for Attendance Testing
Create realistic Venezuelan student data for UEIPAB sections
"""

import os
import sys
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.tenant import Student, Section

# Venezuelan common names for realistic data
MALE_NAMES = [
    "Alejandro", "Carlos", "Daniel", "Eduardo", "Francisco", "Gabriel", "Héctor", "Iván",
    "José", "Luis", "Miguel", "Nicolás", "Omar", "Pedro", "Rafael", "Santiago"
]

FEMALE_NAMES = [
    "Alejandra", "Beatriz", "Carmen", "Diana", "Elena", "Fernanda", "Gabriela", "Isabella",
    "Julia", "Karla", "Laura", "María", "Natalia", "Paola", "Rosa", "Sofía"
]

LAST_NAMES = [
    "García", "Rodríguez", "López", "Martínez", "González", "Pérez", "Sánchez", "Ramírez",
    "Cruz", "Flores", "Gómez", "Díaz", "Morales", "Jiménez", "Herrera", "Medina",
    "Castro", "Vargas", "Ramos", "Ortega", "Delgado", "Aguilar", "Mendoza", "Silva"
]

def populate_students():
    """Create sample students for all UEIPAB sections"""

    # Connect to tenant database
    engine = create_engine('mysql+pymysql://root:Temporal2024!@localhost/ueipab_2025_data')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get all sections
        sections = session.query(Section).filter_by(academic_year='2025-2026', is_active=True).all()

        if not sections:
            print("❌ No se encontraron secciones activas")
            return

        student_counter = 1
        total_students = 0

        for section in sections:
            print(f"📚 Creando estudiantes para {section.name}...")

            # Create 25-35 students per section
            import random
            num_students = random.randint(25, 35)

            for i in range(num_students):
                # Randomly assign gender
                gender = random.choice(['M', 'F'])

                # Choose appropriate name
                if gender == 'M':
                    first_name = random.choice(MALE_NAMES)
                else:
                    first_name = random.choice(FEMALE_NAMES)

                last_name = f"{random.choice(LAST_NAMES)} {random.choice(LAST_NAMES)}"
                full_name = f"{first_name} {last_name}"

                # Generate cedula escolar (school ID)
                cedula_escolar = f"E{student_counter:05d}"

                # Create student
                student = Student(
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    cedula_escolar=cedula_escolar,
                    gender=gender,
                    grade_level=section.grade_level,
                    section_id=section.id,
                    academic_year='2025-2026',
                    parent_name=f"Padre/Madre de {first_name}",
                    parent_phone=f"+58-{random.randint(200,299)}-{random.randint(1000000,9999999)}",
                    parent_email=f"padre.{first_name.lower()}.{last_name.split()[0].lower()}@gmail.com",
                    is_active=True
                )

                session.add(student)
                student_counter += 1
                total_students += 1

            # Update section student count
            section.current_students = num_students
            section.max_students = max(35, num_students + 5)

            print(f"   ✅ {num_students} estudiantes creados para {section.name}")

        session.commit()
        print(f"\n🎉 ¡Completado! Se crearon {total_students} estudiantes en {len(sections)} secciones")

        # Show summary by gender and grade
        print("\n📊 RESUMEN POR GRADO Y GÉNERO:")
        for grade in sorted(set(s.grade_level for s in sections)):
            male_count = session.query(Student).filter_by(
                grade_level=grade, gender='M', academic_year='2025-2026'
            ).count()
            female_count = session.query(Student).filter_by(
                grade_level=grade, gender='F', academic_year='2025-2026'
            ).count()
            total_grade = male_count + female_count

            print(f"   📚 Grado {grade}: {total_grade} estudiantes (👦 {male_count} | 👧 {female_count})")

    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Iniciando población de estudiantes para UEIPAB...")
    populate_students()