"""
Test script for JARVIS Local Brain Architecture
"""
import sys
import os

# Add root to sys.path
sys.path.append(os.getcwd())

from brain.neurons import JARVISBrain

def test():
    print("--- Brain Initialization ---")
    brain = JARVISBrain()
    
    print("\n--- Initial Stats ---")
    print(brain.stats())
    
    print("\n--- Learning Session ---")
    learned = brain.learn(
        user_message="naku chala okkate ga undi",
        jarvis_response="Arthamindi, Boss. Loneliness is hard, but I am here.",
        context={"language": "telugu", "intent": "distress", "emotion": "sadness"}
    )
    print("Learned:", learned)
    
    print("\n--- Thinking about 'chala' ---")
    thought = brain.think_about("chala")
    print("Knowledge:", thought["data"])
    print("Strongest Connections:", thought["strongest_connections"])
    
    print("\n--- Recalling Associations for 'okkate' ---")
    associations = brain.recall("okkate")
    for assoc in associations:
        print(f"-> {assoc['label']} ({assoc['connection']}) weight: {assoc['weight']}")

if __name__ == "__main__":
    test()
