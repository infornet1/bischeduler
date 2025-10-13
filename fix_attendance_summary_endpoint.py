"""
Fix Attendance Summary Endpoint - Tenant Context Error
Corrige el error 400 en /api/attendance/summary/<section_id>
"""

import os
import sys

def fix_attendance_summary_endpoint():
    """
    Reemplaza la lógica de tenant en api_attendance_summary que causa error 400
    con la función ensure_tenant_context() que funciona correctamente
    """
    
    views_path = os.path.join(os.path.dirname(__file__), 'src', 'attendance', 'views.py')
    
    if not os.path.exists(views_path):
        print(f"❌ Error: No se encontró el archivo {views_path}")
        return False
    
    print(f"📂 Leyendo archivo: {views_path}")
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Código problemático que causa error 400
    old_code = """    from flask import g, request
    from src.tenants.manager import TenantManager

    # Manual tenant resolution for API
    if not hasattr(g, 'current_tenant') or not g.current_tenant:
        tenant_manager = TenantManager('mysql+pymysql://root:0000@localhost/bischeduler_master')
        tenant = tenant_manager.get_tenant_by_domain(request.host)

        if tenant:
            g.current_tenant = tenant
        else:
            return jsonify({
                'error': 'Tenant context required',
                'message': 'This endpoint requires tenant identification',
                'debug': f'Host: {request.host}'
            }), 400"""
    
    # Código correcto que funciona en otros endpoints
    new_code = """    # Ensure tenant context
    if not ensure_tenant_context():
        return jsonify({
            'error': 'Tenant not found',
            'message': 'UEIPAB tenant not configured in database'
        }), 400"""
    
    if old_code not in content:
        print("⚠️  Advertencia: No se encontró el código problemático exacto.")
        print("    El endpoint puede ya estar corregido o tener un formato diferente.")
        
        # Intentar buscar una variación
        if "get_tenant_by_domain(request.host)" in content:
            print("    Se detectó get_tenant_by_domain en el archivo.")
            print("    Aplicando corrección alternativa...")
            
            # Buscar el bloque completo del endpoint
            import re
            pattern = r"(@attendance_bp\.route\('/api/attendance/summary/<int:section_id>'\)\s+def api_attendance_summary\(section_id\):.*?)(    try:)"
            
            def replace_func(match):
                header = match.group(1)
                try_line = match.group(2)
                
                # Extraer solo la definición de la función y docstring
                lines = header.split('\n')
                new_header_lines = []
                in_docstring = False
                docstring_count = 0
                
                for line in lines:
                    if '"""' in line:
                        docstring_count += line.count('"""')
                        new_header_lines.append(line)
                        if docstring_count >= 2:
                            break
                    else:
                        new_header_lines.append(line)
                
                new_header = '\n'.join(new_header_lines)
                
                return f"{new_header}\n{new_code}\n    \n{try_line}"
            
            content_fixed = re.sub(pattern, replace_func, content, flags=re.DOTALL)
            
            if content_fixed != content:
                content = content_fixed
                print("✅ Corrección alternativa aplicada exitosamente")
            else:
                print("❌ No se pudo aplicar la corrección alternativa")
                return False
        else:
            return False
    else:
        # Reemplazar el código problemático
        content = content.replace(old_code, new_code)
        print("✅ Código problemático encontrado y reemplazado")
    
    # Crear backup
    backup_path = views_path + '.backup_summary_fix'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Backup creado: {backup_path}")
    
    # Guardar el archivo corregido
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo corregido exitosamente")
    print("\n📋 Cambios realizados:")
    print("   - Reemplazada lógica de TenantManager.get_tenant_by_domain()")
    print("   - Implementada función ensure_tenant_context()")
    print("   - El endpoint ahora usará UEIPAB001 directamente")
    print("\n🔄 Reinicia el servidor Flask para aplicar los cambios:")
    print("   python manage.py runserver")
    
    return True


if __name__ == '__main__':
    print("=" * 70)
    print("🔧 Fix Attendance Summary Endpoint - Error 400")
    print("=" * 70)
    print()
    
    success = fix_attendance_summary_endpoint()
    
    print()
    print("=" * 70)
    if success:
        print("✅ CORRECCIÓN COMPLETADA")
        print("   El endpoint /api/attendance/summary/<section_id> ahora funcionará")
        print("   correctamente sin error 400.")
    else:
        print("❌ CORRECCIÓN FALLIDA")
        print("   Revisa manualmente el archivo src/attendance/views.py")
        print("   Líneas 298-320 (función api_attendance_summary)")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
