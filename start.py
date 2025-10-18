"""
Launcher for AI Voice Assistant
Starts both Flask app and WebSocket server
"""

import subprocess
import sys
import time
import os

def main():
    print("\n" + "="*60)
    print("🚀 Starting AI Voice Assistant System")
    print("="*60 + "\n")
    
    # Check if .env has OpenAI key
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  WARNING: OPENAI_API_KEY not set in .env")
        print("📝 The system will run but AI features won't work")
        print("   Add your OpenAI API key to .env to enable AI\n")
        time.sleep(2)
    
    processes = []
    
    try:
        # Start Flask app (port 5000)
        print("1️⃣  Starting Flask webhook server (port 5000)...")
        flask_process = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append(('Flask', flask_process))
        time.sleep(3)  # Give Flask time to start
        
        # Start WebSocket server (port 5001)
        print("2️⃣  Starting WebSocket server (port 5001)...")
        ws_process = subprocess.Popen(
            [sys.executable, 'websocket_server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append(('WebSocket', ws_process))
        
        print("\n" + "="*60)
        print("✅ Both servers are starting...")
        print("="*60)
        print("\n📝 Check terminal output above for:")
        print("   - Ngrok public URL")
        print("   - WebSocket server status")
        print("\n💡 Press Ctrl+C to stop both servers\n")
        
        # Keep script running and monitor processes
        while True:
            for name, process in processes:
                if process.poll() is not None:
                    print(f"\n❌ {name} server stopped unexpectedly!")
                    raise KeyboardInterrupt
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        for name, process in processes:
            process.terminate()
            print(f"   ✓ {name} server stopped")
        print("\n👋 Goodbye!\n")
        sys.exit(0)

if __name__ == '__main__':
    main()
