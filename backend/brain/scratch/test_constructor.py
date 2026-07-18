"""
Test script for JARVIS Word Constructor Agent
"""
import sys
import os

# Add root to sys.path
sys.path.append(os.getcwd())

from brain.neurons import JARVISBrain
from brain.agents  import WordConstructorAgent

def test():
    # Set encoding for Windows console
    os.environ["PYTHONIOENCODING"] = "UTF-8"
    
    print("--- Brain Initialization ---")
    brain = JARVISBrain()
    
    print("\n--- Agent Initialization ---")
    agent = WordConstructorAgent(brain)
    
    print("\n--- Deconstructing 'chestunnanu' ---")
    analysis = agent.analyze_word("chestunnanu")
    
    print("\nWord:", analysis["word"])
    print("Meaning:", analysis["constructed_meaning"])
    print("Confidence:", analysis["confidence"])
    print("Breakdown:", analysis["breakdown_display"])
    print("Question:", analysis["question"])
    
    print("\n--- Simulating User Feedback (Correct) ---")
    feedback = agent.process_feedback("chestunnanu", is_correct=True)
    print("Result:", feedback["message"])
    
    print("\n--- Verification: Checking Brain for 'chestunnanu' ---")
    neuron = brain.graph.get_neuron("chestunnanu")
    if neuron:
        print("Neuron found in LTM!")
        print("Data:", neuron.data)
        print("Strength:", neuron.strength)
    else:
        print("Error: Neuron not saved!")

if __name__ == "__main__":
    test()
