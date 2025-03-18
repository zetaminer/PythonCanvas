import os
import json
import requests
from flask import Flask, request, redirect, session, jsonify

# Load configuration from JSON file
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: config.json not found.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in config.json.")
        exit(1)

# Load the config
config = load_config()

# Set up OAuth credentials
API_URL = config.get("API_URL")
CLIENT_ID = config.get("CLIENT_ID")
CLIENT_SECRET = config.get("CLIENT_SECRET")
REDIRECT_URI = config.get("REDIRECT_URI")




# Configuration
AUTHORIZATION_URL = f"{API_URL}/login/oauth2/auth"
TOKEN_URL = f"{API_URL}/login/oauth2/token"

# Flask App Setup
app = Flask(__name__)
app.secret_key = "your_secret_key"


@app.route("/")
def home():
    return '<a href="/login">Login with Canvas</a>'


@app.route("/login")
def login():
    """ Redirects to Canvas OAuth2 Authorization URL """
    auth_url = f"{AUTHORIZATION_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
    return redirect(auth_url)


@app.route("/callback")
def callback():
    """ Handles the OAuth2 callback and exchanges code for an access token """
    code = request.args.get("code")
    if not code:
        return "Error: No authorization code provided."

    # Exchange code for an access token
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }

    response = requests.post(TOKEN_URL, data=data)
    token_info = response.json()

    if "access_token" in token_info:
        session["access_token"] = token_info["access_token"]
        return redirect("/profile")

    return "Error fetching access token."


@app.route("/profile")
def profile():
    """ Fetch user profile using the access token """
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/login")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{CANVAS_BASE_URL}/api/v1/users/self/profile", headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())

    return "Error fetching profile data."


if __name__ == "__main__":
    app.run(debug=True, port=5000)
