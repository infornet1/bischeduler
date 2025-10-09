"""
Migración: Actualizar tabla monthly_attendance_summary
Agrega columnas necesarias para resúmenes mensuales por grado
"""

from sqlalchemy import create_engine, text

def migrate_table():
    engine = create_engine('mysql+pymysql://root:0000@localhost/ueipab_2025_data')
    
    print('=' * 70)
    print('MIGRACIÓN: monthly_attendance_summary')
    print('=' * 70)
    print()
    
    with engine.connect() as conn:
        # Agregar columnas faltantes
        migrations = [
            ("section_count", "ALTER TABLE monthly_attendance_summary ADD COLUMN section_count INT NOT NULL DEFAULT 0"),
            ("male_students", "ALTER TABLE monthly_attendance_summary ADD COLUMN male_students INT NOT NULL DEFAULT 0"),
            ("female_students", "ALTER TABLE monthly_attendance_summary ADD COLUMN female_students INT NOT NULL DEFAULT 0"),
            ("total_students", "ALTER TABLE monthly_attendance_summary ADD COLUMN total_students INT NOT NULL DEFAULT 0"),
            ("working_days", "ALTER TABLE monthly_attendance_summary ADD COLUMN working_days INT NOT NULL DEFAULT 0"),
            ("attendance_sum", "ALTER TABLE monthly_attendance_summary ADD COLUMN attendance_sum INT NOT NULL DEFAULT 0"),
            ("average_attendance", "ALTER TABLE monthly_attendance_summary ADD COLUMN average_attendance DECIMAL(5,2) NOT NULL DEFAULT 0.00"),
            ("calculated_at", "ALTER TABLE monthly_attendance_summary ADD COLUMN calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ("calculated_by", "ALTER TABLE monthly_attendance_summary ADD COLUMN calculated_by VARCHAR(100)")
        ]
        
        for col_name, sql in migrations:
            try:
                print(f"Agregando columna: {col_name}...", end=' ')
                conn.execute(text(sql))
                conn.commit()
                print("✅")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("⚠️  Ya existe")
                else:
                    print(f"❌ Error: {e}")
        
        print()
        print('=' * 70)
        print('✅ MIGRACIÓN COMPLETADA')
        print('=' * 70)
        print()
        print('NOTA: La tabla ahora tiene columnas mixtas.')
        print('      - Columnas antiguas (student_id, present_days, etc.) - No se eliminan')
        print('      - Columnas nuevas (section_count, male_students, etc.) - Agregadas')
        print()
        print('Reinicia el servidor Flask para usar la nueva estructura.')

if __name__ == '__main__':
    migrate_table()