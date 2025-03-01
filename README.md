```markdown
# Jarvis - AI Chat Assistant

A sophisticated AI chat interface powered by Google's Gemini 1.5 Pro model, built with Streamlit.

## Features

- 🤖 Chat with Gemini 1.5 Pro, one of the most advanced AI language models
- 🎭 Multiple chat personas: Basic Assistant, Technical Expert, Creative Writer, Professional Consultant
- 🎛️ Adjustable creativity level (temperature) for varied responses
- 📝 Three response styles: Concise, Standard, and Detailed
- 🔄 Persistent chat history stored in MongoDB
- 🌓 Dark mode interface for comfortable viewing
- 📱 Responsive layout that works on multiple devices

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/jarvis-ai.git
   cd jarvis-ai
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   MONGODB_URI=your_mongodb_connection_string
   ```

4. Alternatively, create an `app.yaml` file for deployment:
   ```yaml
   runtime: python
   env: flex
   entrypoint: streamlit run app.py --server.port=$PORT
   
   env_variables:
     GEMINI_API_KEY: "your_gemini_api_key"
     MONGODB_URI: "your_mongodb_connection_string"
   ```

## Usage

Run the application locally:
```
streamlit run app.py
```

Then open your browser to http://localhost:8501

## Configuration

The application uses several configuration sources in the following order:
1. Environment variables
2. app.yaml file
3. `.env` file (loaded by python-dotenv)

## MongoDB Integration

Chat history is stored in MongoDB for persistence. The application uses the following structure:
- Database: `streamlitchat`
- Collection: `chatrecords`

Each chat message contains:
- `session_id`: Unique identifier for the chat session
- `timestamp`: UTC time when message was sent
- `user_message`: The message from the user
- `bot_response`: The response from Gemini model
- `platform`: Where the chat is occurring (default: 'streamlit')
- `ip_address`: Anonymized IP (default: 'streamlit_session')
- `model`: The model used (default: 'gemini-1.5-pro')

## Deployment

This application can be deployed to Google Cloud Platform using the app.yaml configuration.

## Requirements

- Python 3.7+
- Streamlit 1.28.0+
- Google Generative AI Python library
- MongoDB

## License

[Specify your license]

## Author

[Your Name]
```

You can customize this README by adding your name, choosing a license, and adding any additional sections specific to your project.
You can customize this README by adding your name, choosing a license, and adding any additional sections specific to your project.