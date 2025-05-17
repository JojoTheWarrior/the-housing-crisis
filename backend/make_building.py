import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from PIL import ImageFile
import pyperclip
from io import BytesIO
import base64
import PIL.Image

ImageFile.LOAD_TRUNCATED_IMAGES = True # config for the image generation

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

preamble = "please make a pixel art themed building of the following type that will be specified later. Draw it from a perspective isometric view, on a square cell that is viewed from an angle 30 degrees above the horizontal."

client = genai.Client(api_key=api_key)

def generate_building_image(building_type):
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=f"{preamble}. the building type is: {building_type}. please make the backgroud transparent. avoid using colors with RGB values where R, G, and B >= 195. this is for the background transparency algorithm (so avoid whites and grays).",
        config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
        )
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            mime_type = part.inline_data.mime_type
            # check the mime type
            if mime_type.startswith("image/"):
                try:
                    image_bytes = base64.b64decode(part.inline_data.data)
                    with open(f"./pre_{building_type}.png", "wb") as f:
                        f.write(image_bytes)
                    remove_background(f"./pre_{building_type}.png", f"./{building_type}.png")
                    return "./{building_type}.png"
                except Exception as e:
                    print("failed to decode image")


def remove_background(image_path, output_path):
    image = Image.open(image_path).convert("RGBA")
    pixels = image.load()

    width, height = image.size

    for r in range(height):
        for c in range(width):
            R,G,B,A = pixels[r, c]
            if R >= 195 and G >= 195 and B >= 195:
                pixels[r,c] = (0,0,0,0)
    
    image.save(output_path)
    print("saved transparent image")