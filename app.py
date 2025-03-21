import streamlit as st
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
from uuid import uuid4
import yaml
from mongo_utils import get_db_connection, store_chat_message, get_chat_history_by_session
# Import the image generation functionality
from imagen import generate
import base64
from PIL import Image
import io

# Load from .env as fallback for local development
load_dotenv()

# Function to get configuration from app.yaml or environment
def get_config():
    # First try to get from environment (which would be set by app.yaml in deployment)
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    mongodb_uri = os.environ.get('MONGODB_URI')
    
    # If not found in environment, try to load from app.yaml directly
    if not all([gemini_api_key, mongodb_uri]):
        try:
            with open('app.yaml', 'r') as yaml_file:
                config = yaml.safe_load(yaml_file)
                env_vars = config.get('env_variables', {})
                gemini_api_key = gemini_api_key or env_vars.get('GEMINI_API_KEY')
                mongodb_uri = mongodb_uri or env_vars.get('MONGODB_URI')
        except Exception as e:
            st.warning(f"Could not load config from app.yaml: {e}")
    
    # Fallback to environment variables loaded by dotenv
    gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
    mongodb_uri = mongodb_uri or os.getenv('MONGODB_URI')
    
    return {
        'gemini_api_key': gemini_api_key,
        'mongodb_uri': mongodb_uri
    }

# Remove the set_custom_theme function and replace with simpler page config
def set_custom_theme():
    # No custom styling needed when using default Streamlit theme
    pass

config = get_config()

# Set page configuration
st.set_page_config(
    page_title="Gemini AI Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Gemini AI Chat\nDark mode chat interface powered by Google's Gemini 1.5 Pro model."
    }
)

# Apply custom theme
set_custom_theme()

# Configure MongoDB
db, chats_collection = get_db_connection()
if chats_collection is None:
    st.error("MongoDB connection failed. Check your connection string.")

# Configure Gemini API
if config['gemini_api_key']:
    genai.configure(api_key=config['gemini_api_key'])
else:
    st.error("Gemini API key not found in configuration.")

# Create the model with improved configuration
generation_config = {
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

# Initialize session state for chat history and settings
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

if "settings" not in st.session_state:
    st.session_state.settings = {
        "response_length": "Standard",
        "chat_context": "Basic Assistant"
    }

# Initialize session state for image generation
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []

# Different context options for the chatbot
CONTEXT_OPTIONS = {
    "Basic Assistant": "You are a helpful, friendly AI assistant. Be concise and clear in your responses.",
    "Technical Expert": "You are a technical expert AI with deep knowledge of programming and computer science. Provide detailed technical answers with code examples when appropriate.",
    "Creative Writer": "You are a creative AI writer with a flair for engaging, descriptive language. Be imaginative and inspiring in your responses.",
    "Professional Consultant": "You are a professional consultant AI with a formal, business-oriented communication style. Provide structured, analytical responses."
}

# Get the current context
INITIAL_CONTEXT = CONTEXT_OPTIONS[st.session_state.settings["chat_context"]]

# Initialize Gemini chat
@st.cache_resource
def get_gemini_chat(_context, _temp=0.9):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config={"temperature": _temp, "top_p": 0.95, "top_k": 40, "max_output_tokens": 8192},
    )
    chat = model.start_chat(history=[])
    chat.send_message(_context)
    return chat

chat = get_gemini_chat(INITIAL_CONTEXT, 0.9)

# Function to process messages and update chat history
def process_message(user_message):
    try:
        # Check if this is an image generation request
        if user_message.lower().startswith("generate image:") or user_message.lower().startswith("create image:"):
            # Extract the image prompt
            image_prompt = user_message.split(":", 1)[1].strip()
            
            # Display user message in chat
            st.session_state.chat_history.append({"role": "user", "content": user_message})
            
            # Generate the image
            with st.spinner("Generating image..."):
                image_path = process_image_generation_from_chat(image_prompt)
            
            if image_path:
                # Create response with image
                bot_response = f"I've generated an image based on your prompt: '{image_prompt}'. You can view it in the Generated Images tab."
                
                # Store in session state
                st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                
                # Store conversation in MongoDB
                store_chat_message(
                    st.session_state.session_id, 
                    user_message, 
                    bot_response, 
                    platform='streamlit',
                    ip_address="streamlit_session",
                    model='gemini-1.5-pro'
                )
                
                return bot_response
            else:
                bot_response = "I encountered an error while trying to generate that image. Please try again with a different description."
                st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                return bot_response
        
        # Handle regular chat messages
        # Display user message in chat
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        # Show a spinner while waiting for the response
        with st.spinner("Thinking..."):
            # Get response from Gemini
            response = chat.send_message(user_message)
            bot_response = response.text.strip()
        
        # Store in session state
        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
        
        # Store conversation in MongoDB using our utility function
        store_chat_message(
            st.session_state.session_id, 
            user_message, 
            bot_response, 
            platform='streamlit',
            ip_address="streamlit_session",
            model='gemini-1.5-pro'
        )
        
        return bot_response
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "I encountered an error processing your request. Please try again."

# Layout with columns
col1, col2 = st.columns([5, 1])  # Adjust ratio to give more space to chat

# Modify the sidebar content to remove custom HTML styling
with col2:
    st.sidebar.title("Gemini Chat 🤖")
    
    # Add tabs for Chat and Image Generation
    tab1, tab2 = st.sidebar.tabs(["Chat Settings", "Image Generation"])
    
    with tab1:
        # Chat settings in sidebar
        st.sidebar.title("Chat Settings")
        
        # Chat persona selector
        selected_context = st.sidebar.selectbox(
            "Chat Persona",
            options=list(CONTEXT_OPTIONS.keys()),
            index=list(CONTEXT_OPTIONS.keys()).index(st.session_state.settings["chat_context"]),
        )
        
        # Temperature slider removed
        
        # Change radio buttons to dropdown for response style
        selected_length = st.sidebar.selectbox(
            "Response Style",
            options=["Concise", "Standard", "Detailed"],
            index=["Concise", "Standard", "Detailed"].index(st.session_state.settings["response_length"]),
            help="Controls how detailed the AI responses should be"
        )
        
        # Apply settings button
        if st.sidebar.button("Apply Settings"):
            # Update settings
            st.session_state.settings["chat_context"] = selected_context
            st.session_state.settings["response_length"] = selected_length
            
            # Re-initialize chat with new settings
            new_context = CONTEXT_OPTIONS[selected_context]
            if selected_length == "Concise":
                new_context += " Keep your responses very brief and to the point."
            elif selected_length == "Detailed":
                new_context += " Provide detailed, comprehensive responses."
                
            # Reinitialize the chat with new context (using default temperature)
            chat = get_gemini_chat(new_context, 0.9)
            
            st.sidebar.success("Settings applied!")
            st.rerun()
        
        # Clear chat button with confirmation
        if st.sidebar.button("Clear Chat History", type="secondary"):
            st.session_state.chat_history = []
            st.sidebar.success("Chat history cleared!")
            st.rerun()
    
    with tab2:
        st.header("Generate Images")
        image_prompt = st.text_area("Describe the image you want to generate:", 
                                   placeholder="An Indian Temple with a beautiful sunset")
        
        if st.button("Generate Image"):
            with st.spinner("Generating image..."):
                try:
                    # Generate a unique filename for each image
                    img_filename = f"generated_image_{len(st.session_state.generated_images)}.png"
                    img_path = os.path.join("generated_images", img_filename)
                    
                    # Ensure the directory exists
                    os.makedirs("generated_images", exist_ok=True)
                    
                    # Generate the image
                    output_path = generate(prompt_text=image_prompt, output_path=img_path)
                    
                    if output_path:
                        # Add to session state
                        st.session_state.generated_images.append({
                            "path": output_path,
                            "prompt": image_prompt,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.success("Image generated successfully!")
                    else:
                        st.error("Failed to generate image.")
                except Exception as e:
                    st.error(f"Error generating image: {str(e)}")
    
    # Information section
    st.sidebar.markdown("---")
    st.sidebar.subheader("About")
    st.sidebar.info("""
    **Gemini AI Chat**
    
    Powered by Google's Gemini 1.5 Pro model.
    
    This application lets you interact with one of the most advanced AI language models.
    
    Your chat history is stored in MongoDB for future reference.
    """)

with col1:
    # Simplify main chat area
    # Add tabs for Chat and Generated Images
    chat_tab, images_tab = st.tabs(["Chat", "Generated Images"])
    
    with chat_tab:
        st.title("💬 Gemini AI Chat")
        
        # Welcome message with simple markdown
        if not st.session_state.chat_history:
            st.info("Welcome to Gemini AI Chat! Start a conversation by typing a message below.")

        # Display chat messages with improved styling
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(message["content"])
        
        # Chat input using Streamlit's native chat input
        if prompt := st.chat_input("Ask Gemini something...", key="chat_input"):
            process_message(prompt)
            st.rerun()
    
    with images_tab:
        st.title("🖼️ Generated Images")
        
        if not st.session_state.generated_images:
            st.info("No images generated yet. Use the Image Generation tab in the sidebar to create images.")
        else:
            # Display generated images in a grid
            cols = st.columns(2)  # Display 2 images per row
            
            for i, img_data in enumerate(st.session_state.generated_images):
                col_idx = i % 2
                with cols[col_idx]:
                    try:
                        st.image(img_data["path"], caption=f"Prompt: {img_data['prompt']}")
                        st.caption(f"Generated on: {img_data['timestamp']}")
                        # Add a download button
                        with open(img_data["path"], "rb") as file:
                            btn = st.download_button(
                                label="Download Image",
                                data=file,
                                file_name=os.path.basename(img_data["path"]),
                                mime="image/png"
                            )
                    except Exception as e:
                        st.error(f"Error displaying image {i+1}: {str(e)}")

# Add a function to handle image generation from chat context
def process_image_generation_from_chat(prompt):
    try:
        # Generate a unique filename
        img_filename = f"generated_image_{len(st.session_state.generated_images)}.png"
        img_path = os.path.join("generated_images", img_filename)
        
        # Ensure the directory exists
        os.makedirs("generated_images", exist_ok=True)
        
        # Generate the image
        output_path = generate(prompt_text=prompt, output_path=img_path)
        
        if output_path:
            # Add to session state
            st.session_state.generated_images.append({
                "path": output_path,
                "prompt": prompt,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return output_path
        return None
    except Exception as e:
        print(f"Error generating image from chat: {str(e)}")
        return None