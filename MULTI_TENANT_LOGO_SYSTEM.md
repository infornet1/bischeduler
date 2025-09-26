# Multi-Tenant Logo System Implementation Plan
**Enhancement to Phase 1.75: Branding & Visual Identity**

## 🎯 **Feature Overview**

Enable Venezuelan K12 schools to upload and automatically display their institutional logos throughout the BiScheduler platform, creating a personalized branding experience for each tenant.

---

## 🔍 **Requirements Analysis**

### **User Stories**
1. **School Administrator**: "I want to upload our school logo so students and teachers see our institutional identity"
2. **Student/Teacher**: "When I log in, I want to see my school's logo, not just the generic BiScheduler logo"
3. **Parent**: "I want to recognize this is my child's school system when I access the platform"

### **Technical Requirements**
- **File Upload**: Secure logo upload for tenant admins
- **Dynamic Resolution**: Automatic logo display based on current tenant context
- **Fallback System**: BiScheduler logo when no custom logo exists
- **Multi-Format Support**: PNG, JPG, SVG logo formats
- **Responsive Sizing**: Logos work across desktop/mobile interfaces
- **Security Validation**: File type, size, and content validation

---

## 🏗️ **Implementation Strategy**

### **Phase 1.8: Multi-Tenant Logo System** ⭐ **NEW ENHANCEMENT PHASE**
**Duration**: 2-3 hours
**Impact**: Low-Medium (High Value)
**Dependencies**: Phase 1.5 (Multi-Tenant Foundation), Phase 1.75 (Branding)

#### **Backend Implementation**

##### **1. Database Schema Enhancement**
```sql
-- Add to existing tenants table in master database
ALTER TABLE tenants ADD COLUMN logo_filename VARCHAR(255);
ALTER TABLE tenants ADD COLUMN logo_uploaded_at DATETIME;
ALTER TABLE tenants ADD COLUMN logo_file_size INT;
```

##### **2. File Storage System**
```python
# src/core/file_storage.py
class TenantLogoStorage:
    """Secure file storage for tenant logos"""

    STORAGE_PATH = '/var/www/dev/bischeduler/static/tenants/logos/'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB limit

    def save_tenant_logo(self, tenant_id: str, file) -> str:
        """Save uploaded logo with security validation"""

    def get_tenant_logo_url(self, tenant_id: str) -> Optional[str]:
        """Get logo URL for tenant, fallback to BiScheduler logo"""

    def delete_tenant_logo(self, tenant_id: str) -> bool:
        """Remove tenant logo file"""
```

##### **3. Enhanced Branding Manager**
```python
# Update src/core/branding.py
class BrandingManager:
    def get_tenant_branding(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced with dynamic logo resolution"""
        branding = self._get_default_branding(tenant)

        # Check for custom tenant logo
        if tenant and tenant.logo_filename:
            branding['assets']['logo_full'] = f'/static/tenants/logos/{tenant.logo_filename}'
            branding['assets']['institution_logo'] = f'/static/tenants/logos/{tenant.logo_filename}'
            branding['has_custom_logo'] = True
        else:
            branding['has_custom_logo'] = False

        return branding
```

##### **4. Logo Upload API Endpoint**
```python
# src/api/tenants.py
@tenants_bp.route('/<tenant_id>/logo', methods=['POST'])
@require_tenant_admin
def upload_tenant_logo(tenant_id):
    """Upload custom logo for tenant"""

@tenants_bp.route('/<tenant_id>/logo', methods=['DELETE'])
@require_tenant_admin
def delete_tenant_logo(tenant_id):
    """Remove custom tenant logo"""
```

#### **Frontend Implementation**

##### **5. Logo Upload Interface**
```html
<!-- Tenant admin settings page -->
<div class="logo-management">
    <h3>Institutional Logo</h3>
    <div class="current-logo">
        <img src="{{ current_logo_url }}" alt="Current Logo" height="80">
    </div>
    <form id="logo-upload-form" enctype="multipart/form-data">
        <input type="file" name="logo" accept=".png,.jpg,.jpeg,.svg">
        <button type="submit">Upload Logo</button>
    </form>
</div>
```

##### **6. Dynamic Logo Display**
```html
<!-- Global header template -->
<header class="navbar">
    {% if branding.has_custom_logo %}
        <img src="{{ branding.assets.institution_logo }}" alt="{{ tenant.institution_name }}" height="40">
        <img src="{{ branding.assets.logo_full }}" alt="BiScheduler" height="30" class="platform-logo">
    {% else %}
        <img src="{{ branding.assets.logo_full }}" alt="BiScheduler" height="40">
    {% endif %}
</header>
```

#### **7. Security & Validation**
```python
# src/utils/file_validation.py
class LogoValidator:
    """Comprehensive logo file validation"""

    def validate_logo_file(self, file) -> ValidationResult:
        """Multi-layer validation:
        - File extension check
        - MIME type validation
        - File size limits
        - Image content verification
        - Malware scanning (basic)
        """
```

---

## 🎨 **User Experience Flow**

### **School Administrator Workflow**
1. **Login to BiScheduler** as tenant admin
2. **Navigate to Settings** → "Institutional Branding"
3. **Upload Logo**: Drag & drop or browse for school logo
4. **Preview**: See how logo appears in platform header
5. **Save**: Logo immediately available for all school users

### **School User Experience**
1. **Access Platform**: via subdomain (e.g., `escuela-bolivar.bischeduler.ueipab.edu.ve`)
2. **See School Logo**: Instantly recognize their institution
3. **Dual Branding**: School logo + BiScheduler platform badge
4. **Consistent Experience**: Logo appears throughout platform

---

## 🔧 **Implementation Details**

### **File Organization**
```
static/
├── branding/                    # Platform assets
│   ├── logo_concept.svg
│   └── favicon.svg
└── tenants/                     # Tenant-specific assets
    └── logos/
        ├── ueipab_logo.png      # UEIPAB custom logo
        ├── colegio_bolivar.jpg  # School logos
        └── escuela_miranda.svg
```

### **URL Structure**
```
# Platform logo (default)
/static/branding/logo_concept.svg

# Tenant-specific logos
/static/tenants/logos/{tenant_code}_logo.{ext}

# API endpoints
POST /api/tenants/{tenant_id}/logo     # Upload logo
GET  /api/tenants/{tenant_id}/logo     # Get logo info
DELETE /api/tenants/{tenant_id}/logo   # Remove logo
```

### **Database Storage**
```sql
-- Example tenant records with logos
INSERT INTO tenants (tenant_id, institution_name, institution_code, logo_filename)
VALUES
  ('uuid-ueipab', 'UEIPAB', 'UEIPAB', 'ueipab_logo.png'),
  ('uuid-bolivar', 'Escuela Bolivar', 'BOLIVAR', 'colegio_bolivar.jpg');
```

---

## 📊 **Benefits Analysis**

### **For Schools**
- **Brand Recognition**: Students/teachers immediately identify their institution
- **Professional Appearance**: Customized platform experience
- **Institutional Pride**: School identity preserved in digital platform
- **Marketing Value**: School branding visible in all platform interactions

### **For BiScheduler Platform**
- **Competitive Advantage**: Multi-tenant customization differentiator
- **Higher Adoption**: Schools more likely to adopt branded solution
- **Professional Credibility**: Enterprise-level customization capability
- **Venezuelan Context**: Respects institutional autonomy and identity

### **For UEIPAB**
- **Platform Value**: More attractive offering to invite other schools
- **Revenue Potential**: Premium branding features for subscription tiers
- **Network Effect**: Schools see other institutions using platform

---

## ⚡ **Development Impact Assessment**

### **Minimal Disruption**
- **No Core Changes**: Scheduling engine unaffected
- **Extension of Existing**: Builds on current branding system
- **Isolated Feature**: Can be developed/tested independently

### **Quick Implementation**
- **2-3 Hours Total**: Small addition to foundation work
- **Low Risk**: Simple file upload and display functionality
- **High Reward**: Significant user experience enhancement

### **Future Scalability**
- **Foundation for More**: Color schemes, custom themes, etc.
- **Premium Features**: Advanced branding options for paid tiers
- **Brand Guidelines**: Automated logo sizing and positioning

---

## 🎯 **Recommended Implementation Approach**

### **Option 1: Integrate into Phase 1.75** ⭐ **RECOMMENDED**
- **Timing**: Complete now as branding enhancement
- **Benefit**: Comprehensive branding solution from start
- **Effort**: Additional 2-3 hours

### **Option 2: Create Phase 1.8**
- **Timing**: Separate mini-phase after foundation
- **Benefit**: Can be prioritized independently
- **Effort**: Same 2-3 hours but separate planning

### **Option 3: Defer to Phase 5 (UI Development)**
- **Timing**: Implement with main UI work
- **Benefit**: Integrated with frontend development
- **Risk**: May miss early adoption benefits

---

## 🚀 **RECOMMENDATION: Implement Now (Phase 1.8)**

This enhancement is **highly recommended** because:
1. **Perfect Timing**: Foundation architecture supports it
2. **High Value/Low Effort**: Exceptional ROI on development time
3. **Competitive Advantage**: Differentiates from single-tenant solutions
4. **Venezuelan Context**: Respects institutional identity and autonomy

**Proposed Addition**: **Phase 1.8: Multi-Tenant Logo System (2-3 hours)**

This would make BiScheduler significantly more attractive to Venezuelan K12 institutions while requiring minimal additional development effort.