from google import genai
from pydantic import BaseModel
import json

class District(BaseModel):
    name: str
    population: int
    avg_house_cost: int
    public_support: float


class CityStates(BaseModel):
    districts: dict[str, District]

def update_city(prompt, city_states):
    """
    prompt is a string that is given by the user
    city_states is a json object that contains the informatino about every district in the city
    {
        "districts": {
            "district_1": {
                "name": "District 1",
                "population": 1000,
                "avg house cost": 200000,
                "public support": 0.8
            },
            ...
        }
    }
    
    Take the information in the city_States json file and prompt from the user to
    perform a gemini api call to calculate the new average house cost and the level of public support

    Use the response from the gemini api call to update the city_states json file
    and return the updated city_states json file
    """

    #Initialize the Gemini client
    client = genai.Client(api_key="YOUR_GOOGLE_API_KEY")
    
    # Perform the API call with a structured JSON response schema
    try:
        response = client.models.generate_content(
            model="gemini-2.o-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": CityStates,
            },
        )

        # Use the response as instantiated objects
        updated_city_states: CityStates = response.parsed[0]
        return updated_city_states.dict()
    except Exception as e:
        print(f"Error updating city data: {e}")
        return city_states