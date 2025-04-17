# embedding_app/main.py
import os
import logging
import time
from typing import Optional, Dict, Any
import hashlib # Import for potential future password hashing

import requests
import jwt
from fastapi import FastAPI, Request, HTTPException, Depends, Form, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

# --- Import Custom Config ---
try:
    # Import all necessary configs
    from config import (
        MANUFACTURER_PASSWORDS,
        RLS_COLUMN_NAME,
        RLS_DATASET_ID,
        ADMIN_CREDENTIALS
    )
except ImportError:
    logging.error("FATAL: embedding_app/config.py not found or missing required variables.")
    raise ImportError("Could not load configuration from embedding_app/config.py")

# --- Configuration Loading ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

SUPERSET_URL = os.getenv("SUPERSET_URL", "http://localhost:8088").rstrip('/')
SUPERSET_ADMIN_USER = os.getenv("SUPERSET_ADMIN_USER", "admin")
SUPERSET_ADMIN_PASSWORD = os.getenv("SUPERSET_ADMIN_PASSWORD", "admin")
SUPERSET_DASHBOARD_ID = os.getenv("SUPERSET_DASHBOARD_ID")
SUPERSET_RLS_ROLE_NAME = os.getenv("SUPERSET_RLS_ROLE_NAME", "Gamma")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

logger.info(f"SUPERSET_RLS_ROLE_NAME (base guest role): {SUPERSET_RLS_ROLE_NAME}")
logger.info(f"RLS based on column: '{RLS_COLUMN_NAME}'")
if RLS_DATASET_ID:
    logger.info(f"RLS clause applied specifically to dataset ID: {RLS_DATASET_ID}")
else:
    logger.info("RLS clause applied globally to accessible datasets for the guest user.")
logger.info(f"Admin user configured: '{ADMIN_CREDENTIALS.get('username')}'")
logger.info(f"Allowed CORS requests from: {FRONTEND_URL}")

if not all([SUPERSET_URL, SUPERSET_ADMIN_USER, SUPERSET_ADMIN_PASSWORD, SUPERSET_DASHBOARD_ID]):
    logger.error("FATAL: Missing SUPERSET_URL, SUPERSET_ADMIN_USER, SUPERSET_ADMIN_PASSWORD, or SUPERSET_DASHBOARD_ID in .env")
    raise ValueError("Missing essential Superset configuration in .env file")

# --- FastAPI App Setup ---
app = FastAPI(title="Superset Embedding Middleware")

origins = [FRONTEND_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Models ---
class LoginRequest(BaseModel):
    # Use a generic 'username' field which can be admin or manufacturer
    username: str
    password: str

# --- Helper Functions ---
# get_superset_tokens remains the same
superset_token_cache: Dict[str, Any] = {"access_token": None, "csrf_token": None, "expires": 0}
def get_superset_tokens() -> Dict[str, str]:
    current_time = time.time()
    if (superset_token_cache.get("access_token") and
            superset_token_cache.get("csrf_token") and
            superset_token_cache.get("expires", 0) > current_time + 60):
        logger.info("Using cached Superset API tokens (access & csrf).")
        return {
            "access_token": superset_token_cache["access_token"],
            "csrf_token": superset_token_cache["csrf_token"]
        }

    logger.info("Attempting Superset API login to get access token (for CSRF extraction)...")
    api_login_url = f"{SUPERSET_URL}/api/v1/security/login"
    login_payload = {"username": SUPERSET_ADMIN_USER, "password": SUPERSET_ADMIN_PASSWORD, "provider": "db"}
    try:
        with requests.Session() as session:
            response = session.post(api_login_url, json=login_payload, timeout=10)
            logger.info(f"Superset Login API Response Status: {response.status_code}")
            logger.debug(f"Superset Login Response Text: {response.text}")
            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")
            if not access_token:
                logger.error("Failed to get access_token from Superset API login response.")
                raise HTTPException(status_code=500, detail="Failed to authenticate with Superset API (access_token missing)")

            try:
                decoded_token = jwt.decode(access_token, options={"verify_signature": False}, algorithms=["HS256"])
                csrf_token = decoded_token.get("csrf")
                if not csrf_token:
                     logger.error("CSRF claim not found within the decoded access token JWT.")
                     raise HTTPException(status_code=500, detail="CSRF claim missing in access token")
                logger.info("Successfully extracted CSRF token from access token JWT.")

            except jwt.DecodeError as e:
                 logger.error(f"Failed to decode access token JWT: {e}")
                 raise HTTPException(status_code=500, detail="Failed to decode access token")
            except Exception as e:
                 logger.exception(f"Unexpected error during JWT decoding or CSRF extraction: {e}")
                 raise HTTPException(status_code=500, detail="Error extracting CSRF token from access token")

            cache_duration = 3300
            superset_token_cache["access_token"] = access_token
            superset_token_cache["csrf_token"] = csrf_token
            superset_token_cache["expires"] = current_time + cache_duration
            logger.info(f"Successfully obtained and cached new Superset API tokens (access & jwt-csrf, valid approx {cache_duration // 60} mins).")
            return {"access_token": access_token, "csrf_token": csrf_token}

    except requests.exceptions.Timeout:
        logger.error(f"Timeout connecting to Superset API for login at {api_login_url}")
        raise HTTPException(status_code=504, detail="Timeout connecting to Superset API login.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error connecting to Superset API for login: {e}")
        raise HTTPException(status_code=503, detail=f"Could not connect to Superset API login: {e}")
    except requests.exceptions.HTTPError as e:
        detail = f"Superset API login failed ({e.response.status_code})"
        try:
            superset_error = e.response.json().get("message", e.response.text)
            detail += f": {superset_error}"
        except ValueError:
             detail += f": {e.response.text}"
        logger.error(detail)
        raise HTTPException(status_code=e.response.status_code, detail=detail)
    except Exception as e:
        logger.exception("Unexpected error during Superset API authentication / CSRF extraction.")
        raise HTTPException(status_code=500, detail="Unexpected error during Superset authentication / CSRF extraction.")


# _fetch_guest_token_base remains the same
async def _fetch_guest_token_base(payload: Dict[str, Any]) -> str:
    try:
        tokens = get_superset_tokens()
        access_token = tokens["access_token"]
        csrf_token = tokens["csrf_token"]
    except HTTPException as e:
         logger.error(f"Failed to obtain necessary tokens for guest token fetch: {e.detail}")
         raise e

    guest_token_url = f"{SUPERSET_URL}/api/v1/security/guest_token/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-CSRFToken": csrf_token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    logger.info(f"Attempting to fetch guest token from: {guest_token_url}")
    logger.debug(f"Using Admin Token: Bearer {access_token[:10]}...")
    logger.debug(f"Using JWT-CSRF Token: {csrf_token[:10]}...")
    logger.info(f"Guest Token Request Payload: {payload}")

    try:
        response = requests.post(guest_token_url, headers=headers, json=payload, timeout=15)
        logger.info(f"Superset Guest Token API Response Status: {response.status_code}")
        logger.debug(f"Superset Guest Token API Response Text: {response.text[:500]}")
        response.raise_for_status()

        data = response.json()
        guest_token = data.get("token")
        if not guest_token:
            logger.error("Guest token key 'token' not found in successful Superset API response.")
            raise HTTPException(status_code=500, detail="Guest token missing in Superset response body")

        logger.info("Successfully obtained guest token.")
        return guest_token

    except requests.exceptions.Timeout:
        logger.error(f"Timeout connecting to Superset API for guest token at {guest_token_url}")
        raise HTTPException(status_code=504, detail="Timeout connecting to Superset API guest token.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error connecting to Superset API for guest token: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Could not connect to Superset API for guest token: {e}")
    except requests.exceptions.HTTPError as e:
        detail_message = f"Superset API guest token request failed ({e.response.status_code})"
        try:
            superset_error = e.response.json().get("message", e.response.text)
            if isinstance(superset_error, dict):
                 field_errors = [f"{field}: {', '.join(msgs)}" for field, msgs in superset_error.items()]
                 detail_message += f": {'; '.join(field_errors)}"
            else:
                 detail_message += f": {superset_error}"
        except ValueError:
             detail_message += f": {e.response.text}"
        logger.error(f"Raising HTTPException for guest token failure: {detail_message}")
        raise HTTPException(status_code=e.response.status_code, detail=detail_message)
    except Exception as e:
        logger.exception("Unexpected error fetching Superset guest token.")
        raise HTTPException(status_code=500, detail="Unexpected error fetching guest token.")


# fetch_superset_guest_token_rls remains the same
async def fetch_superset_guest_token_rls(manufacturer: str) -> str:
    """Fetches a guest token with RLS applied based on the Manufacturer column."""
    logger.info(f"Fetching RLS guest token for Manufacturer: '{manufacturer}'")
    rls_clause = f"\"{RLS_COLUMN_NAME}\" = '{manufacturer}'"
    logger.info(f"Constructed RLS clause: {rls_clause}")

    rls_rule = {"clause": rls_clause}
    if RLS_DATASET_ID is not None and isinstance(RLS_DATASET_ID, int):
        rls_rule["dataset_id"] = RLS_DATASET_ID
        logger.info(f"Applying RLS rule to specific dataset ID: {RLS_DATASET_ID}")

    safe_manufacturer_part = "".join(c if c.isalnum() else '_' for c in manufacturer)[:30]
    guest_username = f"guest_mfr_{safe_manufacturer_part}_{int(time.time())}"

    payload = {
        "user": {
            "username": guest_username,
            "first_name": "Embedded Mfr",
            "last_name": f"User ({manufacturer[:20]})",
        },
        "resources": [{"type": "dashboard", "id": SUPERSET_DASHBOARD_ID}],
        "rls": [rls_rule]
    }
    return await _fetch_guest_token_base(payload)


# fetch_superset_guest_token_full remains the same
async def fetch_superset_guest_token_full(user_identifier: str = "full_access") -> str:
    logger.info(f"Fetching FULL access guest token for identifier: {user_identifier}")
    guest_username = f"guest_full_{user_identifier}_{int(time.time())}"
    payload = {
        "user": {
            "username": guest_username,
            "first_name": "Embedded Full",
            "last_name": f"User ({user_identifier[:20]})" # Include identifier in name
        },
        "resources": [{"type": "dashboard", "id": SUPERSET_DASHBOARD_ID}],
        "rls": []
    }
    return await _fetch_guest_token_base(payload)


# --- API Endpoints ---

# Legacy HTML Endpoints (remain unchanged, but likely incompatible with new auth)
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def get_login_page_html(request: Request):
    logger.warning("Serving legacy login HTML page. Authentication may differ from React app.")
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def get_dashboard_page_rls_html(request: Request, manufacturer: Optional[str] = None):
    if not manufacturer:
         logger.warning("Legacy RLS Dashboard page accessed without manufacturer. Redirecting to legacy login.")
         return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    logger.warning(f"Serving legacy RLS dashboard HTML page for manufacturer: {manufacturer}. Template compatibility not guaranteed.")
    context = {"request": request, "dashboard_id": SUPERSET_DASHBOARD_ID, "superset_url": SUPERSET_URL, "manufacturer": manufacturer}
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/dashboard-full", response_class=HTMLResponse, include_in_schema=False)
async def get_dashboard_page_full_html(request: Request):
    logger.info("Serving legacy FULL access dashboard HTML page.")
    context = {"request": request, "dashboard_id": SUPERSET_DASHBOARD_ID, "superset_url": SUPERSET_URL}
    return templates.TemplateResponse("dashboard_full.html", context)


# --- API Endpoints for React Frontend ---

# --- UPDATED Login Endpoint ---
@app.post("/login", status_code=status.HTTP_200_OK)
async def handle_login(login_data: LoginRequest):
    """Handles user login attempt for Admin or Manufacturer."""
    username = login_data.username
    password = login_data.password
    logger.info(f"API Login attempt for username: '{username}'")

    # --- Check if it's the Admin User ---
    if username == ADMIN_CREDENTIALS.get("username"):
        # IMPORTANT: Use secure password comparison in production
        if password == ADMIN_CREDENTIALS.get("password"):
            logger.info(f"API Login successful for Admin user: '{username}'")
            # Return admin user type and identifier
            return {
                "message": "Login successful",
                "user_type": "admin",
                "user_identifier": username # Use the admin username as identifier
            }
        else:
            logger.warning(f"API Login failed for Admin user: '{username}' - Invalid password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Username or Password",
            )

    # --- If not Admin, check if it's a Manufacturer ---
    else:
        expected_password = MANUFACTURER_PASSWORDS.get(username) # username is manufacturer name here

        if expected_password is None:
            logger.warning(f"API Login failed: User '{username}' not found as Admin or Manufacturer.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Username or Password",
            )

        # IMPORTANT: Use secure password comparison in production
        if password == expected_password:
            logger.info(f"API Login successful for Manufacturer: '{username}'")
            # Return manufacturer user type and identifier (manufacturer name)
            return {
                "message": "Login successful",
                "user_type": "manufacturer",
                "user_identifier": username # Use manufacturer name as identifier
            }
        else:
            logger.warning(f"API Login failed for Manufacturer: '{username}' - Invalid password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Username or Password",
            )

# --- RLS Token Endpoint (Unchanged, called by React for manufacturers) ---
@app.get("/get-guest-token-rls")
async def get_guest_token_rls_endpoint(manufacturer: str):
    """Provides an RLS-secured guest token for the specified manufacturer."""
    if not manufacturer:
        logger.error("API RLS Guest token requested without manufacturer.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Manufacturer name is required for RLS token")
    logger.info(f"API Received request for RLS guest token for manufacturer: '{manufacturer}'")
    try:
        token = await fetch_superset_guest_token_rls(manufacturer)
        return {"token": token}
    except HTTPException as e:
        logger.error(f"HTTPException propagated from RLS token fetch for '{manufacturer}': {e.status_code} - {e.detail}")
        raise e
    except Exception as e:
        logger.exception(f"Unexpected error in get_guest_token_rls_endpoint for manufacturer '{manufacturer}'")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error generating RLS guest token")

# --- Full Access Token Endpoint (Unchanged, called by React for admin) ---
@app.get("/get-guest-token-full")
async def get_guest_token_full_endpoint(user_id: str = "default_full_user"):
    """Provides a guest token with full dashboard access (permissions defined by GUEST_ROLE_NAME)."""
    logger.info(f"API Received request for FULL access guest token for user: {user_id}")
    try:
        token = await fetch_superset_guest_token_full(user_identifier=user_id)
        return {"token": token}
    except HTTPException as e:
        logger.error(f"HTTPException propagated from FULL token fetch for {user_id}: {e.status_code} - {e.detail}")
        raise e
    except Exception as e:
        logger.exception(f"Unexpected error in get_guest_token_full_endpoint for user {user_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error generating full access guest token")

# --- Run Instruction ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload_flag = bool(os.getenv("RELOAD", "False").lower() in ['true', '1', 'yes'])
    logger.info(f"Starting FastAPI development server on http://{host}:{port}")
    logger.info(f"Auto-reload {'enabled' if reload_flag else 'disabled'}.")
    uvicorn.run("main:app", host=host, port=port, reload=reload_flag)