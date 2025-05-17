from pydantic import BaseModel, Field, ConfigDict
from google import genai
from dotenv import load_dotenv
import os
import json

class District(BaseModel):
    number: int
    population: int
    avg_house_cost: int = Field(alias="avg_house_cost")
    public_support: float = Field(alias="public_support")
    new_additions: str = Field(default="")

class CityStates(BaseModel):
    districts: dict[str, District]

class Sprite(BaseModel):
    sprite: list[int] = Field(default_factory=list)

def call_gemini(prompt, city_states):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)
    
    print(city_states)
    updated_city_states = get_new_city_states(prompt, city_states, client)
    print(updated_city_states)

    # Extract all the new additions into a single string
    all_new_additions = ". ".join([
        f"District {number}: {district['new_additions']}"
        for number, district in updated_city_states.get("districts", {}).items()
        if district.get("new_additions")
    ])

    print("\nAll New Additions:")
    print(all_new_additions)


    return updated_city_states, all_new_additions

def get_new_city_states(prompt, city_states, client):
    preamble = f"""You are provided with a JSON object representing the current state of a city,
      including detailed information about each district. Your task is to update this JSON object based on the given prompt: {prompt}. 
      The current city state is: {json.dumps(city_states)}. 
      Each district in the JSON object has the following fixed fields: 'number', 'population', 'avg_house_cost', 'public_support', and 'new_additions'. 
      No new fields should be added. The 'population' field represents the number of residents, 
      'avg_house_cost' captures the average property cost in the district, 
      'public_support' is a value between 0 and 1 where 1 indicates full support and 0 indicates no support, 
      and 'new_additions' is a brief, coherent description of physical changes made to the district based on the prompt. 
      This field should only describe tangible, visual modifications, like infrastructure improvements, new buildings, or public spaces, 
      and should not include abstract concepts like policy changes. 
      Avoid explicitly describing the numeric changes in 'population', 'avg_house_cost', or 'public_support' within the 'new_additions' field, 
      as these values should implicitly reflect the impact of the described physical changes.
      If there are no physical, visual, tanlgible changes given through the prompt, keep the 'new_additions' field empty.
      
      For example, appropriate 'new_additions' include phrases like 
      "Built a new subway station.", "Constructed a new park.", or "Established a new community center."
      Physical changes like these should naturally lead to downstream impacts on the other fields.
      For instance, if a district initially has a 'population' of 1000, 'avg_house_cost' of 200000, and 'public_support' of 0.8,
      then building a new subway station might result in a 'population' increase to 1200,
      a 'avg_house_cost' rise to 250000, and a 'public_support' boost to 0.9,
      while the 'new_additions' field could simply state "Built a new subway station."
      Ensure the returned JSON object accurately captures these inferences without directly describing them in the 'new_additions' field.
      
      Another important note is that when you are calculating the house cost, briefly think of supply and demand.
      A higher population would mean a higher demand, and thus a higher house cost. The same workds vice versa.
      The AI model should also be able to make rational and logical decisions based on the prompt.
      For instance, if the population increases, a new apartment complex should be built to accommodate the new residents.
      """


    try:
        # Perform the API call
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{preamble}",
            config={
                "response_mime_type": "application/json",
            },
        )

        # Attempt to parse the response as JSON
        try:
            response_json = json.loads(response.text)
            print("\nParsed JSON:")
            print(json.dumps(response_json, indent=4))
        except json.JSONDecodeError as decode_error:
            print("\nFailed to decode JSON:")
            print(response.text)
            print(f"Decoding Error: {decode_error}")
            return city_states

        # Return the raw response for now
        return response_json

    except Exception as e:
        print(f"\nError updating city data: {e}")
        return city_states
    
def make_new_game_state(game_state, all_new_additions):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # Prepare the input for the model
    preamble = f"""
    You are provided with a JSON object representing the current state of a game city, which contains detailed information about each sprite,
    telling which district they are in.
    This is the current game state: {game_state}.
    You are also provided with a list of changes that should be incorporated into the existing game state.
    These sprites should be correctly assigned to their respective districts and should reflect tangible,
    visual changes to the city's physical environment. 
    Make sure that each sprite is correctly matched to its respective district based on the district numbers provided.
    When incorporating these sprites, maintain the original structure of the JSON object and do not add any unexpected fields.
    Ensure the updated game state accurately captures the impact of these additions while preserving all existing information.
    The AI model should also be able to make rational and logical decisions based on the input.
    Sprites can be added and destroyed based on input about each district.
    To destroy a sprite, change the district number to 0.
    The list of the changes is described here: {all_new_additions}.
    Return the updated game state as a well-structured JSON object.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=preamble,
        config={
            "response_mime_type": "application/json",
        },
    )

    # Extract and return the updated game state from the response
    print(game_state)
    new_game_state = json.loads(response.text)
    print(new_game_state)
    return new_game_state
    
    


# Test the function
if __name__ == "__main__":
    make_new_game_state(
        {'apartment': ['1', '1', '4', '4', '4'],
 'house': ['1', '1', '2'],
 'park': ['3', '3', '3', '2', '4'],
 'subway': ['4']}
        , "Build a stadium in district 1 and 2")
