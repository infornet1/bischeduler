from sqlalchemy import create_engine, inspect

engine = create_engine('mysql+pymysql://root:0000@localhost/ueipab_2025_data')
inspector = inspect(engine)

print('\n' + '='*70)
print('ESTRUCTURA DE LA TABLA: monthly_attendance_summary')
print('='*70)

columns = inspector.get_columns('monthly_attendance_summary')

print('\nColumnas existentes:')
for col in columns:
    print(f"  ✓ {col['name']:30} {col['type']}")

print('\n' + '='*70)
print('Columnas esperadas por el modelo:')
print('='*70)
expected = [
    'id', 'grade_level', 'section_count', 'male_students', 
    'female_students', 'total_students', 'working_days', 
    'attendance_sum', 'average_attendance', 'attendance_percentage',
    'month', 'year', 'calculated_at', 'calculated_by',
    'created_at', 'updated_at'
]

existing_cols = [col['name'] for col in columns]

print('\nComparación:')
for col in expected:
    if col in existing_cols:
        print(f"  ✓ {col}")
    else:
        print(f"  ✗ {col} - FALTA EN LA BASE DE DATOS")

print('\n' + '='*70)