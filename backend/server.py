from flask import Flask, request, jsonify, send_file
import gemini_handler
import make_building
import io
import base64

app = Flask(__name__)

@app.route("/generate_building", methods=["POST"])
def get_image():
    data = request.get_json()
    building_type = data.get("building_type")

    image_bytes = make_building.generate_building_image(building_type)
    base64_str = base64.b64encode(image_bytes).decode('utf-8')

    return jsonify({
        "building_type": building_type,
        "image_base64": base64_str
    })


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