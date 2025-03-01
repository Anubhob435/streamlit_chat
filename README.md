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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Requirements

- Python 3.7+
- Streamlit 1.28.0+
- Google Generative AI Python library
- MongoDB

## License

MIT License

Copyright (c) 2024 Anubhob Dey

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Author

Created with ❤️ by Anubhob Dey

### Connect with me:
- GitHub: [@yourgithubhandle](https://github.com/yourgithubhandle)
- LinkedIn: [Anubhob Dey](https://linkedin.com/in/yourprofile)