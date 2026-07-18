import sys
import os

# Ensure the root project directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socket
import requests
from dotenv import load_dotenv
from config.system_config import JarvisConfig

load_dotenv()

def check_service(name, host, port, protocol="TCP"):
    print(f"Checking {name} ({host}:{port})...")
    try:
        # Low level socket check
        ais = socket.getaddrinfo(host, port)
        with socket.create_connection((host, port), timeout=3):
            print(f"  [UP] {name} Socket: OK")
            return True
    except Exception as e:
        print(f"  [DOWN] {name} Socket: FAILED ({e})")
        return False

def check_http(name, url):
    print(f"Checking {name} HTTP ({url})...")
    try:
        res = requests.get(url, timeout=5)
        print(f"  [UP] {name} HTTP: OK (Status {res.status_code})")
        return True
    except Exception as e:
        print(f"  [DOWN] {name} HTTP: FAILED ({e})")
        return False

def run_diagnostic():
    print("\n--- JARVIS-X NETWORK DIAGNOSTIC ---")
    
    # 1. Ollama
    ollama_url = JarvisConfig.OLLAMA_BASE_URL
    host = ollama_url.split("//")[-1].split(":")[0]
    port = int(ollama_url.split(":")[-1])
    check_service("Ollama", host, port)
    check_http("Ollama", ollama_url)
    
    # 2. Gemini
    check_service("Gemini API", "generativelanguage.googleapis.com", 443)
    
    # 3. Supabase
    if JarvisConfig.SUPABASE_URL:
        sub_host = JarvisConfig.SUPABASE_URL.split("//")[-1]
        check_service("Supabase", sub_host, 443)
    
    print("--- Diagnostic Complete ---\n")

if __name__ == "__main__":
    run_diagnostic()
