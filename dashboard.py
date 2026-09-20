"""Local dashboard for TIMDR-Cyclone-RI: serves www/ (static HTML/JS/JSON,
no build step) on 127.0.0.1:5050. Most data is precomputed real HURDAT2
data bundled in www/data/ (no live calls needed for that). One optional
endpoint, /api/live/current_storms, proxies NHC's real live CurrentStorms.json
feed server-side (so the browser's CORS restrictions don't apply) -- this
is the only network call this app ever makes, it is read-only, and it only
runs when the user clicks the "live" button in the dashboard.

Run: python dashboard.py   (or double-click run_dashboard.bat on Windows)
"""

import json
import os
import urllib.error
import urllib.request
import webbrowser
from threading import Timer

from flask import Flask, jsonify, send_from_directory

REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
WWW_DIR = os.path.join(REPO_ROOT, "www")
PORT = 5050

NHC_CURRENT_STORMS_URL = "https://www.nhc.noaa.gov/CurrentStorms.json"
NHC_FETCH_TIMEOUT_S = 8

app = Flask(__name__, static_folder=None)


@app.route("/")
def index():
    return send_from_directory(WWW_DIR, "index.html")


@app.route("/api/live/current_storms")
def live_current_storms():
    """Server-side proxy for NHC's real live active-storms feed.

    Fetched fresh on every call (no caching, no fallback data) -- if NHC
    is unreachable or the feed is empty (common outside hurricane season),
    that is reported honestly to the frontend rather than papered over.
    """
    try:
        req = urllib.request.Request(
            NHC_CURRENT_STORMS_URL,
            headers={"User-Agent": "TIMDR-Cyclone-RI/1.0 (research dashboard)"},
        )
        with urllib.request.urlopen(req, timeout=NHC_FETCH_TIMEOUT_S) as resp:
            raw = resp.read()
        data = json.loads(raw)
        return jsonify(
            {
                "ok": True,
                "source": NHC_CURRENT_STORMS_URL,
                "activeStorms": data.get("activeStorms", []),
            }
        )
    except urllib.error.URLError as exc:
        return jsonify(
            {
                "ok": False,
                "error": f"Nie udalo sie polaczyc z NHC: {exc.reason}",
                "source": NHC_CURRENT_STORMS_URL,
            }
        ), 502
    except Exception as exc:  # noqa: BLE001 -- report honestly, don't crash the server
        return jsonify(
            {
                "ok": False,
                "error": f"Blad podczas pobierania/parsowania danych NHC: {exc}",
                "source": NHC_CURRENT_STORMS_URL,
            }
        ), 502


@app.route("/<path:filename>")
def www_files(filename):
    return send_from_directory(WWW_DIR, filename)


def main():
    url = f"http://127.0.0.1:{PORT}/"
    Timer(0.8, lambda: webbrowser.open(url)).start()
    print(f"TIMDR-Cyclone-RI dashboard: {url}")
    app.run(host="127.0.0.1", port=PORT, debug=False)


if __name__ == "__main__":
    main()
