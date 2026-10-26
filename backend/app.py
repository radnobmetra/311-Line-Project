from pathlib import Path
import os

import firebase_admin
from firebase_admin import auth as firebase_auth

from flask import Flask, abort, g, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=None)

# Angular build location inside the container.
STATIC_DIR = (Path(__file__).resolve().parent.parent / "static").resolve()

# firebase_admin.initialize_app(options={"projectId": os.environ["FIREBASE_PROJECT_ID"]})
firebase_admin.initialize_app(options={"projectId": "admin-96a00"})


# Return a JSON status indicating that the backend is running.
@app.get("/api/test")
def test():
    return jsonify({"status": "ok"})


# Return current logged in user's email. Information is returned from auth interceptor
@app.get("/api/user")
def get_current_user():
    return jsonify(
        {
            "id": g.user["uid"],
            "name": "Admin",
            "username": g.user.get("email"),
            "email": g.user.get("email"),
        }
    )


# Should return stored contacts from google cloud or a db.
@app.get("/api/contacts")
def get_contacts():
    return jsonify([])


# After the dashboard is built in the container, this API function serves the built frontend website.
@app.get("/", defaults={"path": ""})
@app.get("/<path:path>")
def serve_frontend(path):
    # Unknown API endpoints must not return Angular HTML.
    if path == "api" or path.startswith("api/"):
        return jsonify({"error": "Endpoint not found"}), 404

    requested_file = (STATIC_DIR / path).resolve()

    # Prevent access outside the Angular build directory.
    if not requested_file.is_relative_to(STATIC_DIR):
        abort(404)

    if requested_file.is_file():
        return send_from_directory(STATIC_DIR, path)

    # Return 404 for missing assets.
    if Path(path).suffix:
        abort(404)

    # Let Angular handle frontend routes.
    response = send_from_directory(STATIC_DIR, "index.html")
    response.headers["Cache-Control"] = "no-cache"
    return response


# This function gets called before every API request to make sure it's protected.
# Secured backend API endpoints by verifying Firebase tokens with the Firebase Admin SDK.
# Reject missing or invalid tokens with `401`.
@app.before_request
def protect_api():
    path = request.path

    # Angular pages and assets can load without a token.
    if path != "/api" and not path.startswith("/api/"):
        return None

    # Public test check.
    if path == "/api/test":
        return None

    authorization = request.headers.get("Authorization", "")
    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return jsonify({"error": "Authentication required"}), 401

    token = parts[1]

    try:
        decoded_token = firebase_auth.verify_id_token(token)

    except firebase_auth.CertificateFetchError:
        # Verification service failure; still deny access.
        return jsonify({"error": "Authentication temporarily unavailable"}), 503

    except (firebase_auth.InvalidIdTokenError, ValueError):
        return jsonify({"error": "Invalid or expired token"}), 401

    # Make verified identity available to this request's routes.
    g.user = decoded_token
