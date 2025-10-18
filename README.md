

# Twilio AI Voice Assistant

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

### 4. Configure Twilio Webhook

1. Go to [Twilio Console → Phone Numbers → Manage Incoming Numbers](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
2. Click on your Twilio number (e.g., `+1XXXYYYZZZZ`)
3. Scroll to **Voice Configuration**
4. Under **“A CALL COMES IN”**, set:

   * **Webhook URL:** `https://your-ngrok-url.ngrok.io/voice`
   * **HTTP Method:** `POST`
5. Click **Save**

---

### 5. Test Your Setup

Call your Twilio number (e.g., **+1 (XXX) XXX-XXXX**)

You should hear:

> “Hello! Thanks for calling. For now, we are just testing this line.”

---

## 📁 Project Structure

```
app-phoneCall/
├── app.py              # Main Flask application
├── .env                # Environment variables (Twilio credentials)
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── logs/
    └── call_logs.csv   # Call logs (auto-created)
```

---

## 📊 Call Logs

All inbound calls are logged to `logs/call_logs.csv` with:

* Timestamp
* Caller number (From)
* Your Twilio number (To)
* Call SID
* Call Status

---

## 🔧 Troubleshooting

### Ngrok Issues

* Ensure ngrok is installed:

  ```bash
  pip install pyngrok
  ```
* If ngrok fails, run it manually:

  ```bash
  ngrok http 5000
  ```

  Then update the Twilio webhook with the new public URL.

### Port Already in Use

* Change the port in `.env`:

  ```
  PORT=8080
  ```

  Then rerun `python app.py`.

### Twilio Webhook Errors

* Ensure your ngrok URL is publicly accessible
* Webhook URL should end with `/voice`
* Verify HTTP method is set to `POST`

---

## 🎯 Future Extensions

This project can easily be extended for:

* **AI Streaming:** Add voice AI integration (OpenAI, ElevenLabs, etc.)
* **Order Capture:** Capture customer orders via natural conversation
* **Interactive Menus:** Add IVR (Interactive Voice Response) options
* **Call Recording:** Record calls for QA
* **Database Integration:** Store call logs in a database

---

## 📝 Notes

* The greeting uses Twilio’s text-to-speech with the “Alice” voice
* Calls automatically hang up after a short delay
* Ngrok free-tier URLs change on each restart

---

## 🔐 Security Best Practices

1. Never commit `.env` files to version control
2. Use environment variables on your hosting platform
3. Prefer Twilio API Key + Secret over Auth Token when possible
4. Validate incoming requests to ensure they originate from Twilio

---

## 📞 Support

* [Twilio Voice Documentation](https://www.twilio.com/docs/voice)
* [Flask Documentation](https://flask.palletsprojects.com/)
* [Ngrok Documentation](https://ngrok.com/docs)

---

Made with ❤️ for testing Twilio inbound calls

