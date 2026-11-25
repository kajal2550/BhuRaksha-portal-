def user_role_context(request):
    """Exposes current user role, permissions, and unread notifications to all templates."""
    role = 'public'
    unread_notifications = 0
    mfa_verified = False

    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            role = request.user.profile.role
        elif request.user.is_superuser:
            role = 'admin'

        try:
            from security.models import Notification
            unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
        except Exception:
            unread_notifications = 0

        # Check if user has completed OTP or if session is verified
        mfa_verified = request.session.get('mfa_verified', False)

    return {
        'CURRENT_ROLE': role,
        'IS_FARMER': role == 'farmer',
        'IS_REVENUE_OFFICER': role in ['revenue_officer', 'admin'],
        'IS_AGRI_OFFICER': role in ['agri_officer', 'admin'],
        'IS_AUDITOR': role in ['auditor', 'admin'],
        'IS_ADMIN': role == 'admin' or request.user.is_superuser,
        'UNREAD_NOTIFICATIONS_COUNT': unread_notifications,
        'MFA_VERIFIED': mfa_verified,
    }
