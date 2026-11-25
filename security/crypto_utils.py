import base64
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings

def get_fernet():
    key = getattr(settings, 'FERNET_KEY', None)
    if not key:
        # Default fallback key
        key = Fernet.generate_key()
    return Fernet(key.encode('utf-8') if isinstance(key, str) else key)

def encrypt_pii(plain_text: str) -> str:
    """Encrypt sensitive string (e.g., Aadhaar / Phone) with Fernet."""
    if not plain_text:
        return ""
    f = get_fernet()
    encrypted_bytes = f.encrypt(plain_text.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')

def decrypt_pii(encrypted_text: str) -> str:
    """Decrypt Fernet-encrypted string."""
    if not encrypted_text:
        return ""
    try:
        f = get_fernet()
        decrypted_bytes = f.decrypt(encrypted_text.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception:
        return encrypted_text  # Fallback if raw

def mask_aadhaar(plain_or_decrypted: str) -> str:
    """Return masked format: XXXX-XXXX-4589."""
    if not plain_or_decrypted or len(plain_or_decrypted) < 4:
        return "XXXX-XXXX-XXXX"
    clean = plain_or_decrypted.replace("-", "").replace(" ", "")
    last_four = clean[-4:]
    return f"XXXX-XXXX-{last_four}"

def mask_phone(phone: str) -> str:
    """Mask phone number: +91 98*** **210."""
    if not phone or len(phone) < 4:
        return "+91 XXXXX XXXXX"
    return f"{phone[:6]}*****{phone[-3:]}"
