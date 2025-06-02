import json
import os
import time
from datetime import datetime
import requests

TOKEN_FILE = "spotify_token.json"
SKIP_LOG_FILE = "skip_log.json"

TOKEN_URL = "https://accounts.spotify.com/api/token"
CURRENT_PLAYBACK_URL = "https://api.spotify.com/v1/me/player/currently-playing"
REMOVE_TRACK_URL = "https://api.spotify.com/v1/me/tracks"

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def refresh_token(refresh_token):
    response = requests.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    })
    if response.status_code == 200:
        tokens = response.json()
        token_data = load_json(TOKEN_FILE)
        token_data.update(tokens)
        save_json(TOKEN_FILE, token_data)
        return tokens["access_token"]
    else:
        raise Exception("Failed to refresh token: " + response.text)

def get_current_playback(access_token):
    response = requests.get(CURRENT_PLAYBACK_URL, headers={
        "Authorization": f"Bearer {access_token}"
    })
    if response.status_code == 401:
        raise Exception("Token expired")
    if response.status_code == 200:
        return response.json()
    if response.status_code == 204:
        return None
    raise Exception(f"Spotify API error: {response.status_code} - {response.text}")

def remove_track(access_token, track_id):
    response = requests.delete(REMOVE_TRACK_URL, headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }, json={
        "ids": [track_id]
    })
    return response.status_code == 200

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def log_removed(track_id, name, artist):
    log(f"Removed from Favorites: '{name}' by {artist}")
    skipped = load_json(SKIP_LOG_FILE)
    if "removed" not in skipped:
        skipped["removed"] = []
    skipped["removed"].append({
        "id": track_id,
        "title": name,
        "artist": artist,
        "timestamp": datetime.now().isoformat()
    })
    save_json(SKIP_LOG_FILE, skipped)

def main_loop():
    token_data = load_json(TOKEN_FILE)
    access_token = token_data.get("access_token")
    refresh_token_val = token_data.get("refresh_token")

    last_track_id = None
    last_progress = None
    current_track_displayed = None

    while True:
        try:
            playback = get_current_playback(access_token)

            if playback and playback.get("is_playing") and playback.get("item"):
                track_id = playback["item"]["id"]
                progress_seconds = playback.get("progress_ms", 0) / 1000
                track_name = playback["item"]["name"]
                artist_name = playback["item"]["artists"][0]["name"]

                # Display current song if it changed
                if track_id != current_track_displayed:
                    log(f"Now Playing: '{track_name}' by {artist_name}")
                    current_track_displayed = track_id

                # If the previous track was skipped
                if last_track_id and last_track_id != track_id:
                    if last_progress is not None and last_progress <= 5:
                        success = remove_track(access_token, last_track_id)
                        if success:
                            log_removed(last_track_id, last_track_name, last_artist_name)

                # Update current track info
                last_track_id = track_id
                last_progress = progress_seconds
                last_track_name = track_name
                last_artist_name = artist_name

            else:
                last_track_id = None
                last_progress = None
                current_track_displayed = None

        except Exception as e:
            log(f"Error: {str(e)}")
            if "token expired" in str(e).lower():
                log("Refreshing token...")
                access_token = refresh_token(refresh_token_val)

        time.sleep(5)

if __name__ == "__main__":
    try:
        log("Spotify Skip Auto-Unlike running...")
        main_loop()
    except Exception as e:
        log(f"Fatal error: {str(e)}")
        save_json(SKIP_LOG_FILE, {"error": str(e)})
        log("Exiting...")
        exit(1)
