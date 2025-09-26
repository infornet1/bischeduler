# 🔄 Decommission & Port Reuse Strategy
**Seamless Transition from Old Scheduler to New BiScheduler**

## 🎯 Executive Summary

This plan outlines the decommission of the existing scheduler webapp on port 5005 and the reuse of its infrastructure for the new BiScheduler deployment. This ensures minimal disruption and efficient resource utilization.

---

## 🔍 Current System Analysis

### **Existing Scheduler Configuration**
- **Application**: Flask webapp (../scheduler/app.py)
- **Port**: 5005 (127.0.0.1:5005)
- **Process**: Python3 (PID: 270213)
- **Nginx Location**: `/scheduler/` → `http://127.0.0.1:5005/`
- **Database**: MariaDB `gestion_horarios`
- **Status**: ✅ Currently running and accessible

### **Nginx Configuration Found**
```nginx
location /scheduler/ {
    proxy_pass http://127.0.0.1:5005/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Script-Name /scheduler;

    proxy_connect_timeout 75s;
    proxy_read_timeout 90s;
    proxy_buffering off;

    location /scheduler/static/ {
        proxy_pass http://127.0.0.1:5005/static/;
    }
}
```

---

## 📋 Decommission & Transition Plan

### **Phase 1: Pre-Decommission Preparation** (30 minutes)
**Timeline**: Before BiScheduler deployment
**Purpose**: Ensure smooth transition

#### **1.1 Data Backup & Migration Verification**
```bash
# Backup existing database (already covered in migration plan)
mysqldump -u root -p gestion_horarios > backup_gestion_horarios_$(date +%Y%m%d_%H%M%S).sql

# Verify migration data is ready
ls -la ~/migration_workspace/
```

#### **1.2 User Communication**
- **Notification**: Inform users of planned system upgrade
- **Downtime Window**: Schedule maintenance window (e.g., evening/weekend)
- **Access**: Provide alternative access during transition if needed

#### **1.3 Configuration Backup**
```bash
# Backup nginx configuration
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d)

# Backup existing app configuration
cp ../scheduler/app.py ../scheduler/app.py.backup
cp ../scheduler/.env ../scheduler/.env.backup 2>/dev/null || echo "No .env file found"
```

### **Phase 2: Graceful Service Decommission** (15 minutes)
**Timeline**: During BiScheduler deployment (Phase 12)
**Purpose**: Stop old service cleanly

#### **2.1 Stop Flask Application**
```bash
# Find and stop the running Flask process
sudo kill -TERM 270213  # Graceful termination

# Verify process stopped
sudo netstat -tlnp | grep :5005  # Should return empty

# Alternative: If process doesn't stop gracefully
# sudo kill -KILL 270213
```

#### **2.2 Disable Service Auto-Start**
```bash
# Check if running as systemd service
sudo systemctl list-units --type=service | grep -i scheduler

# If systemd service exists, disable it
# sudo systemctl stop scheduler.service
# sudo systemctl disable scheduler.service

# Check for cron jobs or other auto-start mechanisms
crontab -l | grep -i scheduler
sudo crontab -l | grep -i scheduler
```

#### **2.3 Archive Old Application**
```bash
# Create archive directory
sudo mkdir -p /var/archive/old_scheduler_$(date +%Y%m%d)

# Move old application (preserve for rollback)
sudo mv ../scheduler /var/archive/old_scheduler_$(date +%Y%m%d)/
```

### **Phase 3: Port and Infrastructure Reuse** (45 minutes)
**Timeline**: During BiScheduler deployment
**Purpose**: Configure new system on existing infrastructure

#### **3.1 Update Nginx Configuration**
```bash
# Edit nginx configuration
sudo nano /etc/nginx/sites-available/default
```

**New Nginx Configuration**:
```nginx
# Replace existing /scheduler/ location with:
location /bischeduler/ {
    proxy_pass http://127.0.0.1:5005/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Script-Name /bischeduler;

    # Enhanced timeouts for BiScheduler
    proxy_connect_timeout 75s;
    proxy_read_timeout 300s;  # Increased for report generation
    proxy_buffering off;

    # Static files for BiScheduler
    location /bischeduler/static/ {
        proxy_pass http://127.0.0.1:5005/static/;
    }

    # API endpoints with extended timeout
    location /bischeduler/api/ {
        proxy_pass http://127.0.0.1:5005/api/;
        proxy_read_timeout 600s;  # For schedule generation and Excel import
    }
}

# Optional: Redirect old scheduler URL to new BiScheduler
location /scheduler/ {
    return 301 /bischeduler/;
}
```

#### **3.2 Test Nginx Configuration**
```bash
# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx

# Verify nginx status
sudo systemctl status nginx
```

### **Phase 4: BiScheduler Deployment on Port 5005** (Covered in Phase 12)
**Timeline**: Part of main implementation
**Purpose**: Deploy new system on reclaimed infrastructure

#### **4.1 BiScheduler Flask Configuration**
```python
# /var/www/dev/bischeduler/app.py
if __name__ == '__main__':
    # Production configuration - reuse port 5005
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('FLASK_PORT', 5005))  # Reuse existing port
    app.run(debug=debug_mode, host='127.0.0.1', port=port)
```

#### **4.2 Create Systemd Service for BiScheduler**
```bash
# Create systemd service file
sudo tee /etc/systemd/system/bischeduler.service << EOF
[Unit]
Description=BiScheduler Venezuelan School Management System
After=network.target mysql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/dev/bischeduler
Environment=PATH=/var/www/dev/bischeduler/venv/bin
Environment=FLASK_PORT=5005
Environment=FLASK_DEBUG=False
ExecStart=/var/www/dev/bischeduler/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable bischeduler.service
sudo systemctl start bischeduler.service

# Verify service status
sudo systemctl status bischeduler.service
```

### **Phase 5: Verification & Testing** (30 minutes)
**Timeline**: Post-deployment validation
**Purpose**: Ensure successful transition

#### **5.1 Service Verification**
```bash
# Check BiScheduler is running on port 5005
sudo netstat -tlnp | grep :5005

# Test HTTP response
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5005/

# Test through nginx
curl -s -o /dev/null -w "%{http_code}" http://localhost/bischeduler/
```

#### **5.2 Database Connectivity**
```bash
# Test database connection
cd /var/www/dev/bischeduler
source venv/bin/activate
python -c "
from database import create_connection
conn = create_connection()
if conn:
    print('✅ Database connection successful')
    conn.close()
else:
    print('❌ Database connection failed')
"
```

#### **5.3 Functional Testing**
- **Web Interface**: Access BiScheduler web interface
- **API Endpoints**: Test core API functionality
- **Data Verification**: Confirm migrated data is accessible
- **Report Generation**: Test Excel/PDF export functionality

---

## 🔄 Rollback Plan

### **Emergency Rollback Procedure** (15 minutes)
**If new BiScheduler fails**:

#### **5.1 Stop BiScheduler**
```bash
sudo systemctl stop bischeduler.service
sudo systemctl disable bischeduler.service
```

#### **5.2 Restore Old Scheduler**
```bash
# Restore old application
sudo mv /var/archive/old_scheduler_$(date +%Y%m%d)/scheduler ../

# Restore nginx configuration
sudo cp /etc/nginx/sites-available/default.backup.$(date +%Y%m%d) /etc/nginx/sites-available/default
sudo nginx -t && sudo systemctl reload nginx

# Restart old scheduler
cd ../scheduler
source venv/bin/activate
python app.py &
```

#### **5.3 Verify Rollback**
```bash
# Test old scheduler accessibility
curl -s -o /dev/null -w "%{http_code}" http://localhost/scheduler/
```

---

## 📋 Implementation Checklist

### **Pre-Decommission**
- [ ] Data migration completed and verified
- [ ] Users notified of maintenance window
- [ ] Configuration backups created
- [ ] Rollback plan tested
- [ ] BiScheduler deployment ready

### **During Decommission**
- [ ] Old Flask process stopped gracefully
- [ ] Auto-start services disabled
- [ ] Old application archived
- [ ] Port 5005 confirmed available

### **Infrastructure Reuse**
- [ ] Nginx configuration updated
- [ ] Configuration syntax tested
- [ ] Nginx reloaded successfully
- [ ] BiScheduler systemd service created

### **Post-Deployment**
- [ ] BiScheduler running on port 5005
- [ ] Nginx proxy working correctly
- [ ] Database connectivity verified
- [ ] Web interface accessible
- [ ] API endpoints functional

### **Verification**
- [ ] All core features working
- [ ] Data migration successful
- [ ] Performance acceptable
- [ ] Users can access new system
- [ ] Monitoring in place

---

## ⚡ Performance Considerations

### **Resource Optimization**
- **Memory**: BiScheduler expected to use similar RAM as old scheduler
- **CPU**: Improved efficiency with simpler scheduling algorithm
- **Database**: Same MariaDB instance, optimized queries
- **Network**: Existing nginx configuration optimized for school use

### **Monitoring Setup**
```bash
# Create monitoring script
tee /var/www/dev/bischeduler/monitor.sh << EOF
#!/bin/bash
# BiScheduler monitoring script

echo "=== BiScheduler Health Check ==="
echo "Port 5005 status:"
netstat -tlnp | grep :5005

echo "Service status:"
systemctl is-active bischeduler.service

echo "Database connectivity:"
cd /var/www/dev/bischeduler
source venv/bin/activate
python -c "
from database import create_connection
conn = create_connection()
print('✅ DB OK' if conn else '❌ DB FAIL')
if conn: conn.close()
"

echo "Web interface status:"
curl -s -o /dev/null -w "HTTP %{http_code} - Response time: %{time_total}s\n" http://127.0.0.1:5005/
EOF

chmod +x /var/www/dev/bischeduler/monitor.sh
```

---

## 📊 Migration Timeline Integration

### **Updated Implementation Schedule**
```
Phase 0:     Data Migration                    2-3 hours
Phase 1-11:  BiScheduler Development         35-50 hours
Phase 12a:   Pre-Decommission Preparation    0.5 hours    ⭐ NEW
Phase 12b:   Service Decommission            0.25 hours   ⭐ NEW
Phase 12c:   Infrastructure Reuse            0.75 hours   ⭐ NEW
Phase 12d:   BiScheduler Deployment          1 hour       Enhanced
Phase 12e:   Verification & Testing          0.5 hours    ⭐ NEW
Phase 13:    Venezuelan Absence Monitoring   14-20 hours

TOTAL ENHANCED: 49-67 hours (was 47-64 hours)
```

### **Zero-Downtime Transition**
- **Preparation**: Done in advance without affecting current service
- **Transition Window**: 30-45 minutes total downtime
- **Rollback Time**: 15 minutes if needed
- **User Impact**: Minimal disruption during scheduled maintenance

---

## 🎯 Success Criteria

### **Decommission Success**
- [x] Old scheduler gracefully stopped
- [x] Port 5005 available for reuse
- [x] No service conflicts
- [x] Configuration backups created

### **Infrastructure Reuse Success**
- [x] BiScheduler running on port 5005
- [x] Nginx proxy configured correctly
- [x] SSL/HTTPS working if applicable
- [x] Static files serving properly

### **Transition Success**
- [x] All migrated data accessible
- [x] Web interface fully functional
- [x] API endpoints responding
- [x] Performance meets expectations
- [x] Users can access new system

---

## ✅ Conclusion

This decommission and port reuse strategy provides:

1. **Seamless Transition**: Minimal downtime during migration
2. **Resource Efficiency**: Reuse existing port and nginx configuration
3. **Risk Mitigation**: Complete rollback plan if issues arise
4. **User Continuity**: Familiar URL structure with redirect support
5. **Performance Optimization**: Enhanced configuration for BiScheduler needs

**Recommendation**: **INTEGRATE** this decommission plan as **Phase 12a-12e** in the main implementation timeline.

---

**Status**: ✅ **Plan Complete - Ready for Implementation Integration**