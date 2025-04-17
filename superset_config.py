# superset/superset_config.py
import os
from urllib.parse import quote_plus

try:
    # Import only the necessary variables from connection.py
    from connection import SECRET_KEY as CONN_SECRET_KEY, SQLALCHEMY_DATABASE_URI as CONN_SQLALCHEMY_DATABASE_URI
    print("Successfully imported keys from connection.py")
except ImportError:
    print("Warning: Could not import from connection.py. Using environment variables or defaults.")
    CONN_SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "a-very-secure-secret-key")
    CONN_SQLALCHEMY_DATABASE_URI = os.environ.get("SUPERSET_SQLALCHEMY_DATABASE_URI", "postgresql+psycopg2://superset:superset@db:5432/superset")

# --- Core Superset Settings ---
SECRET_KEY = CONN_SECRET_KEY
SQLALCHEMY_DATABASE_URI = CONN_SQLALCHEMY_DATABASE_URI

# --- Settings for Embedding & Guest Tokens ---
# ENABLE_EMBEDDED_SUPERSET is controlled by env var

ALLOWED_EMBEDDED_DOMAINS = os.environ.get("ALLOWED_EMBEDDED_DOMAINS", "").split(",")
ALLOWED_EMBEDDED_DOMAINS = [domain.strip() for domain in ALLOWED_EMBEDDED_DOMAINS if domain.strip()]
if not ALLOWED_EMBEDDED_DOMAINS:
    ALLOWED_EMBEDDED_DOMAINS = ["http://localhost:8000"]

GUEST_TOKEN_JWT_SECRET = os.environ.get(
    "SUPERSET_GUEST_TOKEN_JWT_SECRET",
    SECRET_KEY # Use main key for dev
)

GUEST_ROLE_NAME = "Gamma"

# --- Session Cookie Settings ---
SESSION_COOKIE_SAMESITE = None
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False

# --- CSRF Settings ---
# WARNING: INSECURE - DO NOT USE IN PRODUCTION
WTF_CSRF_ENABLED = False
WTF_CSRF_EXEMPT_LIST = [ # Keep list in case you re-enable CSRF later
    'superset.views.core.guest_token',
    'app.views.api.guest_token',
    'superset.security.api.guest_token',
    'superset.security.api.SecurityRestApi.guest_token',
    '/api/v1/security/guest_token/'
]

# --- Feature Flags ---
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "ALLOW_CSV_UPLOAD": True, # Ensure this is enabled
    # Add other feature flags as needed
}
ENABLE_PROXY_FIX = True
TALISMAN_ENABLED = False

# --- CORS Configuration ---
ENABLE_CORS = True
CORS_OPTIONS = {
  'supports_credentials': True,
  'allow_headers': ['*'],
  'resources':['*'],
  'origins': ALLOWED_EMBEDDED_DOMAINS
}

# --- Logging Confirmation ---
print("*"*10 + " Custom Superset Config Loaded (v13-CSV_Only) " + "*"*10) # Version bump
print(f"Flask Env: {os.environ.get('FLASK_ENV', 'Not Set (Defaulting to Production!)')}")
print(f"Main SECRET_KEY Loaded: {'******'}")
print(f"Allowed Embedded Domains: {ALLOWED_EMBEDDED_DOMAINS}")
print(f"Guest Token JWT Secret Loaded: {'******'}")
print(f"Guest Role Name (Default): {GUEST_ROLE_NAME}")
print(f"Session Cookie SameSite: {SESSION_COOKIE_SAMESITE}")
print(f"Session Cookie Secure: {SESSION_COOKIE_SECURE}")
print(f"Session Cookie HttpOnly: {SESSION_COOKIE_HTTPONLY}")
print(f"WTF CSRF Enabled: {WTF_CSRF_ENABLED}")
print(f"WTF CSRF Exempt List: {WTF_CSRF_EXEMPT_LIST}")
print(f"Feature Flags: {FEATURE_FLAGS}") # Verify ALLOW_CSV_UPLOAD is True
print(f"Talisman Enabled: {TALISMAN_ENABLED}")
print(f"CORS Enabled: {ENABLE_CORS}")
print(f"CORS Origins: {CORS_OPTIONS.get('origins')}")
print("*"*10 + " Config Loading Complete (v13-CSV_Only) " + "*"*10) # Version bump