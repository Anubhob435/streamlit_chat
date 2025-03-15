import base64
import os
from google import genai
from google.genai import types
# Add these imports
from PIL import Image
import io

def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""IAn Indian Temple with a beautiful sunset"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_modalities=[
            "image",
            "text",
        ],
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
            continue
        if chunk.candidates[0].content.parts[0].inline_data:
            # Get image data
            image_data = chunk.candidates[0].content.parts[0].inline_data.data
            mime_type = chunk.candidates[0].content.parts[0].inline_data.mime_type
            
            # Save original image to temporary file
            temp_file = "temp_image"
            save_binary_file(temp_file, image_data)
            
            try:
                # Open the image using PIL
                img = Image.open(temp_file)
                
                # Convert to RGB if necessary (to handle RGBA or other formats)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as PNG
                png_file = "image.png"
                img.save(png_file, "PNG")
                
                print(f"Image converted and saved as PNG: {png_file}")
                
                # Display the image
                img.show()
                
                # Remove temporary file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
            except Exception as e:
                print(f"Error processing image: {e}")
        else:
            print(chunk.text)

if __name__ == "__main__":
    generate()
