"""
BiScheduler Tenant Logo Storage System
Secure file management for multi-tenant branding
"""

import os
import uuid
import hashlib
import imghdr
from typing import Optional, Tuple
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import logging

logger = logging.getLogger(__name__)


class TenantLogoStorage:
    """
    Secure file storage for tenant logos
    Handles upload, validation, and management of institutional logos
    """

    # Storage configuration
    BASE_PATH = '/var/www/dev/bischeduler/static/tenants/logos/'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg', 'webp'}
    ALLOWED_MIME_TYPES = {
        'image/png',
        'image/jpeg',
        'image/svg+xml',
        'image/webp'
    }
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB limit
    MIN_FILE_SIZE = 1024  # 1KB minimum (prevent empty files)

    def __init__(self):
        """Initialize storage system and ensure directory exists"""
        self.ensure_storage_directory()

    def ensure_storage_directory(self):
        """Create storage directory if it doesn't exist"""
        os.makedirs(self.BASE_PATH, exist_ok=True)
        # Create .gitkeep to ensure directory is tracked
        gitkeep_path = os.path.join(self.BASE_PATH, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            open(gitkeep_path, 'a').close()

    def validate_file(self, file: FileStorage) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive file validation

        Args:
            file: Uploaded file from request

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not file or not file.filename:
            return False, "No file provided"

        # Check file extension
        filename = secure_filename(file.filename)
        if not self._allowed_file(filename):
            return False, f"Invalid file type. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}"

        # Check file size (read without consuming)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > self.MAX_FILE_SIZE:
            return False, f"File too large. Maximum size: {self.MAX_FILE_SIZE / (1024 * 1024)}MB"

        if file_size < self.MIN_FILE_SIZE:
            return False, "File too small or empty"

        # Verify it's actually an image (content validation)
        file.seek(0)
        header = file.read(512)
        file.seek(0)

        # Check magic bytes for common image formats
        if not self._is_valid_image_content(header):
            return False, "File content does not match a valid image format"

        return True, None

    def save_tenant_logo(self, tenant_id: str, file: FileStorage, uploaded_by: str = None) -> dict:
        """
        Save uploaded logo with security validation

        Args:
            tenant_id: Unique tenant identifier
            file: Uploaded file from request
            uploaded_by: Admin who uploaded the file

        Returns:
            Dict with file information or raises exception
        """
        # Validate file
        is_valid, error_message = self.validate_file(file)
        if not is_valid:
            raise ValueError(error_message)

        # Generate secure filename
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()

        # Create unique filename with tenant ID
        unique_filename = f"{tenant_id}_{uuid.uuid4().hex[:8]}.{extension}"
        file_path = os.path.join(self.BASE_PATH, unique_filename)

        # Save file
        try:
            file.save(file_path)

            # Get file info
            file_size = os.path.getsize(file_path)

            # Generate checksum for integrity
            file_hash = self._generate_file_hash(file_path)

            logger.info(f"Logo saved for tenant {tenant_id}: {unique_filename}")

            return {
                'filename': unique_filename,
                'original_name': original_filename,
                'file_size': file_size,
                'mime_type': file.content_type,
                'uploaded_at': datetime.now(timezone.utc),
                'uploaded_by': uploaded_by,
                'file_hash': file_hash,
                'file_path': file_path
            }

        except Exception as e:
            # Clean up on failure
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"Failed to save logo for tenant {tenant_id}: {str(e)}")
            raise

    def delete_tenant_logo(self, tenant_id: str, logo_filename: str) -> bool:
        """
        Remove tenant logo file

        Args:
            tenant_id: Unique tenant identifier
            logo_filename: Filename to delete

        Returns:
            True if deleted successfully
        """
        if not logo_filename:
            return False

        # Ensure filename belongs to this tenant (security check)
        if not logo_filename.startswith(f"{tenant_id}_"):
            logger.warning(f"Security: Attempted to delete logo not belonging to tenant {tenant_id}")
            return False

        file_path = os.path.join(self.BASE_PATH, logo_filename)

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Logo deleted for tenant {tenant_id}: {logo_filename}")
                return True
            else:
                logger.warning(f"Logo file not found for deletion: {file_path}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete logo for tenant {tenant_id}: {str(e)}")
            return False

    def get_tenant_logo_url(self, tenant_id: str, logo_filename: str = None) -> Optional[str]:
        """
        Get logo URL for tenant, with fallback to BiScheduler logo

        Args:
            tenant_id: Unique tenant identifier
            logo_filename: Optional specific logo filename

        Returns:
            URL to logo or None
        """
        if logo_filename:
            # Verify file exists
            file_path = os.path.join(self.BASE_PATH, logo_filename)
            if os.path.exists(file_path):
                return f"/static/tenants/logos/{logo_filename}"

        # Fallback to BiScheduler logo
        return "/static/branding/logo_concept.svg"

    def _allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def _is_valid_image_content(self, header: bytes) -> bool:
        """
        Validate file content matches image format
        Check magic bytes for security
        """
        # PNG signature
        if header.startswith(b'\x89PNG\r\n\x1a\n'):
            return True

        # JPEG signatures
        if header.startswith(b'\xff\xd8\xff'):
            return True

        # SVG (XML-based)
        if b'<svg' in header[:512] or b'<?xml' in header[:100]:
            return True

        # WebP
        if header.startswith(b'RIFF') and b'WEBP' in header[8:12]:
            return True

        return False

    def _generate_file_hash(self, file_path: str) -> str:
        """Generate SHA-256 hash of file for integrity checking"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def get_storage_statistics(self) -> dict:
        """Get storage usage statistics"""
        total_size = 0
        file_count = 0

        for filename in os.listdir(self.BASE_PATH):
            if filename != '.gitkeep':
                file_path = os.path.join(self.BASE_PATH, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1

        return {
            'total_logos': file_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'storage_path': self.BASE_PATH
        }

    def cleanup_orphaned_logos(self, active_tenants: list) -> int:
        """
        Remove logos not associated with active tenants

        Args:
            active_tenants: List of active tenant IDs

        Returns:
            Number of files cleaned up
        """
        cleaned_count = 0

        for filename in os.listdir(self.BASE_PATH):
            if filename == '.gitkeep':
                continue

            # Extract tenant ID from filename
            tenant_id = filename.split('_')[0] if '_' in filename else None

            if tenant_id and tenant_id not in active_tenants:
                file_path = os.path.join(self.BASE_PATH, filename)
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                    logger.info(f"Cleaned orphaned logo: {filename}")
                except Exception as e:
                    logger.error(f"Failed to clean orphaned logo {filename}: {str(e)}")

        return cleaned_count


# Global storage instance
tenant_logo_storage = TenantLogoStorage()