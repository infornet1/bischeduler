"""
BiScheduler Configuration Management
Environment-specific settings for multi-tenant K12 platform
"""

import os
from datetime import timedelta


class BaseConfig:
    """Base configuration with common settings"""

    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True,
        'echo': False
    }

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Multi-tenant settings
    MASTER_DATABASE_URL = os.environ.get('MASTER_DATABASE_URL') or \
    'mysql+pymysql://root:0000@localhost/bischeduler_master'

    # Venezuelan education settings
    DEFAULT_TIMEZONE = 'America/Caracas'
    BIMODAL_START_TIME = '07:00'
    BIMODAL_END_TIME = '14:20'
    STANDARD_CLASSROOM_CAPACITY = 35

    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

    # Rate limiting
    RATELIMIT_STORAGE_URL = "memory://"

    # CORS settings
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]


class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""

    DEBUG = True
    TESTING = False

    # Development database - use tenant database for UEIPAB data
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:0000@localhost/ueipab_2025_data'

    # Relaxed CORS for development
    CORS_ORIGINS = ["*"]

    # Enhanced logging
    LOG_LEVEL = 'DEBUG'


class TestingConfig(BaseConfig):
    """Testing environment configuration"""

    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False

    # In-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False

    # Test JWT settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)


class ProductionConfig(BaseConfig):
    """Production environment configuration"""

    DEBUG = False
    TESTING = False

    # Production database (from environment)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:0000@localhost/bischeduler_prod'

    # Enhanced security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Production CORS (specific domains only)
    CORS_ORIGINS = [
        "https://scheduler.ueipab.edu.ve",
        "https://bischeduler.ueipab.edu.ve"
    ]

    # Production logging
    LOG_LEVEL = 'INFO'

    # Enhanced rate limiting
    RATELIMIT_STORAGE_URL = "redis://localhost:6379/0"


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}