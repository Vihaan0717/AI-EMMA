import subprocess
import time
import requests
import os
import sys

# Configure stdout/stderr to use UTF-8
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def test_server():
    print("Starting voice cloner server...")
    # Add project root to path
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    server_proc = subprocess.Popen(
        [sys.executable, "backend/services/voice_cloner_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True
    )
    
    # Wait for server to boot
    print("Waiting 40 seconds for XTTSv2 model load...")
    time.sleep(40)
    
    try:
        url = "http://localhost:8768/synthesize"
        payload = {
            "text": "Hello, this is a test of the dynamically cloned female voice agent.",
            "language": "en",
            "speaker_wav": os.path.abspath("Voicesamp/female_ref.wav")
        }
        print(f"Sending synthesize request to {url}...")
        res = requests.post(url, json=payload, timeout=60)
        
        if res.status_code == 200:
            print("Successfully synthesized audio!")
            output_file = "Voicesamp/cloned_test_output.wav"
            with open(output_file, "wb") as f:
                f.write(res.content)
            print(f"Cloned audio sample saved to: {output_file}")
            print(f"Output file size: {os.path.getsize(output_file)} bytes")
        else:
            print(f"Synthesis failed with status {res.status_code}: {res.text}")
            
    except Exception as e:
        print(f"Error calling server: {e}")
        # Print first few lines of server stdout/stderr
        print("Server stdout/stderr output:")
        try:
            outs, errs = server_proc.communicate(timeout=2)
            print("STDOUT:", outs)
            print("STDERR:", errs)
        except Exception as ex:
            print("Could not retrieve server output:", ex)
    finally:
        print("Stopping voice cloner server...")
        server_proc.terminate()
        server_proc.wait()
        print("Server stopped.")

if __name__ == "__main__":
    sys.exit(test_server())
