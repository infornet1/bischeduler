# BiScheduler Production Deployment Guide
**Complete Infrastructure Documentation for Venezuelan K12 Platform**

## 📋 **Current Production Status**

### **System Information**
- **Environment**: Production (Live)
- **URL**: https://dev.ueipab.edu.ve/bischeduler/
- **Server**: UEIPAB Infrastructure
- **Port**: 5005
- **Status**: ✅ **OPERATIONAL**

### **Deployment Date**
- **Initial Deployment**: September 2024
- **Last Update**: September 27, 2025
- **Current Version**: Phase 11.1 Complete
- **Uptime**: Continuous operation since deployment

---

## 🏗️ **Infrastructure Architecture**

### **System Stack**
```
┌─────────────────────────────────────────┐
│            Nginx Reverse Proxy         │
│        (Port 80/443 → Port 5005)       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Gunicorn WSGI Server            │
│     (Multiple Workers on Port 5005)    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│        Flask Application                │
│    (BiScheduler Multi-Tenant Core)     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│           MariaDB Database              │
│    (Schema-per-tenant isolation)       │
└─────────────────────────────────────────┘
```

### **Directory Structure**
```
/var/www/dev/bischeduler/
├── src/                     # Application source code
├── templates/               # Jinja2 HTML templates
├── static/                  # CSS, JS, images
├── venv/                    # Python virtual environment
├── migration_workspace/     # Data migration tools
├── tests/                   # Test suite (Phase 9)
├── docs/                    # Documentation
├── deployment/              # Deployment configs
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── wsgi.py                  # WSGI entry point
└── manage.py               # Management commands
```

---

## 🚀 **Current Deployment Configuration**

### **Gunicorn Configuration**
**Current Command**:
```bash
/var/www/dev/bischeduler/venv/bin/gunicorn \
  --workers 1 \
  --bind 127.0.0.1:5005 \
  --timeout 120 \
  wsgi:application
```

**Configuration Details**:
- **Workers**: 1 (single worker process)
- **Bind Address**: 127.0.0.1:5005 (localhost only)
- **Timeout**: 120 seconds
- **WSGI Module**: wsgi:application

### **Environment Variables**
```bash
# Application Environment
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration
DATABASE_URL=mysql://user:password@localhost/bischeduler_master
SQLALCHEMY_DATABASE_URI=mysql://user:password@localhost/bischeduler_master

# Security
SECRET_KEY=[REDACTED]
JWT_SECRET_KEY=[REDACTED]

# Multi-Tenant
TENANT_RESOLVER=subdomain
DEFAULT_TENANT=ueipab

# Venezuelan Configuration
TIMEZONE=America/Caracas
LANGUAGE=es_VE
```

### **Nginx Configuration**
```nginx
# Location block for BiScheduler
location /bischeduler/ {
    proxy_pass http://127.0.0.1:5005/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Timeout configuration
    proxy_read_timeout 300;
    proxy_connect_timeout 60;
    proxy_send_timeout 300;

    # File upload size
    client_max_body_size 50M;
}
```

---

## 🔧 **Deployment Procedures**

### **Standard Deployment Process**

#### **1. Pre-Deployment Checklist**
- [ ] Code tested in development environment
- [ ] Database migrations prepared
- [ ] Environment variables configured
- [ ] Backup current database
- [ ] Check system resources (disk, memory, CPU)

#### **2. Deployment Steps**
```bash
# 1. Navigate to application directory
cd /var/www/dev/bischeduler

# 2. Activate virtual environment
source venv/bin/activate

# 3. Pull latest code (if using git)
git pull origin main

# 4. Install/update dependencies
pip install -r requirements.txt

# 5. Run database migrations
python manage.py db upgrade

# 6. Collect static files (if applicable)
python manage.py collect-static

# 7. Test configuration
python manage.py check-config

# 8. Restart Gunicorn
sudo systemctl restart bischeduler
# OR kill and restart manually:
pkill -f "gunicorn.*bischeduler"
nohup /var/www/dev/bischeduler/venv/bin/gunicorn \
  --workers 1 --bind 127.0.0.1:5005 --timeout 120 \
  wsgi:application > logs/gunicorn.log 2>&1 &

# 9. Verify deployment
curl -I http://127.0.0.1:5005/health
```

#### **3. Post-Deployment Verification**
- [ ] Application responds to health check
- [ ] Login functionality works
- [ ] Database connections successful
- [ ] Static files loading correctly
- [ ] Error logs checked for issues

---

## 🗄️ **Database Management**

### **Current Database Setup**
- **Engine**: MariaDB
- **Version**: 10.6+
- **Architecture**: Multi-tenant with schema-per-tenant
- **Master Database**: `bischeduler_master`
- **Tenant Databases**: `ueipab_2025_2026`, etc.

### **Backup Procedures**
```bash
# Daily automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)

# Backup master database
mysqldump -u backup_user -p bischeduler_master > \
  /var/backups/bischeduler/master_$DATE.sql

# Backup all tenant databases
mysql -u backup_user -p -e "SHOW DATABASES LIKE 'ueipab_%'" | \
grep -v Database | while read db; do
  mysqldump -u backup_user -p $db > \
    /var/backups/bischeduler/${db}_$DATE.sql
done

# Compress backups older than 1 day
find /var/backups/bischeduler/ -name "*.sql" -mtime +1 -exec gzip {} \;

# Remove backups older than 30 days
find /var/backups/bischeduler/ -name "*.gz" -mtime +30 -delete
```

### **Database Migration Commands**
```bash
# Create new migration
python manage.py db migrate -m "Description of changes"

# Apply migrations
python manage.py db upgrade

# Rollback last migration
python manage.py db downgrade

# Show migration history
python manage.py db history
```

---

## 📊 **Monitoring & Logging**

### **Application Logs**
```bash
# Log locations
/var/www/dev/bischeduler/logs/
├── gunicorn.log              # Gunicorn access/error logs
├── application.log           # Flask application logs
├── error.log                 # Error-specific logs
├── access.log               # Request access logs
└── performance.log          # Performance metrics

# Real-time log monitoring
tail -f logs/application.log
tail -f logs/error.log
tail -f /var/log/nginx/access.log | grep bischeduler
```

### **System Health Checks**
```bash
# Check application status
curl -I http://127.0.0.1:5005/health

# Check database connection
python manage.py db-status

# Check Gunicorn processes
ps aux | grep gunicorn | grep bischeduler

# Check port availability
sudo lsof -i :5005

# Check system resources
df -h /var/www/dev/bischeduler
free -h
top -p $(pgrep -f "gunicorn.*bischeduler")
```

### **Performance Monitoring**
```bash
# Response time check
time curl -s http://127.0.0.1:5005/health

# Database performance
mysql -e "SHOW PROCESSLIST;"
mysql -e "SHOW ENGINE INNODB STATUS;" | grep -A 20 "LATEST DETECTED DEADLOCK"

# Memory usage
python -c "
import psutil
for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
    if 'gunicorn' in proc.info['name']:
        print(f'PID: {proc.info[\"pid\"]}, Memory: {proc.info[\"memory_info\"].rss / 1024 / 1024:.1f} MB')
"
```

---

## 🚨 **Troubleshooting Guide**

### **Common Issues & Solutions**

#### **1. Application Won't Start**
```bash
# Check for port conflicts
sudo lsof -i :5005

# Check Python environment
source venv/bin/activate
python -c "import flask; print(flask.__version__)"

# Check configuration
python manage.py check-config

# Check logs
tail -50 logs/error.log
```

#### **2. Database Connection Issues**
```bash
# Test database connection
mysql -h localhost -u [username] -p[password] -e "SELECT 1;"

# Check database status
sudo systemctl status mariadb

# Verify database exists
mysql -e "SHOW DATABASES LIKE 'bischeduler%';"
```

#### **3. Performance Issues**
```bash
# Check system resources
htop
iotop
df -h

# Analyze slow queries
mysql -e "SELECT * FROM information_schema.processlist WHERE time > 5;"

# Check Gunicorn worker status
ps aux | grep gunicorn
```

#### **4. Nginx/Proxy Issues**
```bash
# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Check Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log | grep bischeduler
```

---

## 🔐 **Security Configuration**

### **SSL/TLS Setup**
- **Certificate Provider**: Let's Encrypt (recommended)
- **SSL Termination**: Nginx level
- **HTTPS Redirect**: Configured in Nginx

### **Firewall Configuration**
```bash
# UFW rules for BiScheduler
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw deny 5005/tcp    # Block direct access to Gunicorn
```

### **Application Security**
- **JWT Secret**: Rotated regularly
- **Database Credentials**: Stored in environment variables
- **File Permissions**: Restricted to web user
- **Debug Mode**: Disabled in production

---

## 📈 **Scaling & Optimization**

### **Performance Tuning**
```bash
# Optimal Gunicorn configuration for higher load
/var/www/dev/bischeduler/venv/bin/gunicorn \
  --workers 4 \
  --worker-class sync \
  --worker-connections 1000 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --bind 127.0.0.1:5005 \
  --timeout 120 \
  --keepalive 2 \
  --preload \
  wsgi:application
```

### **Database Optimization**
```sql
-- Index optimization for common queries
CREATE INDEX idx_schedule_assignments_teacher_day
ON schedule_assignments(teacher_id, day_of_week);

CREATE INDEX idx_schedule_assignments_section_time
ON schedule_assignments(section_id, time_period_id, day_of_week);

-- Query cache configuration
SET GLOBAL query_cache_size = 268435456;  -- 256MB
SET GLOBAL query_cache_type = ON;
```

---

## 📋 **Maintenance Procedures**

### **Regular Maintenance Tasks**

#### **Daily**
- [ ] Check application logs for errors
- [ ] Verify backup completion
- [ ] Monitor disk space usage
- [ ] Check system resources

#### **Weekly**
- [ ] Review performance metrics
- [ ] Update system packages
- [ ] Clear old log files
- [ ] Verify database integrity

#### **Monthly**
- [ ] Security updates
- [ ] Database optimization
- [ ] Review and update documentation
- [ ] Disaster recovery test

### **Maintenance Scripts**
```bash
# Log cleanup script
#!/bin/bash
# Clear logs older than 30 days
find /var/www/dev/bischeduler/logs/ -name "*.log" -mtime +30 -delete

# Rotate current logs
mv logs/application.log logs/application.log.$(date +%Y%m%d)
touch logs/application.log
chown www-data:www-data logs/application.log

# Restart application to start fresh logging
sudo systemctl restart bischeduler
```

---

## 🆘 **Emergency Procedures**

### **Quick Recovery Steps**
```bash
# 1. Stop application
pkill -f "gunicorn.*bischeduler"

# 2. Restore from backup
mysql -u root -p bischeduler_master < /var/backups/latest_master.sql

# 3. Restart application
cd /var/www/dev/bischeduler
source venv/bin/activate
nohup gunicorn --workers 1 --bind 127.0.0.1:5005 wsgi:application &

# 4. Verify functionality
curl -I http://127.0.0.1:5005/health
```

### **Disaster Recovery**
1. **Complete System Failure**: Restore from full system backup
2. **Database Corruption**: Restore from latest database backup
3. **Application Corruption**: Redeploy from git repository
4. **Configuration Issues**: Restore configuration files from backup

---

## 📞 **Support Contacts**

### **Technical Support Levels**
- **Level 1**: UEIPAB IT Support
- **Level 2**: System Administrator
- **Level 3**: Development Team

### **Escalation Procedures**
1. **Application Issues**: Check logs, restart service
2. **Database Issues**: Contact database administrator
3. **Infrastructure Issues**: Contact system administrator
4. **Code Issues**: Contact development team

---

## 📊 **Performance Baseline**

### **Current Performance Metrics**
- **Average Response Time**: < 200ms
- **Peak Concurrent Users**: 50-100
- **Database Query Time**: < 50ms average
- **Memory Usage**: ~500MB per worker
- **CPU Usage**: < 30% under normal load

### **Capacity Planning**
- **Current Capacity**: 200+ concurrent users
- **Recommended Scaling**: Add workers at 150+ users
- **Database Limits**: Current setup handles 1000+ students
- **Storage Growth**: ~10MB per month per school

---

**Document Version**: 2.0
**Last Updated**: September 28, 2025
**Next Review**: December 2025

---

*Production deployment guide for BiScheduler Venezuelan K12 Multi-Tenant Platform*