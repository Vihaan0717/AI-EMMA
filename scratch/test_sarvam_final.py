import requests
import json

def test_sarvam():
    url = "http://localhost:11434/api/generate"
    system = "You are a helpful Telugu assistant."
    prompt = "Annaya, ela unnaru?"
    
    # Matching the modelfile template
    full_prompt = f"<s>[SYSTEM_PROMPT]{system}[/SYSTEM_PROMPT][INST]{prompt}[/INST]<think>"
    
    payload = {
        "model": "mashriram/sarvam-m",
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "stop": ["</s>", "[INST]"]
        }
    }
    
    print(f"Sending request to Sarvam-M...")
    r = requests.post(url, json=payload)
    response = r.json()['response']
    
    with open("scratch/test_sarvam_final.txt", "w", encoding="utf-8") as f:
        f.write(response)
    print("Done. Saved to scratch/test_sarvam_final.txt")

if __name__ == "__main__":
    test_sarvam()
