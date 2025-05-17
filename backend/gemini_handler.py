import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

preamble = "so im working on a game that's about the housing crisis. essentially, the demand is very high from all the young adults and immigrants who want to purchase houses. however, the prices are driven high by conservative homeowners, who need high prices to retire. it's a really difficult problem to solve in our real world, so this project is a simulator that allows the user to try new things and see how his city ends up. it isn't supposed to be easy to beat - it should literally be impossible until the player comes up with the perfect society." \
            "the frontend involves a mayor who manages a 2D grid city. each year, he can make one policy. and this is not restricted, since we're using AI to accept literally any prompt. based on the policy, the AI needs to adjust and figure out how the game should proceed." \
            "this is interesting because we want the player to have some freedom, but we still need some confinement so the game has structure. for exampe, im not sure if we should hardcode what \"city variables\" like GDP and average income and population, or if we just should roll with whatever. and of course the policies need to be \"reasonable\" so the mayor can't just say whatever. maybe there should even be punishments if the mayor is too ambitious and says \"invest in housing on mars\" or smth."

explain_grid_system = "the grid is an 8x8 json file. each cell has the following fixed variables: [], as well as the following free variables: []"

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=f"{preamble} the current game state is: initial state."
)

print(response.text)