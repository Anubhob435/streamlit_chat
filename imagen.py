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

def generate(prompt_text="An Indian Temple with a beautiful sunset", output_path="generated_image.png"):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt_text),
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
            
            # Decode and save the image
            try:
                # First, decode the base64 data if it's encoded that way
                # Some APIs return raw binary data, others return base64-encoded data
                try:
                    # Try to decode base64 data
                    decoded_data = base64.b64decode(image_data)
                except:
                    # If not base64, use the original data
                    decoded_data = image_data
                
                # Create a PIL Image from binary data
                image = Image.open(io.BytesIO(decoded_data))
                
                # Save the image
                image.save(output_path)
                print(f"Image saved to {output_path}")
                
                return output_path
            except Exception as e:
                print(f"Error saving image: {e}")
                # Let's try an alternative approach by saving the raw data first
                try:
                    with open("temp_raw_image", "wb") as f:
                        f.write(image_data)
                    print("Saved raw image data for debugging")
                    
                    # Try saving with the original save_binary_file function
                    save_binary_file(output_path, image_data)
                    print(f"Attempted to save using direct binary write to {output_path}")
                    return output_path
                except Exception as e2:
                    print(f"Second attempt failed: {e2}")
                return None
        else:
            text_response = chunk.text
            print(text_response)
            
    return None

if __name__ == "__main__":
    image_path = generate()
    if image_path:
        # For local testing, open the image
        try:
            img = Image.open(image_path)
            img.show()
        except Exception as e:
            print(f"Error displaying image: {e}")
