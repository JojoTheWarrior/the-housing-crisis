from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
# import gemini_handler
import make_building
import io
import base64
import json
from random import choice, randint
from pprint import pprint
from update_city import call_gemini, make_new_game_state

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
    global STATE

    data = json.loads(request.get_data(as_text=True))

    updated_city_states = call_gemini(data['prompt'], STATE)
    STATE['districts'] = updated_city_states[0]['districts']
    all_new_additions = updated_city_states[1]


    def district_from_coords(coords):
        for district, coordinates in DISTRICT_TO_COORDS.items():
            if coords in coordinates:
                return district
        return None

    def generate_coordinates(d, taken):
        available_set = set(DISTRICT_TO_COORDS[d])
        taken_set = set(taken)
        leftover = list(available_set.difference(taken_set))
        return choice(leftover)


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

    new_game_state = make_new_game_state(game_state, all_new_additions)

    pprint(new_game_state)
    pprint(STATE['sprites'])


    original_keys = set(STATE['sprites'].keys())
    new_keys = set(new_game_state.keys())
    new_structures = list(original_keys.difference(new_keys))

    new_state = {}

    for k,v in new_game_state.items():
        new_state[k] = []

        for i in range(len(v)):
            district = new_game_state[k][i]

            if district != '0':
                # add existing coordinates
                if len(new_state[k]) + 1 <= len(STATE['sprites'][k][i]):
                    new_state[k].append(STATE['sprites'][k][i])

                # generate new coordinates
                else:
                    new_state[k].append(generate_coordinates(district, STATE['sprites'][k]))

                # no more space in district
                if len(new_state[k]) >= len(DISTRICT_TO_COORDS[district]):
                    new_state[k].pop()

    pprint(new_state)
    # STATE = new_state

    # generate images based on new_structures
    for structure in new_structures:
        pass  # make call to image generating api

    return {'status': 'ok'}

city_avg_house_price = 0
city_public_support = 0

@app.route('/process-prompt', methods=['POST'])
def process_prompt():
    data = request.json()
    input_string = data.get("input_string", "")

    # Calculate city_avg_house_price
    total_house_value = 0
    total_houses = 0
    for district_id, district in STATE['districts'].items():
        num_houses = len(STATE['sprites'].get('house', []))
        total_house_value += district['avg_house_price'] * num_houses
        total_houses += num_houses

    city_avg_house_price = total_house_value // total_houses if total_houses > 0 else 0

    # Calculate city_public_support (weighted average)
    total_support = 0
    total_population = 0
    for district in STATE['districts'].values():
        total_support += district['public_support'] * district['population']
        total_population += district['population']

    city_public_support = total_support / total_population if total_population > 0 else 0
    city_public_support = round(city_public_support, 2)  # Round to 2 decimal places for clarity

    return jsonify([city_avg_house_price, city_public_support, STATE['sprites']])



if __name__ == "__main__":
    app.run(debug=True)