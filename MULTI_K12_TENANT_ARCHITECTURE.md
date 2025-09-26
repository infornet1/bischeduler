# 🏫 Multi-K12 Tenant Architecture - BiScheduler
**Scalable Multi-School Management Platform for Venezuelan Education Network**

## 🎯 Executive Summary

BiScheduler will be enhanced to support multiple K-12 institutions across Venezuela, with UEIPAB.edu.ve as the master tenant managing invited guest schools. This multi-tenant architecture enables shared infrastructure while maintaining data isolation and customization per school.

---

## 🔍 Requirements Analysis

### **Business Requirements**
- **Master Tenant**: UEIPAB.edu.ve manages the platform
- **Guest Schools**: Invited K-12 institutions with similar academic needs
- **Shared Academic System**: Common academic management requirements
- **Venezuelan Compliance**: All schools need government reporting
- **Data Isolation**: Complete separation between schools
- **Unified Management**: Central administration by UEIPAB

### **Discovered Data Structure**
From the uploaded Matrícula template (`lista_de_estudiantes20250926-1-12p9kcj.xls`):
- **215 students** with complete family data
- **122 columns** including gender data (Column R: "Género")
- **Up to 3 representatives** per student (parents/guardians)
- **2 authorized representatives** per student
- **Rich demographic data** for government compliance

---

## 🏗️ Multi-Tenant Architecture Design

### **Tenant Isolation Strategy**: Schema-per-Tenant

#### **Shared Components** (Single Database)
```sql
-- Master tenant management
CREATE DATABASE bischeduler_master;

-- Shared tables across all tenants
CREATE TABLE tenants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subdomain VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    status ENUM('active', 'suspended', 'inactive') DEFAULT 'active',
    plan_type ENUM('master', 'guest') NOT NULL,
    master_tenant_id INT NULL,
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_subdomain (subdomain),
    INDEX idx_status (status),
    FOREIGN KEY (master_tenant_id) REFERENCES tenants(id)
);

-- Tenant invitations
CREATE TABLE tenant_invitations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invited_by_tenant_id INT NOT NULL,
    school_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    invitation_token VARCHAR(255) UNIQUE NOT NULL,
    status ENUM('pending', 'accepted', 'expired') DEFAULT 'pending',
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (invited_by_tenant_id) REFERENCES tenants(id),
    INDEX idx_token (invitation_token),
    INDEX idx_status (status)
);

-- Cross-tenant analytics (aggregated, anonymized)
CREATE TABLE platform_statistics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    tenant_count INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Tenant-Specific Schemas**
```sql
-- Each tenant gets its own schema
CREATE DATABASE bischeduler_ueipab;    -- Master tenant
CREATE DATABASE bischeduler_school2;   -- Guest tenant 1
CREATE DATABASE bischeduler_school3;   -- Guest tenant 2

-- Each tenant schema contains full BiScheduler structure:
-- - students, teachers, classes, schedules
-- - time_slots, subjects, classrooms
-- - daily_attendance, monthly_attendance_summary
-- - parent_accounts, teacher_preferences
-- - All business logic tables
```

### **URL Structure**
- **Master Tenant**: `bischeduler.ueipab.edu.ve` or `scheduler.ueipab.edu.ve`
- **Guest Schools**:
  - `bischeduler-escuela1.ueipab.edu.ve`
  - `bischeduler-escuela2.ueipab.edu.ve`
  - `bischeduler-escuela3.ueipab.edu.ve`

### **Authentication & Access Control**

#### **Tenant Resolution Middleware**
```python
# Flask middleware for tenant detection
class TenantMiddleware:
    def process_request(self, request):
        # Extract subdomain from URL
        host = request.host.lower()
        subdomain = self.extract_subdomain(host)

        # Resolve tenant from subdomain
        tenant = Tenant.get_by_subdomain(subdomain)
        if not tenant:
            return abort(404, "School not found")

        # Set tenant context for request
        g.current_tenant = tenant
        g.tenant_db = f"bischeduler_{tenant.subdomain}"

        # Verify tenant is active
        if tenant.status != 'active':
            return abort(503, "School system temporarily unavailable")
```

#### **Role-Based Access Control**
```python
# Enhanced roles for multi-tenant
ROLES = {
    'platform_admin': {  # UEIPAB super admin
        'can_create_tenants': True,
        'can_manage_invitations': True,
        'can_view_platform_analytics': True,
        'can_access_all_tenants': True
    },
    'school_admin': {    # School-level admin
        'can_manage_school_settings': True,
        'can_invite_users': True,
        'can_view_school_analytics': True,
        'tenant_restricted': True
    },
    'teacher': {         # Teacher role (tenant-restricted)
        'can_manage_preferences': True,
        'can_view_schedules': True,
        'can_mark_attendance': True,
        'tenant_restricted': True
    },
    'parent': {          # Parent role (tenant-restricted)
        'can_view_child_schedules': True,
        'can_receive_notifications': True,
        'tenant_restricted': True
    }
}
```

---

## 📊 Enhanced Database Schema

### **Tenant-Aware Tables** (Added to each tenant schema)
```sql
-- Tenant configuration
CREATE TABLE tenant_settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    setting_name VARCHAR(100) NOT NULL,
    setting_value TEXT,
    setting_type ENUM('string', 'integer', 'boolean', 'json') DEFAULT 'string',
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY unique_setting (setting_name)
);

-- School branding and customization
CREATE TABLE school_branding (
    id INT PRIMARY KEY AUTO_INCREMENT,
    school_logo_url VARCHAR(500),
    primary_color VARCHAR(7), -- HEX color
    secondary_color VARCHAR(7),
    school_motto TEXT,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    school_address TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Enhanced students table with tenant awareness
CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_code VARCHAR(50) UNIQUE NOT NULL,
    cedula VARCHAR(20) UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    gender ENUM('Masculino', 'Femenino') NOT NULL, -- From Matrícula
    birth_date DATE NOT NULL,
    grade_level VARCHAR(50) NOT NULL,
    section VARCHAR(10) NOT NULL,
    academic_year YEAR DEFAULT YEAR(CURDATE()),
    enrollment_status ENUM('active', 'inactive', 'transferred') DEFAULT 'active',
    -- Rich demographic data from Matrícula
    birth_city VARCHAR(100),
    birth_state VARCHAR(100),
    nationality VARCHAR(50) DEFAULT 'Venezuela',
    blood_type VARCHAR(10),
    allergies TEXT,
    address TEXT,
    emergency_contact_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_grade_section (grade_level, section),
    INDEX idx_student_code (student_code),
    INDEX idx_enrollment_status (enrollment_status)
);

-- Enhanced parent representatives (up to 3 per student)
CREATE TABLE student_representatives (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    representative_type ENUM('primary', 'secondary', 'emergency') NOT NULL,
    relationship ENUM('Padre', 'Madre', 'Abuelo', 'Abuela', 'Tío', 'Tía', 'Hermano', 'Hermana', 'Tutor Legal', 'Otro') NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    cedula VARCHAR(20),
    phone_mobile VARCHAR(20),
    phone_home VARCHAR(20),
    phone_office VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    occupation VARCHAR(100),
    workplace VARCHAR(200),
    monthly_income DECIMAL(12,2),
    is_primary_contact BOOLEAN DEFAULT FALSE,
    can_pick_up_student BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    INDEX idx_student_type (student_id, representative_type),
    INDEX idx_primary_contact (is_primary_contact)
);
```

### **Cross-Tenant Analytics Tables** (Master database)
```sql
-- Aggregated school statistics
CREATE TABLE tenant_analytics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tenant_id INT NOT NULL,
    total_students INT DEFAULT 0,
    total_teachers INT DEFAULT 0,
    total_classes INT DEFAULT 0,
    attendance_rate DECIMAL(5,2) DEFAULT 0,
    teacher_satisfaction_score DECIMAL(3,2) DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    INDEX idx_tenant (tenant_id)
);
```

---

## 🚀 Implementation Strategy

### **Phase Integration Approach**

#### **Phase 1.5: Multi-Tenant Foundation** ⭐ **NEW PHASE**
**Duration**: 3-4 hours
**Dependencies**: After Phase 1 (Git setup)

- **Master database setup**
  - Create tenant management tables
  - Create invitation system
  - Set up tenant resolution middleware
- **Subdomain routing configuration**
  - Nginx configuration for wildcard subdomains
  - SSL certificate setup for *.ueipab.edu.ve
  - DNS configuration
- **Enhanced authentication system**
  - Tenant-aware user authentication
  - Role-based access control
  - Cross-tenant permission management

#### **Phase 2.5: Tenant Schema Management** ⭐ **NEW PHASE**
**Duration**: 2-3 hours
**Dependencies**: After Phase 2 (Database Layer)

- **Dynamic schema creation**
  - Automated tenant database provisioning
  - Schema migration system for tenant updates
  - Tenant data isolation verification
- **Data migration enhancement**
  - Tenant-specific data import from existing systems
  - Matrícula template processing per school
  - Bulk tenant onboarding tools

### **Development Workflow Enhancement**

#### **Multi-Tenant Development Environment**
```bash
# Enhanced development setup
# Create development tenant databases
mysql -u root -p -e "CREATE DATABASE bischeduler_master;"
mysql -u root -p -e "CREATE DATABASE bischeduler_ueipab;"
mysql -u root -p -e "CREATE DATABASE bischeduler_demo1;"
mysql -u root -p -e "CREATE DATABASE bischeduler_demo2;"

# Local subdomain testing
echo "127.0.0.1 bischeduler.ueipab.local" >> /etc/hosts
echo "127.0.0.1 bischeduler-demo1.ueipab.local" >> /etc/hosts
echo "127.0.0.1 bischeduler-demo2.ueipab.local" >> /etc/hosts
```

---

## 🔧 Technical Implementation

### **Flask Application Structure**
```python
# Enhanced app factory for multi-tenancy
def create_app():
    app = Flask(__name__)

    # Register tenant middleware
    app.before_request(resolve_tenant)
    app.before_request(check_tenant_access)

    # Tenant-aware database connections
    @app.before_request
    def before_request():
        if g.get('current_tenant'):
            g.db = get_tenant_database(g.current_tenant)

    # Register blueprints with tenant prefix
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(platform_bp, url_prefix='/platform')  # Master tenant only

    return app

# Tenant-aware database connection
def get_tenant_database(tenant):
    return create_engine(f"mysql://user:pass@localhost/{tenant.database_name}")
```

### **Invitation System**
```python
# School invitation workflow
class TenantInvitationService:
    def invite_school(self, school_name, contact_email, invited_by_tenant):
        invitation = TenantInvitation(
            invited_by_tenant_id=invited_by_tenant.id,
            school_name=school_name,
            contact_email=contact_email,
            invitation_token=generate_secure_token(),
            expires_at=datetime.now() + timedelta(days=30)
        )

        # Send invitation email
        send_school_invitation_email(invitation)

        return invitation

    def accept_invitation(self, token, school_data):
        invitation = TenantInvitation.get_by_token(token)
        if not invitation or invitation.is_expired():
            raise InvalidInvitationError()

        # Create new tenant
        tenant = self.create_tenant(
            subdomain=school_data['subdomain'],
            name=school_data['name'],
            plan_type='guest',
            master_tenant_id=invitation.invited_by_tenant_id
        )

        # Create tenant database
        self.provision_tenant_database(tenant)

        # Mark invitation as accepted
        invitation.status = 'accepted'
        invitation.save()

        return tenant
```

---

## 📊 Matrícula Template Integration

### **Enhanced Excel Import for Multi-School**
Based on the analyzed template with 215 students and 122 columns:

```python
class MultiTenantMatriculaImporter:
    def import_school_data(self, tenant, file_path):
        df = pd.read_excel(file_path, header=2)

        # Validate Matrícula format
        required_columns = [
            'Grado', 'Sección', 'Nombre', 'Apellido',
            'Cédula de identidad', 'Género', 'Fecha de nacimiento'
        ]

        if not all(col in df.columns for col in required_columns):
            raise InvalidMatriculaFormatError()

        # Import students with tenant isolation
        with tenant_database_context(tenant):
            for _, row in df.iterrows():
                student = self.create_student_from_row(row)
                self.create_representatives_from_row(student, row)

        # Generate import report
        return {
            'total_students': len(df),
            'successful_imports': success_count,
            'failed_imports': failure_count,
            'validation_errors': errors
        }

    def create_representatives_from_row(self, student, row):
        # Primary representative (Representante)
        if row['Nombre de Representante']:
            rep1 = StudentRepresentative(
                student_id=student.id,
                representative_type='primary',
                relationship=row['Parentesco de Representante'],
                first_name=row['Nombre de Representante'],
                last_name=row['Apellido de Representante'],
                cedula=row['Cédula de identidad de Representante'],
                phone_mobile=row['Teléfono celular de Representante'],
                email=row['Correo electrónico de Representante'],
                # ... additional fields from 122 columns
            )
            rep1.save()

        # Secondary representative (Representante.1)
        if row['Nombre de Representante.1']:
            # Similar creation for second representative

        # Third representative (Representante.2)
        if row['Nombre de Representante.2']:
            # Similar creation for third representative
```

---

## 🔒 Security & Compliance

### **Data Isolation Guarantees**
- **Database-level isolation**: Separate schemas per tenant
- **Application-level verification**: Middleware ensures tenant context
- **API security**: All endpoints validate tenant access
- **Cross-tenant prevention**: No data leakage between schools

### **Venezuelan Government Compliance**
- **Per-school reporting**: Each tenant generates own Matrícula reports
- **Aggregated statistics**: Platform-level anonymized analytics
- **Data residency**: All data stays within Venezuelan jurisdiction
- **Audit trails**: Complete activity logging per tenant

---

## 📈 Scalability Considerations

### **Performance Optimization**
- **Connection pooling**: Per-tenant database pools
- **Caching strategy**: Redis with tenant-aware keys
- **Static asset optimization**: CDN with tenant branding
- **Database indexing**: Optimized for multi-tenant queries

### **Growth Planning**
- **Current capacity**: 215 students × N schools
- **Target capacity**: 1000+ students per school, 50+ schools
- **Infrastructure scaling**: Horizontal database scaling
- **Cost optimization**: Shared infrastructure, per-school billing

---

## 🎯 Success Metrics

### **Platform Metrics**
- **School onboarding**: Target 5-10 schools in Year 1
- **User adoption**: >80% teacher satisfaction across all schools
- **System performance**: <3 seconds response time per tenant
- **Data accuracy**: >95% import success rate across all schools

### **Business Metrics**
- **Network effect**: Schools referring other schools
- **Retention rate**: >90% school retention year-over-year
- **Support efficiency**: <24 hour response time
- **Compliance rate**: 100% government reporting success

---

## 📋 Implementation Timeline

### **Enhanced Project Timeline**
| Phase | Component | Duration | Total Hours |
|-------|-----------|----------|-------------|
| **0-1** | Foundation + Git + Migration | 3.5-5.5 hours | Base |
| **1.5** | **Multi-Tenant Foundation** | **3-4 hours** | **NEW** |
| **2** | Database Layer | 2-3 hours | Enhanced |
| **2.5** | **Tenant Schema Management** | **2-3 hours** | **NEW** |
| **3-13** | Core BiScheduler Features | 40-55 hours | Base |
| **Total** | **Multi-Tenant BiScheduler** | **48.5-70.5 hours** | **Enhanced** |

### **Deployment Strategy**
1. **Phase 1**: Deploy master tenant (UEIPAB) with basic features
2. **Phase 2**: Invite 2-3 demo schools for testing
3. **Phase 3**: Production rollout with full feature set
4. **Phase 4**: Network expansion to 10+ schools

---

## ✅ Conclusion

This multi-tenant architecture transforms BiScheduler from a single-school solution into a **scalable Venezuelan education network platform**. Key benefits:

### **For UEIPAB (Master Tenant)**:
- **Platform ownership** and control
- **Revenue opportunity** from guest schools
- **Network effect** from shared improvements
- **Economies of scale** in development and maintenance

### **For Guest Schools**:
- **Proven solution** with UEIPAB validation
- **Cost-effective** shared infrastructure
- **Venezuelan compliance** built-in
- **Continuous improvement** from network effects

### **Technical Excellence**:
- **Complete data isolation** for security
- **Scalable architecture** for growth
- **Professional development** with Git workflow
- **Government compliance** for all schools

**Recommendation**: **IMPLEMENT** multi-tenant architecture as enhanced Phases 1.5 and 2.5 for maximum long-term value and scalability.

---

**Status**: ✅ **Architecture Complete - Ready for Implementation Integration**