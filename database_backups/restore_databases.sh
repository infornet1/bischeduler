#!/bin/bash

# BiScheduler Database Restoration Script
# Venezuelan K12 Multi-Tenant Scheduling Platform
# Restores both master and tenant databases from backups

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Database configuration
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASS:-Temporal2024!}"
MASTER_DB="bischeduler_master"
TENANT_DB="ueipab_2025_data"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🚀 BiScheduler Database Restoration${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Function to check if MySQL is running
check_mysql() {
    echo -e "${YELLOW}🔍 Checking MySQL connection...${NC}"
    if ! mysql -u"$DB_USER" -p"$DB_PASS" -e "SELECT 1;" >/dev/null 2>&1; then
        echo -e "${RED}❌ Cannot connect to MySQL. Check credentials and service status.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ MySQL connection successful${NC}"
}

# Function to find latest backup file
find_latest_backup() {
    local backup_dir="$1"
    local pattern="$2"

    local latest_file=$(find "$backup_dir" -name "$pattern" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)

    if [ -z "$latest_file" ]; then
        echo -e "${RED}❌ No backup files found in $backup_dir matching $pattern${NC}"
        return 1
    fi

    echo "$latest_file"
}

# Function to restore database
restore_database() {
    local db_name="$1"
    local backup_file="$2"
    local description="$3"

    echo -e "${YELLOW}📦 Restoring $description ($db_name)...${NC}"

    # Drop and recreate database
    mysql -u"$DB_USER" -p"$DB_PASS" -e "DROP DATABASE IF EXISTS $db_name;"
    mysql -u"$DB_USER" -p"$DB_PASS" -e "CREATE DATABASE $db_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

    # Restore from backup
    mysql -u"$DB_USER" -p"$DB_PASS" "$db_name" < "$backup_file"

    echo -e "${GREEN}✅ $description restored successfully${NC}"
}

# Function to verify restoration
verify_restoration() {
    echo -e "${YELLOW}🔍 Verifying database restoration...${NC}"

    # Check master database
    local user_count=$(mysql -u"$DB_USER" -p"$DB_PASS" -sN -e "SELECT COUNT(*) FROM $MASTER_DB.users;" 2>/dev/null || echo "0")
    local tenant_count=$(mysql -u"$DB_USER" -p"$DB_PASS" -sN -e "SELECT COUNT(*) FROM $MASTER_DB.tenants;" 2>/dev/null || echo "0")

    # Check tenant database
    local teacher_count=$(mysql -u"$DB_USER" -p"$DB_PASS" -sN -e "SELECT COUNT(*) FROM $TENANT_DB.teachers;" 2>/dev/null || echo "0")
    local student_count=$(mysql -u"$DB_USER" -p"$DB_PASS" -sN -e "SELECT COUNT(*) FROM $TENANT_DB.students;" 2>/dev/null || echo "0")
    local assignment_count=$(mysql -u"$DB_USER" -p"$DB_PASS" -sN -e "SELECT COUNT(*) FROM $TENANT_DB.schedule_assignments;" 2>/dev/null || echo "0")

    echo -e "${BLUE}📊 Database Verification Results:${NC}"
    echo -e "   Master Database ($MASTER_DB):"
    echo -e "   ├── Users: $user_count"
    echo -e "   └── Tenants: $tenant_count"
    echo -e ""
    echo -e "   Tenant Database ($TENANT_DB):"
    echo -e "   ├── Teachers: $teacher_count"
    echo -e "   ├── Students: $student_count"
    echo -e "   └── Schedule Assignments: $assignment_count"
    echo -e ""

    if [ "$user_count" -gt 0 ] && [ "$tenant_count" -gt 0 ] && [ "$teacher_count" -gt 0 ] && [ "$assignment_count" -gt 0 ]; then
        echo -e "${GREEN}✅ All databases restored and verified successfully!${NC}"
        return 0
    else
        echo -e "${RED}❌ Database verification failed. Some tables may be empty.${NC}"
        return 1
    fi
}

# Main execution
main() {
    check_mysql

    # Find latest backup files
    echo -e "${YELLOW}🔍 Finding latest backup files...${NC}"

    local master_backup=$(find_latest_backup "$SCRIPT_DIR/master" "bischeduler_master_*.sql")
    if [ $? -ne 0 ]; then exit 1; fi

    local tenant_backup=$(find_latest_backup "$SCRIPT_DIR/tenants/ueipab_2025" "ueipab_2025_data_*.sql")
    if [ $? -ne 0 ]; then exit 1; fi

    echo -e "${BLUE}📁 Using backup files:${NC}"
    echo -e "   Master: $(basename "$master_backup")"
    echo -e "   Tenant: $(basename "$tenant_backup")"
    echo ""

    # Confirm before proceeding
    read -p "Continue with database restoration? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🚫 Restoration cancelled.${NC}"
        exit 0
    fi

    # Perform restoration
    restore_database "$MASTER_DB" "$master_backup" "Master Database"
    restore_database "$TENANT_DB" "$tenant_backup" "UEIPAB Tenant Database"

    # Verify restoration
    verify_restoration

    echo -e ""
    echo -e "${GREEN}🎉 BiScheduler databases restored successfully!${NC}"
    echo -e ""
    echo -e "${BLUE}🔑 Login Credentials:${NC}"
    echo -e "   Email: admin@ueipab.edu.ve"
    echo -e "   Password: SecurePassword123!"
    echo -e "   Role: platform_admin"
    echo -e ""
    echo -e "${BLUE}🌐 Access URL:${NC}"
    echo -e "   https://dev.ueipab.edu.ve/bischeduler/"
    echo -e ""
}

# Check if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi