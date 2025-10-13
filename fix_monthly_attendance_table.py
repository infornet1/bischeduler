"""
Fix monthly_attendance_summary table - Make student_id nullable
"""
from sqlalchemy import create_engine, text

def fix_table():
    engine = create_engine('mysql+pymysql://root:0000@localhost/ueipab_2025_data')
    
    print('=' * 70)
    print('FIX: monthly_attendance_summary - Hacer student_id opcional')
    print('=' * 70)
    print()
    
    with engine.connect() as conn:
        try:
            # Make student_id nullable
            print("Haciendo student_id nullable...", end=' ')
            conn.execute(text("ALTER TABLE monthly_attendance_summary MODIFY COLUMN student_id INT NULL"))
            conn.commit()
            print("✅")
            
            # Also make other old columns nullable if they exist
            old_columns = [
                'present_days',
                'absent_days',
                'excused_absences',
                'unexcused_absences',
                'late_arrivals'
            ]
            
            for col in old_columns:
                try:
                    print(f"Haciendo {col} nullable...", end=' ')
                    conn.execute(text(f"ALTER TABLE monthly_attendance_summary MODIFY COLUMN {col} INT NULL"))
                    conn.commit()
                    print("✅")
                except Exception as e:
                    if "Unknown column" in str(e):
                        print("⚠️  No existe")
                    else:
                        print(f"❌ {e}")
            
            print()
            print('=' * 70)
            print('✅ CORRECCIÓN COMPLETADA')
            print('=' * 70)
            print()
            print('Ahora la tabla puede almacenar resúmenes por grado (sin student_id)')
            print('Reinicia el servidor Flask.')
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    fix_table()
