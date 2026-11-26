from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import io
import base64

from .models import UserProfile, LoginHistory
from security.integrity_service import log_security_event

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    # Quick 1-Click Role Login for demo / testing
    quick_role = request.GET.get('quick_login')
    if quick_role:
        role_map = {
            'admin': 'admin_user',
            'revenue': 'revenue_officer',
            'farmer': 'farmer_user',
            'agri': 'agri_officer',
            'auditor': 'auditor_user',
        }
        target_username = role_map.get(quick_role)
        if target_username:
            u = User.objects.filter(username=target_username).first()
            if u:
                login(request, u, backend='django.contrib.auth.backends.ModelBackend')
                profile, _ = UserProfile.objects.get_or_create(user=u)
                request.session['mfa_verified'] = True
                messages.success(request, f"Logged in as {u.username} ({profile.get_role_display()}) successfully!")
                return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        ua = request.META.get('HTTP_USER_AGENT', '')

        if user is not None:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            # Direct seamless login
            login(request, user)
            request.session['mfa_verified'] = True
            LoginHistory.objects.create(
                user=user, username_attempted=username,
                ip_address=ip, user_agent=ua, status='SUCCESS'
            )
            log_security_event(user, "USER_LOGIN_SUCCESS", "AUTH", new_vals={"role": profile.role}, request=request)
            messages.success(request, f"Welcome back, {user.username} [{profile.get_role_display()}].")
            return redirect('home')
        else:
            LoginHistory.objects.create(
                user=None, username_attempted=username,
                ip_address=ip, user_agent=ua, status='FAILED'
            )
            messages.error(request, "Invalid username or password! Please check credentials or use Quick 1-Click Login below.")

    return render(request, 'accounts/login.html')


def register_farmer_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        aadhaar = request.POST.get('aadhaar', '').strip()
        role = request.POST.get('role', 'farmer').strip()
        state = request.POST.get('state', '').strip()
        district = request.POST.get('district', '').strip()
        tehsil = request.POST.get('tehsil', '').strip()
        village = request.POST.get('village', '').strip()
        khasra_numbers = request.POST.get('khasra_numbers', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        agree_terms = request.POST.get('agree_terms')

        if not agree_terms:
            messages.error(request, "Please agree to the Digital Public Infrastructure & Data Consent terms.")
            return render(request, 'accounts/register.html', request.POST)

        if password != confirm_password:
            messages.error(request, "Passwords do not match. Please enter again.")
            return render(request, 'accounts/register.html', request.POST)

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'accounts/register.html', request.POST)

        clean_aadhaar = aadhaar.replace(" ", "").replace("-", "")
        if clean_aadhaar and (len(clean_aadhaar) != 12 or not clean_aadhaar.isdigit()):
            messages.error(request, "Please enter a valid 12-digit Aadhaar / Virtual ID number.")
            return render(request, 'accounts/register.html', request.POST)

        clean_phone = phone.replace(" ", "").replace("-", "").replace("+91", "")
        if clean_phone and (len(clean_phone) != 10 or not clean_phone.isdigit()):
            messages.error(request, "Please enter a valid 10-digit mobile number.")
            return render(request, 'accounts/register.html', request.POST)

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, f"Username '{username}' is already taken. Please choose another.")
            return render(request, 'accounts/register.html', request.POST)

        if email and User.objects.filter(email__iexact=email).exists():
            messages.error(request, f"Email address '{email}' is already registered with another account.")
            return render(request, 'accounts/register.html', request.POST)

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        allowed_roles = dict(UserProfile.ROLE_CHOICES).keys()
        if role not in allowed_roles:
            role = 'farmer'

        dept_str = f"{village}, {tehsil}, {district}, {state}".strip(", ")
        if not dept_str:
            dept_str = "Citizen Self-Registered"

        masked_aadhaar = f"XXXX-XXXX-{clean_aadhaar[-4:]}" if len(clean_aadhaar) == 12 else clean_aadhaar

        profile = UserProfile.objects.create(
            user=user,
            role=role,
            phone=clean_phone or phone,
            aadhaar_number=masked_aadhaar,
            department=dept_str
        )

        log_security_event(user, "CITIZEN_REGISTRATION", "ACCOUNTS", new_vals={
            "username": username,
            "role": role,
            "district": district,
            "khasra": khasra_numbers
        }, request=request)

        messages.success(request, f"Registration successful for {full_name or username}! Your digital ID is ready. Please sign in.")
        return redirect('login')

    return render(request, 'accounts/register.html')


def mfa_verify_view(request):
    user_id = request.session.get('pre_mfa_user_id')
    if not user_id:
        return redirect('login')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        
        # In test/demo mode, accept token '123456' or valid TOTP token
        if (device and device.verify_token(token)) or token == '123456':
            login(request, user)
            del request.session['pre_mfa_user_id']
            request.session['mfa_verified'] = True
            log_security_event(user, "MFA_VERIFICATION_SUCCESS", "AUTH", request=request)
            messages.success(request, f"MFA Verified. Multi-Factor Session active for {user.username}.")
            return redirect('home')
        else:
            messages.error(request, "Invalid TOTP Authenticator code. (Demo fallback: 123456)")

    return render(request, 'accounts/mfa_verify.html', {'target_user': user})


def mfa_setup_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    device, created = TOTPDevice.objects.get_or_create(user=request.user, name='default')
    
    # Generate QR Code image
    url = device.config_url
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#00e5ff", back_color="#0a0e14")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()

    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        if device.verify_token(token) or token == '123456':
            device.confirmed = True
            device.save()
            request.user.profile.mfa_enabled = True
            request.user.profile.save()
            messages.success(request, "MFA successfully activated on your account!")
            return redirect('profile_view')
        else:
            messages.error(request, "Verification code failed. Please scan and retry (or enter 123456).")

    return render(request, 'accounts/mfa_setup.html', {'qr_code': qr_b64, 'device': device})


def logout_view(request):
    if request.user.is_authenticated:
        log_security_event(request.user, "USER_LOGOUT", "AUTH", request=request)
    logout(request)
    messages.info(request, "Secure session terminated successfully.")
    return redirect('login')


def lockout_view(request):
    return render(request, 'accounts/lockout.html')
