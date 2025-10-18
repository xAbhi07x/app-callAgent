"""
Twilio Inbound Call Handler
Receives inbound calls, plays a greeting, and logs call metadata
"""

from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from pyngrok import ngrok
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# CSV log file path
LOG_FILE = 'logs/call_logs.csv'

# Initialize CSV file with headers if it doesn't exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'From', 'To', 'CallSid', 'CallStatus'])


def log_call(call_data):
    """Log call metadata to CSV file"""
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            call_data.get('From', 'Unknown'),
            call_data.get('To', 'Unknown'),
            call_data.get('CallSid', 'Unknown'),
            call_data.get('CallStatus', 'Unknown')
        ])


@app.route('/voice', methods=['POST'])
def voice():
    """Handle inbound calls"""
    
    # Get call metadata from Twilio
    call_data = {
        'From': request.form.get('From'),
        'To': request.form.get('To'),
        'CallSid': request.form.get('CallSid'),
        'CallStatus': request.form.get('CallStatus')
    }
    
    # Log the call
    log_call(call_data)
    print(f"📞 Incoming call from {call_data['From']} at {datetime.now().strftime('%H:%M:%S')}")
    
    # Create TwiML response
    response = VoiceResponse()
    
    # Play greeting message
    response.say(
        "Hello! Thanks for calling. For now, we are just testing this line.",
        voice='alice',
        language='en-US'
    )
    
    # Pause for 2 seconds
    response.pause(length=2)
    
    # Hang up
    response.hangup()
    
    return str(response)


@app.route('/voice-ai', methods=['POST'])
def voice_ai():
    """Handle inbound calls with AI assistant (WebSocket streaming)"""
    
    # Get call metadata from Twilio
    call_data = {
        'From': request.form.get('From'),
        'To': request.form.get('To'),
        'CallSid': request.form.get('CallSid'),
        'CallStatus': request.form.get('CallStatus')
    }
    
    # Log the call
    log_call(call_data)
    print(f"📞 AI call from {call_data['From']} at {datetime.now().strftime('%H:%M:%S')}")
    
    # Create TwiML response with WebSocket stream
    response = VoiceResponse()
    
    # WebSocket URL from environment variable
    # You must run ngrok on port 5001 and set this in .env
    ws_url = os.getenv('WEBSOCKET_URL', 'wss://localhost:5001')
    
    if 'your-ngrok-url' in ws_url:
        print("⚠️  WARNING: WEBSOCKET_URL not configured in .env!")
        print("   Run 'ngrok http 5001' and update WEBSOCKET_URL in .env")
    
    # Connect call to WebSocket stream
    connect = response.connect()
    stream = connect.stream(url=ws_url)
    
    # Pass caller info as parameters
    stream.parameter(name='from', value=call_data['From'])
    stream.parameter(name='callSid', value=call_data['CallSid'])
    
    return str(response)


@app.route('/')
def index():
    """Health check endpoint"""
    return """
    ✅ Twilio Inbound Call Handler is running!
    <br><br>
    Endpoints:<br>
    - POST /voice → Simple greeting (original)<br>
    - POST /voice-ai → AI Assistant (WebSocket streaming)<br>
    """


if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    
    # Start ngrok tunnel
    print("\n🚀 Starting ngrok tunnel...")
    public_url = ngrok.connect(port)
    print(f"\n✅ Ngrok tunnel established!")
    print(f"📡 Public URL: {public_url}")
    print(f"\n⚙️  Configure your Twilio number webhook to:")
    print(f"   {public_url}/voice")
    print(f"\n{'='*60}\n")
    
    # Start Flask app
    print(f"🌐 Starting Flask server on port {port}...")
    app.run(debug=True, port=port, use_reloader=False)
