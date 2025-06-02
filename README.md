# Spotify Skip Auto-Unlike

This Python script automatically monitors your currently playing track on Spotify and removes any song from your **Liked Songs** if it was skipped within the first **5 seconds** of playback.

## 🎯 Purpose

The goal of this script is to keep your Liked Songs clean by automatically unliking tracks you skip almost immediately. It assumes that if you skip a song within 5 seconds, you likely don't want to keep it in your favorites.

## ⚙️ Features

- ⏱ Continuously monitors the currently playing track.
- 🧠 Remembers the previously played track and its play duration.
- 🗑 If a track is skipped after 5 seconds or less, it is automatically removed from your Liked Songs.
- 📝 Logs all removed tracks (ID, title, artist, timestamp) to `skip_log.json`.
- 🔄 Automatically refreshes access token if expired.
- 🧼 Minimal terminal output:
  - Displays current song when it starts playing.
  - Logs only when a track is skipped and removed.

## 📄 Requirements

- Python 3.7+
- A Spotify Developer App (to get `CLIENT_ID` and `CLIENT_SECRET`)
- A valid Spotify access token and refresh token with the following scopes:
  - `user-read-playback-state`
  - `user-read-currently-playing`
  - `user-library-modify`

## 🚀 Usage

1. Clone this repository or copy the script locally.
2. Set your `CLIENT_ID` and `CLIENT_SECRET` at the top of the script.
3. Create a `spotify_token.json` file containing:

```json
{
  "access_token": "YOUR_ACCESS_TOKEN",
  "refresh_token": "YOUR_REFRESH_TOKEN"
}
````

4. Run the script:

```bash
python your_script_name.py
```

## 🛑 Behavior

* If no song is playing, the script waits silently.
* If you skip a song in under 5 seconds, it logs the skip and removes the track.
* Songs played longer than 5 seconds are left untouched.
* Only minimal, relevant output is shown.

## 📁 Files

* `spotify_token.json`: Stores your access and refresh tokens.
* `skip_log.json`: Stores a log of removed songs for reference or debugging.

## ⚠️ Notes

* Skipping a track must be detected between two polling cycles. Default is every 5 seconds.
* You may reduce the interval for better accuracy, but too frequent polling may hit rate limits.

## 🧑‍💻 Author

Maintained by \[Denis S. Basler | Black Viper].
