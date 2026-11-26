def user_role_context(request):
    """Exposes current user role, permissions, and unread notifications to all templates."""
    role = 'public'
    unread_notifications = 0
    mfa_verified = False
    display_name = ""

    if request.user.is_authenticated:
        u = request.user
        if u.first_name and u.first_name.strip():
            display_name = u.first_name.strip().title()
        elif u.email and '@' in u.email:
            display_name = u.email.split('@')[0].strip().title()
        elif u.username:
            raw = u.username.split('@')[0]
            if '_' in raw:
                parts = raw.split('_')
                display_name = parts[0].title() if parts[0].lower() not in ['revenue', 'agri', 'admin', 'farmer', 'auditor'] else (parts[1].title() if len(parts) > 1 and parts[1].lower() != 'user' else raw.replace('_', ' ').title())
            else:
                display_name = raw.title()
        else:
            display_name = "User"

        if hasattr(request.user, 'profile'):
            role = request.user.profile.role
        elif request.user.is_superuser:
            role = 'admin'

        try:
            from security.models import Notification
            unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
            recent_notifications = list(Notification.objects.filter(user=request.user).order_by('-created_at')[:5])
        except Exception:
            unread_notifications = 0
            recent_notifications = []

        # Check if user has completed OTP or if session is verified
        mfa_verified = request.session.get('mfa_verified', False)

    return {
        'CURRENT_ROLE': role,
        'DISPLAY_NAME': display_name,
        'IS_FARMER': role == 'farmer',
        'IS_REVENUE_OFFICER': role in ['revenue_officer', 'admin'],
        'IS_AGRI_OFFICER': role in ['agri_officer', 'admin'],
        'IS_AUDITOR': role in ['auditor', 'admin'],
        'IS_ADMIN': role == 'admin' or request.user.is_superuser,
        'UNREAD_NOTIFICATIONS_COUNT': unread_notifications,
        'RECENT_NOTIFICATIONS': recent_notifications if request.user.is_authenticated else [],
        'MFA_VERIFIED': mfa_verified,
    }
