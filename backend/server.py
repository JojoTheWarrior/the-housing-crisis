from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/simulate", methods=["POST"])
def simulate_turn():
    data = request.get_json()

    game_state = data.get("game_state")