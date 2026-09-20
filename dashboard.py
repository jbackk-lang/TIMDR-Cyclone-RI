"""Local dashboard for TIMDR-Cyclone-RI: serves www/ (static HTML/JS/JSON,
no build step) on 127.0.0.1:5050. All data is precomputed real HURDAT2
data bundled in www/data/ -- no live API calls, no hardware needed.

Run: python dashboard.py   (or double-click run_dashboard.bat on Windows)
"""

import os
import webbrowser
from threading import Timer

from flask import Flask, send_from_directory

REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
WWW_DIR = os.path.join(REPO_ROOT, "www")
PORT = 5050

app = Flask(__name__, static_folder=None)


@app.route("/")
def index():
    return send_from_directory(WWW_DIR, "index.html")


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
