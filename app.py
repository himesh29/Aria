import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import markdown  # Import the markdown package to convert markdown to HTML

# Hardcoded Gemini API Key
GEMINI_API_KEY = "AIzaSyBPBlUeKsISDBQGBV-5iihKtwF4aBjWAO4"  # Replace with your actual Gemini API key

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Create the model configuration (removed the invalid "response_mime_type")
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

# Create the generative model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", generation_config=generation_config
)

# Start a chat session
chat_session = model.start_chat(history=[])

# Initialize Flask app
app = Flask(__name__)

# Ensure the uploads directory exists
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    # Render the index page (ensure this is the correct path to your HTML file)
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form['user_message']
    try:
        # Send user message to Gemini API for response
        response = chat_session.send_message(user_message)

        # Convert the response text from Markdown to HTML
        html_response = markdown.markdown(response.text)

        # Check if response is empty or invalid
        if not html_response:
            return jsonify({'response': 'Sorry, I couldn’t generate a response.'})

        return jsonify({'response': html_response})
    except Exception as e:
        # Handle any errors during response generation
        return jsonify({'response': 'Error generating response: ' + str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400

    try:
        # Save the file to the uploads folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Return success message with the uploaded file's name
        return jsonify({'success': True, 'message': 'File uploaded successfully', 'filename': file.filename})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
