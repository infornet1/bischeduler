# BiScheduler - Multi-Tenant K12 Scheduling Platform

BiScheduler is a comprehensive multi-tenant scheduling platform designed specifically for Venezuelan K12 educational institutions. Born from UEIPAB's scheduling needs, it enables multiple schools to manage their academic schedules while maintaining compliance with Venezuelan educational requirements.

## 🎯 Key Features

### Multi-Tenant Architecture
- **Schema-per-tenant isolation** for complete data privacy
- **Tenant invitation system** for easy school onboarding
- **Centralized master database** for tenant management
- **Custom branding** per educational institution

### Venezuelan Education Compliance
- **Matrícula reporting** integration (122-column Excel template)
- **Bimodal schedule support** (7:00 AM - 2:20 PM)
- **Authentic curriculum subjects** (Bachillerato, Primaria, Preescolar)
- **Government reporting** capabilities

### Advanced Scheduling
- **Conflict detection** and resolution
- **Teacher workload optimization**
- **Classroom capacity management**
- **Multi-grade section support**

## 🏗️ Technical Stack

- **Backend**: Python Flask with SQLAlchemy
- **Database**: MariaDB with schema-per-tenant
- **Authentication**: JWT with role-based access
- **Frontend**: Modern web interface
- **Infrastructure**: Nginx reverse proxy
- **Deployment**: Port 5005 (reused from legacy system)

## 🗂️ Project Structure

```
bischeduler/
├── migration_workspace/     # Data migration from legacy system
├── src/                    # Application source code
├── docs/                   # Documentation and planning
├── tests/                  # Test suites
├── deployment/             # Deployment configurations
└── branding/              # Logo and visual assets
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MariaDB 10.6+
- Nginx
- Git

### Installation
```bash
# Clone repository
git clone https://github.com/infornet1/bischeduler.git
cd bischeduler

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python manage.py init-db

# Run application
python manage.py run
```

## 📊 Data Migration

BiScheduler includes comprehensive migration tools to import data from existing UEIPAB scheduling systems:

- **Time Periods**: Venezuelan bimodal schedule (10 periods + 2 breaks)
- **Subjects**: Authentic curriculum (MATEMÁTICAS, CASTELLANO, CIENCIAS, etc.)
- **Teachers**: Faculty with area specializations
- **Infrastructure**: Classrooms and section mappings

Migration saves **8-11 hours** of manual Venezuelan education setup.

## 🎨 Branding

BiScheduler features professional branding inspired by UEIPAB's architectural bridge motif:
- Custom logo design
- Venezuelan education color palette
- Responsive visual identity
- Tenant-specific customization

## 🏫 Target Users

### Primary
- **UEIPAB** (Universidad Experimental de las Fuerzas Armadas Nacional Bolivariana)
- Venezuelan K12 institutions requiring government compliance

### Secondary
- Latin American schools with similar scheduling needs
- Educational institutions seeking multi-tenant solutions

## 📈 Development Phases

1. **Phase 0**: Data Migration ✅
2. **Phase 1a**: Git Integration ⚡ *In Progress*
3. **Phase 1b**: Project Structure
4. **Phase 1.5**: Multi-Tenant Foundation
5. **Phase 1.75**: Branding & Visual Identity
6. **Phase 2**: Core Database Schema
7. **Phase 3**: Authentication & Authorization
8. **Additional phases**: UI, Advanced Features, Testing

## 🤝 Contributing

BiScheduler is developed with careful attention to Venezuelan educational standards and multi-tenant architecture. Contributions should maintain:

- Code quality and documentation
- Venezuelan education compliance
- Multi-tenant data isolation
- Security best practices

## 📄 License

[License information to be determined]

## 🏢 About UEIPAB

Universidad Experimental de las Fuerzas Armadas Nacional Bolivariana is committed to educational excellence and technological innovation in Venezuelan higher education.

---

**Built with ❤️ for Venezuelan education**