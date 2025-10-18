"""
AI Voice Assistant WebSocket Server
Handles real-time audio streaming between Twilio and OpenAI Realtime API
"""

import asyncio
import websockets
import json
import base64
import os
from datetime import datetime
from dotenv import load_dotenv
import audioop

# Load environment variables
load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_WS_URL = 'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01'

# Audio format constants
TWILIO_SAMPLE_RATE = 8000  # Twilio uses 8kHz mulaw
OPENAI_SAMPLE_RATE = 24000  # OpenAI expects 24kHz PCM16


class CallSession:
    """Manages a single call session with Twilio and OpenAI"""
    
    def __init__(self, call_sid):
        self.call_sid = call_sid
        self.stream_sid = None
        self.caller_number = None
        self.transcript = []
        self.order_details = {
            'medicine': None,
            'quantity': None,
            'address': None
        }
        self.openai_ws = None
        self.twilio_ws = None
        
    async def connect_to_openai(self):
        """Establish WebSocket connection to OpenAI Realtime API"""
        if not OPENAI_API_KEY:
            print("⚠️  WARNING: OPENAI_API_KEY not set in .env file")
            return None
            
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'OpenAI-Beta': 'realtime=v1'
        }
        
        try:
            self.openai_ws = await websockets.connect(
                OPENAI_WS_URL,
                extra_headers=headers
            )
            print(f"✅ Connected to OpenAI Realtime API for call {self.call_sid}")
            
            # Configure the session
            await self.configure_openai_session()
            return self.openai_ws
            
        except Exception as e:
            print(f"❌ Failed to connect to OpenAI: {e}")
            return None
    
    async def configure_openai_session(self):
        """Configure OpenAI session with instructions and voice settings"""
        config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": """You are a helpful pharmacy assistant. Your job is to:
1. Greet the caller warmly
2. Help them order medicines or answer pharmacy-related questions
3. For orders, collect: medicine name, quantity, and delivery address
4. Be conversational and natural
5. Confirm the order details before ending the call

Be friendly, efficient, and professional.""",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500
                }
            }
        }
        await self.openai_ws.send(json.dumps(config))
        print("📝 OpenAI session configured")
    
    def convert_mulaw_to_pcm16(self, mulaw_data):
        """Convert Twilio's mulaw 8kHz to OpenAI's PCM16 24kHz"""
        # Step 1: Convert mulaw to linear PCM (8kHz)
        pcm_8k = audioop.ulaw2lin(mulaw_data, 2)  # 2 bytes per sample
        
        # Step 2: Resample from 8kHz to 24kHz (3x upsampling)
        pcm_24k, _ = audioop.ratecv(
            pcm_8k, 2, 1,  # input: data, sample_width, channels
            TWILIO_SAMPLE_RATE,  # input rate
            OPENAI_SAMPLE_RATE,  # output rate
            None  # state (None for first call)
        )
        
        return pcm_24k
    
    def convert_pcm16_to_mulaw(self, pcm_data):
        """Convert OpenAI's PCM16 24kHz to Twilio's mulaw 8kHz"""
        # Step 1: Resample from 24kHz to 8kHz
        pcm_8k, _ = audioop.ratecv(
            pcm_data, 2, 1,
            OPENAI_SAMPLE_RATE,
            TWILIO_SAMPLE_RATE,
            None
        )
        
        # Step 2: Convert linear PCM to mulaw
        mulaw = audioop.lin2ulaw(pcm_8k, 2)
        
        return mulaw


async def handle_twilio_connection(websocket, path):
    """Handle incoming WebSocket connection from Twilio"""
    print(f"\n📞 New connection from Twilio: {websocket.remote_address}")
    
    session = None
    
    try:
        async for message in websocket:
            data = json.loads(message)
            event_type = data.get('event')
            
            # Handle different Twilio events
            if event_type == 'start':
                # Call started - initialize session
                start_data = data.get('start', {})
                call_sid = start_data.get('callSid')
                stream_sid = start_data.get('streamSid')
                
                session = CallSession(call_sid)
                session.stream_sid = stream_sid
                session.twilio_ws = websocket
                session.caller_number = start_data.get('customParameters', {}).get('from')
                
                print(f"🎬 Call started: {call_sid}")
                print(f"📱 From: {session.caller_number}")
                
                # Connect to OpenAI
                openai_ws = await session.connect_to_openai()
                
                if openai_ws:
                    # Start listening to OpenAI responses
                    asyncio.create_task(handle_openai_messages(session))
                else:
                    print("⚠️  Running in fallback mode (no OpenAI connection)")
            
            elif event_type == 'media':
                # Audio data from caller
                if session and session.openai_ws:
                    media = data.get('media', {})
                    payload = media.get('payload')
                    
                    if payload:
                        # Decode base64 mulaw audio
                        mulaw_audio = base64.b64decode(payload)
                        
                        # Convert to PCM16 24kHz for OpenAI
                        try:
                            pcm_audio = session.convert_mulaw_to_pcm16(mulaw_audio)
                            
                            # Send to OpenAI
                            audio_message = {
                                "type": "input_audio_buffer.append",
                                "audio": base64.b64encode(pcm_audio).decode('utf-8')
                            }
                            await session.openai_ws.send(json.dumps(audio_message))
                            
                        except Exception as e:
                            print(f"⚠️  Audio conversion error: {e}")
            
            elif event_type == 'stop':
                # Call ended
                print(f"📴 Call ended: {session.call_sid if session else 'unknown'}")
                
                if session:
                    # Log the session
                    log_call_session(session)
                    
                    # Close OpenAI connection
                    if session.openai_ws:
                        await session.openai_ws.close()
                
                break
    
    except websockets.exceptions.ConnectionClosed:
        print("🔌 Twilio connection closed")
    except Exception as e:
        print(f"❌ Error in Twilio handler: {e}")
    finally:
        if session and session.openai_ws:
            await session.openai_ws.close()


async def handle_openai_messages(session):
    """Listen for messages from OpenAI and forward audio to Twilio"""
    try:
        async for message in session.openai_ws:
            data = json.loads(message)
            event_type = data.get('type')
            
            # Handle different OpenAI events
            if event_type == 'response.audio.delta':
                # OpenAI is sending audio chunks
                audio_delta = data.get('delta')
                
                if audio_delta and session.twilio_ws:
                    # Decode PCM16 audio from OpenAI
                    pcm_audio = base64.b64decode(audio_delta)
                    
                    # Convert to mulaw 8kHz for Twilio
                    try:
                        mulaw_audio = session.convert_pcm16_to_mulaw(pcm_audio)
                        
                        # Send to Twilio
                        media_message = {
                            "event": "media",
                            "streamSid": session.stream_sid,
                            "media": {
                                "payload": base64.b64encode(mulaw_audio).decode('utf-8')
                            }
                        }
                        await session.twilio_ws.send(json.dumps(media_message))
                        
                    except Exception as e:
                        print(f"⚠️  Audio conversion error (OpenAI->Twilio): {e}")
            
            elif event_type == 'conversation.item.input_audio_transcription.completed':
                # Transcription of what caller said
                transcript = data.get('transcript', '')
                if transcript:
                    session.transcript.append({
                        'role': 'caller',
                        'text': transcript,
                        'timestamp': datetime.now().isoformat()
                    })
                    print(f"🗣️  Caller: {transcript}")
            
            elif event_type == 'response.text.delta':
                # AI's text response (for logging)
                text_delta = data.get('delta', '')
                if text_delta:
                    # Accumulate AI response text
                    if not session.transcript or session.transcript[-1]['role'] != 'assistant':
                        session.transcript.append({
                            'role': 'assistant',
                            'text': text_delta,
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        session.transcript[-1]['text'] += text_delta
            
            elif event_type == 'response.done':
                # AI finished responding
                if session.transcript and session.transcript[-1]['role'] == 'assistant':
                    print(f"🤖 AI: {session.transcript[-1]['text']}")
            
            elif event_type == 'error':
                error_data = data.get('error', {})
                print(f"❌ OpenAI error: {error_data}")
    
    except websockets.exceptions.ConnectionClosed:
        print("🔌 OpenAI connection closed")
    except Exception as e:
        print(f"❌ Error in OpenAI handler: {e}")


def log_call_session(session):
    """Log call session to CSV file"""
    import csv
    
    log_file = 'logs/ai_call_logs.csv'
    
    # Create file with headers if it doesn't exist
    file_exists = os.path.exists(log_file)
    
    with open(log_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        if not file_exists:
            writer.writerow([
                'Timestamp', 'CallSid', 'From', 'Medicine', 'Quantity', 
                'Address', 'Transcript', 'Duration'
            ])
        
        # Build full transcript
        full_transcript = ' | '.join([
            f"{item['role'].upper()}: {item['text']}" 
            for item in session.transcript
        ])
        
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            session.call_sid,
            session.caller_number,
            session.order_details.get('medicine', 'N/A'),
            session.order_details.get('quantity', 'N/A'),
            session.order_details.get('address', 'N/A'),
            full_transcript,
            'completed'
        ])
    
    print(f"📝 Call logged to {log_file}")


async def main():
    """Start the WebSocket server"""
    port = 5001
    
    print("\n" + "="*60)
    print("🤖 AI Voice Assistant WebSocket Server")
    print("="*60)
    
    if not OPENAI_API_KEY:
        print("\n⚠️  WARNING: OPENAI_API_KEY not set!")
        print("📝 Add it to your .env file to enable AI features")
        print("   For now, server will run but AI won't respond\n")
    
    server = await websockets.serve(
        handle_twilio_connection,
        '0.0.0.0',
        port
    )
    
    print(f"\n✅ WebSocket server running on ws://0.0.0.0:{port}")
    print(f"📡 Ready to receive Twilio Media Streams")
    print("\n💡 Make sure your Flask app is also running on port 5000")
    print("   to serve the initial webhook\n")
    print("="*60 + "\n")
    
    await server.wait_closed()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down WebSocket server...")
