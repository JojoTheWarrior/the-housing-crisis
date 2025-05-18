import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from PIL import ImageFile
import pyperclip
from io import BytesIO
import io
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
        contents=f"{preamble}. the building type is: {building_type}. please make the background white. keep the width a constant 256 pixels and make sure the long diagonal of the floor takes up that whole width, but you can make the height of the image arbitrarily tall to match the height of the building (i.e. skyscraper v.s. bungalow)",
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
                    return remove_background(image_bytes)
                except Exception as e:
                    print("failed to decode image")


def is_pink(R, G, B):
    # Normalize RGB to [0, 1] range (optional if values are already in 0–255)
    brightness = (R + G + B) / 3

    return (
        R > 150 and            # Red is high
        G >= 50 and G <= 180 and  # Green is moderate
        B >= 100 and B <= 255 and # Blue is moderate-high
        R > G and R > B and    # Red is dominant
        brightness > 100       # Not too dark
    )

def remove_background(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    pixels = image.load()

    width, height = image.size

    for r in range(height):
        for c in range(width):
            R,G,B,A = pixels[r, c]
            threshold = 40
            if R > 190 and G > 190 and B > 190:
            # if (is_pink(R, G, B)):
                pixels[r,c] = (0,0,0,0)
    
    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output.read()