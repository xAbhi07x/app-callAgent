# 🚀 SIMPLE SETUP GUIDE - AI Voice Assistant

## ⚠️ IMPORTANT: Read This First!

This system needs **2 ngrok tunnels** running simultaneously:
- One for Flask (port 5000)
- One for WebSocket server (port 5001)

---

## 📝 Step-by-Step Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Add OpenAI API Key
Open `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
```
Get one at: https://platform.openai.com/api-keys

---

### Step 3: Start the Servers

Run this command:
```bash
python start.py
```

This will start BOTH servers. You'll see output like:
```
1️⃣  Starting Flask webhook server (port 5000)...
2️⃣  Starting WebSocket server (port 5001)...
```

---

### Step 4: Expose via ngrok (IMPORTANT!)

You need to run ngrok to expose your local servers to the internet.

**METHOD 1: Simple (Two terminals)**

Terminal 1:
```bash
ngrok http 5000
```
Note the URL (e.g., `https://abc123.ngrok-free.app`)

Terminal 2:
```bash
ngrok http 5001  
```
Note the URL (e.g., `https://xyz789.ngrok-free.app`)

**METHOD 2: Advanced (One command)**

If you have ngrok paid account:
1. Add your authtoken to `ngrok.yml`
2. Run: `ngrok start --all --config ngrok.yml`

---

### Step 5: Configure Twilio

1. Go to https://console.twilio.com/
2. Navigate to Phone Numbers → Active Numbers
3. Click your number
4. Under "Voice Configuration" → "A CALL COMES IN":
   - URL: `https://abc123.ngrok-free.app/voice-ai`
   - HTTP: POST
5. Save

---

### Step 6: Update WebSocket URL in Code

**IMPORTANT:** The Flask app needs to know where the WebSocket server is!

Open `app.py` and find the `/voice-ai` endpoint.
Update the `ws_url` to match your ngrok URL for port 5001:

```python
ws_url = "wss://xyz789.ngrok-free.app"  # Your WebSocket ngrok URL
```

---

### Step 7: Test!

Call your Twilio number. You should hear the AI assistant!

---

## 🐛 Troubleshooting

**"No module named websockets"**
→ Run: `pip install websockets`

**"OPENAI_API_KEY not set"**
→ Add it to your `.env` file

**AI doesn't respond**
→ Check that BOTH ngrok tunnels are running
→ Verify WebSocket server shows "Connected to OpenAI"

**Call connects but no audio**
→ Check WebSocket URL in `app.py` is correct
→ Make sure it uses `wss://` not `ws://`

---

## ✅ What Success Looks Like

When everything works, you'll see:

**Flask terminal:**
```
📡 Public URL: https://abc123.ngrok-free.app
🌐 Starting Flask server on port 5000...
```

**WebSocket terminal:**
```
✅ WebSocket server running on ws://0.0.0.0:5001
📡 Ready to receive Twilio Media Streams
```

**ngrok terminals:**
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:5000
Forwarding   https://xyz789.ngrok-free.app -> http://localhost:5001
```

---

## 📞 Making a Test Call

1. Call your Twilio number
2. Wait for AI to greet you
3. Say: "I need medicine"
4. AI will ask what you need
5. Say: "Two strips of Dolo 650"
6. AI will ask for address
7. Say: "21 MG Road Pune"
8. AI confirms and ends call

Check `logs/ai_call_logs.csv` to see the full transcript!

---

Need help? Check `README_AI.md` for full documentation.
