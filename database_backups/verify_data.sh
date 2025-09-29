#!/bin/bash

# BiScheduler Database Verification Script
# Quick verification of restored database content

set -e

# Database configuration
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASS:-Temporal2024!}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔍 BiScheduler Database Verification${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Master Database Verification
echo -e "${YELLOW}📊 Master Database (bischeduler_master):${NC}"
mysql -u"$DB_USER" -p"$DB_PASS" -e "
SELECT
    'Platform Admin Users' as item,
    COUNT(*) as count
FROM bischeduler_master.users
WHERE role = 'platform_admin'
UNION ALL
SELECT
    'Total Tenants' as item,
    COUNT(*) as count
FROM bischeduler_master.tenants
UNION ALL
SELECT
    'Active Sessions' as item,
    COUNT(*) as count
FROM bischeduler_master.user_sessions
WHERE is_active = 1;
"

echo ""
echo -e "${YELLOW}📊 Tenant Database (ueipab_2025_data):${NC}"
mysql -u"$DB_USER" -p"$DB_PASS" -e "
SELECT
    'Teachers' as item,
    COUNT(*) as count
FROM ueipab_2025_data.teachers
UNION ALL
SELECT
    'Students' as item,
    COUNT(*) as count
FROM ueipab_2025_data.students
UNION ALL
SELECT
    'Sections' as item,
    COUNT(*) as count
FROM ueipab_2025_data.sections
UNION ALL
SELECT
    'Subjects' as item,
    COUNT(*) as count
FROM ueipab_2025_data.subjects
UNION ALL
SELECT
    'Schedule Assignments' as item,
    COUNT(*) as count
FROM ueipab_2025_data.schedule_assignments
UNION ALL
SELECT
    'Time Periods' as item,
    COUNT(*) as count
FROM ueipab_2025_data.time_periods;
"

echo ""
echo -e "${YELLOW}🏫 Educational Structure (UEIPAB):${NC}"
mysql -u"$DB_USER" -p"$DB_PASS" -e "
SELECT
    name as section,
    grade_level,
    educational_level,
    current_students as students
FROM ueipab_2025_data.sections
WHERE is_active = 1
ORDER BY grade_level, name;
"

echo ""
echo -e "${GREEN}✅ Database verification complete!${NC}"