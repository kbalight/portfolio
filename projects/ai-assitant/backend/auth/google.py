from google_auth_oauthlib.flow import Flow
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "google_credentials.json")

flow = Flow.from_client_secrets_file(
    CLIENT_SECRET_FILE,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
        "https://www.googleapis.com/auth/calendar"
    ],
    redirect_uri="http://127.0.0.1:8000/auth/callback"
)
