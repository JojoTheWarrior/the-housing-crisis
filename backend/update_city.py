from pydantic import BaseModel, Field, Extra, ConfigDict
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
prompt = "Population rose to 2000 so the demand for avg house cost will increase"

class District(BaseModel):
    name: str
    population: int
    avg_house_cost: int = Field(alias="avg house cost")
    public_support: float = Field(alias="public support")


class CityStates(BaseModel):
    districts: dict[str, District]

    model_config = ConfigDict(extra='ignore')


def call_gemini(prompt, city_states):
    """
    prompt is a string that is given by the user
    city_states is a json object that contains the information about every district in the city
    
    Take the information in the city_States json file and prompt from the user to
    perform a gemini api call to calculate the new average house cost and the level of public support.

    Use the response from the gemini api call to update the city_states json file
    and return the updated city_states json file
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
        # Perform the API call with the structured response schema
        response = client.models.generate_content(
            model="gemini-2.o-flash",
            contents=f"{prompt}. Send a new updated json formated data to replace the city_states json data over here: f{json.dumps(city_states)}",
            config={
                "response_mime_type": "application/json",
                "response_schema": list[CityStates],
            },
        )
        print(response.text)

        return response
    except Exception as e:
        print(f"Error updating city data: {e}")
        return city_states


# Test the function
call_gemini(prompt, city_states)
