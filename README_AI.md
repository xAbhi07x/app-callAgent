# Twilio AI Voice Assistant 🤖📞

A Python-based system for receiving phone calls and connecting callers to an AI voice assistant powered by OpenAI's Realtime API. The AI can have natural conversations, answer questions, and capture medicine orders.

## 📋 Features

- ✅ **Real-time AI conversation** - Natural voice interaction powered by OpenAI
- ✅ **Medicine order capture** - Collects medicine name, quantity, and delivery address
- ✅ **Flexible assistant** - Can answer pharmacy questions or handle orders
- ✅ **Auto-transcription** - Logs full conversation transcript
- ✅ **Dual endpoints** - Simple greeting (/voice) or AI assistant (/voice-ai)
- ✅ **Auto ngrok tunneling** - Automatic public URL for local development
- ✅ **CSV logging** - Tracks all calls and orders

---

## 🏗️ Architecture

The system runs **2 servers** working together:

1. **Flask App (port 5000)** - Receives Twilio webhooks, returns TwiML
2. **WebSocket Server (port 5001)** - Handles real-time audio streaming between Twilio ↔ OpenAI

```
Phone Call → Twilio → Flask (/voice-ai) → WebSocket Server → OpenAI Realtime API
                                              ↓
                                         Audio conversion
                                      (mulaw 8kHz ↔ PCM16 24kHz)
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Add your credentials to the `.env` file:

```env
# Twilio (required)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# OpenAI (required for AI features)
OPENAI_API_KEY=sk-xxxxxxxxxx

# Flask
PORT=5000
```

⚠️ **Get your OpenAI API key:** https://platform.openai.com/api-keys  
⚠️ **Important:** Never commit `.env` to version control!

---

### 3. Run the Application

**Option A: Run both servers with one command (recommended)**

```bash
python start.py
```

**Option B: Run manually in separate terminals**

Terminal 1:
```bash
python app.py
```

Terminal 2:
```bash
python websocket_server.py
```

The system will:
1. Start Flask on port 5000 with auto ngrok tunnel
2. Start WebSocket server on port 5001
3. Display the public ngrok URL

---

### 4. Configure Twilio Webhook

**IMPORTANT:** You need to expose BOTH ports via ngrok for the AI assistant to work.

**Step 1: Note your ngrok URL**  
From the Flask startup output, you'll see something like:
```
📡 Public URL: https://abc123.ngrok-free.app
```

**Step 2: Configure Twilio**
1. Go to [Twilio Console](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
2. Click your phone number
3. Under **Voice Configuration** → "A CALL COMES IN":
   - For AI Assistant: `https://abc123.ngrok-free.app/voice-ai` (POST)
   - For simple greeting: `https://abc123.ngrok-free.app/voice` (POST)
4. Click **Save**

**Step 3: Expose WebSocket port**  
The WebSocket server also needs a public URL. Run this in a new terminal:
```bash
ngrok http 5001
```
Note the URL (e.g., `https://xyz789.ngrok-free.app`) - this is automatically used by the system.

💡 **Alternative:** Use ngrok's config file to tunnel both ports with one command.

---

### 5. Test Your Setup

Call your Twilio number!

- **Simple test:** Use `/voice` endpoint → hears pre-recorded greeting
- **AI test:** Use `/voice-ai` endpoint → talks to AI assistant

**Example conversation with AI:**
```
You: "Hello, I need some medicine"
AI: "Hello! I'd be happy to help you with your medicine order. 
     What medication do you need?"
You: "Two strips of Dolo 650"
AI: "Got it, two strips of Dolo 650. May I have your delivery address?"
You: "21 MG Road, Pune"
AI: "Perfect! I've recorded your order. Is there anything else I can help you with?"
```

---

## 📁 Project Structure

```
app-phoneCall/
├── app.py                    # Flask webhook server
├── websocket_server.py       # WebSocket audio streaming server
├── start.py                  # Launcher script (runs both servers)
├── .env                      # Environment variables (API keys)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── logs/
    ├── call_logs.csv         # Basic call logs (all calls)
    └── ai_call_logs.csv      # AI call logs with transcripts
```

---

## 📊 Call Logs

### Basic Calls (`logs/call_logs.csv`)
All calls logged with: Timestamp, From, To, CallSid, Status

### AI Calls (`logs/ai_call_logs.csv`)
AI conversations logged with:
- Timestamp
- Caller number
- Medicine ordered
- Quantity
- Delivery address
- Full conversation transcript
- Call duration

---

## 🔧 Troubleshooting

### "No OpenAI API key" warning
- Add your OpenAI API key to `.env` file
- Get one at: https://platform.openai.com/api-keys
- Make sure it starts with `sk-`

### WebSocket connection fails
- Ensure BOTH ports (5000 and 5001) are exposed via ngrok
- Check that `websocket_server.py` is running
- Verify no firewall blocking port 5001

### Audio conversion errors
- Python's `audioop` module should be built-in
- If missing, try: `pip install audioop-lts`

### Ngrok URL changes
- Free ngrok URLs change on restart
- Update Twilio webhook each time you restart
- Or upgrade to paid ngrok for persistent domains

### Port already in use
- Change Flask port in `.env`: `PORT=8080`
- Make sure to update ngrok command accordingly

---

## 🎯 How It Works (Technical Details)

### Audio Format Conversion
Twilio sends audio as **mulaw 8kHz**, but OpenAI expects **PCM16 24kHz**. The WebSocket server handles conversion:

1. **Incoming (Twilio → OpenAI):**
   - Decode base64 mulaw → Convert mulaw to linear PCM → Resample 8kHz to 24kHz
2. **Outgoing (OpenAI → Twilio):**
   - Resample 24kHz to 8kHz → Convert linear PCM to mulaw → Encode base64

### Real-time Flow
```
Caller speaks → Twilio (mulaw 8kHz) 
    → WebSocket Server (converts to PCM16 24kHz) 
    → OpenAI Realtime API (transcribes + generates response)
    → WebSocket Server (converts to mulaw 8kHz)
    → Twilio (plays to caller)
```

### Session Management
Each call creates a `CallSession` object that:
- Maintains WebSocket connections to both Twilio and OpenAI
- Tracks conversation transcript
- Accumulates order details
- Logs everything to CSV when call ends

---

## 🚀 Next Steps

### Make it Production-Ready
1. Deploy to cloud (Heroku, AWS, GCP, Azure)
2. Use persistent URLs instead of ngrok
3. Add authentication/validation
4. Store logs in database instead of CSV
5. Add monitoring and error alerts

### Enhance AI Capabilities
1. Train AI to extract structured data (medicine, quantity, address)
2. Add confirmation step before finalizing orders
3. Integrate with pharmacy inventory system
4. Add payment processing
5. Send SMS confirmation after order

### Improve UX
1. Add hold music while AI thinks
2. Support multiple languages
3. Add voice authentication
4. Allow order modifications during call
5. Provide estimated delivery time

---

## 📞 API Endpoints

### `POST /voice`
Simple greeting endpoint (original functionality)
- Returns TwiML with pre-recorded message
- Logs call to `call_logs.csv`

### `POST /voice-ai`
AI assistant endpoint (new)
- Returns TwiML that connects call to WebSocket
- Streams audio to OpenAI Realtime API
- Logs conversation to `ai_call_logs.csv`

### `GET /`
Health check endpoint
- Returns server status and available endpoints

---

## 📚 Resources

- [Twilio Media Streams Docs](https://www.twilio.com/docs/voice/media-streams)
- [OpenAI Realtime API Docs](https://platform.openai.com/docs/guides/realtime)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [WebSockets in Python](https://websockets.readthedocs.io/)

---

Made with ❤️ - AI Voice Assistant for Medicine Orders
