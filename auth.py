import hashlib
import os
import binascii
from datetime import datetime, timedelta
from jose import jwt, JWTError
import random
import re

# Security configurations
SECRET_KEY = "SUPER_SECRET_PLATFORM_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str):
    """Hash a password using PBKDF2 with a random salt."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(plain_password: str, hashed_password: str):
    """Verify a stored password against one provided by user."""
    salt = hashed_password[:64].encode('ascii')
    stored_hash = hashed_password[64:].encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', plain_password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return pwdhash == stored_hash

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def generate_otp():
    return str(random.randint(100000, 999999))

def validate_indian_phone(phone: str):
    pattern = r'^(?:\+91|91)?[6-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_email(email: str):
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return bool(re.match(pattern, email))
