import os
from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "http://localhost:3000",
    'https://portal-grs-main.onrender.com',
    'www.portal-grs-main.onrender.com',
    'portal-grs-main.onrender.com',
]

# Certificados SSL
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# CSRF & XSS Protection
CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'