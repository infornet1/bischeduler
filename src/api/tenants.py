"""
BiScheduler Tenant Management API
Multi-tenant operations for Venezuelan K12 institutions
"""

from flask import Blueprint, request, jsonify, g
from marshmallow import Schema, fields, ValidationError
from datetime import datetime, timedelta, timezone
import logging

from src.tenants.manager import TenantManager
from src.tenants.middleware import require_tenant_admin, get_current_tenant
from src.models.master import InstitutionType, TenantStatus
from src.core.file_storage import tenant_logo_storage


logger = logging.getLogger(__name__)
tenants_bp = Blueprint('tenants', __name__)

# Get tenant manager from current app context
def get_tenant_manager():
    """Get tenant manager from Flask app context"""
    from flask import current_app
    return current_app.tenant_manager


# Validation schemas
class TenantCreationSchema(Schema):
    """Schema for validating tenant creation requests"""
    institution_name = fields.Str(required=True, validate=fields.Length(min=3, max=255))
    institution_code = fields.Str(required=True, validate=fields.Length(min=2, max=50))
    institution_type = fields.Enum(InstitutionType, required=True)
    admin_email = fields.Email(required=True)
    contact_phone = fields.Str(validate=fields.Length(max=20))
    institution_address = fields.Str()
    website_url = fields.Url()
    matricula_code = fields.Str(validate=fields.Length(max=20))
    state_region = fields.Str(validate=fields.Length(max=100))
    municipality = fields.Str(validate=fields.Length(max=100))
    rif_number = fields.Str(validate=fields.Length(max=20))
    max_students = fields.Int(validate=fields.Range(min=10, max=10000))
    max_teachers = fields.Int(validate=fields.Range(min=1, max=1000))


class InvitationSchema(Schema):
    """Schema for validating invitation requests"""
    institution_name = fields.Str(required=True, validate=fields.Length(min=3, max=255))
    institution_type = fields.Enum(InstitutionType, required=True)
    admin_email = fields.Email(required=True)
    invitation_message = fields.Str(validate=fields.Length(max=1000))


@tenants_bp.route('/health', methods=['GET'])
def tenant_health():
    """Health check for tenant API"""
    return jsonify({
        'status': 'healthy',
        'service': 'BiScheduler Tenant Management',
        'compliance': 'Venezuelan K12 Education'
    })


@tenants_bp.route('/', methods=['POST'])
@require_tenant_admin
def create_tenant():
    """
    Create a new tenant (Venezuelan K12 institution)
    Requires admin privileges
    """
    try:
        schema = TenantCreationSchema()
        data = schema.load(request.get_json())

        tenant = get_tenant_manager().create_tenant(**data)

        return jsonify({
            'success': True,
            'message': 'Tenant created successfully',
            'tenant': {
                'tenant_id': tenant.tenant_id,
                'institution_name': tenant.institution_name,
                'institution_code': tenant.institution_code,
                'status': tenant.status.value,
                'created_at': tenant.created_at.isoformat()
            }
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation failed',
            'details': e.messages
        }), 400

    except Exception as e:
        logger.error(f"Tenant creation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Tenant creation failed',
            'message': str(e)
        }), 500


@tenants_bp.route('/invite', methods=['POST'])
@require_tenant_admin
def send_invitation():
    """
    Send invitation to Venezuelan school to join BiScheduler platform
    Enables UEIPAB to invite other institutions
    """
    try:
        schema = InvitationSchema()
        data = schema.load(request.get_json())

        current_tenant = get_current_tenant()
        if not current_tenant:
            return jsonify({
                'success': False,
                'error': 'Tenant context required'
            }), 400

        invitation = get_tenant_manager().send_invitation(
            institution_name=data['institution_name'],
            institution_type=data['institution_type'],
            admin_email=data['admin_email'],
            invited_by_tenant_id=current_tenant.tenant_id,
            message=data.get('invitation_message')
        )

        return jsonify({
            'success': True,
            'message': f'Invitation sent to {data["institution_name"]}',
            'invitation': {
                'invitation_code': invitation.invitation_code,
                'institution_name': invitation.institution_name,
                'admin_email': invitation.admin_email,
                'sent_at': invitation.sent_at.isoformat(),
                'expires_at': invitation.expires_at.isoformat()
            }
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation failed',
            'details': e.messages
        }), 400

    except Exception as e:
        logger.error(f"Invitation sending failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Invitation sending failed',
            'message': str(e)
        }), 500


@tenants_bp.route('/<tenant_id>', methods=['GET'])
@require_tenant_admin
def get_tenant(tenant_id):
    """Get tenant information by ID"""
    try:
        tenant = get_tenant_manager().get_tenant_by_id(tenant_id)
        if not tenant:
            return jsonify({
                'success': False,
                'error': 'Tenant not found'
            }), 404

        return jsonify({
            'success': True,
            'tenant': {
                'tenant_id': tenant.tenant_id,
                'institution_name': tenant.institution_name,
                'institution_code': tenant.institution_code,
                'institution_type': tenant.institution_type.value,
                'admin_email': tenant.admin_email,
                'status': tenant.status.value,
                'created_at': tenant.created_at.isoformat(),
                'activated_at': tenant.activated_at.isoformat() if tenant.activated_at else None,
                'last_accessed': tenant.last_accessed.isoformat() if tenant.last_accessed else None,
                'max_students': tenant.max_students,
                'max_teachers': tenant.max_teachers,
                'custom_branding': tenant.custom_branding,
                # Venezuelan-specific fields
                'matricula_code': tenant.matricula_code,
                'state_region': tenant.state_region,
                'municipality': tenant.municipality,
                'rif_number': tenant.rif_number
            }
        })

    except Exception as e:
        logger.error(f"Tenant retrieval failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Tenant retrieval failed',
            'message': str(e)
        }), 500


@tenants_bp.route('/<tenant_id>/activate', methods=['POST'])
@require_tenant_admin
def activate_tenant(tenant_id):
    """Activate a pending tenant"""
    try:
        success = get_tenant_manager().activate_tenant(tenant_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Tenant activation failed'
            }), 400

        return jsonify({
            'success': True,
            'message': f'Tenant {tenant_id} activated successfully'
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Tenant activation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Tenant activation failed',
            'message': str(e)
        }), 500


@tenants_bp.route('/list', methods=['GET'])
@require_tenant_admin
def list_tenants():
    """List all active tenants (admin only)"""
    try:
        tenants = get_tenant_manager().list_active_tenants()

        tenant_list = []
        for tenant in tenants:
            tenant_list.append({
                'tenant_id': tenant.tenant_id,
                'institution_name': tenant.institution_name,
                'institution_code': tenant.institution_code,
                'institution_type': tenant.institution_type.value,
                'status': tenant.status.value,
                'created_at': tenant.created_at.isoformat(),
                'last_accessed': tenant.last_accessed.isoformat() if tenant.last_accessed else None,
                'is_venezuelan_k12': tenant.is_venezuelan_k12
            })

        return jsonify({
            'success': True,
            'tenants': tenant_list,
            'total_count': len(tenant_list)
        })

    except Exception as e:
        logger.error(f"Tenant listing failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Tenant listing failed',
            'message': str(e)
        }), 500


@tenants_bp.route('/current', methods=['GET'])
def get_current_tenant_info():
    """Get information about current tenant from context"""
    tenant = get_current_tenant()
    if not tenant:
        return jsonify({
            'success': False,
            'error': 'No tenant context'
        }), 400

    return jsonify({
        'success': True,
        'tenant': {
            'tenant_id': tenant.tenant_id,
            'institution_name': tenant.institution_name,
            'institution_code': tenant.institution_code,
            'institution_type': tenant.institution_type.value,
            'status': tenant.status.value,
            'is_venezuelan_k12': tenant.is_venezuelan_k12,
            'bimodal_schedule': True,  # All Venezuelan institutions use bimodal
            'timezone': 'America/Caracas'
        }
    })


@tenants_bp.route('/<tenant_id>/logo', methods=['POST'])
@require_tenant_admin
def upload_tenant_logo(tenant_id):
    """
    Upload custom logo for tenant (Phase 1.8 Enhancement)
    Allows Venezuelan K12 schools to maintain institutional identity
    """
    try:
        # Check if tenant exists and user has permission
        tenant = get_tenant_manager().get_tenant_by_id(tenant_id)
        if not tenant:
            return jsonify({
                'success': False,
                'error': 'Tenant not found'
            }), 404

        # Check if file is in request
        if 'logo' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No logo file provided'
            }), 400

        file = request.files['logo']

        # Get current user for audit trail
        uploaded_by = getattr(g, 'current_user', 'admin')  # TODO: Get from JWT

        # Save logo using secure storage
        file_info = tenant_logo_storage.save_tenant_logo(
            tenant_id=tenant.tenant_id,
            file=file,
            uploaded_by=uploaded_by
        )

        # Update tenant record with logo information
        session = get_tenant_manager().SessionLocal()
        try:
            # Delete old logo if exists
            if tenant.logo_filename:
                tenant_logo_storage.delete_tenant_logo(tenant.tenant_id, tenant.logo_filename)

            # Update tenant with new logo info
            tenant.logo_filename = file_info['filename']
            tenant.logo_original_name = file_info['original_name']
            tenant.logo_file_size = file_info['file_size']
            tenant.logo_mime_type = file_info['mime_type']
            tenant.logo_uploaded_at = file_info['uploaded_at']
            tenant.logo_uploaded_by = file_info['uploaded_by']

            session.commit()

            logger.info(f"Logo uploaded for tenant {tenant.institution_name}")

            return jsonify({
                'success': True,
                'message': f'Logo uploaded successfully for {tenant.institution_name}',
                'logo': {
                    'url': tenant.logo_url,
                    'filename': file_info['filename'],
                    'original_name': file_info['original_name'],
                    'size': file_info['file_size'],
                    'uploaded_at': file_info['uploaded_at'].isoformat()
                }
            }), 200

        except Exception as e:
            session.rollback()
            # Clean up uploaded file on database error
            tenant_logo_storage.delete_tenant_logo(tenant.tenant_id, file_info['filename'])
            raise
        finally:
            session.close()

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Logo upload failed for tenant {tenant_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Logo upload failed',
            'message': str(e)
        }), 500


@tenants_bp.route('/<tenant_id>/logo', methods=['DELETE'])
@require_tenant_admin
def delete_tenant_logo(tenant_id):
    """
    Remove custom tenant logo (Phase 1.8 Enhancement)
    Returns to default BiScheduler branding
    """
    try:
        tenant = get_tenant_manager().get_tenant_by_id(tenant_id)
        if not tenant:
            return jsonify({
                'success': False,
                'error': 'Tenant not found'
            }), 404

        if not tenant.logo_filename:
            return jsonify({
                'success': False,
                'error': 'No logo to delete'
            }), 404

        # Delete physical file
        deleted = tenant_logo_storage.delete_tenant_logo(
            tenant.tenant_id,
            tenant.logo_filename
        )

        if deleted:
            # Update tenant record
            session = get_tenant_manager().SessionLocal()
            try:
                tenant.logo_filename = None
                tenant.logo_original_name = None
                tenant.logo_file_size = None
                tenant.logo_mime_type = None
                tenant.logo_uploaded_at = None
                tenant.logo_uploaded_by = None

                session.commit()

                logger.info(f"Logo deleted for tenant {tenant.institution_name}")

                return jsonify({
                    'success': True,
                    'message': f'Logo removed for {tenant.institution_name}'
                })

            except Exception as e:
                session.rollback()
                raise
            finally:
                session.close()
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete logo file'
            }), 500

    except Exception as e:
        logger.error(f"Logo deletion failed for tenant {tenant_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Logo deletion failed',
            'message': str(e)
        }), 500


@tenants_bp.route('/<tenant_id>/logo', methods=['GET'])
def get_tenant_logo_info(tenant_id):
    """
    Get tenant logo information (Phase 1.8 Enhancement)
    Public endpoint for logo display
    """
    try:
        tenant = get_tenant_manager().get_tenant_by_id(tenant_id)
        if not tenant:
            return jsonify({
                'success': False,
                'error': 'Tenant not found'
            }), 404

        if tenant.has_custom_logo:
            return jsonify({
                'success': True,
                'has_logo': True,
                'logo': {
                    'url': tenant.logo_url,
                    'filename': tenant.logo_filename,
                    'original_name': tenant.logo_original_name,
                    'size': tenant.logo_file_size,
                    'mime_type': tenant.logo_mime_type,
                    'uploaded_at': tenant.logo_uploaded_at.isoformat() if tenant.logo_uploaded_at else None
                }
            })
        else:
            return jsonify({
                'success': True,
                'has_logo': False,
                'default_logo': '/static/branding/logo_concept.svg'
            })

    except Exception as e:
        logger.error(f"Failed to get logo info for tenant {tenant_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve logo information'
        }), 500


@tenants_bp.route('/platform/stats', methods=['GET'])
def platform_statistics():
    """Get platform-wide statistics for Venezuelan K12 institutions"""
    try:
        tenants = get_tenant_manager().list_active_tenants()

        # Calculate statistics
        total_institutions = len(tenants)
        k12_institutions = len([t for t in tenants if t.is_venezuelan_k12])
        universities = total_institutions - k12_institutions

        institution_types = {}
        for tenant in tenants:
            inst_type = tenant.institution_type.value
            institution_types[inst_type] = institution_types.get(inst_type, 0) + 1

        return jsonify({
            'success': True,
            'platform': 'BiScheduler Multi-Tenant K12',
            'statistics': {
                'total_institutions': total_institutions,
                'k12_institutions': k12_institutions,
                'universities': universities,
                'institution_types': institution_types,
                'venezuelan_compliance': True,
                'bimodal_schedule_support': True
            },
            'features': [
                'Schema-per-tenant isolation',
                'Venezuelan Matrícula reporting',
                'Bimodal schedule management',
                'Multi-institution invitations',
                'Government compliance tools'
            ]
        })

    except Exception as e:
        logger.error(f"Platform statistics failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Platform statistics failed',
            'message': str(e)
        }), 500