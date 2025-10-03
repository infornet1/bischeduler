#!/usr/bin/env python3
"""
Script to add /bischeduler prefix to missing routes
"""

import re

# Read the file
with open('src/core/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add prefix to bimodal route
content = content.replace(
    "    @app.route('/bimodal')\n    def bimodal():",
    "    @app.route('/bimodal')\n    @app.route('/bischeduler/bimodal')\n    def bimodal():"
)

# Add prefix to matricula route
content = content.replace(
    "    @app.route('/matricula')\n    def matricula():",
    "    @app.route('/matricula')\n    @app.route('/bischeduler/matricula')\n    def matricula():"
)

# Add prefix to reports route
content = content.replace(
    "    @app.route('/reports')\n    def reports():",
    "    @app.route('/reports')\n    @app.route('/bischeduler/reports')\n    def reports():"
)

# Add prefix to admin route
content = content.replace(
    "    @app.route('/admin')\n    def admin():",
    "    @app.route('/admin')\n    @app.route('/bischeduler/admin')\n    def admin():"
)

# Fix attendance blueprint registration
content = content.replace(
    "app.register_blueprint(attendance_bp)",
    "app.register_blueprint(attendance_bp, url_prefix='/bischeduler/attendance')"
)

# Write the file back
with open('src/core/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Routes updated successfully!")
print("   - /bischeduler/bimodal")
print("   - /bischeduler/matricula")
print("   - /bischeduler/reports")
print("   - /bischeduler/admin")
print("   - /bischeduler/attendance/*")
