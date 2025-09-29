# BiScheduler Database Backups

## Overview
This directory contains database backups for the BiScheduler Venezuelan K12 Multi-Tenant Scheduling Platform.

## Structure
```
database_backups/
├── master/                     # Master database backups (bischeduler_master)
│   └── bischeduler_master_*    # Platform admin users, tenants registry
├── tenants/                    # Tenant database backups
│   └── ueipab_2025/           # UEIPAB 2025-2026 academic year data
│       └── ueipab_2025_data_* # Complete school schedule data
└── README.md                   # This file
```

## Current Backups

### Master Database (bischeduler_master)
- **Purpose**: Platform administration, tenant registry, platform admin users
- **Contains**:
  - Platform admin users (admin@ueipab.edu.ve)
  - Tenant definitions and configurations
  - Multi-tenant management data
- **Size**: ~17KB
- **Tables**: users, tenants, tenant_invitations, user_sessions, user_audit_logs

### Tenant Database (ueipab_2025_data)
- **Institution**: UEIPAB - Unidad Educativa Instituto Privado Adventista Barquisimeto
- **Academic Year**: 2025-2026
- **Purpose**: Complete K12 schedule management data
- **Contains**:
  - Students (Venezuelan K12 structure)
  - Teachers and their assignments
  - Subjects (Venezuelan curriculum)
  - Schedule assignments (228 weekly periods)
  - Attendance tracking system
  - Exam scheduling system
- **Size**: ~137KB
- **Educational Levels**: Educación Inicial, Primaria, Media General

## Restoration Instructions

### 1. Restore Master Database
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS bischeduler_master;"
mysql -u root -p bischeduler_master < database_backups/master/bischeduler_master_[timestamp].sql
```

### 2. Restore Tenant Database
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS ueipab_2025_data;"
mysql -u root -p ueipab_2025_data < database_backups/tenants/ueipab_2025/ueipab_2025_data_[timestamp].sql
```

### 3. Verify Restoration
```bash
# Check master database
mysql -u root -p -e "SELECT COUNT(*) as users FROM bischeduler_master.users;"
mysql -u root -p -e "SELECT COUNT(*) as tenants FROM bischeduler_master.tenants;"

# Check tenant database
mysql -u root -p -e "SELECT COUNT(*) as teachers FROM ueipab_2025_data.teachers;"
mysql -u root -p -e "SELECT COUNT(*) as students FROM ueipab_2025_data.students;"
mysql -u root -p -e "SELECT COUNT(*) as assignments FROM ueipab_2025_data.schedule_assignments;"
```

## Database Content Summary

### UEIPAB 2025-2026 Data Overview
- **12 Sections**: From Educación Inicial to 5to. Año
- **14 Teachers**: Venezuelan K12 certified educators
- **70+ Subjects**: Complete Venezuelan curriculum
- **228 Schedule Assignments**: Weekly class periods
- **5 Time Periods**: 7:00 AM - 10:40 AM daily schedule
- **45 Classrooms**: School infrastructure
- **Venezuelan Compliance**: Full K12 regulatory compliance

## Login Credentials

### Platform Admin
- **Email**: admin@ueipab.edu.ve
- **Password**: SecurePassword123!
- **Role**: platform_admin
- **Access**: All tenants, system administration

## Backup Schedule
- **Frequency**: Manual (before major changes)
- **Retention**: Keep last 5 backups
- **Format**: MySQL dump files (.sql)
- **Compression**: None (for easy inspection)

## Git Integration
These backups are version controlled with the main BiScheduler repository for:
- Change tracking
- Rollback capability
- Development environment setup
- Production deployment

## Security Notes
- Passwords in backups are hashed (pbkdf2:sha256)
- No plain text credentials stored
- Backup files should be treated as sensitive data
- Restrict access to authorized personnel only

---
*Generated on: 2025-09-29*
*BiScheduler v1.0*
*Venezuelan K12 Multi-Tenant Scheduling Platform*