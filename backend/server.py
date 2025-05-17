from flask import Flask, request, jsonify
import gemini_handler

app = Flask(__name__)

@app.route("/simulate", methods=["POST"])
def simulate_turn():
    data = request.get_json()

    game_state = data.get("game_state")
    policy = data.get("proposed_policy")

    updated_state, feedback = gemini_handler.process_policy(game_state, policy)

    return jsonify({
        "updated_game_state": updated_state,
        "ai_feedback": feedback
    })

if __name__ == "__main__":
    app.run(debug=True)