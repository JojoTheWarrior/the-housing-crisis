import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import ImageFile
from io import BytesIO
import base64

ImageFile.LOAD_TRUNCATED_IMAGES = True # config for the image generation

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

preamble = "please make a pixel art themed building of the following type that will be specified later. Draw it from a perspective isometric view, on a square cell that is viewed from an angle 30 degrees above the horizontal."

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.0-flash-preview-image-generation",
    contents=f"{preamble}. the building type is: library",
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
            with open("gemini_raw_output.png", "wb") as f:
                f.write(part.inline_data.data)
        except Exception as e:
           print("failed to decode image")
    