from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
# import gemini_handler
import make_building
import io
import base64
import json
from random import choice, randint
from pprint import pprint
from update_city import call_gemini

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'


STATE = {
    "sprites": {

    },
    "districts": {

    }
}

DISTRICT_TO_COORDS = {}


@app.route("/generate_building", methods=["POST"])
def get_image():
    data = request.get_json()
    building_type = data.get("building_type")

    image_bytes = make_building.generate_building_image(building_type)
    base64_str = base64.b64encode(image_bytes).decode('utf-8')
    image_io = io.BytesIO(image_bytes)
    image_io.seek(0)

    return send_file(
        image_io,
        mimetype='image/png',
        as_attachment=False,
        download_name='building.png'  # optional
    )
    """
    return jsonify({
        "building_type": building_type,
        "image_base64": base64_str
    })
    """


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

@app.route("/send-district-coords", methods=["POST"])
@cross_origin()
def send_district_coords():
    global STATE, DISTRICT_TO_COORDS

    DISTRICT_TO_COORDS = json.loads(request.get_data(as_text=True))
    # print(DISTRICT_TO_COORDS)
    # STATE['districts'] = data

    for k,v in DISTRICT_TO_COORDS.items():
        STATE['districts'][k] = {
            "avg_house_price": randint(1_000_000, 2_000_000),
            "public_support": randint(1,100) / 100,
            "population": randint(50_000, 100_000),
            "new_additions": ""
        }

    # initialize default state of the world
    sprites = {
        "house": [
            choice(DISTRICT_TO_COORDS['1']),
            choice(DISTRICT_TO_COORDS['1']),
            choice(DISTRICT_TO_COORDS['2'])
        ],
        "apartment": [
            choice(DISTRICT_TO_COORDS['1']),
            choice(DISTRICT_TO_COORDS['1']),
            choice(DISTRICT_TO_COORDS['4']),
            choice(DISTRICT_TO_COORDS['4']),
            choice(DISTRICT_TO_COORDS['4'])
        ],
        "park": [
            choice(DISTRICT_TO_COORDS['3']),
            choice(DISTRICT_TO_COORDS['3']),
            choice(DISTRICT_TO_COORDS['3']),
            choice(DISTRICT_TO_COORDS['2']),
            choice(DISTRICT_TO_COORDS['4'])
        ],
        "subway": [
            choice(DISTRICT_TO_COORDS['4'])
        ]
    }

    STATE['sprites'] = sprites
    
    return {"status": "ok"}


@app.route("/send-prompt", methods=["POST"])
@cross_origin()
def send_prompt():
    data = json.loads(request.get_data(as_text=True))

    updated_city_states = call_gemini(data['prompt'], STATE)
    STATE['districts'] = updated_city_states[0]['districts']
    all_new_additions = updated_city_states[1]


    def district_from_coords(coords):
        for district, coordinates in DISTRICT_TO_COORDS.items():
            if coords in coordinates:
                return district
        return None

    game_state = {}
    for k,v in STATE['sprites'].items():
        for coordinate in v:
            if k in game_state:
                game_state[k].append(district_from_coords(coordinate))
            else:
                game_state[k] = [district_from_coords(coordinate)]

    # we now have game_state and all_new_additions
    # which are the two prerequisites for the main step

    print("--- HERE ---")
    print(all_new_additions)
    pprint(game_state)


    return {'status': 'ok'}


if __name__ == "__main__":
    app.run(debug=True)