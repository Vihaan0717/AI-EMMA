import socket
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def check_host(host, port):
    print(f"Checking {host}:{port}...")
    try:
        # 1. Low level socket check
        ais = socket.getaddrinfo(host, port)
        print(f"  - Socket getaddrinfo: SUCCESS ({ais[0][4]})")
        
        # 2. Try to connect
        with socket.create_connection((host, port), timeout=3):
            print(f"  - Socket Connection: SUCCESS")
    except Exception as e:
        print(f"  - ERROR: {e}")

def check_http(url):
    print(f"Checking HTTP {url}...")
    try:
        res = requests.get(url, timeout=3)
        print(f"  - HTTP Status: {res.status_code}")
    except Exception as e:
        print(f"  - ERROR: {e}")

print("--- Network Diagnostic ---")
print(f"CWD: {os.getcwd()}")
print(f"OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL')}")

# Check Localhost
check_host("127.0.0.1", 11434)
check_http("http://127.0.0.1:11434")

# Check Google (Cloud)
check_host("generativelanguage.googleapis.com", 443)
check_http("https://generativelanguage.googleapis.com")

print("--- End Diagnostic ---")
