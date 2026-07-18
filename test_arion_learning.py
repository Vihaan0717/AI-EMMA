import os
from nexus_master import NexusMaster

def test_arion_learning():
    print("Testing Arion's Deep Learning Tool...\n")
    master = NexusMaster()
    
    # Path to the zip file
    zip_path = os.path.abspath("WhatsApp Chat with Amma.zip")
    
    if not os.path.exists(zip_path):
        print(f"File not found: {zip_path}")
        return
        
    print(f"Testing arion_learn_from_chat on {zip_path}")
    call_str = f'<CALL: arion_learn_from_chat("{zip_path}")>'
    tool, result = master.parse_and_execute_tool(call_str)
    
    print(f"\n--- Result from {tool} ---")
    print(result)

if __name__ == "__main__":
    test_arion_learning()
