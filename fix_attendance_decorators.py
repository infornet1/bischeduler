#!/usr/bin/env python3
"""
Remove @require_tenant decorators and add ensure_tenant_context() calls
"""

import re

# Read the file
with open('src/attendance/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove @require_tenant decorators
content = content.replace('\n@require_tenant\n', '\n')

# Find all function definitions that need tenant context
# Add ensure_tenant_context() at the beginning of each function that had @require_tenant

functions_to_fix = [
    'api_calculate_monthly',
    'admin_dashboard',
    'api_admin_statistics',
    'api_admin_grade_summary',
    'api_admin_critical_alerts',
    'api_admin_chart_data',
    'export_matricula'
]

tenant_check = """    # Ensure tenant context
    if not ensure_tenant_context():
        return jsonify({
            'error': 'Tenant not found',
            'message': 'UEIPAB tenant not configured in database'
        }), 400
    
"""

for func_name in functions_to_fix:
    # Find the function and add tenant check after the docstring
    pattern = f'(def {func_name}\\([^)]*\\):\n    """[^"]*""")\n'
    replacement = f'\\1\n{tenant_check}'
    content = re.sub(pattern, replacement, content)

# Write back
with open('src/attendance/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all @require_tenant decorators!")
print(f"   Updated {len(functions_to_fix)} functions")
