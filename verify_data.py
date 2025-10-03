#!/usr/bin/env python3
"""
Verify database data and connections
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.core.app import create_app, db
from src.models.tenant import Teacher, Student, Section, Classroom, ScheduleAssignment
from sqlalchemy import func

def verify_database_data():
    """Verify what data exists in the database"""
    print('🔍 Verificando Datos en la Base de Datos')
    print('=' * 70)
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # Check Teachers
            print('\n👨‍🏫 PROFESORES:')
            teacher_count = db.session.query(func.count(Teacher.id)).scalar()
            print(f'   Total de profesores: {teacher_count}')
            
            if teacher_count > 0:
                teachers = db.session.query(Teacher).limit(5).all()
                print(f'   Primeros 5 profesores:')
                for t in teachers:
                    print(f'   - ID: {t.id}, Nombre: {t.first_name} {t.last_name}, Cédula: {t.cedula}')
            
            # Check Students
            print('\n👨‍🎓 ESTUDIANTES:')
            student_count = db.session.query(func.count(Student.id)).scalar()
            print(f'   Total de estudiantes: {student_count}')
            
            if student_count > 0:
                students = db.session.query(Student).limit(5).all()
                print(f'   Primeros 5 estudiantes:')
                for s in students:
                    print(f'   - ID: {s.id}, Nombre: {s.first_name} {s.last_name}, Cédula: {s.cedula}')
            
            # Check Sections
            print('\n📚 SECCIONES:')
            section_count = db.session.query(func.count(Section.id)).scalar()
            print(f'   Total de secciones: {section_count}')
            
            if section_count > 0:
                sections = db.session.query(Section).all()
                print(f'   Todas las secciones:')
                for sec in sections:
                    print(f'   - ID: {sec.id}, Nombre: {sec.name}, Año: {sec.grade_level}, Capacidad: {sec.capacity}')
            
            # Check Classrooms
            print('\n🏫 AULAS:')
            classroom_count = db.session.query(func.count(Classroom.id)).scalar()
            print(f'   Total de aulas: {classroom_count}')
            
            if classroom_count > 0:
                classrooms = db.session.query(Classroom).limit(5).all()
                print(f'   Primeras 5 aulas:')
                for c in classrooms:
                    print(f'   - ID: {c.id}, Nombre: {c.name}, Capacidad: {c.capacity}, Tipo: {c.classroom_type}')
            
            # Check Schedule Assignments
            print('\n📅 ASIGNACIONES DE HORARIO:')
            assignment_count = db.session.query(func.count(ScheduleAssignment.id)).scalar()
            print(f'   Total de asignaciones: {assignment_count}')
            
            if assignment_count > 0:
                assignments = db.session.query(ScheduleAssignment).limit(5).all()
                print(f'   Primeras 5 asignaciones:')
                for a in assignments:
                    print(f'   - ID: {a.id}, Profesor ID: {a.teacher_id}, Sección ID: {a.section_id}')
                    print(f'     Día: {a.day_of_week}, Hora: {a.start_time} - {a.end_time}')
            
            # Summary
            print('\n' + '=' * 70)
            print('📊 RESUMEN:')
            print(f'   ✅ Profesores: {teacher_count}')
            print(f'   ✅ Estudiantes: {student_count}')
            print(f'   ✅ Secciones: {section_count}')
            print(f'   ✅ Aulas: {classroom_count}')
            print(f'   ✅ Asignaciones de horario: {assignment_count}')
            print('=' * 70)
            
            # Check database connection info
            print('\n🔗 INFORMACIÓN DE CONEXIÓN:')
            print(f'   Base de datos: {app.config.get("SQLALCHEMY_DATABASE_URI")}')
            
        except Exception as e:
            print(f'\n❌ Error al consultar la base de datos: {e}')
            print(f'\n💡 Posibles causas:')
            print(f'   1. La base de datos no existe')
            print(f'   2. Las tablas no han sido creadas')
            print(f'   3. Credenciales incorrectas')
            print(f'   4. El servidor MySQL no está corriendo')

if __name__ == '__main__':
    verify_database_data()
