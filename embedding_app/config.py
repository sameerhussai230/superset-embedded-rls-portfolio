# embedding_app/config.py

# --- Admin User Configuration ---
# Credentials for the special admin user who gets full access
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin" # IMPORTANT: Use a strong, hashed password in production
}

# --- RLS Configuration ---

# Mapping of Manufacturer names to their login passwords
# IMPORTANT: Storing plain text passwords here is insecure for production.
MANUFACTURER_PASSWORDS = {
    "Cipla Ltd": "cipla",
    "Torrent Pharmaceuticals Ltd": "torrent",
    "Sun Pharmaceutical Industries Ltd": "sun",
    "Intas Pharmaceuticals Ltd": "intas",
    "Lupin Ltd": "lupin",
    # Add more manufacturers and passwords as needed
}

# The name of the column in your Superset dataset used for RLS filtering
RLS_COLUMN_NAME = "Manufacturer"

# Optional: Specify the Superset dataset ID if the RLS clause should only apply to this dataset.
RLS_DATASET_ID = None # Set to an integer ID if needed

# --- Other Configurations (Optional) ---
# You could move other related settings here if desired,
# but keep sensitive items like API keys in .env