# 🚀 QUICK START - Run Your AI Voice Assistant

## ✅ Your Setup is Complete!

All API keys are configured. Just follow these steps:

---

## 📝 Step-by-Step Instructions

### **Step 1: Start Both Servers**

Open a terminal and run:

```bash
python start.py
```

You should see:
```
1️⃣  Starting Flask webhook server (port 5000)...
2️⃣  Starting WebSocket server (port 5001)...
✅ Both servers are starting...
📡 Public URL: https://abc123.ngrok-free.app
```

**⚠️ Keep this terminal open!**

---

### **Step 2: Expose Port 5001 via ngrok**

Open a **NEW terminal** and run:

```bash
ngrok http 5001
```

You'll see something like:
```
Forwarding   https://xyz789.ngrok-free.app -> http://localhost:5001
```

**📝 Copy the ngrok URL** (e.g., `https://xyz789.ngrok-free.app`)

---

### **Step 3: Update WebSocket URL in .env**

Open the `.env` file and update this line:

```env
WEBSOCKET_URL=wss://xyz789.ngrok-free.app
```

Replace `your-ngrok-url-for-port-5001` with the URL from Step 2.

**Important:** Use `wss://` not `https://`

---

### **Step 4: Restart Flask Server**

In the first terminal:
1. Press `Ctrl+C` to stop the servers
2. Run `python start.py` again

This reloads the new WebSocket URL.

---

### **Step 5: Configure Twilio Webhook**

1. Go to: https://console.twilio.com/
2. Navigate to: **Phone Numbers** → **Manage** → **Active Numbers**
3. Click your number: `+1 (507) 565-0264`
4. Under **Voice Configuration** → "A CALL COMES IN":
   - **URL:** `https://abc123.ngrok-free.app/voice-ai`
     (Use the URL from Step 1, add `/voice-ai`)
   - **HTTP Method:** `POST`
5. Click **Save**

---

### **Step 6: Test It! 🎉**

**Call your Twilio number:** `+1 (507) 565-0264`

You should hear the AI assistant!

**Try saying:**
- "Hello, I need some medicine"
- "I want to order Dolo 650"
- "Can you help me?"

---

## 📊 Check the Logs

After the call, check:
- `logs/call_logs.csv` - Basic call info
- `logs/ai_call_logs.csv` - Full AI conversation transcript

---

## 🐛 Troubleshooting

### **AI doesn't respond / No audio**
- ✅ Check both servers are running
- ✅ Verify WEBSOCKET_URL in `.env` is correct
- ✅ Make sure it starts with `wss://` not `https://`
- ✅ Confirm ngrok is running on port 5001

### **"OPENAI_API_KEY not set" warning**
- ✅ Already set! Ignore if servers start fine

### **Call connects but hangs up immediately**
- ✅ Check Twilio webhook URL ends with `/voice-ai`
- ✅ Verify it's set to POST method

### **Still issues?**
Run this to test:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI Key:', os.getenv('OPENAI_API_KEY')[:10] + '...')"
```

Should show: `OpenAI Key: sk-proj-f8...`

---

## 🎯 What Success Looks Like

**Terminal 1 (Flask):**
```
📡 Public URL: https://abc123.ngrok-free.app
🌐 Starting Flask server on port 5000...
📞 AI call from +918709196524 at 20:15:32
```

**Terminal 2 (ngrok for port 5001):**
```
Forwarding   https://xyz789.ngrok-free.app -> http://localhost:5001
```

**Terminal 3 (start.py output):**
```
✅ WebSocket server running on ws://0.0.0.0:5001
📡 Ready to receive Twilio Media Streams
🎬 Call started: CA3b6b8f34...
✅ Connected to OpenAI Realtime API
🗣️  Caller: Hello, I need medicine
🤖 AI: Hello! I'd be happy to help...
```

---

## 🎉 You're All Set!

Your AI voice assistant is now live and ready to take calls!

**Next Steps:**
- Make test calls
- Check conversation logs
- Customize the AI instructions (in `websocket_server.py`)

**Need help?** Check `SETUP.md` for detailed documentation.
