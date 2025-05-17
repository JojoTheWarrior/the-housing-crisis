from pydantic import BaseModel, Field, ConfigDict
from google import genai
from dotenv import load_dotenv
import os
import json

city_states ={
    "districts": {
        "district_1": {
            "number": 1,
            "population": 1000,
            "avg house cost": 200000,
            "public support": 0.8,
            "new_additions": ""
        },
        "district_2": {
            "number": 2,
            "population": 3000,
            "avg house cost": 300000,
            "public support": 0.7,
            "new_additions": ""
        },
        "district_3": {
            "number": 3,
            "population": 500,
            "avg house cost": 150000,
            "public support": 0.9,
            "new_additions": ""
        },
        "district_4": {
            "number": 4,
            "population": 2000,
            "avg house cost": 250000,
            "public support": 0.6,
            "new_additions": ""
        },
        "district_5": {
            "number": 5,
            "population": 4000,
            "avg house cost": 350000,
            "public support": 0.5,
            "new_additions": ""
        }
    }
}


prompt = "The population in District 2 has doubled due to recent economic growth. Update the city state accordingly." \
"Build a new community center in District 3 to encourage local engagement and strengthen community ties." 

class District(BaseModel):
    number: int
    population: int
    avg_house_cost: int = Field(alias="avg house cost")
    public_support: float = Field(alias="public support")
    new_additions: str = Field(default="")

class CityStates(BaseModel):
    districts: dict[str, District]


def call_gemini(prompt, city_states):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)
    
    print(city_states)
    updated_city_states = get_new_city_states(prompt, city_states, client)
    print(updated_city_states)

    # Extract all the new additions into a single string
    all_new_additions = ". ".join([
        f"District {district['number']}: {district['new_additions']}"
        for district in updated_city_states.get("districts", {}).values()
        if district.get("new_additions")
    ])

    print("\nAll New Additions:")
    print(all_new_additions)


    return updated_city_states

def get_new_city_states(prompt, city_states, client):
    preamble = f"""You are provided with a JSON object representing the current state of a city,
      including detailed information about each district. Your task is to update this JSON object based on the given prompt: {prompt}. 
      The current city state is: {json.dumps(city_states)}. 
      Each district in the JSON object has the following fixed fields: 'number', 'population', 'avg house cost', 'public support', and 'new_additions'. 
      No new fields should be added. The 'population' field represents the number of residents, 
      'avg house cost' captures the average property cost in the district, 
      'public support' is a value between 0 and 1 where 1 indicates full support and 0 indicates no support, 
      and 'new_additions' is a brief, coherent description of physical changes made to the district based on the prompt. 
      This field should only describe tangible, visual modifications, like infrastructure improvements, new buildings, or public spaces, 
      and should not include abstract concepts like policy changes. 
      Avoid explicitly describing the numeric changes in 'population', 'avg house cost', or 'public support' within the 'new_additions' field, 
      as these values should implicitly reflect the impact of the described physical changes.
      If there are no physical, visual, tanlgible changes given through the prompt, keep the 'new_additions' field empty.
      
      For example, appropriate 'new_additions' include phrases like 
      "Built a new subway station.", "Constructed a new park.", or "Established a new community center."
      Physical changes like these should naturally lead to downstream impacts on the other fields.
      For instance, if a district initially has a 'population' of 1000, 'avg house cost' of 200000, and 'public support' of 0.8,
      then building a new subway station might result in a 'population' increase to 1200,
      a 'avg house cost' rise to 250000, and a 'public support' boost to 0.9,
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




# Test the function
call_gemini(prompt, city_states)
