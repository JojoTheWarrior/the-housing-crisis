from pydantic import BaseModel, Field, ConfigDict
from google import genai
from dotenv import load_dotenv
import os
import json

city_states = {
    "districts": {
        "district_1": {
            "name": "District 1",
            "population": 1000,
            "avg house cost": 200000,
            "public support": 0.8
        },
        "district_2": {
            "name": "District 2",
            "population": 2000,
            "avg house cost": 300000,
            "public support": 0.7
        }
    }
}
prompt = "Population for district 1 rose to 2000 so the emand for avg house cost will increase" 

class District(BaseModel):
    name: str
    population: int
    avg_house_cost: int = Field(alias="avg house cost")
    public_support: float = Field(alias="public support")


class CityStates(BaseModel):
    districts: dict[str, District]


def call_gemini(prompt, city_states):
    """
    Take the information in the city_states json file and prompt from the user to
    perform a gemini api call to calculate the new average house cost and the level of public support.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    # Initialize the Gemini client
    client = genai.Client(api_key=api_key)
    
    # Update city states using the Gemini API
    print(city_states)
    updated_city_states = update_city(prompt, city_states, client)
    print(updated_city_states)
    return updated_city_states

def update_city(prompt, city_states, client):
    try:
        # Perform the API call
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{prompt}. Send a new updated JSON formatted data to replace the city_states JSON data over here: {json.dumps(city_states)}",
            config={
                "response_mime_type": "application/json",
            },
        )

        # Print the raw response for inspection
        print("\nRaw API Response:")
        print(response.text)

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
