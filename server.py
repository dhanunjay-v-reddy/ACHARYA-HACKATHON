import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "frontend"))
CORS(app)

STATS_FILE = os.path.join(BASE_DIR, "focus_stats.json")

@app.route("/stats")
def stats():
    try:
        with open(STATS_FILE) as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Focus Guard not running yet"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return send_from_directory(os.path.join(BASE_DIR, "frontend"), "index.html")

if __name__ == "__main__":
    print("🌐 Dashboard running at http://localhost:5000")
    app.run(debug=True, port=5000)